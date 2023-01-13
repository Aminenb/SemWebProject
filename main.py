from flask import Flask, render_template, request
from flask import jsonify
import rdflib
import json
import requests
from base64 import b64encode
from courses import events
from externalevents import events2
from next import eventsn
app=Flask(__name__)



@app.route('/delete/<string:item>/')
def delete_item(item):
    url="https://territoire.emse.fr/ldp/Fadl_NaitBachir/"+item
    username = 'ldpuser'
    password = 'LinkedDataIsGreat'

    credentials = f'{username}:{password}'.encode('utf-8')
    encoded_credentials = b64encode(credentials).decode('utf-8')
    slug = 'Fadl_NaitBachir'

    headers = {
        'Content-Type': 'text/turtle',
        'Authorization': f'Basic {encoded_credentials}',
        'Slug': slug,
    }
    response = requests.delete(url, headers=headers)
    del events[item+"/"]
    return render_template('json.html', all_events=events)




@app.route('/add_event/', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        newevent = request.form.get('turtle')

        server_url = 'https://territoire.emse.fr/ldp/FadlNaitBachir/events/'
        slug = 'Fadl_NaitBachir'
        username = 'ldpuser'
        password = 'LinkedDataIsGreat'

        # Encode the username and password for the request
        credentials = f'{username}:{password}'.encode('utf-8')
        encoded_credentials = b64encode(credentials).decode('utf-8')

        headers = {
            'Content-Type': 'text/turtle',
            'Authorization': f'Basic {encoded_credentials}',
            'Slug': slug,
        }
        response = requests.post(server_url, headers=headers, data=str(newevent))
        return "The event is addad successefuly"
    return render_template('add_event.html')



@app.route('/update_event/<string:item>/', methods=['GET', 'POST'])
def update_event(item):
    if request.method == 'POST':
        title = request.form.get('title')
        location = request.form.get('location')
        startDate = request.form.get('startDate')
        endDate = request.form.get('endDate')
        description = request.form.get('description')
        new_values = [title, location, startDate, endDate, description]
        url = "https://territoire.emse.fr/ldp/FadlNaitBachir/courses/"+item
        source_url = "https://territoire.emse.fr/ldp/FadlNaitBachir/courses/"
        # récupération de la ressource existante
        username = 'ldpuser'
        password = 'LinkedDataIsGreat'

        credentials = f'{username}:{password}'.encode('utf-8')
        encoded_credentials = b64encode(credentials).decode('utf-8')
        slug = 'Fadl_NaitBachir'

        headers = {
            'Content-Type': 'text/turtle',
            'Authorization': f'Basic {encoded_credentials}',
            'Slug': slug,
        }
        response = requests.get(url, headers=headers)
        data = response.text
        g = rdflib.Graph()
        g.parse(data=data, format='turtle')
        predicate = ['title', 'location', 'startDate', 'endDate', 'description']
        predicates = [rdflib.URIRef('https://schema.org/' + item) for item in predicate]
        old_triples = []
        for x in predicates:
            result = g.triples((None, x, None))
            for s, p, o in result:
                old_triple = (s, p, o)
                old_triples.append(old_triple)
        new_triples = []
        for w in old_triples:
            new_triples.append((w[0], w[1], rdflib.Literal(new_values[old_triples.index(w)])))
            print(new_triples[old_triples.index(w)])
        for w in old_triples:
            g.remove(w)
            g.add(new_triples[old_triples.index(w)])
        g.remove((rdflib.term.URIRef(url), rdflib.term.URIRef('http://www.w3.org/ns/ldp#hasMemberRelation'),
                  rdflib.term.URIRef('http://www.w3.org/ns/ldp#member')))
        g.remove((rdflib.term.URIRef(url), rdflib.term.URIRef('https://carbonldp.com/ns/v1/platform#modified'), None))
        g.remove((rdflib.term.URIRef(url), rdflib.term.URIRef('https://carbonldp.com/ns/v1/platform#created'), None))
        g.remove((rdflib.term.URIRef(url), rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
                  rdflib.term.URIRef('http://www.w3.org/ns/ldp#Container')))
        g.remove((rdflib.term.URIRef(url), rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
                  rdflib.term.URIRef('http://www.w3.org/ns/ldp#RDFSource')))
        g.remove((rdflib.term.URIRef(url), rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
                  rdflib.term.URIRef('http://www.w3.org/ns/ldp#BasicContainer')))
        g.remove((rdflib.term.URIRef(url), rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
                  rdflib.term.URIRef('http://www.w3.org/ns/ldp#Resource')))
        g.remove((rdflib.term.URIRef(url), rdflib.term.URIRef('http://www.w3.org/ns/ldp#hasMemberRelation'),
                  rdflib.term.URIRef('http://www.w3.org/ns/ldp#member')))
        g.remove((rdflib.term.URIRef(url), rdflib.term.URIRef('http://www.w3.org/ns/ldp#membershipResource'),
                  rdflib.term.URIRef(url)))
        g.remove((rdflib.term.URIRef(url), rdflib.term.URIRef('http://www.w3.org/ns/ldp#insertedContentRelation'),
                  rdflib.term.URIRef('http://www.w3.org/ns/ldp#MemberSubject')))
        g.remove((rdflib.term.URIRef(url), rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
                  rdflib.term.URIRef('https://carbonldp.com/ns/v1/platform#Document')))
        res=""
        for s in g:
            res+=str(s)+"\n"
        new_resource = g.serialize(format='turtle')
        response = requests.delete(url, headers=headers)
        response = requests.post(source_url, headers=headers, data=new_resource)
        if response.status_code == 201:
            events[item+'/']['title']=title
            events[item + '/']['location'] =location
            events[item + '/']['description'] =description
            events[item + '/']['start_date'] =startDate
            events[item + '/']['end_date'] =endDate
            return "The event is updated successefuly"
    return render_template('update_event.html', thisevent=jsonify(events[item+'/']))


@app.route('/addevents/')
def addevents():
    return render_template('add_event.html')


@app.route('/nextevents/')
def nextevents():
    return render_template('nextevents.html', next_events=eventsn)


@app.route('/extevents/')
def extevents():
    return render_template('extevents.html', ext_events=events2)


@app.route('/json/')
def jsondata():
    return render_template('json.html', all_events=events)

@app.route('/')
def index():
    return render_template('json.html', all_events=events)
if __name__ == '__main__':
    app.run(debug=True)

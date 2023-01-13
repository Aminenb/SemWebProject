import json
import requests
from base64 import b64encode

url =  'https://territoire.emse.fr/ldp/FadlNaitBachir/courses/'

query = f"""PREFIX ldp: <http://www.w3.org/ns/ldp#>
PREFIX sh: <https://schema.org/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT ?resource ?start_date ?end_date ?desc ?tit ?loc
WHERE {{
    <{url}> ldp:member ?resource .
    ?resource sh:startDate ?start_date;
         sh:endDate ?end_date;
         sh:description ?desc;
         sh:title ?tit;
         sh:location ?loc.
    FILTER(?start_date > NOW())
}}
"""

username = 'ldpuser'
password = 'LinkedDataIsGreat'

# Encode the username and password for the request
credentials = f'{username}:{password}'.encode('utf-8')
encoded_credentials = b64encode(credentials).decode('utf-8')

headers = {
    "Accept": "application/sparql-results+json",
    "Content-Type": "application/sparql-query",
    'Authorization': f'Basic {encoded_credentials}'
}
response = requests.post(url, headers=headers, data = query)
eventsn = {}
events = response.json()
for i in range (len(events['results']['bindings'])):
    data = events['results']['bindings'][i]
    eventsn[data["resource"]["value"].\
          split('https://territoire.emse.fr/ldp/FadlNaitBachir/courses/')[1]] = \
          {'start_date': data['start_date']['value'], 'description':data['desc']['value'],\
          'end_date':data['start_date']['value'],'location':data['loc']['value'],\
          'title':data['tit']['value']}















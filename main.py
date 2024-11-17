import json
import urllib.request
import boto3
url = 'https://data.sanjoseca.gov/api/3/action/datastore_search?resource_id=15408d78-9734-4ea1-b3e5-a0f99568dd9b'  
fileobj = urllib.request.urlopen(url)
response_dict = json.loads(fileobj.read())
data = response_dict['result']['records']

for d in data:
    print(d['Name'] + ' ' + d['CrashDateTime'] + ' ' + d['CollisionType'] + ' ' + d['Longitude'] + ' ' + d['Latitude'])





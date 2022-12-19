import json
import requests

from tresjolie import JOURNEYS_API, ENDPOINT_STOP_POINTS


url = JOURNEYS_API + ENDPOINT_STOP_POINTS
r = requests.get(url)
json_data = r.json()
stops = json_data['body']
    
names = {}
for s in stops:
    name = s['name']
    if name in names:
        names[name].append(s)
    else:
        names[name] = [s]

dup_count = 0
for n in names:
    name_list = names[n]
    if len(name_list) > 1:
        print(n, len(name_list))
        dup_count += 1

print(len(names))
print(dup_count)

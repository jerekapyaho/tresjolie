import json
import sys

with open(sys.argv[1], 'r') as f:
    data = json.load(f)

stop_data = data['body']
all_stops = []
for raw_stop in stop_data:
    location = raw_stop['location']
    location_parts = location.split(',')
    latitude = float(location_parts[0])
    longitude = float(location_parts[1])
    stop = {'code': raw_stop['shortName'],
            'name': raw_stop['name'],
            'lat': latitude,
            'lon': longitude,
            'muni': raw_stop['municipality']['shortName']}
    all_stops.append(stop)

with open(sys.argv[2], 'w') as out_file:
    json.dump(all_stops, out_file)

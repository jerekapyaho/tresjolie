import sys
import json

from tresjolie import Stop

def read_stops(stop_file_name):
    stop_data = None
    with open(stop_file_name) as stop_file:
        stop_data = json.load(stop_file)
    stops = []
    for s in stop_data['stops']:
        stops.append(Stop(s['code'], s['name'], s['latitude'], s['longitude']))
    return stops

def stops_by_name(stops):
    index = {}
    for stop in stops:
        index.setdefault(stop.name, []).append(stop)
    return index

if __name__ == '__main__':
    stop_file_name = sys.argv[1]
    stops = read_stops(stop_file_name)
    print(len(stops))

    by_name = stops_by_name(stops)
    print(by_name)

    # Take only stop names with more than one entry on the list
    multiples = {}
    for k in by_name.keys():
        if len(by_name[k]) > 1:
            multiples[k] = by_name[k]
    print(len(multiples))

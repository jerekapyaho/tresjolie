# Update the stops and lines in a Firebase realtime database instance

import os
import sys
import requests
import logging
import argparse
import json

def read_json_data(json_filename):
    json_data = None
    with open(json_filename) as json_file:
        json_data = json.load(json_file)
    return json_data    

db_url = os.environ['FIREBASE_DB_URL']

# Direct logs to standard output too
root_logger = logging.getLogger()
log_handler = logging.StreamHandler(sys.stdout)
log_handler.setLevel(logging.INFO)
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_handler.setFormatter(log_formatter)

def get_current_stops():
    url = db_url + '/stop.json'
    r = requests.get(url)
    json_data = r.json()

    # Firebase returns the data as one object. It is keyed by stop ID.
    stop_ids = list(json_data.keys())
    stops = []
    for s in stop_ids:
        # print('%s: %s' % (s, json_data[s]))
        stops.append(json_data[s])

    return stops

def test_removal():
    current = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    removed = {3, 6, 7}
    final = [x for x in current if not x in removed]
    print('%s -- %s -- %s' % (current, removed, final))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Populate an empty Firebase database from a JSON file.')
    parser.add_argument('-j', '--json', help='Name of JSON data file')
    args = parser.parse_args()

    current_stops = get_current_stops()
    print('Got %d stops from Firebase' % len(current_stops))

    fresh_stops = read_json_data(args.json)['stops']
    print('Got %d fresh stops from JSON file' % len(fresh_stops))

    # Find new stops (stops which are in the fresh stops list but not in current)
    current_stop_codes = [s['code'] for s in current_stops]
    fresh_stop_codes = [s['code'] for s in fresh_stops]
    added_stop_codes = set(current_stop_codes) - set(fresh_stop_codes)
    print('Added stops: %s' % added_stop_codes)

    removed_stop_codes = set(fresh_stop_codes) - set(current_stop_codes)
    print('Removed stops: %s' % removed_stop_codes)

    stops = []

    print('Removing stops')
    for s in current_stops:
        code = s['code']
        if code in removed_stop_codes:
            print('DELETE %s' % code)
        else:
            print('%s not in current stops' % code)
            stops.append(s)

    print('Adding stops')
    for s in fresh_stops:
        code = s['code']
        if code in added_stop_codes:
            print('PUT %s' % code)
            stops.append(s)            

    print('Final list has %d stops' % len(stops))

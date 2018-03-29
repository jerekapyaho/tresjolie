# Update the stops and lines in a Firebase realtime database instance

import os
import sys
import requests
import logging
import argparse
import json

from tresjolie import Stop

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
        new_stop = Stop.from_json(json_data[s])
        print(new_stop)
        stops.append(new_stop)

    return stops

def test_removal():
    current = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    removed = {3, 6, 7}
    final = [x for x in current if not x in removed]
    print('%s -- %s -- %s' % (current, removed, final))

def test_equal():
    stop1 = Stop('0001', 'Keskustori M', 61.49751, 23.76151, None, ['4', '4Y'], '837', 'A')
    stop2 = Stop('0001', 'Keskustori M', 61.49751, 23.76151, None, ['4', '4Y'], '837', 'A')
    print(stop1 == stop2)
    stop2 = Stop('0001', 'Keskustori M', 61.49752, 23.76151, None, ['4', '4Y'], '837', 'A')
    print(stop1 == stop2)

# Transform lines from "lines":["4", "4Y"] to "lines":{"4": true, "4Y": true}
# for Firebase
def lines_transformed_for_firebase(stop):
    transformed_lines = {}
    for line in stop.lines:
        transformed_lines[line] = True
    return transformed_lines

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Populate an empty Firebase database from a JSON file.')
    parser.add_argument('-j', '--json', help='Name of JSON data file')
    args = parser.parse_args()

    current_stops = get_current_stops()
    print('Got %d stops from Firebase' % len(current_stops))

    fresh_stop_data = read_json_data(args.json)['stops']
    fresh_stops = []
    for json_data in fresh_stop_data:
        fresh_stops.append(Stop.from_json(json_data))
    print('Got %d fresh stops from JSON file' % len(fresh_stops))

    # Find new stops (stops which are in the fresh stops list but not in current)
    current_stop_codes = [s.code for s in current_stops]
    fresh_stop_codes = [s.code for s in fresh_stops]
    removed_stop_codes = set(current_stop_codes) - set(fresh_stop_codes)
    print('Removed stops: %s' % sorted(list(removed_stop_codes)))
    added_stop_codes = set(fresh_stop_codes) - set(current_stop_codes)
    print('Added stops: %s' % sorted(list(added_stop_codes)))

    stops = []

    print('Removing stops')
    for s in current_stops:
        if s.code in removed_stop_codes:
            print('curl -X DELETE "%s/stop/%s.json"' % (db_url, s.code))
        else:
            stops.append(s)

    print('Adding stops')
    for s in fresh_stops:
        if s.code in added_stop_codes:
            s.lines = lines_transformed_for_firebase(s)
            print('curl -X PUT -d "%s" "%s/stop/%s.json"' % (json.dumps(s.as_json()), db_url, s.code))
            stops.append(s)            
    
    print('Final list has %d stops' % len(stops))

    fresh_stops_dict = {}
    for s in fresh_stops:
        fresh_stops_dict[s.code] = s
    #print('Fresh stops in dict: %s' % fresh_stops_dict)

    differing_stops = []
    for s in stops:
        fresh_stop = fresh_stops_dict[s.code]
        if s == fresh_stop:
            #print('%s OK' % s.code)
            pass
        else:
            diff = s.difference_to(fresh_stop)
            if diff != {}:
                print('%s diff: %s' % (s.code, diff))
                differing_stops.append(s)
    #print('Differing stops: %s' % differing_stops)
    print('There are %d differing stops' % len(differing_stops))

    for s in differing_stops:
        # TODO: Create proper JSON payload for patches
        print('curl -X PATCH -d "TBD" "%s/stop/%s.json"' % (db_url, s.code))

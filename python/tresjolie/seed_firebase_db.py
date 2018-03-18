# Initially populate a new, empty Firebase Realtime Database

import os
import sys
import requests
import logging
import argparse
import json
import geohash

import google
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

scopes = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/firebase.database'
    ]

def read_json_data(json_filename):
    json_data = None
    with open(json_filename) as json_file:
        json_data = json.load(json_file)
    return json_data    

db_url = os.environ['FIREBASE_DB_URL']
access_token = ''

# Direct logs to standard output too
root_logger = logging.getLogger()
log_handler = logging.StreamHandler(sys.stdout)
log_handler.setLevel(logging.INFO)
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_handler.setFormatter(log_formatter)

def put_stops(stops_data):
    headers = {'Authorization': 'Bearer %s' % access_token}

    for stop in stops_data:
        code = stop['code']

        transformed_lines = {}
        for line in stop['lines']:
            transformed_lines[line] = True
        stop['lines'] = transformed_lines
        url = db_url + '/stop/%s.json' % code
        r = requests.put(url, headers=headers, data=json.dumps(stop))
        status = r.status_code
        print('PUT %s - %s - %s' % (url, status, json.dumps(stop)))
    
def put_lines(lines_data):
    headers = {'Authorization': 'Bearer %s' % access_token}

    for line in lines_data:
        line_name = line['name']
        url = db_url + '/line/%s.json' % line_name
        r = requests.put(url, headers=headers, data=json.dumps(line))
        status = r.status_code
        print('PUT %s - %s - %s' % (url, status, json.dumps(line)))
        
def put_stops_locations(stops_data):
    headers = {'Authorization': 'Bearer %s' % access_token}

    for stop in stops_data:
        code = stop['code']

        lat = stop['latitude']
        lon = stop['longitude']
        gh = geohash.encode(lat, lon, precision=10)  # match GeoFire default precision
        data = {'g': gh,
                'l': {'0': lat, '1': lon}}
        url = db_url + '/stop_location/%s.json' % code
        r = requests.put(url, headers=headers, data=json.dumps(data))
        status = r.status_code
        print('PUT %s - %s - %s' % (url, status, json.dumps(data)))
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Populate an empty Firebase database from a JSON file.')
    parser.add_argument('-j', '--json', help='Name of JSON data file')
    parser.add_argument('-k', '--keys', help='Firebase service account key file')
    args = parser.parse_args()

    keys = args.keys
    credentials = service_account.Credentials.from_service_account_file(keys, scopes=scopes)
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)
    access_token = credentials.token

    data = read_json_data(args.json)
    print(len(data['stops']))
    put_stops(data['stops'])

    print(len(data['lines']))
    put_lines(data['lines'])

    put_stops_locations(data['stops'])


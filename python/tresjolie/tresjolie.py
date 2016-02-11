import csv
import sys
import codecs
import json
import argparse
import re
import os
import requests

def natural_sort_key(s, _nsre=re.compile('([0-9]+)')):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(_nsre, s)]

class Stop:
    def __init__(self, code, name, latitude, longitude, direction=None, lines=[], municipality='', zone=''):
        self.code = code
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.direction = direction
        self.lines = lines
        self.municipality = municipality
        self.zone = zone

    def as_csv(self):
        stop_lines = ' '.join(self.lines)
        return '%d,%s,%s,%.5f,%.5f,%s,%s,%s,%s' % (int(self.code), self.code, self.name, self.latitude, self.longitude, self.direction or '', stop_lines, self.municipality, self.zone)

    def as_json(self):
        result = {'code': self.code, 
                 'name': self.name, 
                 'latitude': self.latitude, 
                 'longitude': self.longitude,
                 'lines': self.lines,
                 'municipality': self.municipality,
                 'zone': self.zone}
                 
        # Omit the direction value if it is not set
        if self.direction != None:
            result['direction'] = self.direction
        
        return result    

    def as_java(self):
        stop_lines = ' '.join(self.lines)
        src_template = 'stops.add(new Stop(%d, "%s", "%s", %s, %s, "%s", "%s", "%s", "%s"));'
        return src_template % (int(self.code), self.code, self.name, self.latitude, self.longitude, self.direction or '', stop_lines, self.municipality, self.zone) 
                            
    def as_source(self, src):
        result = None
    
        if src == 'csv':
            result = self.as_csv()
        elif src == 'json':
            result = self.as_json()
        elif src == 'java':
            result = self.as_java()
        
        return result
        
    def __repr__(self):
        fmt = 'Stop: code=%s name="%s" latitude=%.5f longitude=%.5f'
        return fmt.format(self.code, self.name, self.latitude, self.longitude)


def read_dirs(dir_file):
    dirs = {}
    f = open(dir_file, 'r')
    try:
        reader = csv.reader(f)
        row_num = 0
        for row in reader:
            dirs[row[0]] = row[1]
            row_num += 1
    finally:
        f.close()
    return dirs    
    

# Use the Journeys API to get stop points.
# See http://wiki.itsfactory.fi/index.php/Journeys_API
JOURNEYS_API = 'http://data.itsfactory.fi/journeys/api/1/'
ENDPOINT_STOP_POINTS = 'stop-points'  # returns all stop points
ENDPOINT_JOURNEYS = 'journeys'
ENDPOINT_LINES = 'lines'

def lines_for_stop(stop_code):
    url = JOURNEYS_API + ENDPOINT_LINES
    #print('Loading lines for stop %s from Journeys API, url = "%s"' % (stop_code, url))
    params = {'stopPointId': stop_code}
    r = requests.get(url, params=params)
    json_data = r.json()
    lines = json_data['body']
    print('stop %s - %d lines.' % (stop_code, len(lines)))
    stop_lines = []
    for line in lines:
        stop_lines.append({'name': line['name'], 'description': line['description']})
    return stop_lines


def collect(data_path, dir_file):
    dir_filename = os.path.join(data_path, dir_file)
    directions = read_dirs(dir_filename)
    print('Read %d stop directions from CSV file "%s".' % (len(directions), dir_filename))
    
    url = JOURNEYS_API + ENDPOINT_LINES
    #print('Loading lines from Journeys API, url = "%s"' % url)
    r = requests.get(url)
    json_data = r.json()
    lines = json_data['body']
    print('Read %d lines from Journeys API.' % len(lines))
        
    all_lines = [{'name': line['name'], 'description': line['description']} for line in lines]
    
    # Now we have a list of all the lines.

    url = JOURNEYS_API + ENDPOINT_STOP_POINTS
    #print('Loading stop points from Journeys API, url = "%s"' % url)
    r = requests.get(url)
    json_data = r.json()
    
    # The JSON returned from Journeys API is JSend-compatible.
    # See http://labs.omniti.com/labs/jsend for details.
    stops = json_data['body']
    print('Loaded %d stop points from Journeys API.' % len(stops))

    all_stops = []

    for s in stops:
        coords = s['location'].split(',')
        stop = Stop(s['shortName'], s['name'], float(coords[0]), float(coords[1]))

        stop.municipality = None
        if 'municipality' in s:
            stop.municipality = s['municipality']['shortName']
        stop.zone = s['tariffZone']
        
        stop_lines = lines_for_stop(stop.code)
        
        line_names = [line['name'] for line in stop_lines]
        stop.lines = sorted(line_names, key=natural_sort_key)
        
        stop.direction = None
        if stop.code in directions:
            stop.direction = directions[stop.code]
        
        all_stops.append(stop)

    data = {'stops': [], 'lines': all_lines}
    for stop in all_stops:
        data['stops'].append(stop.as_json())
    return data

            
def locate(latitude, longitude, distance):
    # Get a bounding box around the location
    sw_corner, ne_corner = geodesy.bounding_box(lat, lon, distance)
    location_param = 'location=%.5f,%.5f:%.5f,%.5f' % (sw_corner[0], sw_corner[1], ne_corner[0], ne_corner[1])

    url = JOURNEYS_API + ENDPOINT_STOP_POINTS
    params = {'location': location_param}
    r = requests.get(url, params=params)
    print('Loading stop points from %s' % url)
    
    json_data = r.json()
    return json_data['body']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Load stop points and lines from Journeys API and generate JSON, or report stops within a given distance from the specified location.')
    parser.add_argument('action', help='What to do; one of collect | locate')
    parser.add_argument('-d', '--distance', type=float, help='Distance from current location in kilometers', default=0.5)
    parser.add_argument('-i', '--dirfile', help='Filename of directions CSV file', default='stop_directions.csv')
    parser.add_argument('-p', '--path', help='Path of related data files', default='.')
    parser.add_argument('-a', '--latitude', help='Latitude of current location in decimal degrees', type=float)
    parser.add_argument('-o', '--longitude', help='Longitude of current location in decimal degrees', type=float)    
    args = parser.parse_args()

    if args.action == 'collect':
        data = collect(args.path, args.dirfile)
        print(json.dumps(data))
    elif args.action == 'locate':
        nearest_stops = locate(args.latitude, args.longitude, args.distance)
        for stop in nearest_stops:
            print('%s %s' % (stop['shortName'], stop['name']))        
    else:
        print('Unknown action:', args.action)
        parser.print_help()

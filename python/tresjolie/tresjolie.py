# Generate source code from the stops list.
# Pass an argument to determine the output language: java, csharp, objc.
# Uses several input files to synthesize the data.

# Note: requires Python 3 for Unicode-aware CSV handling

import csv
import sys
import codecs
import pprint
import json
import itertools
import statistics # Python 3.4 or later
import argparse
import re
import os
import requests

import geodesy # pull in our own utility functions

# Credit: http://stackoverflow.com/questions/2870466/python-histogram-one-liner
def histogram(L):
    d = {}
    for x in L:
        if x in d:
            d[x] += 1
        else:
            d[x] = 1
    return d
    
    
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

def csv_main(args):
    # Look at the command line to find out which type of output is wanted.
    src_language = args.source
    if src_language == 'java':
        src_template = 'stops.add(new Stop(%d, "%s", "%s", %s, %s, "%s", "%s", "%s"));'
    elif src_language == 'csharp':
        src_template = 'stopsDb.Stops.InsertOnSubmit(new Stop() { ID = %d, Code = "%s", Name = "%s", Latitude = %s, Longitude = %s, Direction = "%s", Lines = "%s", Municipality = "%s" });'
    elif src_language == 'objc':
        src_template = '[[BMStop alloc] initWithDictionary:@{ @"stopID": @(%d), @"stopCode": @"%s", @"stopName": @"%s", @"stopLatitude": @(%s), @"stopLongitude": @(%s), @"stopDirection": @"%s", @"stopLines": @"%s", @"stopMuni": @"%s" }],'
    elif src_language == 'csv':
        src_template = '%d,%s,%s,%s,%s,%s,%s,%s'
    elif src_language == 'sql':
        src_template = 'INSERT INTO stop VALUES (%d, "%s", "%s", %s, %s, "%s", "%s", "%s");'
    elif src_language == 'json':
        pass # Will handle JSON as a special case
    else:
        print('Can\'t handle:', src_language)
        sys.exit(-1)

    #print('Source code to generate: ', src_language)

    data_path = args.path
    
    # Set this to True if there is something wrong with the results
    check_output = False
    
    # Dictionary, where each entry has key = stop ID, value = other stop attributes
    all_stops = {}

    data_filename = data_path + args.filename
    
    # Read the master stops file and create entries in all_stops.
    # NOTE: We will treat all values as strings since we're generating source code.
    # If we need to do calculations, the latitude and longitude values are 
    # explicitly converted to floats as needed.   
    with codecs.open(data_filename, encoding='utf-8') as infile:
        reader = csv.reader(infile)
        for columns in reader:
            stop_id = int(columns[0])
            
            the_stop = dict(stop_id=stop_id, stop_code=columns[1], stop_name=columns[2], stop_lat=columns[3], stop_lon=columns[4])
            all_stops[stop_id] = the_stop
        infile.close()

    #print('number of stops = %d' % (len(all_stops)))
    #print('all_stops = ', all_stops)
        
    infile = codecs.open(data_path + 'stop_lines.csv', 'rb', encoding='utf-8')
    try:
        reader = csv.reader(infile)
        for row in reader:
            stop_id = int(row[0])
            stop_lines = row[1]

            if stop_id in all_stops:
                stop = all_stops[stop_id]
                stop['stop_lines'] = stop_lines
            else:
                print('no stop %d found for lines' % (stop_id))
                check_output = True
    finally:
        infile.close()

    infile = codecs.open(data_path + 'stop_directions.csv', 'rb', encoding='utf-8')
    try:
        reader = csv.reader(infile)
        for row in reader:
            stop_id = int(row[0])
            stop_dir = row[1]
            
            if stop_id in all_stops:
                the_stop = all_stops[stop_id]
                the_stop['stop_dir'] = stop_dir
            else:
                print('no stop %d found for direction' % (stop_id))
                check_output = True
    finally:
        infile.close()
        
    infile = codecs.open(data_path + 'stop_munis.csv', 'rb', encoding='utf-8')
    try:
        reader = csv.reader(infile)
        for row in reader:
            stop_id = int(row[0])
            stop_muni = row[1]
            
            if stop_id in all_stops:
                the_stop = all_stops[stop_id]
                the_stop['stop_muni'] = stop_muni
            else:
                print('no stop %d found for municipality' % (stop_id))
                check_output = True
    finally:
        infile.close()
        
    pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(all_stops)
    
    if src_language == 'json':
        # Parse bulk imports want the data inside a 'results' array
        data = { 'results': [] }
    
        for stop_id in sorted(all_stops):
            stop = all_stops[stop_id]

            j = { 'code': stop['stop_code'], 
                  'name': stop['stop_name'],
                  'muni': stop['stop_muni'] }
            
            if 'stop_dir' in stop:
                j['dir'] = stop['stop_dir']
                
            if 'stop_lines' in stop:
                j['lines'] = stop['stop_lines'].split(' ')  # use a JSON array
                
            # Make a Parse-compatible GeoPoint object from the stop coordinates
            gp = { '__type': 'GeoPoint', 'latitude': float(stop['stop_lat']), 'longitude': float(stop['stop_lon']) }
            j['location'] = gp
            
            data['results'].append(j)
        print(json.dumps(data))
    else:
        # pick out each stop, sorted by stop ID    
        for stop_id in sorted(all_stops):
            stop = all_stops[stop_id]

            stop_dir = ''
            if 'stop_dir' in stop:
                stop_dir = stop['stop_dir']
            
            stop_lines = ''
            if 'stop_lines' in stop:
                stop_lines = stop['stop_lines']
            
            print(src_template % (stop['stop_id'], stop['stop_code'], stop['stop_name'], stop['stop_lat'], stop['stop_lon'], stop_dir, stop_lines, stop_muni))
        
        if check_output:
            print('*** CHECK OUTPUT FOR ERRORS ***')
    
    return  # don't do the stats - comment this out if you want them
    # NOTE: the statistics module requires Python 3.4 or later.
    
    munis = set(['T', 'K', 'L', 'N', 'O', 'P', 'Va', 'Ve', 'Y'])
    for stop_id in all_stops: # no need to call keys() on the dict
        stop = all_stops[stop_id]
        if stop['stop_muni'] in munis:
            latitudes.append(float(stop['stop_lat']))
    avg_lat = statistics.mean(latitudes)
    earth_radius = geodesy.geocentric_radius(avg_lat)

    # Make a 2-combination of all the stops
    distances = []
    for stop_tuple in itertools.combinations(all_stops.keys(), 2):
        stop1 = all_stops[stop_tuple[0]]
        stop2 = all_stops[stop_tuple[1]]
        dist = geodesy.haversine(float(stop1['stop_lat']), float(stop1['stop_lon']), float(stop2['stop_lat']), float(stop2['stop_lon']))
        distances.append(dist)

    print('Municipalities: ', munis)
    print('Average latitude = %.f, computed Earth radius = %.f km' % (avg_lat, earth_radius))
    print('%d stop distances, mean distance = %.f km, median distance = %.f km' % (len(distances), statistics.mean(distances), statistics.median(distances)))


def csv_row(stop):
    """Constructs a CSV row from the stop."""
    dir = ''
    if 'dir' in stop:
        dir = stop['dir']
        
    stop_lines = ' '.join(stop['lines'])
        
    columns = [stop['code'], stop['name'], str(stop['lat']), str(stop['lon']), dir, stop_lines, stop['muni'], stop['zone']]
    return ','.join(columns)


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
    
    
def json_object(stop):
    """Constructs a Parse-compatible JSON object from the stop."""
    j = { 'code': stop['code'], 
          'name': stop['name'],
          'muni': stop['muni'] }
        
    if 'stop_dir' in stop:
        j['dir'] = stop['dir']
            
    if 'stop_lines' in stop:
        j['lines'] = stop['lines'].split(' ')  # use a JSON array
            
    # Make a Parse-compatible GeoPoint object from the stop coordinates
    gp = { '__type': 'GeoPoint', 'latitude': float(stop['lat']), 'longitude': float(stop['lon']) }
    j['location'] = gp
    
    return j

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
    parser = argparse.ArgumentParser(description='Load stop points from Journeys API. Generate source code, or report stops within a given distance from the specified location.')
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

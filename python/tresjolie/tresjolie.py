# Generate source code from the stops list.
# Pass an argument to determine the output language: java, csharp, objc.
# Uses several input files to synthesize the data.

# Note: requires Python3 for Unicode-aware CSV handling

import csv
import sys
import codecs
import pprint
import json
import itertools
import statistics # Python 3.4 or later
import urllib
import urllib.request
import argparse

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
    """
    Constructs a CSV row from the stop.
    """
    columns = [stop['code'], stop['name'], str(stop['lat']), str(stop['lon']), stop['muni'], stop['zone']]    
    return ','.join(columns)


def json_object(stop):
    """
    Constructs a Parse-compatible JSON object from the stop.
    """
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

# Use the Journeys API to get stop points
JOURNEYS_API = 'http://data.itsfactory.fi/journeys/api/1/'
ENDPOINT_STOP_POINTS = 'stop-points'  # returns all stop points
# For Journeys API documentation, see http://wiki.itsfactory.fi/index.php/Journeys_API

def api_main(args):
    url = JOURNEYS_API + ENDPOINT_STOP_POINTS
    print('Loading stop points from %s' % url)
    
    r = requests.get(url)
    
    #response = urllib.request.urlopen(url)
    # urlopen returns bytes, but we know they're UTF-8
    #reader = codecs.getreader("utf-8")
    #json_data = json.load(reader(response))
    #print json.dumps(json_data, indent=4)

    json_data = r.json()
    #print(json_data)
    
    # The JSON returned from Journeys API is JSend-compatible.
    # See http://labs.omniti.com/labs/jsend for details.
    stops = json_data['body']
    print('Got %d stops' % len(stops))

    all_stops = []
    # Collect the municipality counts
    municipalities = []

    municipality_names = {}

    for stop in stops:
        coords = stop['location'].split(',')
        stop_lat = float(coords[0])
        stop_lon = float(coords[1])
    
        muni_code = stop['municipality']['shortName']
        municipalities.append(muni_code)

        muni_name = stop['municipality']['name']
        if not muni_name in municipality_names:
            municipality_names[muni_code] = muni_name
        
        current_stop = { 'code': stop['shortName'], 
                         'name': stop['name'],
                         'lat': stop_lat,
                         'lon': stop_lon,
                         'muni': muni_code,
                         'zone': stop['tariffZone'] }
        all_stops.append(current_stop)
    
    if args.source == 'json':
        # Generate some Parse-compatible JSON.
        # For Parse bulk imports we need the data to be inside a 'results' array.
        data = { 'results': [] }
        for stop in all_stops:
            data['results'].append(json_object(stop))
        print(json.dumps(data))
    
    elif args.source == 'csv':
        for stop in all_stops:
            print(csv_row(stop))
            

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process a GTFS stops.txt file or use the Journeys API to load stop points. Generate source code, or report stops within a given distance from the specified location.')
    parser.add_argument('action', help='What to do; one of generate | locate')
    parser.add_argument('-d', '--distance', type=float, help='Distance from current location in kilometers', default=0.5)
    parser.add_argument('-f', '--filename', help='Filename of stops file', default='stops.txt')
    parser.add_argument('-p', '--path', help='Path of related data files. Must have a trailing path separator.')
    parser.add_argument('-a', '--latitude', help='Latitude of current location in decimal degrees', type=float)
    parser.add_argument('-o', '--longitude', help='Longitude of current location in decimal degrees', type=float)    
    parser.add_argument('-s', '--source', help='Generate source code in SOURCE, where SOURCE = json | csharp | java | objc | sql | csv', default='json')
    args = parser.parse_args()

    #csv_main(args)
    if args.action == 'generate':
        api_main(args)
    elif args.action == 'locate':
        # Get the location and the desired distance
        lat = args.latitude
        lon = args.longitude
        distance = args.distance
        
        # Get a bounding box around the location
        sw_corner, ne_corner = geodesy.bounding_box(lat, lon, distance)
        location_params = 'location=%.5f,%.5f:%.5f,%.5f' % (sw_corner[0], sw_corner[1], ne_corner[0], ne_corner[1])

        url = JOURNEYS_API + ENDPOINT_STOP_POINTS + '?' + location_params
        print('Loading stop points from %s' % url)
        response = urllib.request.urlopen(url)
        # urlopen returns bytes, but we know they're UTF-8
        reader = codecs.getreader("utf-8")
        json_data = json.load(reader(response))
        stops = json_data['body']
        print(stops)
        
        for stop in stops:
            print('%s %s' % (stop['shortName'], stop['name']))

    else:
        print('Unknown action:', args.action)
        parser.print_help()
        
        
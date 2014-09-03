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

import geodesy # pull in our own utility functions

def main(argv):
    # Look at the command line to find out which type of output is wanted.
    src_language = argv[0]
    if src_language == 'java':
        src_template = 'stops.add(new Stop(%d, "%s", "%s", %s, %s, "%s", "%s", "%s"));'
    elif src_language == 'csharp':
        src_template = 'this.Items.Add(new ItemViewModel() { StopID = %d, StopCode = "%s", StopName = "%s", StopLatitude = %s, StopLongitude = %s, StopDirection = "%s", StopLines = "%s", StopMuni = "%s" });'
    elif src_language == 'objc':
        src_template = '[[BMStop alloc] initWithDictionary:@{ @"stopID": @(%d), @"stopCode": @"%s", @"stopName": @"%s", @"stopLatitude": @(%s), @"stopLongitude": @(%s), @"stopDirection": @"%s", @"stopLines": @"%s", @"stopMuni": @"%s" }],'
    elif src_language == 'csv':
        src_template = '%d,%s,%s,%s,%s,%s,%s,%s'
    elif src_language == 'sql':
        src_template = 'INSERT INTO stop VALUES (%d, "%s", "%s", %s, %s, "%s", "%s", "%s");'
    elif src_language == 'json':
        pass # Will handle JSON as a special case
    else:
        print('Can''t handle:', src_language)
        sys.exit(-1)
                    
    #print('Source code to generate: ', src_language)
    
    # Set this to True if there is something wrong with the results
    check_output = False
    
    # Dictionary, where each entry has key = stop ID, value = other stop attributes
    all_stops = {}

    # Read the master stops file and create entries in all_stops.
    # NOTE: We will treat all values as strings since we're generating source code.
    # If we need to do calculations, the latitude and longitude values are 
    # explicitly converted to floats as needed.   
    with codecs.open('stops.csv', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        for columns in reader:
            stop_id = int(columns[0])
            
            the_stop = dict(stop_id=stop_id, stop_code=columns[1], stop_name=columns[2], stop_lat=columns[3], stop_lon=columns[4])
            all_stops[stop_id] = the_stop
        infile.close()

    #print('number of stops = %d' % (len(all_stops)))
    #print('all_stops = ', all_stops)
        
    infile = codecs.open('stop_lines.csv', 'rb', encoding='utf-8')
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

    infile = codecs.open('stop_directions.csv', 'rb', encoding='utf-8')
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
        
    infile = codecs.open('stop_munis.csv', 'rb', encoding='utf-8')
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
        
if __name__ == "__main__":
    main(sys.argv[1:])

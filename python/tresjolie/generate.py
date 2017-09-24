import json
import argparse

def read_json_data(json_filename):
    json_data = None
    with open(json_filename) as json_file:
        json_data = json.load(json_file)
    return json_data    


def generate_stops(stops, source):
    result = []
    
    src_template = '%d,%s,%s,%.5f,%.5f,%s,%s,%s,%s'
	
    if source == 'java':
        src_template = 'stops.add(new Stop(%d, "%s", "%s", %s, %s, "%s", "%s", "%s", "%s"));'
    elif source == 'csharp':
        src_template = 'stopsDb.Stops.InsertOnSubmit(new Stop() { ID = %d, Code = "%s", Name = "%s", Latitude = %s, Longitude = %s, Direction = "%s", Lines = "%s", Municipality = "%s", Zone = "%s" });'
    elif source == 'objc':
        src_template = '[[BMStop alloc] initWithDictionary:@{ @"stopID": @(%d), @"stopCode": @"%s", @"stopName": @"%s", @"stopLatitude": @(%s), @"stopLongitude": @(%s), @"stopDirection": @"%s", @"stopLines": @"%s", @"stopMuni": @"%s", @"stopZone": @"%s" }],'
    elif source == 'sql':
        src_template = 'INSERT INTO stops_tre VALUES (%d, "%s", "%s", %s, %s, "%s", "%s", "%s", "%s");'
    elif source == 'csv':
        src_template = '%d,%s,%s,%.5f,%.5f,%s,%s,%s,%s'
    
    for s in stops:
        #print(s)
        stop_dir = ''
        if 'direction' in s:
            stop_dir = s['direction']
        stop_lines = ' '.join(s['lines'])
        statement = src_template % (int(s['code']), s['code'], s['name'], s['latitude'], s['longitude'], stop_dir, stop_lines, s['municipality'] or '', s['zone'])
        result.append(statement)

    return result
    
    
def generate_lines(lines):
    result = []
    for l in lines:
        result.append('%s,%s' % (l['name'], l['description']))
    return result
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate source code from stops and lines saved as JSON.')
    parser.add_argument('-j', '--json', help='Name of JSON data file')
    parser.add_argument('-s', '--source', help='Type of source code to generate. One of csv, objc, java, sql, csharp.', default='csv')
    args = parser.parse_args()

    data = read_json_data(args.json)
    stops = generate_stops(data['stops'], args.source)
    print('-' * 40)
    print('stops.csv:')
    for s in stops:
        print(s)

    print()
    
    lines = generate_lines(data['lines'])
    print('-' * 40)
    print('lines.csv:')
    for l in lines:
        print(l)
	
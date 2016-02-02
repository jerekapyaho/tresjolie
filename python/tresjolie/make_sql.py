import argparse
import json
import csv

# stop_id, stop_code, stop_name, stop_latitude, stop_longitude, stop_dir, stop_lines, stop_muni, stop_zone
sql_template = 'INSERT INTO %s VALUES (%d, \'%s\', \'%s\', %s, %s, \'%s\', \'%s\', \'%s\', \'%s\');'

def make_sql_from_json(json_filename, table_name):
    json_data = None
    with open(json_filename) as json_file:
        json_data = json.load(json_file)    
    stops = json_data['stops']
    
    for s in stops:
        line_str = ' '.join(s['lines'])
        dir_str = ''
        if 'dir' in s:
            dir_str = s['dir']
        
        stop_code = int(s['code'])
        
        statement = sql_template % (table_name, stop_code, s['name'], s['lat'], s['lon'], dir_str, line_str, s['muni'], s['zone'])
        print(statement)

def make_sql_from_csv(csv_filename, table_name):
    f = open(csv_filename, 'r')
    try:
        reader = csv.reader(f)
        row_num = 0
        for s in reader:
            row_num += 1
            stop_code = int(s[0])
            statement = sql_template % (table_name, stop_code, s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7])
            print(statement)
    finally:
        f.close()        

def make_java_from_csv(csv_filename):
# int stopID, String stopCode, String stopName, double latitude, double longitude, String direction, String lines, String municipality, String tariffZone    
    src_template = 'stops.add(new Stop(%d, "%s", "%s", %s, %s, "%s", "%s", "%s", "%s"));'

    f = open(csv_filename, 'r')
    try:
        reader = csv.reader(f)
        row_num = 0
        for s in reader:
            row_num += 1
            stop_code = int(s[0])
            statement = src_template % (stop_code, s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7])
            print(statement)
    finally:
        f.close()        

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate SQL INSERT statements from JSON or CSV.')
    parser.add_argument('source', help='Source type; one of json | csv')
    parser.add_argument('-c', '--csvfilename', help='Name of CSV file', default='stops-tre.csv')
    parser.add_argument('-j', '--jsonfilename', help='Name of JSON file', default='stops_tre.json')
    parser.add_argument('-t', '--tablename', help='Name of SQL table to insert to', default='stops_tre')

    args = parser.parse_args()
    
    if args.source == 'json':
        make_sql_from_json(args.jsonfilename, args.tablename)
    else:
        make_sql_from_csv(args.csvfilename, args.tablename)
        #make_java_from_csv(args.csvfilename)

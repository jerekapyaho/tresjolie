import argparse
import json
import csv

create_stop_table_sql = 'CREATE TABLE stop(stop_id INTEGER PRIMARY KEY, stop_code TEXT NOT NULL, stop_name TEXT NOT NULL, stop_lat DOUBLE NOT NULL, stop_lon DOUBLE NOT NULL, stop_dir TEXT, stop_lines TEXT, stop_muni TEXT, stop_zone TEXT);'
create_line_table_sql = 'CREATE TABLE line(line_name TEXT PRIMARY KEY, line_desc TEXT NOT NULL);'

stop_sql_template = 'INSERT INTO stop VALUES (%d, \'%s\', \'%s\', %s, %s, \'%s\', \'%s\', \'%s\', \'%s\');'
line_sql_template = 'INSERT INTO line VALUES (\'%s\', \'%s\');'


def make_sql_from_json(json_filename):
    print(create_stop_table_sql)
    print(create_line_table_sql)
    
    json_data = None
    with open(json_filename) as json_file:
        json_data = json.load(json_file)    
    stops = json_data['stops']
    
    for s in stops:
        line_str = ' '.join(s['lines'])
        dir_str = ''
        if 'direction' in s:
            dir_str = s['direction']
        
        statement = stop_sql_template % (int(s['code']), s['code'], s['name'], s['latitude'], s['longitude'], dir_str, line_str, s['municipality'], s['zone'])
        print(statement)
        
    lines = json_data['lines']
    for l in lines:
        statement = line_sql_template % (l['name'], l['description'])
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
        make_sql_from_json(args.jsonfilename)
    else:
        make_sql_from_csv(args.csvfilename, args.tablename)
        #make_java_from_csv(args.csvfilename)

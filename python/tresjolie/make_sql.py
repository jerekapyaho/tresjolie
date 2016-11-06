import argparse
import json
import csv

create_stop_table_sql = 'CREATE TABLE stop(stop_id INTEGER PRIMARY KEY, stop_code TEXT NOT NULL, stop_name TEXT NOT NULL, stop_lat DOUBLE NOT NULL, stop_lon DOUBLE NOT NULL, stop_dir TEXT, stop_lines TEXT, stop_muni TEXT, stop_zone TEXT);'
create_stop_table_sql_android = 'CREATE TABLE stop(_id INTEGER PRIMARY KEY AUTOINCREMENT, stop_id INTEGER NOT NULL, stop_code TEXT NOT NULL, stop_name TEXT NOT NULL, stop_lat DOUBLE NOT NULL, stop_lon DOUBLE NOT NULL, stop_dir TEXT, stop_lines TEXT, stop_muni TEXT, stop_zone TEXT);'
# The only difference on Android is the _id column
create_line_table_sql = 'CREATE TABLE line(line_name TEXT PRIMARY KEY, line_desc TEXT NOT NULL);'
create_line_table_sql_android = 'CREATE TABLE line(_id INTEGER PRIMARY KEY AUTOINCREMENT, line_name TEXT NOT NULL, line_desc TEXT NOT NULL);'

stop_sql_template = 'INSERT INTO stop VALUES (%d, \'%s\', \'%s\', %s, %s, \'%s\', \'%s\', \'%s\', \'%s\');'
stop_sql_template_android = 'INSERT INTO stop (stop_id, stop_code, stop_name, stop_lat, stop_lon, stop_dir, stop_lines, stop_muni, stop_zone) VALUES (%d, \'%s\', \'%s\', %s, %s, \'%s\', \'%s\', \'%s\', \'%s\');'
line_sql_template = 'INSERT INTO line VALUES (\'%s\', \'%s\');'
line_sql_template_android = 'INSERT INTO line VALUES (%d, \'%s\', \'%s\');'


def make_sql_from_json(json_filename, platform):
    create_stop = create_stop_table_sql
    create_line = create_line_table_sql
    if platform == 'Android':
        create_stop = create_stop_table_sql_android
        create_line = create_line_table_sql_android
    print(create_stop)
    print(create_line)
    
    json_data = None
    with open(json_filename) as json_file:
        json_data = json.load(json_file)    
    stops = json_data['stops']
    
    for s in stops:
        line_str = ' '.join(s['lines'])
        dir_str = ''
        if 'direction' in s:
            dir_str = s['direction']
        
        stop_template = stop_sql_template
        if platform == 'Android':
            stop_template = stop_sql_template_android
        statement = stop_template % (int(s['code']), s['code'], s['name'], s['latitude'], s['longitude'], dir_str, line_str, s['municipality'], s['zone'])
        print(statement)
        
    line_id = 1
    lines = json_data['lines']
    for l in lines:
        statement = line_sql_template % (l['name'], l['description'])
        if platform == 'Android':
            statement = line_sql_template_android % (line_id, l['name'], l['description'])
        line_id += 1
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
    parser.add_argument('-p', '--platform', help='Platform to target, must be iOS or Android', default='iOS')

    args = parser.parse_args()
    #print('platform = %s' % args.platform)
    if args.source == 'json':
        make_sql_from_json(args.jsonfilename, args.platform)
    else:
        make_sql_from_csv(args.csvfilename, args.tablename)
        #make_java_from_csv(args.csvfilename)

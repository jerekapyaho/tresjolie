import json
import requests
import argparse
import re
import csv

def read_stops(filename):
    stops = []
    with open(filename) as json_file:
        json_data = json.load(json_file)
        #print(json_data)
    
        stops = json_data['results']
        return stops


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

    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Determine running directions for stops.')
    parser.add_argument('-f', '--filename', help='Filename of Parse-compatible stops file', default='Stop.json')
    parser.add_argument('-d', '--dirfile', help='Name of file with stop codes and running directions', default='stop_directions.csv')
    args = parser.parse_args()
    
    stops = read_stops(args.filename)
    print('stops = ', len(stops))

    dirs = read_dirs(args.dirfile)
    print('dirs = ', len(dirs))
    print(type(dirs))

    match_count = 0        
    for s in stops:
        stop_code = s['code']
        if stop_code in dirs:
            print(s['objectId'], stop_code, dirs[stop_code])
            match_count += 1
    print(match_count)

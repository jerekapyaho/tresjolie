import csv
import sys
import json
import requests
import argparse
import time


PARSE_API = 'https://api.parse.com'


# Credit: http://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks-in-python
def chunks(l, n):
    n = max(1, n)
    return [l[i:i + n] for i in range(0, len(l), n)]


# Batch update the Parse objects.
def batch_update(stops):
    # Since Parse can only accept up to 50 requests per batch,
    # let's split the stops into lists of that size.
    stop_lists = chunks(stops, 50)
    
    for l in stop_lists:
        reqs = []
        
        # Make a request object for all the updates in this batch
        for s in l:
            if not 'dir' in s:
                continue
                
            #line_list = ' '.join(s['lines'])
            #print(line_list)     
            
            reqs.append({ 'method': 'PUT',  # use PUT for object updates
                          'path': '/1/classes/' + args.classname + '/' + s['objectId'],
                          'body': { 'dir': s['dir'] } })
        #print('Number of requests in this batch:', len(reqs))    
        print(reqs)    
        
        # Construct the actual batch request
        payload = { 'requests': reqs }            
        print(json.dumps(payload))
        
        headers = { 'X-Parse-Application-Id': args.appid,
                    'X-Parse-REST-API-Key': args.key,
                    'Content-Type': 'application/json' }
            
        url = PARSE_API + '/1/batch'
        
        # Batches are POST requests
        r = requests.post(url, headers=headers, data=json.dumps(payload))
        print(r.text)

        # Throttle a bit to keep within the Parse 30 req/s limit 
        time.sleep(2)


def read_csv(filename):
    dict = {}
    f = open(filename, 'r')
    try:
        reader = csv.reader(f)
        row_num = 0
        for row in reader:
            dict[row[0]] = row[1]
            row_num += 1
    finally:
        f.close()
    return dict    


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Update Stop objects in Parse with lines.')
    parser.add_argument('-a', '--appid', help='Your Parse application ID')    
    parser.add_argument('-k', '--key', help='Your REST API key')
    parser.add_argument('-m', '--mapfilename', help='Filename of CSV file with objectId to stop code mapping', default='Stop-objectId-code.csv')
    parser.add_argument('-c', '--classname', help='Name of Parse object class', default='Stop')
    parser.add_argument('-d', '--dirdatafile', help='Name of file with stop codes and running directions', default='Stop-code-dir.csv')

    args = parser.parse_args()
    
    print('Application ID =', args.appid)
    print('REST API key =', args.key)
    
    #stops = []
    #with open(args.filename) as json_file:
    #    stops = json.load(json_file)    

    object_ids = read_csv(args.mapfilename)
    #print(object_ids)
    
    dirs = read_csv(args.dirdatafile)
    print('dirs = ', len(dirs))
    #print(type(dirs))
    
    match_count = 0
    
    # Swap the keys and values in stops
    mapping = {y:x for x,y in object_ids.items()}
    #print(mapping)
          
    stops = []
    for s in mapping:
        stop_code = s
        if stop_code in dirs:
            stops.append({ 'dir': dirs[stop_code], 'objectId': mapping[stop_code] })
            match_count += 1
    print(match_count)
    
    #print(stops)
    
    batch_update(stops)

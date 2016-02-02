import json
import requests
import argparse
import re

JOURNEYS_API = 'http://data.itsfactory.fi/journeys/api/1/'
ENDPOINT_STOP_POINTS = 'stop-points'  # returns all stop points
ENDPOINT_JOURNEYS = 'journeys'
ENDPOINT_LINES = 'lines'

def read_stops(filename):
    stops = []
    with open(filename) as json_file:
        json_data = json.load(json_file)
        #print(json_data)
    
        stops = json_data['results']
        return stops
    

def natural_sort_key(s, _nsre=re.compile('([0-9]+)')):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(_nsre, s)]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Determine which lines serve stops.')
    parser.add_argument('-f', '--filename', help='Filename of Parse-compatible stops file', default='Stop.json')    
    args = parser.parse_args()
    
    stops = read_stops(args.filename)
    print(len(stops))
    
    # For debugging: just a couple of stops    
    #stops = [ { 'code': '0001' }, { 'code': '0002' }, { 'code': '0003' } ]
    #stops = stops[: 10]
    
    request_count = 0   # how many Journeys API requests we have made
    
    stop_request_counts = []  # save the number of requests made for each stop
    
    for s in stops:
        stop_request_count = 0  # how many requests for this stop only
        
        # Save the stop code for later
        stop_code = s['code']
        
        # Remove anything we're not going to update
        s.pop('code')
        s.pop('createdAt')
        s.pop('location')
        s.pop('muni')
        s.pop('name')
        s.pop('updatedAt')
        # We should have only objectId left.
        # Later we'll add lines.
        
        url = JOURNEYS_API + ENDPOINT_JOURNEYS
        params = { 'stopPointId': stop_code }
        r = requests.get(url, params=params)
        stop_request_count += 1
        #print(r.url)
        json_data = r.json()
        
        stop_journeys = []
        if json_data['status'] == 'success':
            for i in json_data['body']:
                stop_journeys.append(i)
            #print(len(stop_journeys))
            paging = json_data['data']['headers']['paging']
            page_size = paging['pageSize']
            have_more_data = paging['moreData']
            #print('have_more_data =', have_more_data)
            next_index = paging['startIndex'] + page_size
            while have_more_data:
                #print('Getting more data, startIndex = %d' % next_index)
                params['startIndex'] = next_index
                paging_request = requests.get(url, params=params)
                stop_request_count += 1
                #print(paging_request.url)
                more_data = paging_request.json()
                for i in more_data['body']:
                    stop_journeys.append(i)
                #print(len(stop_journeys))
                more_paging = more_data['data']['headers']['paging']
                have_more_data = more_paging['moreData']
                page_size = more_paging['pageSize']
                next_index = more_paging['startIndex'] + page_size

        #print(s['code'], len(stop_journeys))
        
        line_urls = []
        for j in stop_journeys:
            line_urls.append(j['lineUrl'])
        
        # Find the unique line URLs by turning the list into a set
        unique_line_urls = set(line_urls)
        #print(len(line_urls), ' / ', len(unique_line_urls))        
        #print(unique_line_urls)
        
        # Turn the uniqued line URLs back into a list.
        stop_line_urls = list(unique_line_urls)
        
        # Actually we can just get the line's name from the line URL.
        # We don't need to hit the lines API endpoint, since we only
        # need the names.
        line_names = []
        for u in stop_line_urls:
            pos = u.rfind('/')
            line_name = u[pos + 1 :]
            line_names.append(line_name)
            
        s['lines'] = sorted(line_names, key=natural_sort_key)
            
        print(s['objectId'], stop_code, s['lines'])
        
        stop_request_counts.append(stop_request_count)
        request_count += stop_request_count

    # Combine the line URLs for all stops into one list, so that we can
    # avoid calling the Journeys API multiple times for the lines.
    # Since the list of line URLs is already unique, we just append them
    # into one big list and then unique that.
    #line_urls = []
    #for s in stops:
    #    for u in s['line_urls']:
    #        line_urls.append(u)
    #print(line_urls)
    #unique_line_urls = set(line_urls)
    #print(unique_line_urls)
    #print(len(line_urls), ' / ', len(unique_line_urls))
    
    print(json.dumps(stops))   

    #all_lines = []
    #for l in unique_line_urls:
    #    url = JOURNEYS_API + ENDPOINT_LINES
    #    r = requests.get(url)
    #    json_data = r.json()
    #    body = json_data['body'][0]
        
    #    all_lines.append({ 'url': body['url'],
    #                       'name': body['name'],
    #                       'description': body['description'] })
    #print(all_lines)
    
    print('Requests to Journeys API: %d' % request_count)
    print('Average requests per stop: %.1f' % (sum(stop_request_counts) / float(len(stop_request_counts))))

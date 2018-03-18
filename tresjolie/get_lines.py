import json
import requests

JOURNEYS_API = 'http://data.itsfactory.fi/journeys/api/1/'
ENDPOINT_LINES = 'lines'

if __name__ == '__main__':
    all_lines = []
    url = JOURNEYS_API + ENDPOINT_LINES
    r = requests.get(url)
    json_data = r.json()
    lines = json_data['body']
    
    for l in lines:
        print('%s,%s' % (l['name'], l['description']))

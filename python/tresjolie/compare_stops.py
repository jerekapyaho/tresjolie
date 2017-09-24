import sys
import json

def compare_stops(a_name, b_name):
    a_data = None
    with open(a_name) as a_file:
        a_data = json.load(a_file)    
    a_stops = {}
    a_json_stops = a_data['stops']
    for json_stop in a_json_stops:
        code = int(json_stop['code'])
        a_stops[code] = json_stop['name']
    #print(len(a_stops), a_stops)

    b_data = None
    with open(b_name) as b_file:
        b_data = json.load(b_file)    
    b_stops = {}
    b_json_stops = b_data['stops']
    for json_stop in b_json_stops:
        code = int(json_stop['code'])
        b_stops[code] = json_stop['name']
    #print(len(b_stops), b_stops)

    a_stop_codes = sorted(a_stops.keys())
    b_stop_codes = sorted(b_stops.keys())

    row_strings = []

    print(a_stops[9602])

    for code in range(0, 10000):
        row_string = ''
        
        found = False
        row_string += ' '
        a_name = ''
        if code in a_stop_codes:
            a_name = a_stops[code]
            row_string += '%4d %-30s' % (code, a_name) 
            found = True
        row_string += ' '
        b_name = ''
        if code in b_stop_codes:
            b_name = b_stops[code]
            row_string += '    %4d %-30s' % (code, b_name)
            found = True
        name_different = a_name != b_name
        row_prefix = ' '
        if name_different:
            row_prefix = '*'
        if found:
            row_strings.append(row_prefix + row_string)
    
    for r in row_strings:
        print(r)



if __name__ == '__main__':
    a_name = None
    b_name = None
    if len(sys.argv) != 3:
        print('Need two filenames')
        sys.exit()
    
    a_name = sys.argv[1]
    b_name = sys.argv[2]

    compare_stops(a_name, b_name)



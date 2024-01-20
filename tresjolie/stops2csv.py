import sys
import json

data = None
output = []

with open(sys.argv[1], 'r', encoding='utf-8') as f:
    data = json.load(f)

    for stop in data['stops']:
        s = f"{stop['code']},\"{stop['name']}\","
        s += f"{stop['latitude']},{stop['longitude']},"
        lines = stop['lines']
        s += ' '.join(lines) + ',' if lines else ','
        s += f"{stop['municipality']},{stop['zone']}"
        output.append(s)

with open(sys.argv[2], 'w', encoding='utf-8') as f:
    for line in output:
        f.write(line)
        f.write('\n')

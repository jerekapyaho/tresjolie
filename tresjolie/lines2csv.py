import sys
import json

data = None
output = []

with open(sys.argv[1], 'r', encoding='utf-8') as f:
    data = json.load(f)

    for line in data['lines']:
        output.append(f"{line['name']},\"{line['description']}\"")

with open(sys.argv[2], 'w', encoding='utf-8') as f:
    for line in output:
        f.write(line)
        f.write('\n')

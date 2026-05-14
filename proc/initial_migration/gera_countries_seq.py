import json
from pprint import pprint
json_data=open('countries.json')

data = json.load(json_data)


with open("countries.seq", "w") as text_file:
    for country in data:
        if country['fields'].has_key('code'):
            seq_row = "%s|%s\n" % (country['fields']['code'], country['pk'])
            text_file.write(seq_row)

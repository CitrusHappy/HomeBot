import json
import re

data = json.loads(open('Data/jared.json',  encoding="utf8").read())


for _messages in data['messages']:
    print(_messages['author']['name'])
    print(re.sub(r'[^A-Za-z0-9 ]+', '', _messages['content']))
    input(">>continnue")

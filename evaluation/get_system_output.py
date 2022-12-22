import requests
import json
import sys

qa_url = 'http://127.0.0.1:5000/answer'
try:
    output_file = sys.argv[1]
except:
    print("please provide output file")
    exit(1)

dataset = []
with open('./evaluation/evalcoll.json', encoding='utf8') as json_file:
    dataset = json.load(json_file)

try:
    with open(output_file, encoding='utf8') as json_file:
        answered = json.load(json_file)
except FileNotFoundError:
    answered = []

answered_ids = []
for q in answered:
    answered_ids.append(int(q["id"]))

qcounter = len(dataset)
acounter = len(answered_ids)
print('remaining: '+str(qcounter-acounter)+' questions')
for q in dataset:
    if(q["id"] in answered_ids):
        continue
    else:
        print(q["id"])
    print(q['question'])
    payload = {
        'question' : q['question'],
    }
    r = requests.get(qa_url, params=payload)
    try:
        response = json.loads(r.text)
    except json.decoder.JSONDecodeError:
        print(r.text)
        sys.exit(1)
    answered.append({
        "id":q["id"],
        "question":q["question"],
        "answers": response["answers"],
        "type" : q["type"]
    })
    with open(output_file, 'w') as outfile:
        json.dump(answered, outfile)

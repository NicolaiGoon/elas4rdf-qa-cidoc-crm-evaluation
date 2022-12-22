"""
This script is used to create a file that only includes answers that received a
score equal or higher to a given threshold
e.g. to only keep answers with a score >= 0.5
`python filter_system_output.py 0.5`
"""
import json
import sys

dataset = []

try:
    infile = sys.argv[3]
except:
    infile = None


with open(infile, encoding='utf8') as json_file:
    dataset = json.load(json_file)

out2 = []
threshold = float(sys.argv[1])

try:
    qtype = sys.argv[2]
except:
    qtype = None



if(qtype and qtype == "ALL"):
    qtype = None

for q in dataset:
    newans = []
    
    # filter question types
    if(qtype and qtype != q["type"]):
        continue

    for ans in q['answers']:
        if float(ans['score']) >= threshold: 
            newans.append(ans)
           
    out2.append({
    	"id": int(q["id"]),
    	"question": q["question"],
    	"answers": newans,
        "type":q["type"]
    })

with open('./evaluation/system_output_filtered.json', 'w') as outfile:
    json.dump(out2, outfile)
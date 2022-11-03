import json
from re import template
import requests

# SPARQL_URL = "http://127.0.0.1:8890/sparql"
SPARQL_URL = "http://ldf.fi/ww1lod/sparql"


def sparql_query(query_string):
    url = SPARQL_URL
    payload = {
        "query": query_string,
        # "default-graph-uri": "http://localhost:8890/cidoc-crm"
    }
    headers = {"Accept":"application/json"}
    response = requests.get(url,params=payload,headers=headers)
    return response.json()

query = '''
prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix crm: <http://www.cidoc-crm.org/cidoc-crm/>
prefix skos: <http://www.w3.org/2004/02/skos/core#>

select distinct ?rLabel 
(group_concat(distinct ?whoL;separator='|') as ?carriedOutBy) 
(group_concat(distinct ?placeL;separator='|') as ?tookPlaceAt) 
(group_concat(distinct ?tstart;separator='|') as ?BeginsAt)
(group_concat(distinct ?featuresL;separator='|') as ?showsFeatures)
(group_concat(distinct ?fallsWithinL;separator='|') as ?fallsWithin)
(group_concat(distinct ?participantL;separator='|') as ?hadParticipant)
{
?s rdf:type crm:E5_Event .
?s skos:prefLabel ?rLabel .
# FILTER (lang(?rLabel) = 'en') .
optional {?s crm:P14_carried_out_by ?who . ?who skos:prefLabel ?whoL}
optional {?s crm:P7_took_place_at ?place . ?place skos:prefLabel ?placeL}
optional {
    ?s crm:P4_has_time-span ?timespan . 
    ?timespan crm:P82a_begin_of_the_begin ?tstart . 
 }
optional {?s crm:P130_shows_features_of ?features . ?features skos:prefLabel ?featuresL}
optional {?s crm:P10_falls_within ?falls . ?falls skos:prefLabel ?fallsWithinL}
optional {?s crm:P11_had_participant ?participant . ?participant skos:prefLabel ?participantL}
} groupby(?rLabel)
'''

templates = {
    "BeginsAt" : "When did the {0} started?",
    "tookPlaceAt" : "Where took place the {0}?",
    "carriedOutBy" : "Who accomplished the {0}?",
    "showsFeatures" : "What features does {0} show?",
    "fallsWithin" : "What events fall within {0}?",
    "hadParticipant" : "Who participated at the {0}?"
}

statistics = {

}

dataset = []
res = sparql_query(query)
id = 0
for obj in res["results"]["bindings"]:
    rLabel = obj["rLabel"]["value"]
    for key in obj:
        if(key != "rLabel"): 
            
            if (key not in statistics): statistics[key] = 0
            
            # keep at most 600 questions for each type
            if (statistics[key] > 600): 
                continue
            
            id += 1
            statistics[key] += 1
            answers = obj[key]["value"].split("|")
            dataset.append({
                "id":id,
                "question" : templates[key].format(rLabel),
                "answers" : list(set(answers)),
                "type" : key
            })

with open("./evaluation/evalcoll.json","w",encoding="utf-8") as outfile:
    json.dump(dataset,outfile)

print("Question type stats:\n")

total = 0
for qtype in statistics:
    total += statistics[qtype]
for qtype in statistics:
    print(qtype+"\ttotal: "+str(statistics[qtype])+"\t percentage: "+str(round(statistics[qtype]/total,3)))

print("Total Questions: "+str(total))
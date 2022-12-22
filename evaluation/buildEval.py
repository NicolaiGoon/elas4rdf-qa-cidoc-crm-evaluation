import json
import random
import re

import requests
from evaluate import normalize_answer

# SPARQL_URL = "http://127.0.0.1:8890/sparql"
SPARQL_URL = "http://ldf.fi/ww1lod/sparql"


def sparql_query(query_string):
    url = SPARQL_URL
    payload = {
        "query": query_string,
        # "default-graph-uri": "http://localhost:8890/cidoc-crm"
    }
    headers = {"Accept": "application/json"}
    response = requests.get(url, params=payload, headers=headers)
    return response.json()


query = """
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
"""

templates = {
    "BeginsAt": [
        "What was the date on which the {0} happened?",
        "When did the {0} take place?",
        "What was the start date of the {0}?",
        "What is the specific date of the {0}?",
        "When was the beginning of {0}?",
    ],
    "tookPlaceAt": [
        "Where took place the {0}?",
        "Where the {0} happend?",
        "In what place the {0} happend?",
        "What is the place of the {0}?",
    ],
    "carriedOutBy": [
        "Who accomplished the {0}?",
        "Who performed the {0}?",
        "Who was responsible for the {0}?",
        "Who carried out the {0}?",
    ],
    "showsFeatures": [
        "What features does the {0} show?",
        "What are the characteristics of the {0}?",
        "What are the ascpects of the {0}?",
    ],
    "fallsWithin": [
        "What events fall within the {0}?",
        "What happened at the same period with the {0}?",
        "What events happened in parallel with the {0}?",
        "What events has similar time-span as the {0}?",
    ],
    "hadParticipant": [
        "Who participated at the {0}?",
        "Who was involved at the {0}?",
        "Who took part in the {0}?",
    ],
    "hadParticipantBegins": [
        "When the events with participant {0} happened?",
        "What are the starting dates of the events that {0} was involved?",
        "When took place the events where {0} was involved?",
    ],
    "falltookPlace": [
        "Where the events that fall within the {0} took place?",
        "What are the places where events happend in parallel with the {0}?",
        "Where happened the events with similar time-span as the {0}?",
    ],
    "fallhasTimeSpan": [
        "When the events that fall within the {0} started?",
        "What are the starting dates of the events that happend in parallel with the {0}?",
        "When the events that happened at the same period as the {0} began?",
        "When the events with similar time-span as the {0} took place?",
    ],
}


def clearQuestion(question):
    """
    removes parenthesis with its content and multiple spaces
    """
    # return question
    q1 = re.sub("\(.*\)", " ", question)
    q2 = re.sub("\s{2,}", " ", q1)
    return q2.replace(" ?", "?")


answer_tokens = []
dataset = []
res = sparql_query(query)
id = 0
for obj in res["results"]["bindings"]:
    rLabel = obj["rLabel"]["value"]
    for key in obj:
        if key != "rLabel":
            id += 1
            answers = obj[key]["value"].split("|")
            template_variation = random.randint(0, len(templates[key]) - 1)
            q = templates[key][template_variation].format(rLabel)
            q = clearQuestion(q)
            a = list(set(answers))

            answer_tokens.append(len(set((" ".join(normalize_answer(a))).split(" "))))

            dataset.append(
                {
                    "id": id,
                    "question": q,
                    "answers": a[:10],
                    "entity": rLabel,
                    "type": key,
                }
            )

query = """
PREFIX event: <http://purl.org/NET/c4dm/event.owl#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
SELECT ?partL (group_concat(distinct ?begin;separator=' | ') as ?beginLL) WHERE {
  optional {?event crm:P11_had_participant ?part .
  ?event crm:P4_has_time-span ?time .
  ?time ?p ?begin .
  FILTER(REGEX(STR(?p), "cidoc-crm.org/cidoc-crm/P82a_begin_of_the_begin")) .
  ?event skos:prefLabel ?eventL . 
  ?part skos:prefLabel ?partL . 
#   FILTER (lang(?eventL) = 'en') .
  }
} groupby(?partL)
"""

res = sparql_query(query)

for obj in res["results"]["bindings"]:
    participant = obj["partL"]["value"]
    answers = obj["beginLL"]["value"].split("|")
    id += 1
    a = list(set(answers))
    template_variation = random.randint(0, len(templates["hadParticipantBegins"]) - 1)
    q = templates["hadParticipantBegins"][template_variation].format(participant)
    answer_tokens.append(len(set((" ".join(normalize_answer(a))).split(" "))))

    dataset.append(
        {
            "id": id,
            "question": q,
            "answers": a[:10],
            "entity": participant,
            "type": "hadParticipantBegins",
        }
    )

query = """
PREFIX event: <http://purl.org/NET/c4dm/event.owl#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
SELECT ?eventL 
(group_concat(distinct ?placeL;separator='|') as ?falltookPlace) 
(group_concat(distinct ?begin;separator='|') as ?fallhasTimeSpan) WHERE {
  ?event crm:P10_falls_within ?event2 .
  ?event skos:prefLabel ?eventL .
  ?event2 skos:prefLabel ?event2L .
  optional {?event2 crm:P7_took_place_at ?place . ?place skos:prefLabel ?placeL}
  optional {?event2 crm:P4_has_time-span ?time . ?time ?p ?begin . FILTER(REGEX(STR(?p), "cidoc-crm.org/cidoc-crm/P82a_begin_of_the_begin")) .}
#  FILTER (lang(?eventL) = 'en') .
} groupby(?eventL)
"""

res = sparql_query(query)

for obj in res["results"]["bindings"]:
    participant = obj["eventL"]["value"]
    for key in obj:
        if key != "eventL":
            answers = obj[key]["value"].split("|")
            id += 1
            a = list(set(answers))
            template_variation = random.randint(0, len(templates[key]) - 1)
            q = templates[key][template_variation].format(participant)
            answer_tokens.append(len(set((" ".join(normalize_answer(a))).split(" "))))

            dataset.append(
                {
                    "id": id,
                    "question": q,
                    "answers": a[:10],
                    "entity": participant,
                    "type": key,
                }
            )


# filter dublicates and create statistics

statistics = {}

unique = set()
udataset = []
total = 0
id = 1
for o in dataset:
    entry_hash = json.dumps({"entity": o["entity"], "type": o["type"]})
    if entry_hash not in unique:
        unique.add(entry_hash)
        if o["type"] not in statistics:
            statistics[o["type"]] = 0
        if statistics[o["type"]] >= 300:
            continue
        statistics[o["type"]] += 1
        q = o
        q["id"] = id
        id += 1
        total += 1
        udataset.append(q)
    # else:
    #     if o['question'] not in dub: dub[o['question']] = []
    #     dub[o["question"]].append(o["answers"])


# with open("./evaluation/dublicates.json","w",encoding="utf-8") as outfile:
#     json.dump(dub,outfile)

with open("./evaluation/evalcoll.json", "w", encoding="utf-8") as outfile:
    json.dump(udataset, outfile)

print("Question type stats:\n")

for qtype in statistics:
    print(
        qtype
        + "\ttotal: "
        + str(statistics[qtype])
        + "\t percentage: "
        + str(round(100 * statistics[qtype] / total, 3))
        + "%"
    )

print("\nTotal Questions in exported Dataset: " + str(total))
print(
    "Unique Questions: "
    + str(len(unique))
    + ", Questions in Initial Dataset: "
    + str(len(dataset))
)
print("Average Answer length (tokens): " + str(sum(answer_tokens) / len(answer_tokens)))
# %%

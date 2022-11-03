import json
import matplotlib.pyplot as plt
import sys



with open(sys.argv[1], encoding='utf8') as json_file:
    dataset = json.load(json_file)

try:
    prefix = sys.argv[2]
except:
    prefix = ""

types = set()
for entry in dataset:
    types.add(entry["type"])

thresholds = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

for t in types:
    p =  []
    r = []
    f1 = []
    acc = []
    print("type: "+t)
    for entry in dataset:
        if(t == entry["type"]):
            p.append(entry["precision"])
            r.append(entry["recall"])
            f1.append(entry["f1"])
            acc.append(entry["accuracy"])
    plt.clf()
    plt.plot(thresholds,p,label="Precision")
    plt.plot(thresholds,r,label="Recall")
    plt.plot(thresholds,f1,label="F1")
    plt.plot(thresholds,acc,label="Accuracy")
    plt.xlabel("Threshold")
    plt.axis([0,1,0,100])
    plt.legend()
    plt.title("Metrics for Answer type: "+t)
    # plt.show()
    plt.savefig("./figures/"+prefix+t+".png")




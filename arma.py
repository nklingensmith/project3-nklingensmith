import os
import argparse
import csv
import itertools

def combiner(item1, item2, itemsnum):
    if itemsnum == 1:
        return (item1, item2)
    else:
        combarr = []
        for k in item1:
            if k not in combarr:
                combarr.append(k)
        for k in item2:
            if k not in combarr:
                combarr.append(k)
        combarr.sort()
        return tuple(combarr)
def check_support(assdict, item, itemsnum):
    support = 0
    if itemsnum == 1:
        for k in assdict:
            if item in assdict[k]:
                support += 1
    else:
        for k in assdict:
            bothin = True
            for itemi in item:
                bothin = bothin and itemi in assdict[k]
            if bothin:
                support += 1

    return support

parser = argparse.ArgumentParser(description='A-Priori association rule mining algorithm.')
parser.add_argument('input_filename')
parser.add_argument('output_filename')
parser.add_argument('min_support_percentage', type=float)
parser.add_argument('min_confidence', type=float)

args = parser.parse_args()
assdict = {}
basesets = []
validsets = {}
conf = {}
totaltransactions = 0
numitems = 0
with open(args.input_filename) as csvfile:
    reader = csv.reader(csvfile, delimiter=',', skipinitialspace=True)
    for row in reader:
       assdict[row[0]] = row[1:]
       totaltransactions += 1

#for k in assdict:
#    for i in range(len(assdict[k])):
#        if i == 0:
#            continue
#        for comb in itertools.combinations(assdict[k],i):
#            itemsets.add(comb)
#
#print(itemsets)
for k in assdict:
    for v in assdict[k]:
        if v not in basesets:
            basesets.append(v)
numitems = len(basesets)
basesets.sort()
validsets[1] = {}

for i in range(numitems):
    support = check_support(assdict, basesets[i], 1)
    if support / totaltransactions >= args.min_support_percentage:
        validsets[1][basesets[i]] = support

for i in range(numitems):
    if i <= 1: continue
    validsets[i] = {}
    j = 0
    for vj in validsets[i-1]:
        k = 0
        for vk in validsets[i-1]:
            if k <= j: 
                k += 1
                continue
            neword = combiner(vj, vk, i-1)
            if len(neword) != i: continue
            support = check_support(assdict, neword, i)
            if support / totaltransactions >= args.min_support_percentage:
                validsets[i][neword] = support
            k += 1
        j += 1

for i in range(numitems):
    if i <= 1: continue
    for v in validsets[i]:
        for comb in itertools.permutations(v):
            for j in range(1, len(comb),1):
                if(j == 1):
                    side1 = comb[0]
                    side2 = comb[j:]
                else:
                    side1 = tuple(comb[:j])
                    side2 = tuple(comb[j:])
                
                if side1 not in validsets[j]: continue
                if validsets[i][v] / validsets[j][side1] >= args.min_confidence:
                    if len(side2) == 1:
                        side2 = side2[0]
                    else:
                        side2 = tuple(sorted(side2))
                    conf[(v, side1, side2)] = validsets[i][v] / validsets[j][side1]
with open(args.output_filename, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    for i in range(numitems):
        if i == 0: continue
        for k in validsets[i]:
            towrite = []
            towrite.append("S")
            towrite.append("{0:.4f}".format(validsets[i][k] / totaltransactions))
            if i == 1:
                towrite.append(str(k))
            else:
                for j in range(len(k)):
                    towrite.append(str(k[j]))
            writer.writerow(towrite)
    
    for k in conf:
        towrite = []
        towrite.append("R")
        towrite.append("{0:.4f}".format(validsets[len(k[0])][k[0]] / totaltransactions))
        towrite.append("{0:.4f}".format(conf[k]))
        if type(k[1]) is str:
            towrite.append(k[1])
        else:
            for i in range(len(k[1])):
                towrite.append(str(k[1][i]))
        towrite.append("\'=>\'")
        if type(k[2]) is str:
            towrite.append(k[2])
        else:
            for i in range(len(k[2])):
                towrite.append(str(k[2][i]))
        writer.writerow(towrite)
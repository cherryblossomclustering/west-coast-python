#!/bin/usr/python

from os import listdir
from os.path import isfile, join
from collections import OrderedDict
import pprint

# hard-coded
version='1.5.5'
mypath = './outputs/D2'
model_root = '/dropbox/16-17/573/Data/models/devtest'

def merge_two_dicts(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z

class Vividict(OrderedDict):
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value

def recursive_print(dict1, dict2, depth, string):
    for k, v in dict1.items():
        if depth == 3:

            new_string = string + "." + k
            

            print("<EVAL ID=\"%s\">" % (new_string))
            print("<PEER-ROOT>")
            print(mypath)
            print("</PEER-ROOT>")
            print("<MODEL-ROOT>")
            print(model_root)
            print("</MODEL-ROOT>")
            # print(string)
            
            print("<INPUT-FORMAT TYPE=\"SPL\">")
            print("</INPUT-FORMAT>")
            print("<PEERS>")
       
            for x, y in v.items():
                print("<P ID=\"%s\">%s</P>" % (x, ".".join([new_string, x])))
                # print(x)

            print("</PEERS>")
            print("<MODELS>")
            
            x = new_string.split(".")
            for x, y in dict2[x[0]][x[1]][x[2]].items():
                print("<M ID=\"%s\">%s</M>" % (x, ".".join([new_string, x])))
                # print(x)

            print("</MODELS>")
            print("</EVAL>")
        else:
            if string == "":
                new_string = string + k
            else:
                new_string = string + "." + k
            recursive_print(v, dict2, depth+1, new_string)

model_list = list()

files = [f for f in listdir(mypath) if isfile(join(mypath, f))]
d = Vividict()

for f in files:
    tokens = f.split('.')

    token1 = tokens[0]
    token2 = tokens[1]
    token3 = tokens[2]
    token4 = tokens[3]
    token5 = tokens[4]

    d[token1][token2][token3][token4][token5]

model_files = [f for f in listdir(mypath) if isfile(join(mypath, f))]
model_dict = Vividict()

for g in model_files:
    tokens = g.split('.')

    token1 = tokens[0]
    token2 = tokens[1]
    token3 = tokens[2]
    token4 = tokens[3]
    token5 = tokens[4]

    model_dict[token1][token2][token3][token4][token5]

print("<ROUGE_EVAL version=\"%s\">" % (version))
this_list = recursive_print(d, model_dict, 0, "")
print("</ROUGE_EVAL>")

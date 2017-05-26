# Karen Kincy - calculate IDF and CBOW model from Wikipedia corpus
# LING 573
# 5-24-2017
# Deliverable #4
# background_corpus_wiki.py

import nltk
from string import punctuation
import json 
from math import log
import sys
from collections import OrderedDict
from gensim.models import Word2Vec

# arguments for program: background_corpus_wiki.py backgroundFile limitDocs
backgroundFile =  sys.argv[1]
limitDocs = int(sys.argv[2])

# calculate IDF for TF*IDF
backgroundCount = OrderedDict()
idf = OrderedDict() 
numberDocs = 0

background = open(backgroundFile, "r")

sentences = []
for line in background:
    
    # use this to limit number of documents loaded
    if numberDocs == limitDocs:
        break 
    
    # look for tag marking each new doc
    if "#s-doc" in line:
        numberDocs += 1
        continue

    if line == "":
        continue
    
    # ignore first three tokens; they are just tags:
    # #s-sent 1       37      After a tour together...
    tokens = nltk.word_tokenize(line.lower())
    tokens = tokens[4:]
    
    # save cleaned tokens for CBOW model
    sentences.append(tokens)

    # count tokens in background corpus
    for word in tokens:
        word = word.lower()
        if not all((char in punctuation) for char in word):
            if word not in backgroundCount:
                backgroundCount[word] = 1
            else:
                backgroundCount[word] += 1
   
# calculate IDF for terms
for term, count in backgroundCount.items():
    idf[term] = log(numberDocs / float(count))
    

# train CBOW model on cleaned sentences
cbow = Word2Vec(sentences, size=100, window=5, min_count=5, max_vocab_size=25000)

# cache out IDF scores to JSON file
with open("wikipediaIDF.json", "w") as file:
    json.dump(idf, file)

# cache out CBOW model to file
with open("wikipediaCBOW", "wb") as file:
    cbow.save(file)



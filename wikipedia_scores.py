# Karen Kincy - query expansion via Wikipedia articles on topics
# LING 573
# 5-23-2017
# Deliverable #4
# wikipedia_scores.py

import nltk
from string import punctuation 
from math import log 
from nltk.corpus import stopwords
import os
import json
import sys
import operator
import re
from collections import OrderedDict

# key = name of topic (identical to guided summary)
# value = dictionary of <word, TF*IDF> pairs
scores = {}

# arguments for program: 
# wikipedia_scores.py inputDirectory wikiIDFCache corpusChoice
directory =  sys.argv[1]
wikiIDFCache = sys.argv[2]
corpusChoice = sys.argv[3]

# load the cached out IDF scores from Wikipedia background corpus
idf = {}
if corpusChoice == "wikipedia":
    with open(wikiIDFCache) as file:
        idf = json.load(file)
    
    
elif corpusChoice == "reuters":
    from nltk.corpus import reuters
    backgroundCount = {}
    corpus = reuters.words()
    numberDocs = len(reuters.fileids())
    for word in corpus:
        word = word.lower()
        if not all((char in punctuation) for char in word):
            if word not in backgroundCount:
                backgroundCount[word] = 1
            else:
                backgroundCount[word] += 1

    for term, count in backgroundCount.items():
        idf[term] = log(numberDocs / float(count))
    

stopWords = set(stopwords.words('english'))
moreStops = {"'s", "ft", "km", "m", "mm", "kg", "mph", "kmph", \
             "lb", "sq", "mi", "cu"}
stopWords = stopWords | moreStops

docCount = 1
for filename in os.listdir(directory):
    file = open(directory + filename, "r")
    termCounts = {}
    termFreq = {}
    
    # get name of topic from filename
    topic = ""
    filename = filename[:-4] # ignore ".txt" extension
    tokens = filename.split("_")
    del tokens[0]
    for token in tokens:
        topic += token + " "
    
    topic = topic.strip()
    
    lineCount = 0
    for line in file:
        # ignore first three lines of Wikpedia articles (date, line, title)
        if (lineCount == 0) or (lineCount == 1) or (lineCount == 2):
            lineCount += 1
            continue

        lineCount += 1
        
        # clean text in file using regexes
        line = re.sub("\[[^\s]+\]", "", line)
        line = re.sub("[^A-Za-z\-\'\s]+", " ", line)
        
         # remove excess whitespaces and newlines
        line = " ".join(line.split())
        
        # ignore blank lines
        if line == "":
            continue
        
        # lowercase and tokenize
        tokens = nltk.word_tokenize(line.lower())

        # count sentence tokens; ignore stopwords
        for token in tokens:
            if token not in stopWords:
                if token not in termCounts:
                    termCounts[token] = 1
                else:
                    termCounts[token] += 1

    
    # calculate term frequency for this topic
    for term, count in termCounts.items():
        termFreq[term] = count / docCount
    termFreq = sorted(termFreq.items(), key=operator.itemgetter(1), reverse=True)
     
    # calculate tf*idf for each term in this topic
    tfidf = {}
    for term, tf in termFreq:
        if term in idf:
            tfidf[term] = tf * idf[term]
        else:
            tfidf[term] = tf
    
    # calculate centroid for this article 
    centroidSize = 100
    allTerms = sorted(tfidf.items(), key=operator.itemgetter(1), reverse=True)
    centroid = OrderedDict(allTerms[:centroidSize])
    
    print("\n" + topic + "\n")
    for term, tfidf in centroid.items():
        print(term, tfidf)
    
    # add centroid to this topic to scores
    scores[topic] = centroid
        

# cache out entire set of scores to JSON file
with open("wikipediaScores.json", "w") as file:
    json.dump(scores, file)
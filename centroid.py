# Karen Kincy - centroid-based summarization algorithm
# Travis Nguyen - redundancy penalty and knapsack algorithm
# LING 573
# 5-5-2017
# Deliverable #3
# centroid.py

import nltk
from string import punctuation 
import json 
import sys
import operator
import re
import random
import string
from math import log
from collections import OrderedDict
from knapsack import knapsack
import time

start = time.time()

# arguments for program:
# centroid.py <inputFile> <centroidSize> <topN> <corpusChoice> \
# <centroidWeight> <positionWeight> <firstWeight> <redundancyWeight>
inputFile = sys.argv[1]
centroidSize = int(sys.argv[2])
topN = int(sys.argv[3])
corpusChoice = sys.argv[4]
centroidWeight = float(sys.argv[5])
positionWeight = float(sys.argv[6])
firstWeight = float(sys.argv[7])
redundancyWeight = float(sys.argv[8])


# represents a sentence in centroid-based summarization algorithm
class Sentence:
    def __init__(self, text, tokens, allTokens, wordCount, \
                 headline, position, doc, chronology):
        self.text = text
        self.tokens = tokens            # lowercased; no punct-only tokens
        self.allTokens = allTokens
        self.wordCount = wordCount
        self.headline = headline
        self.position = position
        self.doc = doc 
        self.chronology = chronology    # integer rank for chronological order
        self.centroidScore = 0.0
        self.positionScore = 0.0
        self.firstSentScore = 0.0
        self.totalScore = 0.0
        self.redundancyPenalty = 0.0
        
# each Cluster holds a list of Sentence instances and a centroid of top N terms
class Cluster:    
    def __init__(self, number, topicID, topic, documents, tf, tfidf, centroid):
        self.number = number
        self.topicID = topicID
        self.topic = topic        
        self.documents = documents      # dict of <int, list<Sentence>> pairs
        self.tf = tf                    # dict of <term, TF> pairs
        self.tfidf = tfidf              # dict of <term, TF*IDF> pairs
        self.centroid = centroid        # OrderedDict of <term, TF*IDF> pairs
        

# calculate IDF from background corpus
backgroundCount = {}
idf = {}


# implemented choice of background corpora
corpus = []
numberDocs = 1
if corpusChoice == "brown":
    from nltk.corpus import brown
    corpus = brown.words(categories='news')
    numberDocs = len(brown.fileids(categories='news'))
    
elif corpusChoice == "brown_all":
    from nltk.corpus import brown
    corpus = brown.words()
    numberDocs = len(brown.fileids())
    
elif corpusChoice == "reuters":
    from nltk.corpus import reuters
    corpus = reuters.words()
    numberDocs = len(reuters.fileids())

else:
    sys.stderr.write("incorrect choice for corpus.\n")

for word in corpus:
    word = word.lower()
    if not all((char in punctuation) for char in word):
        if word not in backgroundCount:
            backgroundCount[word] = 1
        else:
            backgroundCount[word] += 1

for term, count in backgroundCount.items():
    idf[term] = log(float(numberDocs) / float(count))


# read in the preprocessed corpora from a JSON file
with open(inputFile) as file:
    corpora = json.load(file)
    
# after cleaning text with regexes, save to file to verify processing
afterRegexes = open("afterRegexes.txt", "w")

# for each cluster, extract documents sentence-by-sentence
clusters = []
clusterNumber = 0

# tracy was here
for topicID, value in corpora.items():
    docCount = 1
    termCounts = {}
    termFreq = {}
    documents = {}
    
    for document in value["docs"]:
        headline = document["headline"].replace("\n", " ")
     
        # NOTE: start sentence count at 1 for positional value calculation
        sentCount = 1
        
        # tokenize, lowercase, remove punctuation tokens,
        # strip newline and tab characters;
        # use regexes to clean preprocessing artifacts
        for chronology, line in document["sentences"].items():
            line = re.sub("\n{2,}.+\n{2,}", "", line)     
            line = re.sub(".*\n*.*(By|BY|by)(\s\w+\s\w+?\))", "", line) 
            line = re.sub("^[0-9\-:\s]+", "", line)
            line = re.sub("^usa\s+", "", line)
            line = re.sub("^[A-Z]+;", "", line)
            line = re.sub("^[\s\S]+News\sService", "", line)
            line = re.sub("^BY[\s\S]+News", "", line)
            line = re.sub("MISC.[\s\S]+\)", "", line)
            line = re.sub(".*\(RECASTS\)", "", line)
            line = re.sub(".*\(REFILING.+\)", "", line)
            line = re.sub(".*\(UPDATES.*\)", "", line)

            # remove excess whitespaces and newlines
            line = " ".join(line.split())
            
            # added more regexes 
            line = re.sub("^\&[A-Z]+;", "", line)
            line = re.sub("^[A-Z]+.*_", "", line)
            line = re.sub("^[_]+.*", "", line)
            line = re.sub("^[A-Z]+.*_", "", line)
            line = re.sub("^.*OPTIONAL.*\)", "", line)
            line = re.sub("^.*optional.*\)", "", line)
            line = re.sub("^.*\(AP\)\s+--", "", line)
            line = re.sub("^.*\(AP\)\s+_", "", line)
            line = re.sub("^.*[A-Z]+s+_", "", line)
            line = re.sub("^.*\(Xinhua\)", "", line)
            
            # ignore lines with quotes in them;
            # quotes are disruptive to summaries
            if '"' in line:
                continue
            
            # losing some useful information with this hack
            if "NEWS STORY" in line:
                continue
            
            # these sentences seem to be junk
            if "PROFILE" in line:
                continue
            
            # ignore advertising garbage
            if "Non-subscribers" in line:
                continue
            
            # ignore all caps sentences
            if line.upper() == line:
                continue
            
            # ignore blank lines
            if len(line) == 0:
                continue 
            
            afterRegexes.write(line + "\n\n")
            
            # lowercase all the tokens
            rawTokens = nltk.word_tokenize(line.lower())

             # Karen: changing to actual length of tokens
            wordCount = len(rawTokens)

            allTokens = {}
            sentenceTokens = {}
            for token in rawTokens:

                # save ALL tokens in sentence;
                # need for knapsack algorithm
                if token not in allTokens:
                    allTokens[token] = 1
                else:
                    allTokens[token] += 1
                
                # remove punctuation-only tokens
                if not all((char in punctuation) for char in token):
        
                    # save local counts for sentence;
                    # need for first sentence overlap score
                    if token not in sentenceTokens:
                        sentenceTokens[token] = 1
                    else:
                        sentenceTokens[token] += 1
                    
                    # save global counts for cluster;
                    # need for centroid score
                    if token not in termCounts:
                        termCounts[token] = 1
                    else:
                        termCounts[token] += 1

            # sort sentences by document into dictionary;
            # key = document number, value = list of Sentence instances                 
            if docCount not in documents:
                documents[docCount] = []
                documents[docCount].append(Sentence
                         (line, sentenceTokens, allTokens, wordCount, \
                          headline, sentCount, docCount, chronology))
            else:
                documents[docCount].append(Sentence
                         (line, sentenceTokens, allTokens, wordCount, \
                          headline, sentCount, docCount, chronology))     
 
            sentCount += 1
        docCount += 1
    
    # calculate term frequency for this cluster
    for term, count in termCounts.items():
        termFreq[term] = count / docCount
    termFreq = sorted(termFreq.items(), key=operator.itemgetter(1), reverse=True)
     
    # calculate tf*idf for each term in this cluster
    tfidf = {}
    for term, tf in termFreq:
        if term in idf:
            tfidf[term] = tf * idf[term]
        else:
            tfidf[term] = tf
    
    # remove noisy terms leftover from tokenizing
    tfidf.pop("'s", None)
    tfidf.pop("n't", None)
    
    # calculate centroid for cluster
    allTerms = sorted(tfidf.items(), key=operator.itemgetter(1), reverse=True)
    centroid = OrderedDict(allTerms[:centroidSize])
    
    # calculate centroid score for each sentence;
    # sum of scores for all words in the centroid
    for document, sentences in documents.items():
        for sentence in sentences:
            for token in sentence.tokens:
                if token in centroid:
                    sentence.centroidScore += centroid[token]

    # calculate positional score for each sentence
    for document, sentences in documents.items():
        bestCentroidScore = 0.0
        for sentence in sentences:
            if sentence.centroidScore > bestCentroidScore:
                bestCentroidScore = sentence.centroidScore
        
        # set positional score of first sentence in document
        # equal to highest centroid score of all sentences in document
        N = len(sentences)
        firstSentence = sentences[0]
        for sentence in sentences:
            score = (N - sentence.position + 1) / N
            score = score * bestCentroidScore
            sentence.positionScore = score 
     
            # calculate first sentence overlap for each sentence
            overlap = 0.0
            for word, count in firstSentence.tokens.items():
                if word in sentence.tokens:
                    overlap += count * sentence.tokens[word]
            sentence.firstSentScore = overlap

            # total these scores for each sentence;
            # weight each of these scores
            sentence.totalScore = \
            (sentence.centroidScore * centroidWeight) \
            + (sentence.positionScore * positionWeight) \
            + (sentence.firstSentScore * firstWeight)
            
            # tracy was here
            # save topicID for each cluster from JSON file
    
    clusters.append(Cluster(clusterNumber, topicID, value["title"], documents, \
                            termFreq, tfidf, centroid))
    clusterNumber += 1

# generate set of unique alphanums for summary filenames 
alphanums = set()
for i in range(100):
    key = ""
    for j in range(10):
        key += random.choice(string.ascii_uppercase + string.digits)
    
    alphanums.add(key)

 
# for each cluster, select the best sentences for summary
# using redundancy penalty and knapsack algorithm
for cluster in clusters:

    # output centroid for each cluster (for sanity check)
    sys.stdout.write("Cluster #{0}\n".format(cluster.number))
    sys.stdout.write("Topic: {0}\n".format(cluster.topic))
#    sys.stdout.write("TopicID: {0}\n".format(cluster.topicID))
#    sys.stdout.write("Centroid: \n")
#    
#    for term, tfidf in cluster.centroid.items():
#        sys.stdout.write("{0}\t{1}\n".format(term, tfidf))
#    sys.stdout.write("\n")
    
    # save the top sentences for each cluster
    sents = []  
    for document, sentences in cluster.documents.items():
        for sentence in sentences:
            sents.append(sentence)

    word_list = set()

    for idx, sent in enumerate(sents):
        
        # penalize every sentence based on the overlapping words
        # first sentence does not get penalized at all
        if idx == 0: # first sentence
            sent_words = sents[0].tokens.keys()
            word_list = set(word_list) & set(sent_words)

        else:
            sent1 = sents[idx-1]
            sent2 = sents[idx]

            # get types of words in each sentence
            sent1_words = sent1.tokens.keys()
            sent2_words = sent2.tokens.keys()

            # get word count for each sentence
            sent1_len = sent1.wordCount
            sent2_len = sent2.wordCount

            # calculate cross-sentence word overlap
            new_word_list = set(word_list) | set(sent2_words)
            overlap = set(word_list) & set(sent2_words)
            overlap_len = len(overlap)

            # to cover strange case of zero-length sentences
            if sent1_len != 0 or sent2_len != 0:
                # calculate redundancy penalty
                redundancyPenalty = float(2 * overlap_len) / float(sent1_len + sent2_len)

                # calculate total score of sentence
                cur_sent = sents[idx]
                cur_sent.redundancyPenalty = (redundancyPenalty * redundancyWeight)
                cur_sent.totalScore = cur_sent.totalScore - cur_sent.redundancyPenalty

            word_list = new_word_list

    bestSentences = sorted(sents, key=lambda x: x.totalScore, reverse=True)[:topN]

    # createList
    knapsackList = list()

    # changed so knapsack algorithm only considers top N sentences
    curWordCount = 0.0
    for sentence in bestSentences: 
        curWordCount += sentence.wordCount
        knapsackList.append([sentence, sentence.wordCount])

    # limit of 100 whitespace-delimited tokens for each summary
    threshold = 100
    bestScore, bestList = knapsack(knapsackList, threshold)
    bestSummary = list()

    # to improve information ordering,
    # sort knapsack output by chronological order of sentences
    chronList = sorted(bestList, key=lambda x: x[0].chronology, reverse=False)

    for result in chronList:
        bestSummary.append(result[0].text)
        
    #  output summary to stdout (for sanity check)
    sys.stdout.write("\n".join(bestSummary))
    sys.stdout.write("\n\n")

 
    # output each summary to filename with format:
    # [id_part1]-A.M.100.[id_part2].[some_unique_alphanum]
    # where topic ID in the form "D0901A" is split into:
    # id_part1 = D0901, and id_part2 = A
    unique = alphanums.pop()
    filename = cluster.topicID[:-1] + "-A.M.100." + cluster.topicID[-1] \
                             + "." + unique
                             

    # write each summary to a file;
    # each sentence in summary should be on its own line
#    output = open(filename, "w")
#    output.write("\n".join(bestSummary))
#    output.write("\n\n")
#    output.close()

    
end = time.time()
sys.stdout.write("{0} seconds runtime\n".format(end - start))

afterRegexes.close()
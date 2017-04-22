# Karen Kincy
# LING 573
# 4-21-2017
# Deliverable #2
# centroid.py

from string import punctuation 
import nltk
import json 
import sys
import operator
import re
from math import log
from nltk.corpus import brown
from collections import OrderedDict
from knapsack import knapsack

# arguments for program:
# centroid.py <inputFile> <centroidSize> <topN> <corpusChoice>

inputFile = sys.argv[1]
centroidSize = int(sys.argv[2])
topN = int(sys.argv[3])
corpusChoice = sys.argv[4]

# Travis was here
compressionRate = 0.25

# represents a sentence in centroid-based summarization algorithm
class Sentence:
    def __init__(self, text, tokens, allTokens, wordCount, headline, position, doc):
        self.text = text
        self.tokens = tokens            # lowercased; no punct-only tokens
        self.allTokens = allTokens
        self.wordCount = wordCount
        self.headline = headline
        self.position = position
        self.doc = doc
        self.positionScore = 0.0
        self.firstSentScore = 0.0
        self.centroidScore = 0.0
        self.totalScore = 0.0
        self.redundancyPenalty = 0.0
        
# each Cluster holds a list of Sentence instances and a centroid of top N terms
class Cluster:    
    def __init__(self, name, topic, documents, tf, tfidf, centroid):
        self.name = name
        self.topic = topic              
        self.documents = documents      # dict of <int, list<Sentence>> pairs
        self.tf = tf                    # dict of <term, TF> pairs
        self.tfidf = tfidf              # dict of <term, TF*IDF> pairs
        self.centroid = centroid        # OrderedDict of <term, TF*IDF> pairs
        

# calculate IDF from background corpus
backgroundCount = {}
idf = {}

if corpusChoice == "brown":
    brownNews = brown.words(categories='news')
    for word in brownNews:
        word = word.lower()
        if not all((char in punctuation) for char in word):
            if word not in backgroundCount:
                backgroundCount[word] = 1
            else:
                backgroundCount[word] += 1

    numberDocs = len(brown.fileids(categories='news'))
    for term, count in backgroundCount.items():
        idf[term] = log(float(numberDocs) / float(count))

# elif corpusChoice == "nyt":
    # TODO implement choice of background corpora
 
else:
    sys.stderr.write("incorrect choice for corpus; must be 'brown'\n")
     
    
# read in the preprocessed corpora from a JSON file
with open(inputFile) as file:
    corpora = json.load(file)

# for each cluster, extract documents sentence-by-sentence
clusters = []
for key, value in corpora.items():
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
        for line in document["sentences"]:
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

            line = " ".join(line.split())
            
            # losing some useful information with this hack
            if "NEWS STORY" in line:
                continue
            
            # ignore blank lines
            if len(line) == 0:
                continue 
            
            rawTokens = nltk.word_tokenize(line.lower())

            # Travis was here
            wordCount = 0

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

                    # Travis was here
                    wordCount += 1

            # sort sentences by document into dictionary;
            # key = document number, value = list of Sentence instances                 
            if docCount not in documents:
                documents[docCount] = []
                documents[docCount].append(Sentence
                         (line, sentenceTokens, allTokens, wordCount, headline, sentCount, docCount))
            else:
                documents[docCount].append(Sentence
                         (line, sentenceTokens, allTokens, wordCount, headline, sentCount, docCount))     
 
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

            # total these scores for each sentence
            sentence.totalScore = sentence.centroidScore + sentence.positionScore \
            + sentence.firstSentScore 
    
    clusters.append(Cluster(key, value["title"], documents, termFreq, tfidf, centroid))


# output the clusters and their centroids 
for cluster in clusters:
    sys.stdout.write("Cluster #{0}\n".format(cluster.name))
    sys.stdout.write("Topic: {0}\n".format(cluster.topic))
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

    # Travis was here
#    for idx, sent in enumerate(sents):
#        # penalize every sentence based on the overlapping words
#        # first sentence does not get penalized at all
#        if sent.position == 1: # first sentence
#            pass
#        else:
#            sent1 = sents[idx-1]
#            sent2 = sents[idx]
#
#            # get types of words in each sentence
#            sent1_words = sent1.tokens.keys()
#            # print("sent1 length: %d" % (len(sent1_words)))
#            sent2_words = sent2.tokens.keys()
#            # print("sent2 length: %d" % (len(sent2_words)))
#
#            sent1_len = 0
#            sent2_len = 0
#
#            for token, count in sent1.tokens.items():
#                sent1_len += int(count)
#            
#            for token, count in sent2.tokens.items():
#                sent2_len += int(count)
#            
#            # calculate cross-sentence word overlap
#            overlap = set(sent1_words) & set(sent2_words)
#            overlap_len = len(overlap)
#
#            # to cover strange case of zero-length sentences
#            if sent1_len != 0 or sent2_len != 0:
#                # calculate redundancy penalty
#                redundancyPenalty = float(2 * overlap_len) / float(sent1_len + sent2_len)
#
#                # calculate total score of sentence
#                cur_sent = sents[idx]
#                cur_sent.redundancyPenalty = redundancyPenalty
#                cur_sent.totalScore = cur_sent.totalScore - cur_sent.redundancyPenalty

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
                cur_sent.redundancyPenalty = redundancyPenalty
                cur_sent.totalScore = cur_sent.totalScore - cur_sent.redundancyPenalty

            word_list = new_word_list

    bestSentences = sorted(sents, key=lambda x: x.totalScore, reverse=True)[:topN]

#    for sentence in bestSentences:
#        sys.stdout.write("from doc #{0}:\n".format(sentence.doc))
#        sys.stdout.write("{0} {1}\n".format(sentence.position, sentence.text))
#        sys.stdout.write("centroid score: {0}\n".format(sentence.centroidScore))
#        sys.stdout.write("position score: {0}\n".format(sentence.positionScore))
#        sys.stdout.write("first sentence score: {0}\n".format(sentence.firstSentScore))
#        sys.stdout.write("total score: {0}\n\n".format(sentence.totalScore))

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

    # sys.stdout.write("Threshold: %s\n" % threshold)
    # sys.stdout.write("Best score: %s\n" % bestScore)
    # sys.stdout.write("\n")

    bestSummary = list()

    for thing in bestList:
        bestSummary.append(thing[0].text)

    # each sentence in summary should be on its own line
    sys.stdout.write("\n".join(bestSummary))

    sys.stdout.write("\n\n")

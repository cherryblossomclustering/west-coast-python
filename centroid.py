# Karen Kincy - centroid-based summarization algorithm
# Travis Nguyen - redundancy penalty and knapsack algorithm
# LING 573
# 5-25-2017
# Deliverable #4
# centroid.py

import nltk
from string import punctuation 
import json 
import sys
import operator
import time
import argparse, functools
from gensim.models import Word2Vec
from math import log
from collections import OrderedDict
from knapsack import knapsack
import collections
from math import sqrt
from key import Key
from keylogger import Keylogger

start = time.time()
# tracy was here
# arguments for program:
# centroid.py <inputFile> <centroidSize> <topN> <corpusChoice> \
# <centroidWeight> <positionWeight> <firstWeight> <redundancyWeight>
args_parser = argparse.ArgumentParser(description="Create document summaries.")
args_parser.add_argument("inputFile", help="Name of corpus file")
args_parser.add_argument("--size", help="Size of centroid.", type=int, required=True)
args_parser.add_argument("--topN", help="Number of top N sentences to grab per cluster.", type=int, required=True)
args_parser.add_argument("--corpus", help="Specify which corpus to use: Reuters or Brown.", required=True)
args_parser.add_argument("--centWeight", help="Weight of each centroid.", type=float, required=True)
args_parser.add_argument("--posWeight", help="Weight to attribute to sentence position w/i document.", type=float, required=True)
args_parser.add_argument("--first", help="Weight to attribute to first sentence w/i document.", type=float, required=True)
args_parser.add_argument("--red", help="Weight to attribute to redundancy penalty", type=float, required=True)
args_parser.add_argument("--topW", help="Weight added for each sentences that matches topic", type=float, required=True)
args_parser.add_argument("--wikiScores", help="JSON file with top 100 terms from Wikipedia articles")
args_parser.add_argument("--wikiWeight", help="Weight to Wikipedia score", type=int, required=True)
args_parser.add_argument("--wikiIDF", help="Cached out IDF scores from Wikipedia", required=False)
args_parser.add_argument("--wikiCBOW", help="Cached out CBOW model from Wikipedia", required=False)

args = args_parser.parse_args()

inputFile = args.inputFile
centroidSize = args.size
topN = args.topN
corpusChoice = args.corpus
centroidWeight = args.centWeight
positionWeight = args.posWeight
firstWeight = args.first
redundancyWeight = args.red
topicWeight = args.topW
wikipediaScores = args.wikiScores
wikiWeight = args.wikiWeight
wikiIDF = args.wikiIDF
wikiCBOW = args.wikiCBOW

# custom sorter for the sentences after being placed in knapsack
def sent_sort(a, b):
    if a[0].position == 1: # favors 1st sentences
        if b[0].position == 1 and b[0].date < a[0].date:
            return -1
        else:
            return 1
    if a[0].date < b[0].date:
        return 1
    elif a[0].date == b[0].date:
        if a[0].position <= b[0].position:
            return 1
        else:
            return -1
    else:
        return -1

# represents a sentence in centroid-based summarization algorithm
class Sentence:
    def __init__(self, text, tokens, allTokens, wordCount, \
                 headline, position, doc, date):
        self.text = text
        self.tokens = tokens            # lowercased; no punct-only tokens
        self.allTokens = allTokens
        self.wordCount = wordCount
        self.headline = headline
        self.position = position
        self.doc = doc 
        self.date = date                # date the document was created
        self.centroidScore = 0.0
        self.positionScore = 0.0
        self.firstSentScore = 0.0
        self.topicScore = 0.0
        self.wikipediaScore = 0.0       # based on terms from Wikipedia article
        self.totalScore = 0.0
        self.redundancyPenalty = 0.0
        
# each Cluster holds a list of Sentence instances and a centroid of top N terms
class Cluster:    
    def __init__(self, number, topicID, topic, topicTokens, documents, tf, tfidf, centroid):
        self.number = number
        self.topicID = topicID
        self.topic = topic              # the topic associated with this cluster   
        self.topicTokens = topicTokens      
        self.documents = documents      # dict of <int, list<Sentence>> pairs
        self.tf = tf                    # dict of <term, TF> pairs
        self.tfidf = tfidf              # dict of <term, TF*IDF> pairs
        self.centroid = centroid        # OrderedDict of <term, TF*IDF> pairs
     
 
# this key is shared among all summary output files
# alphanum = "PEWYV0JHEG"

# generate unique alphanumeric key for this test run
#for j in range(10):
#    alphanum += random.choice(string.ascii_uppercase + string.digits)

alphanum = Key()
keylogger = Keylogger('key.log')
keylogger.log_key(alphanum, sys.argv[1:])

# calculate IDF from background corpus
backgroundCount = {}
idf = {}

# implemented choice of background corpora
corpus = []
numberDocs = 1
if corpusChoice == "brown":
    from nltk.corpus import brown
    corpus = brown.words(categories='news')
    cbow = Word2Vec(brown.sents(categories="news"))
    numberDocs = len(brown.fileids(categories='news'))
    
elif corpusChoice == "brown_all":
    from nltk.corpus import brown
    corpus = brown.words()
    cbow = Word2Vec(brown.sents())
    numberDocs = len(brown.fileids())
    
elif corpusChoice == "reuters":
    from nltk.corpus import reuters
    corpus = reuters.words()
    cbow = Word2Vec(reuters.sents())
    numberDocs = len(reuters.fileids())
    
elif corpusChoice == "wikipedia":
    from nltk.corpus import reuters
    with open(wikiIDF) as file:
        idf = json.load(file)
    cbow = Word2Vec.load(wikiCBOW)

else:
    cbow = None
    sys.stderr.write("incorrect choice for corpus.\n")

if corpusChoice != "wikipedia":
    for word in corpus:
        word = word.lower()
        if not all((char in punctuation) for char in word):
            if word not in backgroundCount:
                backgroundCount[word] = 1
            else:
                backgroundCount[word] += 1
    
    for term, count in backgroundCount.items():
        idf[term] = log(numberDocs / float(count))


# read in the preprocessed corpora from a JSON file
corpora = OrderedDict() 
with open(inputFile) as file:
    corpora = json.load(file, object_pairs_hook=collections.OrderedDict)
    
# load the cached out Wikipedia scores 
wikipedia = {}
with open(wikipediaScores) as file:
    wikipedia = json.load(file)
    
# for each cluster, extract documents sentence-by-sentence
clusters = []
clusterNumber = 0

# tracy was here
for topicID, value in corpora.items():
    docCount = 1
    termCounts = {}
    termFreq = {}
    documents = {}
    topic = value["title"]
    topicTokens = value["title"].lower().split()
                
    for document in value["docs"]:
        headline = document["headline"].replace("\n", " ")

        # NOTE: start sentence count at 1 for positional value calculation
        sentCount = 1
        
        # tokenize, lowercase, remove punctuation tokens,
        # strip newline and tab characters;
        # use regexes to clean preprocessing artifacts
        date = document["id"][-13:-5]
        for chronology, line in document["sentences"].items():  
            
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
                          headline, sentCount, docCount, date))
            else:
                documents[docCount].append(Sentence
                         (line, sentenceTokens, allTokens, wordCount, \
                          headline, sentCount, docCount, date))
 
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
    # sum of scores for all words in the centroid;
    for document, sentences in documents.items():
        for sentence in sentences:
            for token in sentence.tokens:
                if token in centroid:
                    sentence.centroidScore += centroid[token]

                # also calculate topic score for this sentence; 
                # use CBOW model to check similarity of token vs. topic term
                for topic_word in topicTokens:
                    if token in cbow.wv and topic_word in cbow.wv \
                    and cbow.wv.similarity(topic_word, token) >= 0.75:
                        sentence.topicScore += 1    # bonus point
                        break                       # only look at one similar topic word for each token
                    elif token == topic_word:       # just in case the word embeddings do not have that topic word but the words match
                        sentence.topicScore += 1
                        break
                
                # calculate Wikipedia score using CBOW model to check similarity
                if topic in wikipedia:       
                    for topic_word in wikipedia[topic]:
                        if token in cbow.wv and topic_word in cbow.wv \
                        and cbow.wv.similarity(topic_word, token) >= 0.75:
                            sentence.wikipediaScore += 1
                            break
                        elif token == topic_word:
                            sentence.wikipediaScore += 1
                            break

                # TF*IDF version of Wikipedia score           
#                if topic in wikipedia:
#                     if token in wikipedia[topic]:
#                         sentence.wikipediaScore += wikipedia[topic][token]


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
            + (sentence.firstSentScore * firstWeight) \
            + (sentence.topicScore * topicWeight) \
            + (sentence.wikipediaScore * wikiWeight)

    
    clusters.append(Cluster(clusterNumber, topicID, topic, topicTokens, documents, \
                            termFreq, tfidf, centroid))
    clusterNumber += 1


# for each cluster, select the best sentences for summary
# using redundancy penalty and knapsack algorithm
for cluster in clusters:

    # output centroid for each cluster (for sanity check)
    sys.stdout.write("Cluster #{0}\n".format(cluster.number))
    sys.stdout.write("Topic: {0}\n".format(cluster.topic))
    sys.stdout.write("TopicID: {0}\n".format(cluster.topicID))
#    sys.stdout.write("Centroid: \n")
#    
#    for term, tfidf in cluster.centroid.items():
#        sys.stdout.write("{0}\t{1}\n".format(term, tfidf))
#    sys.stdout.write("\n")

    # save all sentences for each cluster
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
    
    
    # use cosine similarity to remove redundant sentences
    allSents = set(bestSentences)
    redundantSents = set()
    for firstIndex, first in enumerate(bestSentences):
        
        # don't double-count redundancy
        if first in redundantSents:
            continue
        
        firstDenom = 0.0
        for word, count in first.tokens.items():
            firstDenom += pow(count, 2)
            
        for secondIndex, second in enumerate(bestSentences):
            
            # don't double-count redundancy
            if second in redundantSents:
                continue 
            
            # ignore if sentences are identical
            if firstIndex == secondIndex:
                continue
            
            numerator = 0.0
            secondDenom = 0.0
            for word, count in second.tokens.items():
                secondDenom += pow(count, 2)
                if word in first.tokens:
                    numerator += count * first.tokens[word]
        
            denominator = sqrt(firstDenom) * sqrt(secondDenom)
            cosineSim = numerator / denominator
            
            # 0.7 seems to be good threshold
            if cosineSim > 0.7:
#                print(cosineSim)
#                print(first.text)
#                print(second.text)

                # add the lower-scoring "copycat" sentence to redundant set
                if first.totalScore > second.totalScore:
                    redundantSents.add(second)
                
                else:
                    redundantSents.add(first)
    
    # remove redundant sentences 
    bestSentences = list(allSents - redundantSents)

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

    # tracy was here
    # sort knapsack output by date and order of sentences
    chronList = sorted(bestList, key=functools.cmp_to_key(sent_sort))

    for result in chronList:
        bestSummary.append(result[0].text)
        
    #  output summary to stdout (for sanity check)
    sys.stdout.write("\n".join(bestSummary))
    sys.stdout.write("\n\n")

    # output each summary to filename with format:
    # [id_part1]-A.M.100.[id_part2].[some_unique_alphanum]
    # where topic ID in the form "D0901A" is split into:
    # id_part1 = D0901, and id_part2 = A
    filename = cluster.topicID[:-1] + "-A.M.100." + cluster.topicID[-1] \
                             + "." + alphanum.get_key()
        
    # write each summary to a file;
    # each sentence in summary should be on its own line
    output = open(filename, "w")
    output.write("\n".join(bestSummary))
    output.write("\n\n")
    output.close()

end = time.time()
sys.stdout.write("{0} seconds runtime\n".format(end - start))
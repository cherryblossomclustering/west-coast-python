#!/usr/bin/env python3

# Tracy Rohlin - sentence compression for content realization
# Karen Kincy - additional regexes for cleaning input text
# LING 573
# 5-25-2017
# Deliverable #4
# compressor.py

import re, sys, json, time
import subprocess
import string
from nltk import pos_tag
from nltk import word_tokenize
from nltk.tree import *
from copy import deepcopy
import collections
from collections import OrderedDict

def scrubber(line):
    # remove junk from input corpora
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
    line = re.sub("@", "", line)
    line = re.sub(r"SOURCE:.*", "", line)
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
    
    # even more regexes for D4 -- they never end!
    line = re.sub("[A-Za-z\-\.\s\&;]*\(.+\)\s+_", "", line)
    line = re.sub("(?i)by\s[A-Z]+(\s[A-Z\.]+)?\s[A-Z]+.?", "", line)
    line = re.sub("([A-Z\s\-\(\)]{2,})\s\(\w+\)\s--\s", "", line)
    line = re.sub("[A-Za-z\s=\(\-)]+///", "", line)
    line = re.sub("[A-Za-z\s=\(\-)]+=", "", line)
    line = re.sub("[A-Z]{2,}[A-Za-z,\s\.]+--\s", "", line)
    line = re.sub("^\s*--\s*", "", line)
    line = re.sub("([A-Z\s]+\s){2,}", "", line)
    
    # again, remove excess whitespaces and newlines
    line = " ".join(line.split())
    line = " ".join(line.split("\n"))
    
    # ignore sentences less than 5 tokens long
    if len(word_tokenize(line)) < 5:
        return ""
      
    # ignore lines with quotes in them;
    # quotes are disruptive to summaries
    match = re.search("\"|''|``", line)
    if match:
        return ""
    
    # losing some useful information with this hack
    if "NEWS STORY" in line:
        return ""
    
    # these sentences seem to be junk
    if "PROFILE" in line:
        return ""
    
    # ignore advertising garbage
    if "Non-subscribers" in line:
        return ""
    
    # ignore all caps sentences
    if line.upper() == line:
        return ""
    
    # ignore blank lines
    if len(line) == 0:
        return "" 
    
    return line


def regex_and_pos_remover(sentence):

    date_words = {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
                      "january", "february", "march", "april", "may", "june", "july", "august",
                    "september", "october", "november", "december", "today", "tomorrow", "yesterday",
                      "week", "day", "month"}
    temp_markers = {"next", "last", "past", "after", "late", "this"}
    prepositions = {"for", "in", "on"}
    hour_markers = {"morning", "evening", "afternoon", "night"}
    temporal_words = {"hereafter", "afterward", "before", "conclusion", "now"}
    advs_to_keep = {"especially", "virtually", "allegedly", "nearly", "almost", "up", "down", "not", 'north'
                    'south', 'east', 'west', 'northeast', 'southeast', 'northwest', 'southwest'}
    sentence = re.sub(r"^(\b\w+\b\s*){2,3}\,", "", sentence, flags=re.IGNORECASE).strip()        # remove any transition phrases
    # remove attributives
    sentence = re.sub(r"\,[\sA-Za-z-]*(said|say|reported|report|ruled|according|argued|argue)+.*\.", ".", sentence, flags=re.IGNORECASE)
    tagged_sent = pos_tag(sentence.split())
    tagged_len = len(tagged_sent)
    clean = []
    i = 0
    while i < tagged_len:
        cur_word = tagged_sent[i][0]
        cur_word = cur_word[:-1] if cur_word[-1] == "," else cur_word
        cur_word = cur_word[:-2] if cur_word[-2:] == "'s" else cur_word
        if tagged_sent[i][1] == "RB" or cur_word.lower() in temporal_words:
            if tagged_sent[i][0].lower() in advs_to_keep:
                clean.append(cur_word)
                
        elif cur_word.lower() in date_words:
            if i-1 > 0:
                prev_word = tagged_sent[i-1][0]
                prev_word = prev_word[:-1] if prev_word[-1] == "," else prev_word
                prev_word = prev_word[:-2] if prev_word[-2:] == "'s" else prev_word
                if clean and (prev_word.lower() in prepositions or prev_word.lower() in temp_markers):
                   del clean[-1]
                   
            if i+1 < tagged_len:
                next_word = tagged_sent[i+1][0]
                next_word = next_word[:-1] if next_word[-1] == "," else next_word
                if next_word in hour_markers:
                    del tagged_sent[i+1]
                    tagged_len -= 1
        else:
            if cur_word.lower() != "can" or cur_word.lower() != "have":     # remove modals
                clean.append(cur_word)
        i += 1


    sentence =  " ".join(clean)
    last_char = "." if sentence[-1] not in string.punctuation else ""
    return sentence[0].upper() + sentence[1:] + last_char

def traverse(t):
    if len(t) == 0:
        return t
    else:
        i = 0
        num_children = len(t)
        while i < num_children:
            next_node = t[i]
            try:
                label = next_node.label().strip()
                if (label == "CC"):
                    if next_node[0] == 'and' and next_node.right_sibling().label().strip() == "S":
                        sibling_index = 0
                        for j in range(i, len(t)):
                            if t[j].label().strip() == "S":
                                sibling_index = i
                                break


                        t.remove(t[i])
                        t.remove(t[sibling_index])
                        return None
                else:
                    node = traverse(next_node)
                    if node != None:
                        t[i] =  node
                    else:
                        i -= 1
                i += 1
            except AttributeError:
                return t
    return t


def parse_compressor(sentence):
    args = ["/opt/jdk8/bin/java", "-classpath", "./src:/NLP_TOOLS/tool_sets/stanford-corenlp/latest/*:.",
            "ParserCompressor"] + ['"{0}"'.format(sentence)]

    tokens = word_tokenize(sentence)
    orig_spellings = {}
    for t in tokens:                # hold onto the original capitalization as it affects ROUGE
        lower_token = t.lower()
        if lower_token not in orig_spellings:
            orig_spellings[lower_token] = t

    results = subprocess.check_output(args, universal_newlines=True)
    tree = ParentedTree.fromstring(results)
    clean_tree = []
    for leaf in tree.leaves():
        clean_token = str(leaf)
        try:
            clean_tree.append(orig_spellings[clean_token])
        except KeyError:
            clean_tree.append(clean_token)
    prev_char = clean_tree[0]
    if not prev_char.isalnum():
        clean_tree = prev_char + " ".join(clean_tree[1:])
    else:
        clean_tree = " ".join(clean_tree)
    clean_tree = re.sub(r"\s\$\s", " $", clean_tree)
    clean_tree = re.sub(r"\s\(\s", " (", clean_tree)
    clean_tree = re.sub(r"\s\)\s", ") ", clean_tree)
    clean_tree = re.sub(r' (?=\W)', '', clean_tree)
    return clean_tree[0].upper() + clean_tree[1:] 


def sentence_compressor(line):
    clean_line = scrubber(line)
    if len(clean_line) > 0:
        clean_line = regex_and_pos_remover(clean_line)
        #clean_line = parse_compressor(clean_line)      # reduces scores
    return clean_line

def load_json(in_json, out_json):
    data = OrderedDict() 
    with open(in_json, "r") as j_file:
        data = json.load(j_file, object_pairs_hook=collections.OrderedDict)
        
    # after regexes, save to file to verify processing
    afterRegexes = open("afterRegexes.txt", "w")
    sentence_counter = 1
    
    # make a deep copy of data
    compressed = deepcopy(data)
    
    for cluster_id in compressed.keys():
        for doc in compressed[cluster_id]['docs']:
            for sent_id, sentence in doc["sentences"].items():
                print("Cleaning sentence # " + str(sentence_counter))
                sentence_counter += 1
                clean_sentence = sentence_compressor(sentence)

                afterRegexes.write("\n" + clean_sentence + "\n")
                doc["sentences"][sent_id] = clean_sentence
                          
            
    with open(out_json, "w") as j_out:
        json.dump(compressed, j_out)

    afterRegexes.close()


if __name__ == "__main__":
    time0 = time.time()
    load_json(sys.argv[1], sys.argv[2])
    time1 = time.time()
    print((time1-time0)/60)
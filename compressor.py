#!/usr/bin/env python3

import re, sys, json
import subprocess
from nltk import pos_tag

def scrubber(line):
    if "`" in line or "''" in line:
        return ""
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
    line = re.sub("^\s+--", "", line)

    # even more regexes for D4
    line = re.sub("^[A-Z\-\s,]+\.+--", "", line)

    # again, remove excess whitespaces and newlines
    line = " ".join(line.split())

    # ignore lines with quotes in them;
    # quotes are disruptive to summaries
    if '"' in line:
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
        cur_word = tagged_sent[i][0].lower()
        cur_word = cur_word[:-1] if cur_word[-1] == "," else cur_word
        cur_word = cur_word[:-2] if cur_word[-2:] == "'s" else cur_word
        if tagged_sent[i][1] == "RB" or cur_word in temporal_words:
            if tagged_sent[i][0].lower() in advs_to_keep:
                clean.append(cur_word)
        elif cur_word in date_words:
            if i-1 > 0:
                prev_word = tagged_sent[i-1][0].lower()
                prev_word = prev_word[:-1] if prev_word[-1] == "," else prev_word
                prev_word = prev_word[:-2] if prev_word[-2:] == "'s" else prev_word
                if clean and (prev_word in prepositions or prev_word in temp_markers):
                   del clean[-1]
            if i+1 < tagged_len:
                next_word = tagged_sent[i+1][0]
                next_word = next_word[:-1] if next_word[-1] == "," else next_word
                if next_word in hour_markers:
                    del tagged_sent[i+1]
                    tagged_len -= 1
        else:
            if cur_word != "can" or cur_word != "have":     # remove modals
                clean.append(cur_word)
        i += 1
    """clean_sent = re.sub(r"\s\$\s", " $", " ".join(clean).capitalize())
    clean_sent = re.sub(r"\s\(\s", " (", clean_sent)
    clean_sent = re.sub(r"\s\)\s", ") ", clean_sent)
    return re.sub(r' (?=\W)', '', clean_sent.capitalize())"""
    return " ".join(clean).capitalize()

def sentence_compressor(line):
    clean_line = scrubber(line)
    clean_sent = ""
    if len(clean_line) > 0:
        clean_sent = regex_and_pos_remover(clean_line)
        #parse_compressor(clean_sent)
    return clean_sent

def parse_compressor(sentence):
    args = ["/opt/jdk8/bin/java", "-classpath", "./src:/NLP_TOOLS/tool_sets/stanford-corenlp/latest/*:.",
            "ParserCompressor"] + ['"{0}"'.format(sentence)]
    results = subprocess.check_output(args, universal_newlines=True)

def load_json(in_json, out_json):
    with open(in_json, "r") as j_file:
        data = json.load(j_file)
    for cluster_id in data.keys():
        cluster = data[cluster_id]
        for i in range(len(cluster['docs'])):
            for sent_id, sentence in cluster['docs'][i]["sentences"].items():
                clean_sentence = sentence_compressor(sentence)
                cluster['docs'][i]["sentences"][sent_id] = clean_sentence
        data[cluster_id] = cluster
    with open(out_json, "w") as j_out:
        json.dump(data, j_out)



if __name__ == "__main__":
    load_json(sys.argv[1], sys.argv[2])

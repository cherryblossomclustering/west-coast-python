import re, string
from nltk import pos_tag, word_tokenize


def temporal_modal_remover(sentence):

    date_words = {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
                      "january", "february", "march", "april", "may", "june", "july", "august",
                    "september", "october", "november", "december", "today", "tomorrow", "yesterday",
                      "week", "day", "month"}
    temp_markers = {"next", "last", "past", "after", "late"}
    prepositions = {"for", "in", "on"}
    hour_markers = {"morning", "evening", "afternoon", "night"}
    temporal_words = {"hereafter", "afterward", "before", "conclusion", "now"}
    advs_to_keep = {"especially", "virtually", "allegedly", "nearly", "almost", "up", "down", "not"}
    sentence = re.sub(r"^(\b\w+\b\s*){2,3}\,", "", sentence, flags=re.IGNORECASE).strip()        # remove any transition phrases
    # remove attributives
    sentence = re.sub(r"\,[\sA-Za-z-]*(said|say|reported|report|ruled|according|argued|argue)+.*\.", ".", sentence, flags=re.IGNORECASE)
    tagged_sent = pos_tag(word_tokenize(sentence))
    tagged_len = len(tagged_sent)
    clean = []
    i = 0
    while i < tagged_len:
        cur_word = tagged_sent[i][0].lower()


        if tagged_sent[i][1] == "RB" or cur_word in temporal_words:
            if tagged_sent[i][0].lower() in advs_to_keep:
                clean.append(cur_word)
            else:
                if i-1 >= 0 and tagged_sent[i-1][0] == ",":
                        del clean[-1]                       # previous token is a comma
                if i+1 < tagged_len and tagged_sent[i+1][0] == ",":
                    del tagged_sent[i+1]
                    tagged_len -= 1
        elif cur_word in date_words:
            if i-1 >= 0:
                prev_word = tagged_sent[i-1][0].lower()
                if (prev_word == "," or prev_word in prepositions or prev_word in temp_markers):
                   del clean[-1]
            if i+1 < tagged_len:
                next_word = tagged_sent[i+1][0]
                if next_word == "," or next_word in hour_markers:
                    del tagged_sent[i+1]
                    tagged_len -= 1
                if i+2 < tagged_len and next_word == "'" and tagged_sent[i+2][0].lower() == 's':
                    del tagged_sent[i+1:i+3]
                    tagged_len -= 2
        else:
            if cur_word != "can" or cur_word != "have":     # remove modals
                clean.append(cur_word)
        i += 1
    clean_sent = re.sub(r"\s\$\s", " $", " ".join(clean).capitalize())
    clean_sent = re.sub(r"\s\(\s", " (", clean_sent)
    clean_sent = re.sub(r"\s\)\s", ") ", clean_sent)
    return re.sub(r' (?=\W)', '', clean_sent.capitalize())

def sentence_compressor(sentence):
    return temporal_modal_remover(sentence)


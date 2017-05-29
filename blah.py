import nltk

with open('test.txt') as f:
    document = f.read()

sentences = nltk.sent_tokenize(document)
sentences = [nltk.word_tokenize(sent) for sent in sentences]
sentences = [nltk.pos_tag(sent) for sent in sentences]

print(sentences)

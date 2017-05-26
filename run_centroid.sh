#!/bin/sh
python3 centroid.py compressed-corpora.json --size 100 --topN 40 --corpus wikipedia --centWeight 5 --posWeight 1 --first 1 --red 100 --topW 10 --wikiScores wikipediaScores50000.json --wikiWeight 200 --wikiIDF wikipediaIDF50000.json --wikiCBOW wikipediaCBOW50000mincount2

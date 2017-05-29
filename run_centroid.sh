#!/bin/sh
python3 centroid.py compressed-eval-corpora.json --size 600 --topN 60 --corpus wikipedia --wikiScores wikipediaScores50000.json --wikiWeight 200 --wikiIDF wikipediaIDF50000.json --wikiCBOW wikipediaCBOW50000mincount2

#!/bin/sh
python3 centroid.py compressed-eval-corpora.json --size 600 --topN 60 --corpus wikipedia --wikiScores /home2/kincyk/573/wikipedia/wikipediaScores50000.json --wikiWeight 200 --wikiIDF /home2/kincyk/573/wikipedia/wikipediaIDF50000.json --wikiCBOW /home2/kincyk/573/wikipedia/wikipediaCBOW50000mincount2

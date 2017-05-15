# west-coast-python
Private repository for the LING 573 (Natural Language Processing Systems and Applications) course at the University of Washington (Spring 2017).


The guided summary file is an SGML document that contains a list of clusters with a set of doc_ids per cluster.  Each doc file is located in either 2 separate directories on the server and is likewise an SGML file containing doc-ids, headlines, topic titles, dates and the actual text of the document.  The parser loads in the guided summary file and recursively searches for the doc-id against both corpus folders and opens the file as needed, reads it, filters out any duplicated headline and the corresponding doc-id, and does some simple reg-ex substitution to remove the sgml tags.  

Command for the sgml parser:
    
        sgml_parser.py /dropbox/16-17/573/Data/Documents/devtest/GuidedSumm10_test_topics.xml /corpora/LDC/LDC02T31/ /corpora/LDC/LDC08T25/  corpora.json
        
But since the result has been previously cached in corpora.json, this program does not need to be run.  Instead corpora.json is loaded directly in to the centroid.py program:

System arguments for centroid.py, which handles centroid-based summarization: 
    
    centroid.py <inputFile> --size <centroidSize> --topN <topN> --corpus <corpusChoice> --centWeight <centroidWeight> --posWeight <sentencePositionWeight> --first <firstSentenceWeight> --red <redundancyPenalty> --topW <topicWeight>    

Currently, the centroid-based summarization algorithm calculates four scores for each sentence in a cluster: the centroid score, position score, first sentence overlap score, and the topic relatedness score. These scores are based on the MEAD system outlined in Radev et. al. (2003). The redundancy algorithm suggested in the original MEAD system compares sentences pairwise, but we have updated the algorithm so that the redundancy penalty is calculated for the current sentence and all sentences already chosen for the summary. This further reduces redundancy and increases the variety of sentences included in the summaries.

For each sentence in a cluster, represented by an instance of the Sentence class, the total score = centroid score + position score + first sentence overlap score + topic relatedness score - redundancy penalty. The total score for each sentence is used by the knapsack algorithm to select the best combination of sentences under the threshold of 100 words (whitespace-delimited tokens).

After selecting the highest scored sentences by way of knapsack.py, the sentences are then sorted using an algorithm similar to that proposed by Bollegala, et al. (2011).  Instead of purely using the date and sentence positions to order the sentences, the algorithm favors sentences that are first in their respective documents, then sorts based on date and finally on sentence positions within the document in the case where two sentences come from documents with the same date.  Preferring first sentences over sorting purely on datetime was found to create more readable summaries by our group.

### ROUGE Evaluation Toolkit

Before running the ROUGE evaluation toolkit, a settings.xml file must be generated:

    python3 generate_settings_xml.py /dropbox/16-17/573/Data/models/devtest ./outputs/D3 settings.xml

Next, run the ROUGE evaluation toolkit: 

    ./ROUGE-1.5.5.pl -e /dropbox/16-17/573/code/ROUGE/data -a -n 4 -x -m -c 95 -r 1000 -f A -p 0.5 -t 0 -l 100 -s -d settings.xml > rouge.out 2>rouge.err

A summary of the results from the ROUGE evaluation toolkit can also be generated, if needed:

    calculate_recall_mean_std.py rouge.out summary.out

NOTES ON RUNNING CENTROID.PY:

Preliminary tests suggest the arguments "--size 100 --topN 10 --corpus reuters --centWeight 5 --posWeight 1 --first 1 --red 100 --topW 1" will produce good summaries. Setting the value of topN too high results in sentences with low scores being selected by the knapsack algorithm, producing poorer summaries as a result. The largest increase in ROUGE scores overall resulted in increasing the centroid weight score to 5 whereas changing the other parameters (position weight, first sentence weight, etc.) reduce the ROUGE recall scores.  Using a continuous BOW to score the similarity between tokens and words in the topic titles (e.g. "Columbine Massacre") increased the scores by about 1% or less depending on the ROUGE metric used.  The continuous BOW's similarity threshold was hand-tuned with the best scores resulting in using a score of >= 0.75 in comparing topic word and token.

The background corpora now includes the choices "brown", "brown_all", and "reuters" to include the "news" subset of the Brown corpus, all of the Brown corpus, and all of the Reuters corpus, respectively.  Through testing we found that the using the Reuters background corpus increases ROUGE scores 1-2% compared to the two Brown corpora choicies. This is likely due to the large size of the Reuters corpus, in addition to its focus on the news domain.

Also note that centroid.py requires the file knapsack.py to run, since this file contains the knapsack algorithm. In addition, centroid.py loads the preprocessed input corpora from the JSON file corpora.json.

CREDITS:

Preprocessing of corpora, topic weight, CBOW, sentence ordering - Tracy

Centroid-based summarization algorithm, weights, more post-processing regexes, choice of background corpora - Karen

Redundancy penalty, knapsack algorithm, ROUGE bug fix, automatic scoring - Travis

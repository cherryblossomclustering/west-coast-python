# west-coast-python
Private repository for the LING 573 (Natural Language Processing Systems and Applications) course at the University of Washington (Spring 2017).


The guided summary file is an SGML document that contains a list of clusters with a set of doc_ids per cluster.  Each doc file is located in either 2 separate directories on the server and is likewise an SGML file containing doc-ids, headlines and the actual text of the document.  The parser loads in the guided summary file and recursively searches for the doc-id against both corpus folders and opens the file as needed, reads it, filters out any duplicated headline and the corresponding doc-id, and does some simple reg-ex substitution to remove the sgml tags.  

Command for the sgml parser:
    
        sgml_parser.py /dropbox/16-17/573/Data/Documents/devtest/GuidedSumm10_test_topics.xml /corpora/LDC/LDC02T31/ /corpora/LDC/LDC08T25/  corpora.json

Command for centroid.py, which handles centroid-based summarization: 

    centroid.py corpora.json 20 10 brown
    
where the system arguments are as follows:
    
    centroid.py <inputFile> <centroidSize> <topN> <corpusChoice>

Currently, the centroid-based summarization algorithm calculates three scores for each sentence in a cluster: the centroid score, position score, and first sentence overlap score. These scores are based on the MEAD system outlined in Radev et. al. (2003). The redundancy algorithm suggested in the original MEAD system compares sentences pairwise, but we have updated the algorithm so that the redundancy penalty is calculated for the current sentence and all sentences already chosen for the summary.

For each sentence in a cluster, represented by an instance of the Sentence class, the total score = centroid score + position score + first sentence overlap score - redundancy penalty. The total score for each sentence is used by the knapsack algorithm to select the best combination of sentences under the threshold of 100 words (whitespace-delimited tokens).

NOTES ON RUNNING CENTROID.PY:

Preliminary tests suggest arguments of centroidSize = 100 and topN = 10 will produce good summaries. Setting the value of topN too high results in sentences with low scores being selected by the knapsack algorithm, producing poorer summaries as a result. We plan to test more parameters and optimize these algorithms for D3.

Please note that the choice of background corpora has not yet been implemented; use the argument "brown" for the last parameter, which defaults to the "news" subset of the Brown corpus (loaded from NTLK).

Also note that centroid.py requires the file knapsack.py to run, since this file contains the knapsack algorithm, and loads the preprocessed input corpora from the JSON file corpora.json.

CREDITS:

Preprocessing of corpora - Tracy

Centroid-based summarization algorithm - Karen

Redundancy penalty and knapsack algorithm - Travis

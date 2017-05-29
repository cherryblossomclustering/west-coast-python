# west-coast-python
Private repository for the LING 573 (Natural Language Processing Systems and Applications) course at the University of Washington (Spring 2017).


The guided summary file is an SGML document that contains a list of clusters with a set of doc_ids per cluster.  Each doc file is located in either 2 separate directories on the server and is likewise an SGML file containing doc-ids, headlines, topic titles, dates and the actual text of the document.  The parser loads in the guided summary file and recursively searches for the doc-id against both corpus folders and opens the file as needed, reads it, filters out any duplicated headline and the corresponding doc-id, and does some simple reg-ex substitution to remove the sgml tags.  

Command for the sgml parser:
    
        sgml_parser.py /dropbox/16-17/573/Data/Documents/devtest/GuidedSumm10_test_topics.xml /corpora/LDC/LDC02T31/ /corpora/LDC/LDC08T25/  <corpus-file>
        
But since the result has been previously cached in corpora.json, this program does not need to be run.  Instead corpora.json is loaded directly in to the centroid.py program.  The eval set has been processed and cached already in the eval-corpora.json file but here is the command line for the eval_parser.py:

      eval_parser.py /dropbox/16-17/573/Data/Documents/evaltest/GuidedSumm11_test_topics.xml /corpora/LDC/LDC11T07 <corpus-file>

This takes about 6.5 hours on Patas due to the nature of the compressed files.

The compressor.py file does sentence compression on a corpus file by cleaning the text through regexes, removing temporal expressions, adjuncts and attributives.  An attempt at parsing and removing the second sibling of the 'and' conjunct was attempted but ultimately reduced scores.  The command for the compressor is:
    
     compressor.py <old-corpus.json> <new-corpus.json>

### Notes on Running Centroid.py:

System arguments for centroid.py, which handles centroid-based summarization: 
    
    centroid.py <inputFile> --size <centroidSize> --topN <topN> --corpus <corpusChoice> --wikiScores <wikipediaScore> --wikiWeight <wikipediaWeight> --wikiIDF <wikipediaIDF> --wikiCBOW <wikipediaCBOW>    
    
Current best parameters:

    centroid.py compressed-eval-corpora.json --size 600 --topN 60 --corpus wikipedia --wikiScores wikipediaScores50000.json --wikiWeight 200 --wikiIDF wikipediaIDF50000.json --wikiCBOW wikipediaCBOW50000mincount2  

Note that centroid.py requires the file knapsack.py to run, since this file contains the knapsack algorithm. In addition, centroid.py requires several cached out input files:

    compressed-eval-corpora.json | compressed-corpora.json
    wikipediaScores50000.json
    wikipediaIDF50000.json
    wikipediaCBOW50000mincount2

The --corpora parameter allows the choice between "wikipedia", "brown", "brown_all", and "reuters" to include the cached out Wikipedia corpus subset, the "news" subset of the Brown corpus, all of the Brown corpus, and all of the Reuters corpus, respectively. Currently, the Wikipedia corpus performs the best.

The centroid-based summarization algorithm calculates four scores for each sentence in a cluster: the centroid score, position score, first sentence overlap score, and the topic relatedness score. These scores are based on the MEAD system outlined in Radev et. al. (2003). The redundancy algorithm suggested in the original MEAD system compares sentences pairwise, but we have updated the algorithm so that the redundancy penalty is calculated for the current sentence and all sentences already chosen for the summary. This further reduces redundancy and increases the variety of sentences included in the summaries. In addition to these four scores, centroid.py calculates a fifth score, wikipediaScore, which improves upon the earlier topic focus score. Additional details about the Wikipedia score and CBOW model follow in the next section.

For each sentence in a cluster, represented by an instance of the Sentence class, the total score = centroid score + position score + first sentence overlap score + topic relatedness score + wikipedia score - redundancy penalty. The total score for each sentence is used by the knapsack algorithm to select the best combination of sentences under the threshold of 100 words (whitespace-delimited tokens).

After selecting the highest scored sentences by way of knapsack.py, the sentences are then sorted using an algorithm similar to that proposed by Bollegala, et al. (2011).  Instead of purely using the date and sentence positions to order the sentences, the algorithm favors sentences that are first in their respective documents, then sorts based on date and finally on sentence positions within the document in the case where two sentences come from documents with the same date.  Preferring first sentences over sorting purely on datetime was found to create more readable summaries by our group.

### Wikipedia Score, IDF, and CBOW model

Please note that the following scripts do not need to be run during testing, since their outputs have been cached out:

    background_corpus_wiki.py
    background_wiki.cmd
    background_wiki.sh
    compressor.py
    eval_parser.py
    sents_from_wiki.cmd
    sents_from_wiki.sh
    sgml_parser.py
    wikipedia_scores.py

Cached outputs:

    corpora.json
    compressed-corpora.json
    compressed-eval-corpora.json
    eval-corpora.json
    wikipediaScores50000.json
    wikipediaIDF50000.json
    wikipediaCBOW50000mincount2
    wikipedia.zip
    
Though the cached outputs do _not_ need to be generated again, you can recreate wikipediaScores5000.json, wikipediaIDF50000.json, and wikipediaCBOW50000mincount2 files by running the following scripts in this order:
    
    condor_submit sents_from_wiki.cmd
    condor_submit background_wiki.cmd
    python3 wikipedia_scores.py ./wikipedia/ wikipediaIDF50000.json wikipedia

Note that sents_from_wiki.cmd produces a large file, around 11 GB, from the tagged and cleaned Wikipedia corpus on Patas.
Also note that wikipedia_scores.py requires the documents in the wikipedia.zip file to be extracted into a folder named wikipedia.

For each topic in both the devtest and evaltest corpora, the relevant Wikipedia article is cached out by manually searching for the topic string on Wikipedia (e.g., "Giant Pandas") and disambiguating the topic by human judgment to find the most relevant article. The text from this article is then downloaded and saved in wikipedia.zip. After removing stopwords, TF-IDF is calculated for every term in the topic article. The top 100 highest-scoring terms per topic are cached out in the wikipediaScores50000.json file. The suffix "50000" refers to using wikipediaIDF50000.json for IDF scores, calculated using 50,000 documents from the Wikipedia corpus on Patas.

The CBOW (continuous bag of words) model was trained using Word2Vec, also using 50,000 documents from the Wikipedia corpus. The following parameters were used during training:

    cbow = Word2Vec(sentences, size=100, window=5, min_count=2, max_vocab_size=25000)
    
The min_count=2 parameter allows the model to ignore terms seen less than two times during training. This reduced the size of the cached  model, and did not significantly affect ROUGE scores.

### ROUGE Evaluation Toolkit

Before running the ROUGE evaluation toolkit, a settings.xml file must be generated:

    python3 generate_settings_xml.py /dropbox/16-17/573/Data/models/devtest ./outputs/D3 settings.xml

Next, run the ROUGE evaluation toolkit: 

    ./ROUGE-1.5.5.pl -e /dropbox/16-17/573/code/ROUGE/data -a -n 4 -x -m -c 95 -r 1000 -f A -p 0.5 -t 0 -l 100 -s -d settings.xml > rouge.out 2>rouge.err

A summary of the results from the ROUGE evaluation toolkit can also be generated, if needed:

    calculate_recall_mean_std.py rouge.out summary.out

### Credits:

Preprocessing of corpora, topic weight, CBOW, sentence ordering - Tracy

Centroid-based summarization algorithm, pre-processing regexes, background corpora, CBOW trained on Wikipedia, Wikipedia topic focus score, cosine similarity redundancy reduction - Karen

Redundancy penalty, knapsack algorithm, ROUGE bug fix, automatic scoring - Travis

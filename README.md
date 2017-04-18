# west-coast-python
Private repository for the LING 573 (Natural Language Processing Systems and Applications) course at the University of Washington (Spring 2017).


The guided summary file is an SGML document that contains a list of clusters with a set of doc_ids per cluster.  Each doc file is located in either 2 separate directories on the server and is likewise an SGML file containing doc-ids, headlines and the actual text of the document.  The parser loads in the guided summary file and recursively searches for the doc-id against both corpus folders and opens the file as needed, reads it, filters out any duplicated headline and the corresponding doc-id, and does some simple reg-ex substitution to remove the sgml tags.  

Command for the sgml parser:
    
        sgml_parser.py /dropbox/16-17/573/Data/Documents/devtest/GuidedSumm10_test_topics.xml /corpora/LDC/LDC02T31/ /corpora/LDC/LDC08T25/  corpora.json

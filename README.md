# west-coast-python
Private repository for the LING 573 (Natural Language Processing Systems and Applications) course at the University of Washington (Spring 2017).

The parser loads in the guided summary file and recursively searches for the doc-id against both corpus folders and opens the file as needed.  

Command for the sgml parser:
    sgml_parser.py /dropbox/16-17/573/Data/Documents/devtest/GuidedSumm10_test_topics.xml /corpora/LDC/LDC02T31/ /corpora/LDC/LDC08T25/  corpora.json

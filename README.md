# west-coast-python
Private repository for the LING 573 (Natural Language Processing Systems and Applications) course at the University of Washington (Spring 2017).

sgml_parser_2.py parses the AQUAINT corpus files and matches the doc_ids found in the GuidedSummary.xml file to the doc_ids found in the corpus files.  The command is: sgml_parser_2.py /corpora/LDC/LDC02T31/ /corpora/LDC/LDC08T25/ /dropbox/16-17/573/Data/Documents/devtest/GuidedSumm10_test_topics.xml corpora.json

The order of the corpus folders is specific as I had to make separate functions for one corpus folder to load the files, and another function for the other corpus folder.

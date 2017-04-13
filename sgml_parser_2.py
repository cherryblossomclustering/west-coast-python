#!/usr/bin/env python

import bs4
import os
import re
import sys, traceback
import logging
import json
import time
from nltk.tokenize import sent_tokenize

class SGMLParser:

    def __init__(self):
        self.time0 = time.time()
        self.clusters = {}
        self.documents = {}
        self.text_files = {}
        self.loaded_files = set()
        self.doc_counter = 1
        self.xml_pattern = re.compile(r"</*\w+>")


    def find_text_files(self, file_path):
        """
        Parses the document xml files and saves them in memory as a {id: {sentence_id : sentence_text}} mapping.

        :param file_path: File path where the document xml files are (i.e., the AQUAINT data is located)
        :rtype : None

        """
        for root, dirs, files in os.walk(file_path):
            files = [f for f in files if "." not in f]
            for f in files:
                self.text_files[str(f)[:12]] = os.path.join(root, f) # some of the files have an added "_ENG".
                                                                     # Truncate this to make hashing easier later.

    def find_xml_files(self, file_path):
        """
        Parses the document xml files and saves them in memory as a {id: {sentence_id : sentence_text}} mapping.

        :param file_path: File path where the document xml files are (i.e., the AQUAINT-2 data is located)
        :rtype : None

        """

        for root, dirs, files in os.walk(file_path):
            files = [f for f in files if str(f).endswith("xml")]
            for f in files:
                self.text_files[(str(f)[:-4]).upper()] = os.path.join(root, f)

    def process_text(self, file_name):
        """
        Parses the xml file that contains the actual text corresponding to the doc_ids.  Reads in text and
        saves the text and associated headline with a doc_id into a document dict.

        :param file_name: String of the xml file name where the document texts are located.
        :rtype : None
        """
        print("Processing text document " + str(self.doc_counter) + "...")
        self.doc_counter += 1
        try:
            with open(file_name, "r") as f_in:
                xml_text = f_in.read()
                parser = bs4.BeautifulSoup(xml_text, "html.parser")
                docs = parser.find_all("doc")
                for d in docs:
                    if d.docno == None:
                        id = d["id"]
                    else:
                        id = self.xml_pattern.sub("", str(d.docno)).strip()

                    text = self.xml_pattern.sub("",  d.text)
                    hl = self.xml_pattern.sub("", str(d.headline)).strip()
                    self.documents[id] = {"headline":hl, "sentences": sent_tokenize(text)}
        except Exception as e:
            print(e)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
            logging.warning(" " + file_name + " does not exist in the document directory.")


    def create_parent(self, parent_file, json_file):
        """Reads the doc meta xml file that links documents by cluster and creates a parent dictionary
        that groups documents by cluster and includes the text from self.documents as well as the title.
        This cluster dict is then loaded into a json file.

        :param parent_file: The file the contains the document ids clustered by topic.
        :param json_file: JSON file where the cluster dict is dumped.
        :rtype : None"""

        print("Processing parent file...")
        with open(parent_file, "r") as pfile:
            parent_sgml = pfile.read()

        cluster_id = 0
        doc_pattern = re.compile('<doc id\s*="|"></doc>')
        title_pattern = re.compile("<[/]*title>")
        parser = bs4.BeautifulSoup(parent_sgml, "html.parser")

        titles = parser.find_all("title")
        clusters = parser.find_all("docseta")
        for c, t in zip(clusters, titles):
            title = title_pattern.sub("", str(t)).strip()
            self.clusters[cluster_id] = {'title':title, "docs":[]}
            docs = c.find_all()
            for d in docs:
                doc_id = doc_pattern.sub("", str(d)).strip()
                # create two possible file_names to check
                text_file_name = doc_id[3:-5] + "_" + doc_id[:3]  # ex: 19990421_APW
                xml_file_name = doc_id[:-7]
                file_name = text_file_name if text_file_name in self.text_files else xml_file_name

                if file_name in self.text_files and file_name not in self.loaded_files:
                    # if we haven't seen the document before, open it and process it before checking for it the doc dict
                    self.loaded_files.add(file_name)
                    self.process_text(self.text_files[file_name])


                if doc_id in self.documents:
                    self.clusters[cluster_id]["docs"].append(self.documents[doc_id])
                else:
                    logging.warning(" " + doc_id + " does not exist in the document dataset.")
            cluster_id += 1

        with open(json_file, "w") as j_file:
            json.dump(self.clusters, j_file)

        time1 = time.time()
        print((time1-self.time0)/60.0)

    def get_clusters(self):
        """Returns the clustered sentences and titles."""
        return self.clusters




if __name__ == "__main__":
    """First argument is the location of the AQUAINT data.  Second argument is the meta doc xml file."""

    sgml = SGMLParser()
    sgml.find_text_files(sys.argv[1])
    sgml.find_xml_files(sys.argv[2])
    sgml.create_parent(sys.argv[3], sys.argv[4])

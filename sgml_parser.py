#!/usr/bin/env python

import bs4
import os
import re
import sys, subprocess
import json, logging, time

from nltk.tokenize import sent_tokenize

class SGMLParser:

    def __init__(self):
        self.time0 = time.time()
        self.clusters = {}
        self.documents = {}
        self.loaded_files = set()
        self.doc_counter = 1
        self.xml_pattern = re.compile(r"</*\w+>")


    def process_text(self, file_path):
        """
        Parses the xml file that contains the actual text corresponding to the doc_ids.  Reads in text and
        saves the text and associated headline with a doc_id into a document dict.

        :param file_name: String of the xml file name where the document texts are located.
        :rtype : None
        """
        print("Processing text document " + str(self.doc_counter) + ": " + file_path)
        self.doc_counter += 1
        try:
            with open(file_path, "r") as f_in:
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
            logging.warning(" " + file_path + " does not exist in the document directory.")




    def create_parent(self, parent_file, corpus_folders, json_file):
        """Reads the doc meta xml file that links documents by cluster and creates a parent dictionary
        that groups documents by cluster and includes the text from self.documents as well as the title.

        :param parent_file: The file the contains the document ids clustered by topic.
        :rtype : None"""
        print("Processing parent file...")
        with open(parent_file, "r") as pfile:
            parent_sgml = pfile.read()

        cluster_id = 0
        doc_pattern = re.compile('<doc id\s*="|"></doc>')
        title_pattern = re.compile("<[/]*title>")
        cl_doc_pattern = re.compile(":<.*>")

        parser = bs4.BeautifulSoup(parent_sgml, "html.parser")
        titles = parser.find_all("title")
        clusters = parser.find_all("docseta")
        for c, t in zip(clusters, titles):
            title = title_pattern.sub("", str(t)).strip()
            self.clusters[cluster_id] = {'title':title, "docs":[]}
            docs = c.find_all()
            for d in docs:
                location = ""
                doc_id = doc_pattern.sub("", str(d)).strip()
                for directory in corpus_folders:
                    command = 'grep -r "{0}" {1}'.format(doc_id, directory)
                    call = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    (location, err)  = call.communicate()
                    if len(location) != 0:
                        location = cl_doc_pattern.sub("", location).strip()
                        break

                if len(location) == 0:
                    logging.warning(" doc_id " + doc_id + " was not found.")

                if location not in self.loaded_files:
                    self.loaded_files.add(location)
                    self.process_text(location)

                if doc_id in self.documents:
                    self.clusters[cluster_id]["docs"].append(self.documents[doc_id])
                else:
                    print("Warning! " + doc_id + " does not exist in the document dataset.")

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
    sgml.create_parent(sys.argv[1], [sys.argv[2], sys.argv[3]], sys.argv[4])
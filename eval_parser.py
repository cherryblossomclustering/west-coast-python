#!/usr/bin/env python

import bs4
import os
import gzip
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
        self.doc_id_pattern = re.compile(r"[A-Z,a-z]{3}\d+\.\d+")


    def load_texts(self, doc_dict):
        """
        Parses the xml file that contains the actual text corresponding to the doc_ids.  Reads in text and
        saves the text and associated headline with a doc_id into a document dict.

        :param file_name: String of the xml file name where the document texts are located.
        :rtype : None
        """

        doc_counter = 1
        for file_path, docs_to_process in doc_dict.items():
            try:
                with gzip.open(file_path, "r") as f_in:
                    xml_text = f_in.read()
                    parser = bs4.BeautifulSoup(xml_text, "html.parser")
                    docs = parser.find_all("doc")

                    for d in docs:

                        if d.docno == None:
                            id = d["id"]
                        else:
                            id = self.xml_pattern.sub("", str(d.docno)).strip()
                        if id in docs_to_process:
                            print("processing doc: " + id)
                            doc_counter += 1
                            date = self.xml_pattern.sub("", str(d.date_time)).strip()
                            text = self.xml_pattern.sub("",  d.text)
                            hl = self.xml_pattern.sub("", str(d.headline)).strip()
                            sents = sent_tokenize(text)
                            sents[0] = self.doc_id_pattern.sub("", sents[0]) # remove doc ids from the text
                            if hl != None:  # remove duplicate headlines
                                try:
                                    sents[0] = re.sub(hl, "", sents[0])
                                except:
                                    logging.warning("Was unable to remove headline: " + hl)
                            self.documents[id] = {"headline":hl, "sentences": sents, "date": date, "id":id}

            except Exception as e:
                print(e)
                logging.warning(" " + file_path + " does not exist in the document directory.")




    def create_parent(self, parent_file, directory, json_file):
        """Reads the doc meta xml file that links documents by cluster and creates a parent dictionary
        that groups documents by cluster and includes the text from self.documents as well as the title.

        :param parent_file: The file the contains the document ids clustered by topic.
        :rtype : None"""

        print("Processing parent file...")
        with open(parent_file, "r") as pfile:
            parent_sgml = pfile.read()

        doc_pattern = re.compile('<doc id\s*="|"></doc>')
        title_pattern = re.compile("<[/]*title>")

        parser = bs4.BeautifulSoup(parent_sgml, "html.parser")
        titles = parser.find_all("title")
        clusters = parser.find_all("docseta")
        to_process = {}
        doc_to_clust_map = {}
        doc_counter = 1
        for c, t in zip(clusters, titles):
            cluster_id = str(c).split()[1][4:-4]
            title = title_pattern.sub("", str(t)).strip()
            self.clusters[cluster_id] = {'title':title, "docs":[]}
            docs = c.find_all()
            for d in docs:
                doc_counter += 1
                # find the location where that doc id is
                doc_id = doc_pattern.sub("", str(d)).strip()
                file_name = doc_id[:14].lower() + ".gz"
                sub_directory = file_name[:7]
                file_path = directory + sub_directory + "/" + file_name
                command = 'zgrep "{0}" {1}'.format(doc_id, file_path)
                call = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                (found, err)  = call.communicate()
                if err:
                    logging.warning(" doc_id " + doc_id + " was not found.")
                else:
                    # map the cluster ids to the documents, so we can put them in the correct clusters after processing
                    if doc_id not in doc_to_clust_map:
                        doc_to_clust_map[doc_id] = []
                    doc_to_clust_map[doc_id].append(cluster_id)

                    if file_path in to_process:
                        to_process[file_path].append(doc_id)
                    else:
                        to_process[file_path] = [doc_id]

        # load the doc xml file and process each document within it
        self.load_texts(to_process)
        for d_id, d_val in self.documents.items():
            for clust in doc_to_clust_map[d_id]:
                self.clusters[clust]["docs"].append(d_val)

        # organize the docs chronologically within each cluster
        self.organize_docs()
        with open(json_file, "w") as j_file:
            json.dump(self.clusters, j_file)

        time1 = time.time()
        print((time1-self.time0)/60.0)


    def organize_docs(self):
        """Organize the documents by datetime and assign a unique id to each sentence."""
        sentence_id = 1
        for c_id, cluster in self.clusters.items():

            docs = sorted(cluster["docs"], key=lambda x: x["date"])
            for d in range(len(docs)):
                sents = {}
                for s in docs[d]["sentences"]:
                    sents[sentence_id] = s
                    sentence_id += 1
                docs[d]["sentences"] = sents
                cluster["docs"] = docs
            self.clusters[c_id] = cluster
        print(str(sentence_id-1))

    def get_clusters(self):
        """Returns the clustered sentences and titles."""
        return self.clusters




if __name__ == "__main__":
    """First argument is the meta doc xml file. Second argument is the location of the AQUAINT data.  """

    sgml = SGMLParser()
    sgml.create_parent(sys.argv[1], sys.argv[2], sys.argv[3])
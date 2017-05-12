#!/bin/usr/python3

"""
generate_settings_xml.py
Author: Travis Nguyen
Last Modified: 11 May 2017

    This script generates an XML file to be used with the ROUGE evaluation toolkit.

    The usage is as follows:

       $ python3 generate_settings_xml.py <model root> <system root> <output file>

    The model root should be the path to the directory containing the gold standard
    summaries, and the system root should be the path to the directory containing
    the summaries to be evaluated.

    The output file is the path to which the results of the evaluated will be
    printed.
"""

import argparse
import pprint
from copy import deepcopy
from os import listdir
from os.path import isfile, join

"""Used to perform autovivification."""
class Vividict(dict):
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value

parser = argparse.ArgumentParser()
parser.add_argument("version", action="store", nargs='?', default="1.5.5", type=str)
parser.add_argument("model_root", action="store", type=str)
parser.add_argument("system_root", action="store", type=str)
parser.add_argument("output_file", action="store", type=str)
args = parser.parse_args()
version = args.version
model_root = args.model_root
system_root = args.system_root
output_file = args.output_file

"""Creates deeply nested dictionaries using autovivification."""
def create_vividict(files):
    vividict = Vividict()

    for f in files:
        tokens = f.split('.')

        token1, token2, token3, token4, token5 = tokens

        vividict[token1][token2][token3][token4][token5]

    return vividict

"""Generates the settings XML file."""
def create_settings_xml(dict1, dict2):
    with open(output_file, 'w+') as f:
        f.write("<ROUGE_EVAL version=\"%s\">\n" % (version))

        def recurse_vividict(dict1, dict2, depth, path):
            for key, val in sorted(dict1.items()):
                new_path = list(path)
                new_path.append(key)

                if depth == 4:
                    partial_path = ".".join(new_path)

                    f.write("<EVAL ID=\"%s\">\n" % (partial_path))
                    f.write("<PEER-ROOT>\n")
                    f.write(system_root + "\n")
                    f.write("</PEER-ROOT>\n")
                    f.write("<MODEL-ROOT>\n")
                    f.write(model_root + "\n")
                    f.write("</MODEL-ROOT>\n")

                    f.write("<INPUT-FORMAT TYPE=\"SPL\">\n")
                    f.write("</INPUT-FORMAT>\n")
                    f.write("<PEERS>\n")

                    for x, y in val.items():
                        f.write("<P ID=\"%s\">%s</P>\n" % (x, ".".join([partial_path, x])))

                    f.write("</PEERS>\n")
                    f.write("<MODELS>\n")

                    for x, y in sorted(dict2[path[0]][path[1]][path[2]].items()):
                        f.write("<M ID=\"%s\">%s</M>\n" % (x, ".".join([partial_path, x])))

                    f.write("</MODELS>\n")
                    f.write("</EVAL>\n")

                else:
                    recurse_vividict(val, dict2, depth+1, new_path)

        recurse_vividict(dict1, dict2, 1, list())
        f.write("</ROUGE_EVAL>\n")

"""Creates a dictionary of dictionaries for model summary files."""
model_files = [f for f in listdir(model_root) if isfile(join(model_root, f))]
model_dict = create_vividict(model_files)

"""Creates a dictionary of dictionaries for system summary files."""
system_files = [f for f in listdir(system_root) if isfile(join(system_root, f))]
system_dict = create_vividict(system_files)

"""Calls the function to create a settings XML file."""
create_settings_xml(system_dict, model_dict)

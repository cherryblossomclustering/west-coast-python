#!/bin/usr/python3

"""calculate_recall_mean_std.py
   Author: Travis Nguyen
   Last Modified: 9 May 2017

   This script calculates the mean and standard deviation of ROUGE-1, ROUGE-2, 
   ROUGE-3, and ROUGE-4 recall scores provided in a scoring file and prints the 
   results to an output file.

   The usage is as follows:

      $ python3 calculate_recall_mean_std.py <scoring file> <output file>

   The output file also includes the minimum recall score and maximum recall score 
   for each n-gram size.
"""

import argparse
import logging
import numpy
import os
import re

parser = argparse.ArgumentParser()
parser.add_argument("scoring_file", action="store", type=str)
parser.add_argument("output_file", action="store", type=str)
args = parser.parse_args()
scoring_file = args.scoring_file
output_file = args.output_file

logging.basicConfig(filename='calculate_recall_mean_std.log', level=logging.DEBUG)

rouge1_recall = list()
rouge2_recall = list()
rouge3_recall = list()
rouge4_recall = list()

prog = re.compile("^([0-9A-Z]+) ROUGE-([1-4]?) Average_R: (\d*\.?\d*) \(95%-conf.int. (\d*\.?\d*) - (\d*\.?\d*)\)$")

with open(scoring_file, 'r+') as f:
    for line in f:
        result = prog.match(line)

        if(result):
            doc_id = str(result.group(1))
            ngram_size = int(result.group(2))
            recall = float(result.group(3))
            ci_lower_bound = float(result.group(4))
            ci_upper_bound = float(result.group(5))

            if(ngram_size == 1):
                rouge1_recall.append(recall)
            elif(ngram_size == 2):
                rouge2_recall.append(recall)
            elif(ngram_size == 3):
                rouge3_recall.append(recall)
            elif(ngram_size == 4):
                rouge4_recall.append(recall)
            else:
                logging.warning("Invalid ROUGE n-gram size: %s." % (recall))

rouge1_mean = numpy.mean(rouge1_recall)
rouge2_mean = numpy.mean(rouge2_recall)
rouge3_mean = numpy.mean(rouge3_recall)
rouge4_mean = numpy.mean(rouge4_recall)

rouge1_std = numpy.std(rouge1_recall)
rouge2_std = numpy.std(rouge2_recall)
rouge3_std = numpy.std(rouge3_recall)
rouge4_std = numpy.std(rouge4_recall)

rouge1_recall_min = min(rouge1_recall)
rouge2_recall_min = min(rouge2_recall)
rouge3_recall_min = min(rouge3_recall)
rouge4_recall_min = min(rouge4_recall)

rouge1_recall_max = max(rouge1_recall)
rouge2_recall_max = max(rouge2_recall)
rouge3_recall_max = max(rouge2_recall)
rouge4_recall_max = max(rouge2_recall)

with open(output_file, 'w+') as f:
    f.write("ROUGE-1" + '\n')
    f.write("Mean: %f" % (rouge1_mean) + '\n')
    f.write("Standard deviation: %f" % (rouge1_std) + '\n')
    f.write("Minimum recall score: %f" % (rouge1_recall_min) + '\n')
    f.write("Maximum recall score: %f" % (rouge1_recall_max) + '\n')
    f.write('\n')   

    f.write("ROUGE-2" + '\n')
    f.write("Mean: %f" % (rouge2_mean) + '\n')
    f.write("Standard deviation: %f" % (rouge2_std) + '\n')
    f.write("Minimum recall score: %f" % (rouge2_recall_min) + '\n')
    f.write("Maximum recall score: %f" % (rouge2_recall_max) + '\n')
    f.write('\n')

    f.write("ROUGE-3" + '\n')
    f.write("Mean: %f" % (rouge3_mean) + '\n')
    f.write("Standard deviation: %f" % (rouge3_std) + '\n')
    f.write("Minimum recall score: %f" % (rouge3_recall_min) + '\n')
    f.write("Maximum recall score: %f" % (rouge3_recall_max) + '\n')
    f.write('\n')

    f.write("ROUGE-4" + '\n')
    f.write("Mean: %f" % (rouge4_mean) + '\n')
    f.write("Standard deviation: %f" % (rouge4_std) + '\n')
    f.write("Minimum recall score: %f" % (rouge4_recall_min) + '\n')
    f.write("Maximum recall score: %f" % (rouge4_recall_max) + '\n')

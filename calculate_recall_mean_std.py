#!/bin/usr/python3

"""
calculate_recall_mean_std.py
Author: Travis Nguyen
Last Modified: 11 May 2017

    This script calculates the mean and standard deviation of the ROUGE-1, ROUGE-2,
    ROUGE-3, and ROUGE-4 average recall scores provided in a results file and prints
    them to an output file.

    The usage is as follows:

       $ python3 calculate_recall_mean_std.py <results file> <output file>

    The output file also includes the minimum average recall score and maximum 
    average recall score for each n-gram size.
"""

import argparse
import logging
import numpy
import os
import re

parser = argparse.ArgumentParser()
parser.add_argument("results_file", action="store", type=str)
parser.add_argument("output_file", action="store", type=str)
args = parser.parse_args()
results_file = args.results_file
output_file = args.output_file

"""Creates a log file."""
logging.basicConfig(filename='calculate_recall_mean_std.log', level=logging.DEBUG)

rouge1_r_list = list()
rouge2_r_list = list()
rouge3_r_list = list()
rouge4_r_list = list()

"""Regular expression to match the average recall scores in the results file."""
prog = re.compile("^([0-9A-Z]+) ROUGE-([1-4]?) Average_R: (\d*\.?\d*) \(95%-conf.int. (\d*\.?\d*) - (\d*\.?\d*)\)$")

with open(results_file, 'r+') as f:
    for line in f:
        result = prog.match(line)

        if(result is not None):
            """
            Collects several kinds of information from the line:
            (1) document ID
            (2) n-gram size (e.g., 1, 2, 3, 4)
            (3) average recall
            (4) lower bound of the confidence interval
            (5) upper bound of the confidence interval
            """

            doc_id = str(result.group(1))
            ngram_size = int(result.group(2))
            recall = float(result.group(3))
            ci_lower_bound = float(result.group(4))
            ci_upper_bound = float(result.group(5))

            if(ngram_size == 1):
                rouge1_r_list.append(recall)
            elif(ngram_size == 2):
                rouge2_r_list.append(recall)
            elif(ngram_size == 3):
                rouge3_r_list.append(recall)
            elif(ngram_size == 4):
                rouge4_r_list.append(recall)
            else:
                logging.warning("Invalid ROUGE n-gram size: %s." % (recall))

"""Calculates the mean of the average recall scores."""
rouge1_mean = numpy.mean(rouge1_r_list)
rouge2_mean = numpy.mean(rouge2_r_list)
rouge3_mean = numpy.mean(rouge3_r_list)
rouge4_mean = numpy.mean(rouge4_r_list)

"""Calculates the standard deviation of the average recall scores."""
rouge1_std = numpy.std(rouge1_r_list)
rouge2_std = numpy.std(rouge2_r_list)
rouge3_std = numpy.std(rouge3_r_list)
rouge4_std = numpy.std(rouge4_r_list)

"""Stores the minimum average recall scores."""
rouge1_r_min = min(rouge1_r_list)
rouge2_r_min = min(rouge2_r_list)
rouge3_r_min = min(rouge3_r_list)
rouge4_r_min = min(rouge4_r_list)

"""Stores the maximum average recall scores."""
rouge1_r_max = max(rouge1_r_list)
rouge2_r_max = max(rouge2_r_list)
rouge3_r_max = max(rouge3_r_list)
rouge4_r_max = max(rouge4_r_list)

with open(output_file, 'w+') as f:
    f.write("ROUGE-1" + '\n')
    f.write("Mean: %f" % (rouge1_mean) + '\n')
    f.write("Standard deviation: %f" % (rouge1_std) + '\n')
    f.write("Minimum recall score: %f" % (rouge1_r_min) + '\n')
    f.write("Maximum recall score: %f" % (rouge1_r_max) + '\n')
    f.write('\n')   

    f.write("ROUGE-2" + '\n')
    f.write("Mean: %f" % (rouge2_mean) + '\n')
    f.write("Standard deviation: %f" % (rouge2_std) + '\n')
    f.write("Minimum recall score: %f" % (rouge2_r_min) + '\n')
    f.write("Maximum recall score: %f" % (rouge2_r_max) + '\n')
    f.write('\n')

    f.write("ROUGE-3" + '\n')
    f.write("Mean: %f" % (rouge3_mean) + '\n')
    f.write("Standard deviation: %f" % (rouge3_std) + '\n')
    f.write("Minimum recall score: %f" % (rouge3_r_min) + '\n')
    f.write("Maximum recall score: %f" % (rouge3_r_max) + '\n')
    f.write('\n')

    f.write("ROUGE-4" + '\n')
    f.write("Mean: %f" % (rouge4_mean) + '\n')
    f.write("Standard deviation: %f" % (rouge4_std) + '\n')
    f.write("Minimum recall score: %f" % (rouge4_r_min) + '\n')
    f.write("Maximum recall score: %f" % (rouge4_r_max) + '\n')

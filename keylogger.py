"""
keylogger.py
Author: Travis Nguyen
Last Modified: 15 May 2017
"""

class Keylogger(object):
    def __init__(self, output_file):
        self.output_file = output_file

    def set_output_file(self, output_file):
        self.output_file = output_file

    def log_key(self, key, trial_data):
        with open(self.output_file, 'a+') as f:
            string = " ".join(trial_data + [key.get_key()])
            f.write("%s\n" % (string))
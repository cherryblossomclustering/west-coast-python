"""
key.py
Author: Travis Nguyen
Last Modified: 14 May 2017
"""

import random
import string

class Key(object):
    def __init__(self):
        self.key = self.create_key()

    def create_key(self):
        key = str()
        for i in range(10):
            key = key + random.choice(string.ascii_uppercase + string.digits)
        return key

    def get_key(self):
        return self.key

    def __str__(self):
        return self.key
        
#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
__Author__ = 'Kayuã Oleques'
__GitPage__ = 'https://github.com/kayua'
__version__ = '{1}.{0}.{0}'
__initial_data__ = '2024/10/20'
__last_update__ = '2024/10/22'
__credits__ = ['INF-UFRGS']

try:
    import re
    import sys
    import queue
    import logging
    import argparse
    import threading

    from flask import Flask
    from flask import jsonify
    from flask import request
    from flask import render_template

except ImportError as error:
    print(error)
    print()
    print("1. (optional) Setup a virtual environment: ")
    print("  python3 -m venv ~/Python3env/ReliableCommunication ")
    print("  source ~/Python3env/DroidAugmentor/bin/activate ")
    print()
    print("2. Install requirements:")
    print("  pip3 install --upgrade pip")
    print("  pip3 install -r requirements.txt ")
    print()
    sys.exit(-1)


class VectorClock:

    def __init__(self, number_processes, process_id):

        self.vector = [0] * number_processes  # Initialize vector with zeros
        self.process_id = process_id
        logging.basicConfig(level=logging.INFO)

    def increment(self):
        print("ANTERIOR #### {} ####".format(self.vector))
        self.vector[self.process_id] += 1
        print("POSTERIOR #### {} ####".format(self.vector))

    def update(self, received_vector):
        print("ANTERIOR #### {} ####".format(self.vector))
        self.vector = [max(self.vector[i], received_vector[i]) for i in range(len(self.vector))]
        self.vector[self.process_id] += 1
        print("POSTERIOR #### {} ####".format(self.vector))

    def send_vector(self):

        vector_string = ','.join(map(str, self.vector))
        return vector_string

    def receive_vector(self, vector_string):

        received_vector = list(map(int, vector_string.split(',')))
        return received_vector


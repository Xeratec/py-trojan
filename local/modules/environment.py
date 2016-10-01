#!/usr/bin/python
import os

def run(id, *args):
    print "[->] In environment module."
   
    return str(os.environ)
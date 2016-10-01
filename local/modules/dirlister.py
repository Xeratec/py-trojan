#!/usr/bin/python
import os

def run(id, *args):
    print "[->] In dirlister module."
    files = os.listdir(".")
    
    return str(files)
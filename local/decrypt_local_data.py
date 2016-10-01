#!/usr/bin/python
import os
import zlib
import base64
import fnmatch
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

def decrypt(plaintext, key):
    rsakey = RSA.importKey(key)
    rsakey = PKCS1_OAEP.new(rsakey)
    
    chunk_size = 256
    offset = 0
    decrypted = ""
    encrypted = base64.b64decode(plaintext)
    
    added_chunk = int(encrypted[:4],base=0)
    encrypted = encrypted[4:]
    print "\tDecrypt: %d bytes " % len(encrypted)
    
    while offset < len(encrypted):
        decrypted += rsakey.decrypt(encrypted[offset:offset+chunk_size])
        offset += chunk_size
    
    decrypted = decrypted[:(len(decrypted)-added_chunk)]
    
    print "\tDecompress: %d bytes " % len(decrypted)
    decrypted = zlib.decompress(decrypted)
    print "\tDecompressed: %d bytes " % len(decrypted) 
    return decrypted

# !----- Main Loop -----!#
with open("keys/data_key") as file_object: 
    data_private_key=file_object.read()
    file_object.close()
    
with open("keys/code_key") as file_object: 
    code_private_key=file_object.read()
    file_object.close()
    
    
for parent, directories,filenames in os.walk("../data"):
    for filename in fnmatch.filter(filenames,"*.data"):
        print "Found: %s" % os.path.join(parent, filename)
        with open("../data/%s" % os.path.join(parent, filename)) as file_object:
            decrypted = decrypt(file_object.read(), data_private_key)
            file_object.close()
        try:
            os.mkdir("data/%s" % parent[-8:])
        except:
            pass
        print "\tSave: data/%s/%s" % (parent[-8:], filename)
        with open("data/%s/%s" % (parent[-8:], filename), 'w') as file_object:
            file_object.write(decrypted)
            file_object.close()
            
for parent, directories,filenames in os.walk("../config"):
    for filename in fnmatch.filter(filenames,"*.json"):
        print "Found: %s" % os.path.join(parent, filename)
        with open("../config/%s" % filename) as file_object:
            decrypted = decrypt(file_object.read(), code_private_key)
            file_object.close()
      
        print "\tSave: config/%s" % filename
        with open("config/%s" % filename, 'w') as file_object:
            file_object.write(decrypted)
            file_object.close()
            
            
            
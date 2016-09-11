#!/usr/bin/python
import zlib
import base64
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
import Crypto.Hash.SHA

def encrypt_string(plaintext, key, VERBOSE=False):
    ## Returns base64 encrypted plaintext
    chunk_size = 256-2-2*Crypto.Hash.SHA.digest_size
    if VERBOSE: print '\tCompressing: %d bytes' % len(plaintext)
    plaintext = zlib.compress(plaintext)
    
    if VERBOSE: print "\tEncrypting %d bytes" % len(plaintext)
    rsakey = RSA.importKey(key)
    rsakey = PKCS1_OAEP.new(rsakey)
    
    encrypted = ""
    offset = 0
    
    while offset < len(plaintext):
        chunk = plaintext[offset:offset+chunk_size]
        if len(chunk) % chunk_size != 0:
            added_chunk =   chunk_size - len(chunk)
            chunk += " " * added_chunk     
            
        encrypted += rsakey.encrypt(chunk)
        offset    += chunk_size
    if added_chunk < 0x10:
        encrypted = "0x0" + str(hex(added_chunk))[2:] + encrypted
    else:
        encrypted = str(hex(added_chunk))+ encrypted
         
    if VERBOSE: print "\tEncrypted: %d bytes" % len(encrypted)
    encrypted = encrypted.encode("base64")
    return encrypted

def decrypt(plaintext, key, VERBOSE=False):
    rsakey = RSA.importKey(key)
    rsakey = PKCS1_OAEP.new(rsakey)
    
    chunk_size = 256
    offset = 0
    decrypted = ""
    encrypted = base64.b64decode(plaintext)
    
    added_chunk = int(encrypted[:4],base=0)
    encrypted = encrypted[4:]
    if VERBOSE: print "\tDecrypt: %d bytes " % len(encrypted)
    
    while offset < len(encrypted):
        decrypted += rsakey.decrypt(encrypted[offset:offset+chunk_size])
        offset += chunk_size
    
    decrypted = decrypted[:(len(decrypted)-added_chunk)]
    
    if VERBOSE: print "\tDecompress: %d bytes " % len(decrypted)
    decrypted = zlib.decompress(decrypted)
    if VERBOSE: print "\tDecompressed: %d bytes " % len(decrypted) 
    return decrypted
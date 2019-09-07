from dataclasses import dataclass, asdict, field
from typing import Dict
import requests
import getopt
import sys
import base64

DEBUG = True

@dataclass
class client_auth:
    
    username : str = ''
    password : str = ''
    auth_base64 : str = ''

@dataclass(order = True)
class command_flags:
    
    auth : bool = False 
    url : bool = False
    set_volume : bool = False
    volume : bool = False
    text : bool = False

@dataclass
class params:

    volume : int = 50
    text : str = ""

@dataclass
class request_components(params):

    headers : Dict[str, str] = field(default_factory = dict)
    base_url : str = 'http://localhost'
    port : int = 8081
    url : str = f'{base_url}:{port}'

def build_url(comps : request_components):

    if comps.base_url[-1] == '/':
        comps.base_url = comps.base_url[:-1]
        
    comps.url = f'{comps.base_url}:{comps.port}'

def encode_client(client : client_auth, comps : request_components):

    creds = f"{client.username}:{client.password}"
    client.auth_base64 = base64.standard_b64encode(creds.encode('ascii')).decode()
    comps.headers['Authorization'] = f'BASIC {client.auth_base64}'

def get_volume(client : client_auth, comps : request_components):

    ROUTE = '/audio/get-volume'
    req_result = requests.get(url = comps.url + ROUTE, headers=comps.headers)

    print(f"{ROUTE} output: " + req_result.content.decode())

def set_volume(client : client_auth, comps : request_components):

    ROUTE = '/audio/set-volume'
    args = {'level': comps.volume}

    req_result = requests.get(url = comps.url + ROUTE, params = args, headers = comps.headers)
    print(f"{ROUTE} output: " + req_result.content.decode())

def say_text(client : client_auth, comps : request_components):

    ROUTE = '/speak/say'
    args = {'text': comps.text}

    req_result = requests.get(url = comps.url + ROUTE, params = args, headers = comps.headers)
    print(f"{ROUTE} output: " + req_result.content.decode())
    #print(r.status_code)

def create_requests(client : client_auth, comps : request_components, flags : command_flags):

    FLAG_TO_FUCTION = {"set_volume" : set_volume, "volume" : get_volume , "text" : say_text}

    if flags.auth:
        
        encode_client(client, comps)
        flags.auth = False

    if flags.url:

        build_url(comps)
        flags.url = False

    for flag, state in asdict(flags).items():
        
        if state:
            FLAG_TO_FUCTION[flag](client, req_comps)
    
    if DEBUG:
        
        print('-' * 50)
        print(client)
        print(comps)

if __name__ == '__main__':
    
    client_creds = client_auth()
    flags = command_flags()
    req_comps = request_components()

    options, _ = getopt.getopt(sys.argv[1:], 'f:l:p:s:t:u:v', 
        ['username=', 'password=', 'port=', 'set-volume=', 'text=', 'url=', 'volume'])

    for opt, arg in options:

        if opt in ('-f', '--username'):

            client_creds.username = arg
            flags.auth = True

        elif opt in ('-l', '--password'):

            client_creds.password = arg
            flags.auth = True

        elif opt in ('-p', '--port'):

            req_comps.port = arg
            flags.auth = True

        elif opt in ('-s', '--set-volume'):
            
            req_comps.volume = arg
            flags.set_volume = True

        elif opt in ('-t', '--text'):

            req_comps.text = arg
            flags.text = True

        elif opt in ('-u', '--url'):
            
            req_comps.base_url = arg
            flags.url = True

        elif opt in ('-v', '--volume'):

            flags.volume = True
        else:
            pass

    create_requests(client_creds, req_comps, flags)
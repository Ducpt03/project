from flask import current_app as app
from pypbc import Parameters, Element, Pairing, G1,G2,Zr
import requests
import os
FOLDER_NAME = 'PP/'


def setup():
    if not os.path.exists(FOLDER_NAME+'param.dat'):
        response = requests.get(f"{app.config['TA_URL']}/apt/setup")
        if response == 200:
            pp = response.json
            param = pp['param']
            g = pp['g']
            param_file = open(FOLDER_NAME+'param.dat', 'w')
            print(param, file = param_file)
            param_file.close()
            g_file = open(FOLDER_NAME+'g.dat', 'w')
            print(param, file = g_file)
            g_file.close()
    param_file = open(FOLDER_NAME+'param.dat', 'r')
    param = Parameters(param_string = param_file.read()) 
    param_file.close()
    pairing = Pairing(param)
    g_file = open(FOLDER_NAME+'g.dat', 'r')
    g = Element(pairing,G1, value = g_file.read())    
    g_file.close()
    return param,g

def fixed_params(param,g):
    pairing = Pairing(param)
    q = int(str(param).split("\n")[1].split(" ")[1])

    def hash1(message):
        return Element.from_hash(pairing, G1, str(message))

    def hash2(element):
        return Element.from_hash(pairing, Zr, str(element))

    def hash3(message):
        return Element.from_hash(pairing, Zr, str(message))
    params = {
            'q': q,
            'e': pairing,
            'g': g,
            'H1': hash1,
            'H2': hash2,
            'H3': hash3
    }
    return params

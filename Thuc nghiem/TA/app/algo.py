from pypbc import Parameters, Pairing, Element, G1, G2, GT, Zr
from flask import current_app as app
import math
import os

PP_FOLDER = 'PP/'
CA_FOLDER = 'CA/'

def public_params():
    if not os.path.exists(PP_FOLDER+ "param.dat"):
        param = Parameters(qbits=4*k,rbits=k)
        params_file = open(PP_FOLDER+"param.dat", 'w')
        print(param, file = params_file)
        params_file.close()
    params_file = open(PP_FOLDER+'param.dat', 'r')
    param_string = params_file.read()
    param = Parameters(param_string = param_string) 
    params_file.close()
    pairing =  Pairing(param)
    if not os.path.exists(PP_FOLDER+'g.dat'): 
        g = Element.random(pairing, G1)
        g_file = open(PP_FOLDER+'g.dat','w')
        print(g, file = g_file)
        g_file.close()
    g_file = open(PP_FOLDER+"g.dat", "r")
    g_string = g_file.read()
    g_file.close()
    return param_string, g_string

def ca(params):
    if not os.path.exists(CA_FOLDER+ "msk.dat"):
        msk = Element.random(params["e"], Zr)
        msk_file = open(CA_FOLDER+"msk.dat", 'w')
        print(msk, file = msk_file)
        msk_file.close()
    msk_file = open(CA_FOLDER+'msk.dat', 'r')
    msk_string = msk_file.read()
    msk = Element(params['e'],Zr,value= int(msk_string,16)) 
    msk_file.close()
    if not os.path.exists(CA_FOLDER+ "p.dat"):
        p = Element(params["e"], G1, value= params["g"] ** msk)
        p_file = open(CA_FOLDER+"p.dat", 'w')
        print(p, file = p_file)
        p_file.close()
    p_file = open(CA_FOLDER+'p.dat', 'r')
    p_string = p_file.read()
    p = Element(params['e'],G1,value= p_string) 
    p_file.close()
    return msk, p

def fix_params(param_string,g_string):
    param = Parameters(param_string = param_string) 

    pairing =  Pairing(param)
    g = Element(pairing,G1, value = g_string)    

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

def keyGen(params):
    pairing = params["e"]
    g = params["g"]
    private_key = Element.random(pairing, Zr)
    public_key = Element(pairing, G1, value=g**private_key)
    return private_key, public_key

def skeyGen(params, attr_list, msk, public_key_to_encrypt):
    attr_string = "".join(attr_list)
    Q = params["H1"](attr_string)
    ak = Element(params["e"], G1, value=Q ** msk)
    int_val = key_byte_to_int(str(ak).encode())
    block_size = len(str(int(params['q'])))-1
    ak_enc, len_msg = elgamal_encrypt_block(int_val, params['g'], params['e'], public_key_to_encrypt, params['q'], block_size)
    return ak_enc, len_msg

def key_byte_to_int(sym_key):
    new_key = ''
    for c in sym_key.decode():
        new_key += str(ord(c)).zfill(3)
    return int(new_key)

def key_int_to_byte(key):

    l = len(str(key))
    # print(f"L = {l}")
    x = math.ceil(l/3) * 3
    # print(f"X = {x}")
    key = str(key).zfill(x)

    new_key = ''
    for i in range(0, x, 3):
        new_key += chr(int(key[i:i+3]))
        
    return new_key.encode()


from pypbc import Parameters, Element, Pairing, G1,G2,Zr
from cryptography.fernet import Fernet
from flask import current_app as app
import random
import math
import os
import requests
FOLDER_NAME = 'web/app/PP/'

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

def encIndex(indexs, params, private_key):
    cleaned_indexs = [word.strip() for word in indexs.split(',')]
    r = random.randint(0, params['q'] - 1)
    x = private_key
    enc_indices = []
    for w in cleaned_indexs:
        print('hash:',params['H1'](w))
        enc_indices.append(params['e'].apply(
            Element(params['e'], G1, value=params['H1'](w) ** int(x)),
            Element(params['e'], G2, value=params['g'] ** r)
        ))
    return enc_indices, r

def sym_key_gen():
    key = Fernet.generate_key()
    return key

def encData(data, sym_key):
    f = Fernet(sym_key)
    encrypted_data = f.encrypt(data.encode())
    return encrypted_data.decode()

def decData(enc_data, sym_key):
    f = Fernet(sym_key)
    encrypted_data = f.decrypt(enc_data)
    return encrypted_data.decode()

def keyGen(params):
    pairing = params["e"]
    g = params["g"]
    private_key = Element.random(pairing, Zr)
    public_key = Element(pairing, G1, value=g**private_key)
    return private_key, public_key

def elgamal_encrypt(msg, g, pairing, public_key, q):
    # Choose random k
    k = Element.random(pairing, Zr)
    # Compute C1 = g^k
    C1 = Element(pairing, G1, value=g**k)
    # Compute C2 = msg + h(k*publci_key) mod q
    # print(f"Pairing: {pairing}")


    kerpk = Element(pairing, G1, value=public_key**k)
    hash_value = Element.from_hash(pairing, Zr, str(kerpk))
    # print(int(hash_value))
    C2 = ( msg + int(hash_value) ) % q
    return C1, C2

def elgamal_decrypt(C1, C2, pairing, private_key, g, q):
    R = Element(pairing, G1, value=C1**private_key)
    hash_value = Element.from_hash(pairing, Zr, str(R))
    message = (C2 - int(hash_value)) % q
    # print(message)
    return message

def elgamal_encrypt_block(msg, g, pairing, public_key, q, block_size = 40):
    # Assume that msg is a long integer
    str_msg = str(msg)
    len_msg = len(str_msg)
    iters = math.ceil(len_msg / block_size)
    # print("Iterations: ", iters)
    # print("Total length of data: ", len_msg)
    encrypted_data = []
    for i in range(iters):
        block_data = str_msg[i*block_size:(i+1)*block_size]
        # print(f"block_data {i}: {block_data}")
        block_int = int(block_data)
        encryption = elgamal_encrypt(block_int, g, pairing, public_key, q)
        encrypted_data.append(encryption)
    return encrypted_data, len_msg

def elgamal_decrypt_block(encrypted_data, g, pairing, private_key, q, len_msg ,block_size = 40):
    decrypted_data = []
    for i in encrypted_data:
        # print(f"I = {i}")
        decryption = elgamal_decrypt(i[0], i[1], pairing, private_key, g, q)
        # print(f"decryption : {decryption}")
        decrypted_data.append(decryption)
    # Combine to single int-string
    str_msg = ""
    iters = math.ceil(len_msg / block_size)
    for i in range(iters):
        if i != iters -1:
            block_data = str(decrypted_data[i]).zfill(block_size)
            str_msg += block_data
        else:
            # print("Here")
            block_data = str(decrypted_data[i]).zfill(len_msg % block_size)
            str_msg += block_data
    # print("Reconstructed length: ", len(str_msg))
    return int(str_msg)

def decrypt_ak(params, ak_enc, private_key_to_decrypt, len_msg):
    block_size = len(str(int(params['q'])))-1
    ak_val = elgamal_decrypt_block(ak_enc, params['g'], params['e'], private_key_to_decrypt, params['q'], len_msg, block_size)
    ak = Element(params["e"], G1, value=key_int_to_byte(ak_val).decode())
    return ak

def decryTrans(params, c, ak_enc, data_owner_pk, data_user_sk, len_msg):
    # print("c in decry:",c)
    v_dash, V = c
    g_power_xy = Element(params["e"], G1, value= data_owner_pk ** data_user_sk)
    # Unsure step
    v = v_dash - int(params['H2'](g_power_xy))
    v = Element(params["e"], Zr, value=v)
    # Decrpyt V
    ak = decrypt_ak(params, ak_enc, data_user_sk, len_msg)
    pairing_value = params["e"].apply(ak, params["g"]) ** v
    hash_pairing_value = params["H2"](pairing_value)
    int_key = V ^ int(hash_pairing_value)
    sym_key = key_int_to_byte(int_key)
    return sym_key

def str_to_G1(str,params):
    element = Element(params['e'],G1,value =str)
    return element

def str_to_G2(str,params):
    element = Element(params['e'],G2,value =str)
    return element

def str_to_Zr(text,params):
    element = Element(params['e'],Zr,value =int(str(text),16))
    return element


def delegate(params, r, owner_public_key):
    rx = int(owner_public_key)**r
    zeta = Element(params["e"], G2, value = rx)
    return zeta
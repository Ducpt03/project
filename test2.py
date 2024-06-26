from pypbc import Parameters, Element, Pairing, G1, G2, Zr
import os 
import warnings
import math
import random
warnings.filterwarnings("ignore", category=DeprecationWarning) 



def key_byte_to_int(sym_key):
    new_key = ''
    for c in sym_key:
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

def fix_params(k):
        if not os.path.exists('params.dat'):
            param = Parameters(qbits=4*k,rbits=k)
            params_file = open('params.dat', 'w')
            print(param, file = params_file)
            params_file.close()

        params_file = open('params.dat', 'r')
        param = Parameters(param_string = params_file.read()) 
        params_file.close()

        pairing =  Pairing(param)

        if not os.path.exists('g.dat'): 
            g = Element.random(pairing, G1)
            g_file = open('g.dat','w')
            print(g, file = g_file)
            g_file.close()
        g_file = open("g.dat", "r")
        g = Element(pairing,G1, value = g_file.read())    
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

def key_gen(params):
    private_key = Element.random(params['e'], Zr)
    public_key = Element(params['e'], G1, value=params['g']**private_key)
    return private_key, public_key

def elgamal_encrypt(msg, g, pairing, keywords , public_key, q):
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
    # keyword_elements = [params['H1'](keyword) for keyword in keywords]
    # C3 = [kw ** k for kw in keyword_elements]
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

def create_index(keyword, sk, g ,params):
    r = Element.random(params['e'], Zr)
    enc_index =  params['e'].apply(
    Element(params['e'], G1, value=params['H1'](keyword))**sk,
    g**r
    )
    return enc_index, r

# def trapdoor(keyword, params, pk, user_sk):
#     td = Element(params["e"], G1, value=params['H1'](keyword)) ** int(user_sk)
#     return td

def trapdoor(params,keyword, user_sk):
    keyword_element = params['H1'](keyword)
    return keyword_element

def search(td, index_dict):
    matches = []
    for keyword, enc_index in index_dict.items():
        try:
            # Convert enc_index and td to strings for comparison
            if str(enc_index) == str(td):
                matches.append(keyword)
        except Exception as e:
            print(f"Error comparing indices: {e}")
    return matches

# def search(pairing, trapdoor, C1, C3):
#     print('Trapdoor',pairing.apply(trapdoor, C1))
#     for kw_enc in C3:
#         print(pairing.apply(kw_enc, g))
#         if pairing.apply(trapdoor, C1) == pairing.apply(kw_enc, g):
#             return True
#     return False



if __name__ == "__main__":
    k = 10
    params = fix_params(k)
    pairing = params['e']
    g = params['g']
    q = params['q']
    sk = Element.random(params['e'], Zr)
    pk = Element(params['e'], G1, value=params['g'] ** sk)

    user_sk, user_pk = key_gen(params)

    message = 'xin chao, day la ma hoa bi mat'
    keywords = ['xin chao', 'bi mat','day la', 'ma hoa']

    msg = key_byte_to_int(message)

    # Encrypt the message
    # encrypted_data, len_msg = elgamal_encrypt_block(msg, g, pairing, pk, q)
    C1, C2 = elgamal_encrypt(msg,g,pairing,keywords,pk, q)

    # decrypt_msg = elgamal_decrypt(C1,C2,pairing,sk,g,q)
    # print(key_int_to_byte(decrypt_msg))



    # Create index dictionary
    index_dict = {}
    r = []
    for keyword in keywords:
        enc_index, k = create_index(keyword,sk,g,params)
        index_dict[keyword] = enc_index
        r.append(k)

    print("Index Dictionary:")
    for keyword, enc_index in index_dict.items():
        print(f"{keyword}: {enc_index}, {r}")

    # Generate trapdoor for keyword 'xin chao'
    kw = 'xin chao'
    # td = trapdoor(kw, params, user_pk, user_sk)
    td = trapdoor(params,kw,user_sk)
    print(f"Trapdoor for '{kw}': {td}")
    # for i in r:
    print(r[1])
    el_td = pairing.apply(td,pk)
    print(el_td)


    # Search for trapdoor match in index dictionary
    # matches = search(pairing,td, C1,C3)
    matches = search(el_td,index_dict)
    if matches:
        print(f"Matches found for trapdoor '{kw}': {matches}")
    else:
        print(f"No matches found for trapdoor '{kw}'")

    test = pairing.apply(params['H1']('xin chao'),g)
    print()
    # Decrypt the message
    # decrypted_data = elgamal_decrypt_block(encrypted_data, g, pairing, sk, q, len_msg)
    # decrypted_key = key_int_to_byte(decrypted_data)
    # print(f"Decrypted key: {decrypted_key.decode()}")

from pypbc import Parameters, Pairing, Element, G1, G2, GT, Zr
import os
PP_FOLDER = 'PP/'
def public_params(k):
    if not os.path.exists(PP_FOLDER+'param.dat'):
            param = Parameters(qbits=4*k,rbits=k)
            params_file = open(PP_FOLDER+'param.dat', 'w')
            print(param, file = params_file)
            params_file.close()
    params_file = open(PP_FOLDER+'param.dat', 'r')
    param = Parameters(param_string = params_file.read()) 
    params_file.close()
    pairing =  Pairing(param)
    if not os.path.exists(PP_FOLDER+'g.dat'): 
        g = Element.random(pairing, G1)
        g_file = open(PP_FOLDER+'g.dat','w')
        print(g, file = g_file)
        g_file.close()
    g_file = open(PP_FOLDER+"g.dat", "r")
    g = Element(pairing,G1, value = g_file.read())    
    g_file.close()
    return param, g

print(public_params(20))
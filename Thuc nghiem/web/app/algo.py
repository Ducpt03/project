from pypbc import Parameters, Pairing, Element, G1, G2, GT, Zr
from flask import current_app as app
import os
import requests


def fix_params(param,g):
    pairing =  Pairing(param)
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


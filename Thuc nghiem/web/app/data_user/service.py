from flask import Blueprint,render_template, request, redirect, url_for, flash, session, jsonify, current_app as app
from pypbc import Parameters, Element,Pairing, G1,G2,Zr
import requests
from cryptography.fernet import Fernet
from collections import defaultdict
from ..models import User
from .. import db
import random
views = Blueprint('views',__name__)



def get_keywords_list(keywords):
    cleaned_keywords = keywords.strip("{}")
    elements = cleaned_keywords.split(",")
    elements = [elem.strip() for elem in elements]
    return elements

def trapdoor(params,  query_words):
    # Use tk to generate the trapdoor
    # Td = []
    # for word in query_words:
    Td = Element(params["e"], G1, value = params['H1'](query_words))
    return Td

def decrypt_data(enc_data, sym_key):
    fernet_key_cleaned = sym_key.strip("b'")
    fernet_key_bytes = fernet_key_cleaned.encode('utf-8')
    fernet = Fernet(fernet_key_bytes)
    decrypted_data = fernet.decrypt(enc_data)
    return decrypted_data.decode()
from flask import Blueprint,render_template, request, redirect, url_for, flash, session, jsonify, current_app as app
from pypbc import Parameters, Element,Pairing, G1,G2,Zr
import requests
from cryptography.fernet import Fernet
from collections import defaultdict
from .models import User
from . import db
import random
views = Blueprint('views',__name__)


@app.route('/api/users', methods=['GET'])
def get_users_json():
    users = User.query.all()
    users_list = [user.to_dict() for user in users]
    return jsonify(users_list)

# @app.route('/request_keygen', methods=['POST','GET'])
# def request_keygen():
#     if request.method == 'POST':

def encrypt_data(data,sym_key):
    fernet = Fernet(sym_key)
    encrypted_data = fernet.encrypt(data.encode())
    return encrypted_data.decode()

def decrypt_data(enc_data, sym_key):
    fernet = Fernet(sym_key)
    decrypted_data = fernet.decrypt(enc_data)
    return decrypted_data.decode()

def sym_keygen():
    key = Fernet.generate_key()
    return key

def get_index_list(indexs):
    cleaned_index = indexs.strip("{}")
    elements = cleaned_index.split(",")
    elements = [elem.strip() for elem in elements]
    return elements


def trapdoor(params,  query_words):
    # Use tk to generate the trapdoor
    Td = []
    for word in query_words:
        Td.append(Element(params["e"], G1, value = params['H1'](word)))
    return Td
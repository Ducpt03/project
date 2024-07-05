# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from pypbc import Parameters,Pairing,Element,G1
import os
import requests
db = SQLAlchemy()
PP_FOLDER = 'PP/'

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    if not os.path.exists(PP_FOLDER+'param.dat'):
        response = requests.get(f"{app.config['TA_URL']}/apt/setup")
        if response.status_code == 200:
            pp = response.json()
            param = pp['param']
            g = pp['g']
            param_file = open(PP_FOLDER+'param.dat', 'w')
            print(param, file = param_file)
            param_file.close()
            g_file = open(PP_FOLDER+'g.dat', 'w')
            print(g, file = g_file)
            g_file.close()
    param_file = open(PP_FOLDER+'param.dat', 'r')
    param = Parameters(param_string = param_file.read()) 
    param_file.close()
    pairing = Pairing(param)
    g_file = open(PP_FOLDER+'g.dat', 'r')
    g = Element(pairing,G1, value = g_file.read())    
    g_file.close()

    app.config['PARAM'] = param
    app.config['G'] = g
        
    db.init_app(app)

    with app.app_context():
        from . import models, views
        db.create_all()
        
    return app

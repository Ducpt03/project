from flask import Flask
from pypbc import Parameters,Element,Pairing,G1
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from .algo import fix_params
import requests
import os
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
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
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
    app.config['PARAM'] = param
    app.config['G'] = g
    app.config['FIX_PARAMS'] = fix_params(param,g)
    db.init_app(app)
    login_manager.init_app(app)
    with app.app_context():
        from .data_owner.main import owner
        from .data_user.main import user
        from .auths import auth
        from .service import views
        app.register_blueprint(auth)
        app.register_blueprint(views)
        app.register_blueprint(owner)
        app.register_blueprint(user)
        db.create_all()
    return app

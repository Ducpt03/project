# config.py

class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:abcde123@localhost/authenticator_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your_secret_key'
    PROXY_URL = 'http://localhost:5003'
    PP_FOLDER = 'PP/'
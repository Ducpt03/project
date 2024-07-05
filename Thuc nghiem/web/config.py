# config.py

class Config:
    SECRET_KEY = 'your_secret_key'
    TA_URL = 'http://localhost:5000'
    DATA_OWNER_URL = 'http://localhost:5001'
    DATABASE_URL = 'http://localhost:5003'
    PROXY_URL = 'http://localhost:5001'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:abcde123@localhost/webserver_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
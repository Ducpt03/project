# config.py

class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:abcde123@localhost/proxy_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your_secret_key'
    DATABASE_SERVER_URL = 'http://localhost:5003'  # Địa chỉ của database server
    PROXY_URL = 'http://localhost:5001'
    TA_URL = 'http://localhost:5000'
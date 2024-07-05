# config.py

class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:abcde123@localhost/database_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your_secret_key'

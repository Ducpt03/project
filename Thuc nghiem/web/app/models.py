from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
from . import db,login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)  
    is_keygen = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_keygen': self.is_keygen
        }
class manageKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    public_key = db.Column(db.String(255), unique = True)
    private_key = db.Column(db.String(255), unique = True)

class manageOwnerFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    file_id = db.Column(db.Integer, unique = True, nullable = False)
    sym = db.Column(db.String(255), unique = True, nullable = False)
    is_create_indexs = db.Column(db.Boolean, default = False)
    is_delegate = db.Column(db.Boolean, default = False)


class getFile:
    def __init__(self, file_id,title, name,content,owner):
        self.file_id = file_id
        self.title = title
        self.name = name
        self.content = content
        self.owner = owner


    def get_file(self):
        return self.title, self.name,self.content,self.owner
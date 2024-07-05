from . import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique =True, nullable =False)
    public_key = db.Column(db.String(255))
    private_key = db.Column(db.String(255))
    is_keygen = db.Column(db.Boolean, default = False)
    

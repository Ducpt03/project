# app/models.py

from . import db

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable = False)
    file_name = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    owner_name = db.Column(db.Text, nullable = False)

    def __repr__(self):
        return f'<EncryptedData {self.file_name}>'

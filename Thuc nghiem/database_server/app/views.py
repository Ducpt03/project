from flask import request,render_template,redirect,url_for ,flash,jsonify,session ,current_app as app
from werkzeug.security import generate_password_hash, check_password_hash
from .models import File
from . import db

cloud_username = 'cloud'
cloud_password = 'abcde123'


@app.route('/cloud/admin')
def home():
    return render_template('base.html')

@app.route('/', methods =['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == cloud_username and password == cloud_password:
            session['username'] = username
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/cloud/store', methods=['POST','GET'])
def store_data():
    if request.method == 'POST':
        data = request.json
        enc_title = data['enc_title']
        enc_filename = data['enc_filename']
        enc_filecontent = data['enc_filecontent']
        owner_name = data['owner_name']
        new_data = File(title = enc_title, file_name = enc_filename,content = enc_filecontent, owner_name = owner_name)
        db.session.add(new_data)
        db.session.commit()
        return jsonify(new_data.id),200
    files = File.query.all()
    return render_template('document.html',files = files)

@app.route('/query', methods=['POST'])
def query_data():
    data = request.json
    file_id = data['match']
    queried_data = File.query.filter_by(id=file_id).first()
    if queried_data:
        file = {
            'title': queried_data.title,
            'file_name':queried_data.file_name,
            'content':queried_data.content,
            'owner_name':queried_data.owner_name
        }
        return jsonify(file),200
    return jsonify({'message': 'File not found'}), 404

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))
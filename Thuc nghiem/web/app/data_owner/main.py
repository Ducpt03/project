from flask import Blueprint, render_template,request,jsonify,session,redirect,url_for,flash,current_app as app
from flask_login import login_required
from ..models import User,manageKey, manageOwnerFile
from .. import db
import requests
from cryptography.fernet import Fernet
from ..algo import fix_params
from .service import sym_key_gen, encData, encIndex,str_to_G1,str_to_Zr,delegate
from pypbc import Element,G1,Zr,G2
import json
owner = Blueprint('owner', __name__)

param = app.config['PARAM']
g = app.config['G']
params = fix_params(param,g)
print
@owner.route("/owner_dashboard/")
@login_required
def owner_dashboard():
    role = session.get('role')
    if 'owner' in session or role == 'data_owner':
        return render_template('data_owner/base.html')
    return redirect(url_for('auth.logout'))

@owner.route("/owner_dashboard/upload", methods = ['POST','GET'])
@login_required
def upload():
    if request.method == 'POST':
        title = request.form.get('title')
        file_name = request.form.get('file_name')
        file_content = request.form.get('file_content')
        indexs = request.form.get('indexs')
        secret = request.form.get('secret')
        owner_name = session.get('username')
        owner_student_id = session.get('student_id')
        owner_id = session.get('user_id')
        user_id = session.get('user_id')
        key = sym_key_gen()
        encrypt_data = {
            'enc_title': encData(title,key),
            'enc_filename': encData(file_name,key),
            'enc_filecontent': encData(file_content,key),
            'owner_name':encData(owner_name,key)
        }
        sk_str = session.get('private_key')
        sk = str_to_Zr(sk_str,params)
        enc_indices,r = encIndex(indexs,params,sk)
        zeta = delegate(params,r,sk)
        print('zeta',zeta)
        response = requests.post(f"{app.config['DATABASE_URL']}/cloud/store", json=encrypt_data)
        if response.status_code == 200:
            file_id = response.json()
            # file_id = data['file_id']
            newfiles = manageOwnerFile(user_id = user_id, file_id = file_id, sym = key.decode('utf-8'))
            db.session.add(newfiles)
            db.session.commit()
            if not newfiles.is_create_indexs and not newfiles.is_delegate:
                response_index = requests.post(f"{app.config['PROXY_URL']}/save_indexs",json={
                    'enc_indices': str(enc_indices),
                    'file_id':file_id,
                    'owner_student_id': owner_student_id
                })
                response_zeta = requests.post(f"{app.config['PROXY_URL']}/api/delegate_user/",json={
                    'owner_student_id': owner_student_id,
                    'zeta': str(zeta),
                    'secret':secret
                })
                response_sym = requests.post(f"{app.config['PROXY_URL']}/api/post_symkey/",json={
                    'file_id': file_id,
                    'sym_key':str(key)
                })
                if response_index.status_code == 200 and response_zeta.status_code == 200 and response_sym.status_code == 200:
                    newfiles.is_create_indexs = True
                    newfiles.is_delegate = True
                    db.session.commit()
                    return jsonify('Upload, create index and delegate successful'),200
            return jsonify('You already upload file'),402
        return jsonify('Can not upload file'),404
    return render_template("data_owner/upload.html")


@owner.route('/owner_dashboard/view', methods = ['POST','GET'])
def view_document():
    user_id = session.get('user_id')
    owner_files = manageOwnerFile.query.filter_by(user_id = user_id).all()
    if not owner_files:
        return jsonify('You have not upload any file yet'),404
    return render_template('data_owner/view.html', files = owner_files)


@owner.route('/owner_dashboard/req_key_gen', methods = ['POST','GET'])
@login_required
def pair_key_gen():
    student_id = session.get('student_id')
    user = User.query.filter_by(student_id = student_id).first()
    key = manageKey.query.filter_by(user_id = user.id).first()
    if request.method == 'POST' and not key:
                if not user.is_keygen:
                    data = {
                        'student_id': student_id
                    }
                    response = requests.post(f"{app.config['TA_URL']}/ta_dashboard/user_keygen", json = data)
                    if response.status_code == 200:
                        key = response.json()
                        public_key = key['public_key']
                        private_key = key['private_key']
                        user.is_keygen = True
                        session['private_key'] = private_key
                        session['public_key'] = public_key  
                        newKeyMan = manageKey(user_id = user.id,public_key = public_key,private_key=private_key)
                        db.session.add(newKeyMan)
                        db.session.commit()
                        flash('Key gen successful!','success')
                    else:
                        return jsonify('Error to generate key'),404
    elif key:
        session['private_key'] = key.private_key
        session['public_key'] = key.public_key  
    return render_template('data_owner/keygen.html', user = user,key=key)

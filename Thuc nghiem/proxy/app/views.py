from flask import request, jsonify, current_app as app
from .models import User, Index_dict, Delegate,symKeyManage,matches_and_key
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import os
from pypbc import *
from .setup import setup,fixed_params
import re
param, g = setup()
params = fixed_params(param,g)

@app.route('/proxy_query', methods=['POST'])
def proxy_query():
    data = request.json
    file_name = data['file_name']
    user = data['user']

    # Xác thực user có quyền truy cập file không
    # Đây chỉ là một ví dụ đơn giản, bạn có thể tích hợp với Authenticator để kiểm tra quyền
    response = requests.post(f"{app.config['DATABASE_SERVER_URL']}/query", json={'file_name': file_name})
    return jsonify(response.json())

@app.route('/user', methods = ['POST'])
def user():
    data = request.json
    user_id = data['user_id']
    public_key = data['public_key']

    user = User.query.filter_by(user_id = user_id).first()
    if user:
        return jsonify({'message':'User already exits in proxy!'}), 404
    new_user = User(user_id = user_id, public_key = public_key)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message':'Add successfull!'}), 200

@app.route('/setup',methods = ['POST'])
def setup():
    data = request.json
    params = data['params']
    g = data['g']
    # Kiểm tra xem file params.dat đã tồn tại và có dữ liệu hay chưa
    if not os.path.isfile('./params.dat') or os.path.getsize('./params.dat') == 0:
        with open('./params.dat', 'w') as params_file:
            print(params, file=params_file)

    # Kiểm tra xem file g.dat đã tồn tại và có dữ liệu hay chưa
    if not os.path.isfile('./g.dat') or os.path.getsize('./g.dat') == 0:
        with open('./g.dat', 'w') as g_file:
            print(g, file=g_file)
            return jsonify({'message':'Setup done!'}),200 
    return jsonify({'Already setup before!'}), 409

@app.route('/save_indexs', methods = ['POST'])
def indices():
    data =request.get_json()
    indexs_str = data['enc_indices']
    owner_student_id = data['owner_student_id']
    file_id = data['file_id']
    pattern = r'\([^()]+\)'
    matches = re.findall(pattern, indexs_str)
    indexs = [match.strip(" ") for match in matches]
    for i in indexs:
        new_index = Index_dict(keyword = i, file_id = file_id,owner_student_id = owner_student_id)
        db.session.add(new_index)
        db.session.commit()
    return jsonify('success'),200

@app.route('/api/delegate_user/',methods=['GET','POST'])
def delegate_user():
    if request.method == 'POST':
        data = request.json
        owner_student_id = data['owner_student_id']
        zeta = data['zeta']
        secret_password = data['secret']
        # hashed_sp = generate_password_hash(secret_password)
        new_delegate = Delegate(owner_student_id = owner_student_id, zeta = zeta, secret_password = secret_password)
        db.session.add(new_delegate)
        db.session.commit()
        return jsonify('Delegate to user successful!'), 200
    return jsonify('Methods not allow'),405   

@app.route('/api/query', methods = ['GET','POST'])
def query_index():
    if request.method == 'POST':
        data = request.json
        owner_student_id = data['owner_student_id']
        password = data['password']
        td_string = data['td']
        # print('td',td_string)
        zeta_list = []
        umerators = []
        matches = []
        # hashed_password = generate_password_hash(password)
        delegates = Delegate.query.filter_by(owner_student_id = owner_student_id, secret_password = password).all()
        for delegate in delegates:
            z = delegate.zeta
            zeta_list.append(z)
        for zeta in zeta_list:
            # print('zeta:',zeta)
            umerator = params["e"].apply(Element(params['e'],G1,value = td_string), Element(params['e'],G2,zeta))
            umerators.append(umerator)
        for u in umerators:        
            indexs = Index_dict.query.filter_by(keyword = u).first()
            if indexs:
                file_id = indexs.file_id
                sym_key = symKeyManage.query.filter_by(file_id = file_id).first()
                match = matches_and_key(file_id,sym_key.symkey)
                matches.append(match)
        matches_list = [match.to_dict() for match in matches]
        # print(matches_list)       
        return jsonify(str(matches_list)), 200
    return jsonify('Access deny!'),404
        
@app.route('/api/get_file_id', methods = ['POST'])
def get_file_id():
    data = request.json
    td = data['td']
    zeta = data['zeta']
    result = params["e"].apply(td, zeta)
    print(str(result))
    indexs = Index_dict.query.filter_by(keyword = result).first()
    if indexs:
        print(indexs)
        return jsonify('success'),200
    return jsonify('failed'),404


@app.route('/api/post_symkey/',methods= ['POST'])
def skey():
    if request.method == 'POST':
        data = request.json
        file_id = data['file_id']
        key = data['sym_key']
        sym_key = symKeyManage.query.filter_by(file_id = file_id).first()
        if not sym_key:
            new_key = symKeyManage(file_id = file_id, symkey = key)
            db.session.add(new_key)
            db.session.commit()
            return jsonify('Upload key successful!'),200
    return jsonify('Your file not exist!'),404

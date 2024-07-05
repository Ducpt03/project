from flask import request, Blueprint,session,redirect,url_for,jsonify,flash ,render_template,current_app as app
from .algo import keyGen, public_params,fix_params, ca
from .models import User
from . import db
import requests
views = Blueprint('views',__name__)
from pypbc import Element, Zr,G1
ta_username = 'ta'
ta_password = 'abcde123'
param,g = public_params()
params = fix_params(param,g)
msk, P = ca(params)

@views.route('/', methods =['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ta_username and password == ta_password:
            session['username'] = username
            return redirect(url_for('views.home'))
    return render_template('login.html')

@views.route('/ta_dashboard/',methods = ['POST','GET'])
def home():
    return render_template('base.html')

@views.route('/ta_dashboard/users', methods = ['POST','GET'])
def users():
    data = request.json
    student_id = data['student_id']
    new_user = User(student_id = student_id)
    db.session.add(new_user)
    db.session.commit()
    return jsonify('Create user successful!'),200

@views.route('/ta_dashboard/user_keygen', methods = ['POST','GET'])
def user_keygen():
    if request.method == 'POST':
        data = request.json
        student_id = data['student_id']
        user = User.query.filter_by(student_id = student_id).first()
        if user:
            if not user.is_keygen:
                private_key, public_key = keyGen(params)
                str_pb = str(public_key)
                str_sk = str(private_key)

                user.public_key = str_pb
                user.private_key = str_sk
                user.is_keygen = True
                db.session.commit()
                key = {
                    'public_key': str_pb,
                    'private_key': str_sk
                }
                return jsonify(key),200
            return jsonify('User already has key!'),404
    users = User.query.all()
    return render_template('keygen.html', users= users)

@views.route('/apt/setup/', methods= ['GET'])
def setup():
    pp = {
        'param': param,
        'g':g,
    }
    return jsonify(pp),200


from flask import Blueprint, render_template, url_for, flash, redirect,session, request,current_app as app
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import User
import requests
auth = Blueprint('auth',__name__)


@auth.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.home'))
    if  request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        student_id = request.form.get('student_id')
        role = request.form.get('role')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password)
        user = User.query.filter_by(email = email, role = role).first()
        if user:
            flash('User already exist!','error')
        data = {
            'student_id':student_id
        }
        print(data)
        response = requests.post(f"{app.config['TA_URL']}/ta_dashboard/users",json=data)
        print(response.json)
        if response.status_code == 200:
            new_user = User(username=username, email=email,student_id = student_id, password_hash=hashed_password, role = role)
            db.session.add(new_user)
            db.session.commit()
            flash('Your account has been created!', 'success')
            return redirect(url_for('auth.login'))
    flash("Can not create your account!",'error')   
    return render_template('register.html')

@auth.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.home'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        user = User.query.filter_by(email= email, role = role).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            session['email'] = user.email
            session['username'] = user.username
            session['student_id'] = user.student_id
            session['role'] = user.role
            session['user_id'] = user.id
            if user.role == 'data_owner':
                return redirect(url_for('owner.owner_dashboard'))
            elif user.role == 'data_user':
                return redirect(url_for('user.user_dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html')

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.home'))

@auth.route("/")
@auth.route("/home")
def home():
    return render_template('index.html')
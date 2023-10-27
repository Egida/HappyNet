from flask import Blueprint, request, render_template, redirect
from flask import g as session

import hmac
import time

from core import SERVER_PEPPER, JWT_SERVER_KEY, TOKEN_EXPIRATION
from base64 import b64decode
from localDB import LocalDB
from auth import calc_JWT, hash_password

login = Blueprint('login_blueprint', __name__)
accounts = LocalDB('./db/accounts.enc')

@login.route('/login', methods=['GET'])
def index():
    if session.user:
        return redirect('/')
    return render_template('login.html')

@login.route('/register', methods=['GET'])
def register():
    if session.user:
        return redirect('/')
    return render_template('register.html')

@login.route('/login', methods=['POST'])
def index_post():
    user, pwd = request.form['username'], request.form['password']
    if not user in accounts.data:
        return render_template('login.html', usr=user, err='Username not found')

    db_password = accounts.data[user]['pwd']['hex']
    usr_password = hash_password(pwd, SERVER_PEPPER, b64decode(accounts.data[user]['pwd']['salt']))['hex']
    if not hmac.compare_digest(db_password, usr_password):
        return render_template('login.html', usr=user, err='Password Missmatch')

    res = redirect('/')
    res.set_cookie('login', calc_JWT(user, time.time() + TOKEN_EXPIRATION, JWT_SERVER_KEY), TOKEN_EXPIRATION)
    return res

@login.route('/register', methods=['POST'])
def register_post():
    user, pwd = request.form['username'], request.form['password']
    if user in accounts.data:
        return render_template('register.html', usr=user, err='Username already taken')

    is_first_account = len(accounts.data) == 0

    usr_password = hash_password(pwd, SERVER_PEPPER)
    
    acc_data: dict = {'pwd': usr_password}

    if is_first_account:
        acc_data['role'] = 'admin'
    else:
        acc_data['active'] = False

    accounts.data[user] = acc_data
    accounts.write_db()

    res = redirect('/')
    res.set_cookie('login', calc_JWT(user, time.time() + TOKEN_EXPIRATION, JWT_SERVER_KEY), TOKEN_EXPIRATION)
    return res

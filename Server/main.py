from flask import Flask, render_template, request, redirect
from flask import g as session
from base64 import b64decode
import hmac
import time

from werkzeug.routing.rules import Rule
from auth.token import JWTBadChecksum, JWTExpired, load_JWT

from core import JWT_SERVER_KEY

from endpoints.group import group, groups
from endpoints.login import login

app = Flask(__name__)
app.register_blueprint(group)
app.register_blueprint(login)

noauth_endpoints = ['/group/json']

@app.route('/')
def dashboard():
    return render_template('dashboard.html', groups=groups, groups_count=len(groups))

@app.route('/logout', methods=['POST'])
def logout():
    res = redirect('/login')
    res.delete_cookie('login')
    return res

@app.before_request
def jwt_check():
    session.user = None

    if request.path in noauth_endpoints: return

    if 'login' in request.cookies:
        try:
            session_data = load_JWT(request.cookies['login'], JWT_SERVER_KEY)
        except (JWTExpired, JWTBadChecksum):
            if request.path != '/login':
                return redirect('/login')
            return
        
        session.user = session_data['id']
    elif request.path != '/login':
        return redirect('/login')


if __name__ == '__main__':
    app.run('0.0.0.0', 6969, debug=True)

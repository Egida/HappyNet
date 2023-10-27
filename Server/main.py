from flask_sock import Sock
from ws.client import WebSocketClient
from ws.live import WebSocketAnalytics

from flask import Flask, render_template, request, redirect, send_file
from flask import g as session

from auth.token import JWTBadChecksum, JWTExpired, load_JWT
from core import JWT_SERVER_KEY

from endpoints.group import group, groups
from endpoints.login import login, accounts
from endpoints.admin import admin

app = Flask(__name__)
app.register_blueprint(group)
app.register_blueprint(login)
app.register_blueprint(admin)

sock = Sock(app)

noauth_endpoints = ['/group/json', '/static/', '/websocket', '/register']

def logout_and_redirect(path):
    res = redirect(path)
    res.delete_cookie('login')
    return res

@app.route('/')
def dashboard():
    seen_groups = [group for group in groups if not session.user in group.banned]
    registration_requests = [user for user in accounts.data if not accounts.data[user].get('active', True)]
    return render_template('dashboard.html', groups=seen_groups, registration_requests=registration_requests)

@app.route('/logout', methods=['POST'])
def logout():
    return logout_and_redirect('/login')

@app.route('/delete', methods=['POST'])
def delete():
    accounts.data.pop(session.user)
    accounts.write_db()
    return logout_and_redirect('/login')


@app.errorhandler(404)
def notfound(error):
    return render_template('404.html', msg='Page not found'), 404

@app.before_request
def jwt_check():
    session.user = None

    for endpoint in noauth_endpoints:
        if request.path.startswith(endpoint): return

    if 'login' in request.cookies:
        try:
            session_data = load_JWT(request.cookies['login'], JWT_SERVER_KEY)
        except (JWTExpired, JWTBadChecksum):
            if request.path != '/login':
                return logout_and_redirect('/login')
            return
        
        if not session_data['id'] in accounts.data:
            if request.path != '/login':
                return logout_and_redirect('/login')

        session.user = session_data['id']
        session.role = accounts.data[session.user].get('role', 'user')
        if not accounts.data[session.user].get('active', True):
            return render_template('401.html', msg='Please wait for your registration to being approved.')
    
    elif request.path != '/login':
        return redirect('/login')

@app.route('/favicon.ico')
def favicon():
    return send_file('./static/img/pepe.ico')

if __name__ == '__main__':
    sock.route('/websocket')(WebSocketClient)
    sock.route('/stalk')(WebSocketAnalytics)
    app.run('0.0.0.0', 6969, debug=True)


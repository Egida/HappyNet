from flask import Blueprint, redirect
from flask import g as session

from endpoints.login import accounts

admin = Blueprint('admin_blueprint', __name__)

@admin.route('/approve/<user>', methods=['POST'])
def approve_user(user):
    if session.role != "admin":
        return render_template('401.html', msg='You must be an admin to access this resource'), 404

    accounts.data[user].pop('active')
    accounts.write_db()

    return redirect('/')

@admin.route('/declyne/<user>', methods=['POST'])
def declyne_user(user):
    if session.role != "admin":
        return render_template('401.html', msg='You must be an admin to access this resource'), 404

    accounts.data.pop(user)
    accounts.write_db()

    return redirect('/')

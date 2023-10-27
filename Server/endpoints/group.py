from flask import Blueprint, request, render_template, redirect
from flask import g as session

from group import Group, find_user, find_group, groups
from endpoints.login import accounts
import string
import json

from ws.client import WebSocketClient

group = Blueprint('groups_blueprint', __name__, url_prefix='/group/')
ok_chars = string.ascii_letters + string.digits + '_-'

def check_group_name(name):
    if len(name) > 22 or len(name) < 2:
        return False

    return all([char in ok_chars for char in name])

@group.route('/json')
def groups_list_json():
    return {
        g.name: {
            'target': g.target,
            'members_count': g.members_count,
            'threads': g.threads,
            'status': g.status,
            'min_power': g.min_power
        } for g in groups
    }

@group.route('/<name>/json')
def group_json(name):
    group = find_group(name)
    if not group:
        return render_template('404.html', msg='Group not found'), 404

    if session.user in group.banned:
        return render_template('404.html', msg='Group not found'), 404

    members = {}
    for member in group.members:
        members[member.name] = member.requests_total

    return {
        'per_second': group.requests_per_second,
        'total': group.requests_total,
        'members': members
    }

@group.route('/<name>')
def group_info(name):
    group = find_group(name)
    if not group:
        return render_template('404.html', msg='Group not found'), 404

    if session.user in group.banned:
        return render_template('404.html', msg='Group not found'), 404

    is_admin = group.admin == session.user
    if accounts.data[session.user].get('role') == 'admin':
        is_admin = True

    return render_template('group.html', group=group, is_admin=is_admin)

@group.route('/<name>/start', methods=['POST'])
def start_attack(name):
    group = find_group(name)
    if not group:
        return render_template('404.html', msg='Group not found'), 404

    if session.user != group.admin:
        return render_template('401.html', msg='You\'re not the Group Admin'), 401

    for member in group.members:
        client = WebSocketClient.connections[member.name]
        client.ws.send(json.dumps({'p': 'start-attack'}))

    group.status = 'RUNNING'

    return redirect(f'/group/{name}')

@group.route('/<name>/stop', methods=['POST'])
def stop_attack(name):
    group = find_group(name)
    if not group:
        return render_template('404.html', msg='Group not found'), 404

    if session.user != group.admin:
        return render_template('401.html', msg='You\'re not the Group Admin'), 401

    for member in group.members:
        client = WebSocketClient.connections[member.name]
        client.ws.send(json.dumps({'p': 'stop-attack'}))

        member.requests_per_second = 0
        member.requests_total = 0

    group.status = 'idle'
    group.requests_per_second = 0
    group.requests_total = 0

    return redirect(f'/group/{name}')


@group.route('/<name>/delete', methods=['POST'])
def delete_group(name):
    group = find_group(name)
    if not group:
        return render_template('404.html', msg='Group not found'), 404

    if session.user != group.admin:
        return render_template('401.html', msg='You\'re not the Group Admin'), 401

    groups.remove(group)

    for member in group.members:
        client = WebSocketClient.connections[member.name]
        client.ws.send(json.dumps({'p': 'kick'}))

    return redirect('/')

@group.route('/<name>/<username>/ban', methods=['POST'])
def ban_user(name, username):
    group = find_group(name)
    if not group:
        return render_template('404.html', msg='Group not found'), 404

    user = find_user(group, username)
    if not user:
        return render_template('404.html', msg='User not found'), 404

    if session.user != group.admin:
        return render_template('401.html', msg='You\'re not the Group Admin'), 401

    group.rem_member(user)
    group.banned.append(user.name)

    client = WebSocketClient.connections[username]
    client.ws.send(json.dumps({'p': 'kick'}))

    return redirect(f'/group/{name}')

@group.route('/<name>/<username>/unban', methods=['POST'])
def unban_user(name, username):
    group = find_group(name)
    if not group:
        return render_template('404.html', msg='Group not found'), 404

    if not username in group.banned:
        return render_template('404.html', msg='This user is not banned from this group ( not found in the ban list )'), 404

    if session.user != group.admin:
        return render_template('401.html', msg='You\'re not the Group Admin'), 401

    group.banned.remove(username)

    return redirect(f'/group/{name}')

@group.route('/<name>/<username>/kick', methods=['POST'])
def kick_user(name, username):
    group = find_group(name)
    if not group:
        return render_template('404.html', msg='Group not found'), 404

    user = find_user(group, username)
    if not user:
        return render_template('404.html', msg='User not found'), 404

    if session.user != group.admin:
        return render_template('401.html', msg='You\'re not the Group Admin'), 401

    group.rem_member(user)
    client = WebSocketClient.connections[username]
    client.ws.send(json.dumps({'p': 'kick'}))

    return redirect(f'/group/{name}')

@group.route('/create', methods=['POST'])
def create_group():
    name, target, min_power = request.form['name'], request.form['target'], int(request.form['minimum-power'])

    if not check_group_name(name):
        return render_template('dashboard.html', group_err = 'Only letters, digits and "-_" are accepted in the group name', groups=groups, groups_count=len(groups))

    if find_group(name):
        return render_template('dashboard.html', group_err = 'The group name is already used', groups=groups, groups_count=len(groups))

    groups.append(Group(name, target, session.user, min_power))
    return redirect(f'/group/{name}')

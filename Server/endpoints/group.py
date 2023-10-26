from flask import Blueprint, request, render_template, redirect
from flask import g as session

from group import Group, Member
import string

group = Blueprint('groups_blueprint', __name__, url_prefix='/group/')
ok_chars = string.ascii_letters + string.digits + '_-'

import random
def random_members():
    return [Member(str(int(random.random() * 10000)), random.randint(2, 8), random.randint(200, 500)) for i in range(random.randint(50, 200))]

def check_group_name(name):
    if len(name) > 22 or len(name) < 2:
        return False

    return all([char in ok_chars for char in name])

groups = [
    Group('TestGroup', 'https://test.com', 'admin'),
    Group('Anonymous', 'https://google.com', 'admin'),
    Group('Lulzsec', 'https://cia.gov', 'admin')
]

def find_group(name):
    for group in groups:
        if group.name == name:
            return group
    return None

@group.route('/json')
def groups_list_json():
    return {g.name: {'target': g.target, 'members_count': g.members_count, 'threads': g.threads} for g in groups}

@group.route('/<name>', methods=['POST'])
def remove_member(name):
    member_name = request.form['user']

    for group in groups:
        if group.name == name:
            break
    else:
        return render_template('404.html', msg='Group not found'), 404

    if session.user != group.admin:
        return render_template('401.html', msg='You\'re not the Group Admin'), 401

    for member in group.members.copy():
        if member.name == member_name:
            group.members.remove(member)
            group.members_count -= 1
            group.threads -= member.threads
            print(member, 'has been removed')

    return redirect(f'/group/{name}')

@group.route('/<name>')
def group_info(name):
    group = find_group(name)
    if not group:
        return render_template('404.html', msg='Group not found'), 404

    return render_template('group.html', group=group)

@group.route('/<name>/delete', methods=['POST'])
def delete_group(name):
    group = find_group(name)
    if not group:
        return render_template('404.html', msg='Group not found'), 404

    if session.user != group.admin:
        return render_template('401.html', msg='You\'re not the Group Admin'), 401

    groups.remove(group)

    return redirect('/')

@group.route('/create', methods=['POST'])
def create_group():
    name, target = request.form['name'], request.form['target']

    if not check_group_name(name):
        return render_template('dashboard.html', group_err = 'Only letters, digits and "-_" are accepted in the group name', groups=groups, groups_count=len(groups))

    if find_group(name):
        return render_template('dashboard.html', group_err = 'The group name is already used', groups=groups, groups_count=len(groups))

    groups.append(Group(name, target, session.user))
    return redirect(f'/group/{name}')

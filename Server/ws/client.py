import json
import secrets
from simple_websocket.ws import Server
from group import Group, Member, find_group

from flask import request

class WebSocketClient:
    connections = {}

    def __init__(self, ws: Server):
        self.ws = ws
        self.handle()

    def handle(self):
        username = None
        current_group: Group = None
        current_group_usr = None

        while True:
            try:
                data = json.loads(self.ws.receive())
            except:
                break

            if data['p'] == 'identify':
                if username: continue

                username = data['username']
                if username in WebSocketClient.connections:
                    username += f'.{secrets.token_hex(4)}'
                
                self.ws.send(json.dumps({'p': 'identify', 'usr': username}))

                WebSocketClient.connections[username] = self

            elif data['p'] == 'join-group':
                if not username:
                    self.ws.send(json.dumps({'p': 'err', 'msg': 'pls-identify'}))
                    return self.ws.close()

                name, cores, threads = data['name'], data['cores'], data['threads']
                group = find_group(name)
                if not group:
                    self.ws.send(json.dumps({'p': 'err', 'msg': 'group-not-found'}))
                    return self.ws.close()

                if threads < group.min_power:
                    self.ws.send(json.dumps({'p': 'err', 'msg': 'not-enough-power'}))
                    return self.ws.close()

                current_group = group
                current_group_usr = Member(username, cores, threads)
                group.add_member(current_group_usr)
                self.ws.send(json.dumps({'p': 'joined'}))

            elif data['p'] == 'analytics':
                if not current_group or not current_group_usr:
                    self.ws.send(json.dumps({'p': 'err', 'msg': 'not-in-group'}))
                    continue

                current_group.requests_total += data['plus']
                current_group_usr.requests_per_second = data['per_second']

                current_group.calc_reqs()

        try:
            self.ws.close()
        except: pass
        if username and username in WebSocketClient.connections:
            WebSocketClient.connections.pop(username)
        if current_group:
            current_group.rem_member(current_group_usr)

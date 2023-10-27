import json
import time
from flask import request
from simple_websocket.ws import Server

from group import find_group, Group

class WebSocketAnalytics:
    def __init__(self, ws: Server):
        self.ws = ws
        if 'name' in request.args:
            group = request.args['name']
            group = find_group(group)
            if not group:
                print('closed, no group')
                return ws.close()
        else:
            print('closed, no name')
            return ws.close()
        
        self.group: Group = group
        self.live_updates()

    def live_updates(self):
        old_data = {}
        while True:
            time.sleep(1)

            members = {}
            for member in self.group.members:
                members[member.name] = member.requests_total

            data = {
                'per_second': self.group.requests_per_second,
                'total': self.group.requests_total,
                'members': members
            }

            if data != old_data:
                self.ws.send(json.dumps(data))
                old_data = data


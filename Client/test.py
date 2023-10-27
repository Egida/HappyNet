import subprocess

from subprocess import STDOUT, Popen, PIPE, CalledProcessError

with Popen([f'.\\libs\\ddos.exe', 'http', '-threads', '100', 'http://127.0.0.1:8000'], stdout=PIPE, stderr=STDOUT, bufsize=1, universal_newlines=True, shell=True) as p:
    for line in p.stdout:
        print(line, end='') # process line here

if p.returncode != 0:
    raise CalledProcessError(p.returncode, p.args)

import json
import os

from cryptography.fernet import Fernet

class LocalDB:
    def __init__(self, json_file: str):
        self.json_file = json_file
        self.key_file = json_file + '.key'

        if self.check_exist():
            self.load_db()

    def check_exist(self):
        if not os.path.exists(self.json_file):
            try:
                os.makedirs('/'.join(self.json_file.replace('\\', '/').split('/')[:-1]))
            except: pass

            self.data = {}
            self.write_db()
            return False

        return True

    def load_db(self):
        with open(self.key_file, 'rb') as f:
            key = f.read()

        fernet = Fernet(key)

        with open(self.json_file, 'rb',) as f:
            data = fernet.decrypt(f.read())
        self.data = json.loads(data)

    def write_db(self):
        key = Fernet.generate_key()
        fernet = Fernet(key)
        
        with open(self.json_file, 'wb') as f:
            f.write(fernet.encrypt(json.dumps(self.data).encode()))
        with open(self.key_file, 'wb') as f:
            f.write(key)


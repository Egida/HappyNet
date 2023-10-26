import json
import os

class LocalDB:
    def __init__(self, json_file: str):
        self.json_file = json_file
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
        with open(self.json_file, 'r', encoding='utf-8') as f:
            data = f.read()
        self.data = json.loads(data)

    def write_db(self):
        with open(self.json_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps(self.data))

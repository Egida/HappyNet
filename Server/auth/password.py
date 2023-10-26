import base64
from hashlib import sha512
from typing import Union
import secrets

def hash_password(password: str, pepper: bytes, salt: Union[bytes, None] = None, work_factors: int = 3):
    if not salt:
        salt = secrets.token_bytes(128)

    for _ in range(work_factors):
        password = sha512(password.encode() + salt + pepper).hexdigest()

    return {'hex': password, 'salt': base64.b64encode(salt).decode()}

if __name__ == '__main__':
    def load_key(file):
        with open(f'../keys/{file}', 'rb') as f:
            key = f.read()
        return key

    pepper = load_key('pepper.priv')

    print(res := hash_password('admin', pepper))

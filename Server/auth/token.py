import base64
import json
import hashlib
import hmac
import time

class JWTBadChecksum(Exception): pass
class JWTExpired(Exception): pass

def calc_JWT(user_id: str, expiration: float, server_key: bytes):
    jwt_data = base64.b64encode(json.dumps({'id': user_id, 'exp': expiration}).encode())
    checksum = hashlib.sha512(jwt_data + server_key).hexdigest()
    return jwt_data.decode() + '.' + checksum

def load_JWT(jwt: str, server_key: bytes) -> dict:
    jwt_data, jwt_checksum = jwt.split('.')
    jwt_dict = json.loads(base64.b64decode(jwt_data.encode()).decode())
    
    check_JWT(jwt_data, float(jwt_dict['exp']), jwt_checksum, server_key)

    return jwt_dict


def check_JWT(jwt_data: str, expiration: float, jwt_checksum: str, server_key: bytes):
    checksum = hashlib.sha512(jwt_data.encode() + server_key).hexdigest()
    if not hmac.compare_digest(checksum, jwt_checksum):
        raise JWTBadChecksum('Checksum Missmatch')
    if time.time() > expiration:
        raise JWTExpired('Token has Expired')


if __name__ == '__main__':
    server_key = b'ciaociao123'
    jwt = calc_JWT('admin', time.time() + 1, server_key)
    print(jwt)
    print(load_JWT(jwt, server_key))
    time.sleep(1.5)
    print(load_JWT(jwt, server_key))

def load_key(file):
    with open(f'keys/{file}', 'rb') as f:
        key = f.read()
    return key

JWT_SERVER_KEY = load_key('jwt.priv')
SERVER_PEPPER = load_key('pepper.priv')

TOKEN_EXPIRATION = 60 * 60 * 24 * 7 # 1 week

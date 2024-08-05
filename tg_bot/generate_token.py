import secrets

def generate_hex_token():
    return secrets.token_hex(16)
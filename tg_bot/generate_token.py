async def generate_hex_token():
    import secrets
    return secrets.token_hex(16)
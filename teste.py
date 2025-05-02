import os

secret_key = os.urandom(32).hex()  # também gera 64 caracteres hexadecimais
print(secret_key)
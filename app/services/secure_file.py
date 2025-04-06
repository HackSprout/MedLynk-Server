from cryptography.fernet import Fernet

def encrypt_token(token, key):
    cipher_suite = Fernet(key)
    return cipher_suite.encrypt(token.encode('utf-8'))

def decrypt_token(encrypted_token, key):
    cipher_suite = Fernet(key)
    return cipher_suite.decrypt(encrypted_token).decode('utf-8')

import hashlib
def hash_password(password, salt):
        iterations = 100000
        hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), iterations)
        return hashed_password.hex()
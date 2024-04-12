import binascii
import os

def generate_salt():
    return binascii.hexlify(os.urandom(16)).decode()

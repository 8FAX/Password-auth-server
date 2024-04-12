import hmac
import sqlite3
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.hash_password import hash_password

def authenticate_user( identifier, password):
        cursor = None
        conn = sqlite3.connect('passwords.db')
        cursor = conn.cursor()
        identifier_upper = identifier.upper()
    
        cursor.execute("SELECT password, salt FROM users WHERE username = ? OR email = ?", (identifier_upper, identifier_upper))
        result = cursor.fetchone()
        if result:
            hashed_password, salt = result
            
            if hmac.compare_digest(hash_password(password, salt), hashed_password):
                return "success"
            else:
                return "error", "incorrect password"
        else:
            return "error", "no account found"
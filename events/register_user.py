import sqlite3
import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.generate_salt import generate_salt
from utils.hash_password import hash_password
from utils.generate_uuid import generate_uuid

def register_user( username, email, password):
        cursor = None
        conn = sqlite3.connect('passwords.db')
        cursor = conn.cursor()
        username_upper = username.upper()
        email_upper = email.upper()
    
        cursor.execute("SELECT COUNT(*) FROM users WHERE email = ?", (email_upper,))
        count = cursor.fetchone()[0]
        if count > 0:
            return "error", "email already exists", None
    
        salt = generate_salt()
        hashed_password = hash_password(password, salt)
        uuid_val = generate_uuid()
        creation_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            cursor.execute('''INSERT INTO users (uuid, username, username, email, email, password, salt, creation_date, last_updated)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (uuid_val, username_upper, username_upper, email_upper, email_upper, hashed_password, salt, creation_date, creation_date))
            conn.commit()
            return "success", uuid_val
        except sqlite3.IntegrityError:
            conn.rollback()
            return "error", "username already exists", None
        

if __name__ == "__main__":
    print(register_user("test", "test", "test"))
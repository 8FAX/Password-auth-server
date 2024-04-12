import uuid
import sqlite3
def generate_uuid():
        cursor = None
        conn = sqlite3.connect('passwords.db')
        cursor = conn.cursor()
        while True:
            uuid_val = str(uuid.uuid4())
            cursor.execute("SELECT COUNT(*) FROM users WHERE uuid = ?", (uuid_val,))
            count = cursor.fetchone()[0]
            if count == 0:
                return uuid_val
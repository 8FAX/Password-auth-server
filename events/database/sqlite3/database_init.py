import sqlite3
def create_table():
        cursor = None
        conn = sqlite3.connect('passwords.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                uuid TEXT PRIMARY KEY,
                                username TEXT UNIQUE,
                                email TEXT,
                                password TEXT,
                                salt TEXT,
                                creation_date TEXT,
                                last_updated TEXT)''')
        conn.commit()
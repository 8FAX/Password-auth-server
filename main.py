import argparse
import sqlite3
import uuid
import hashlib
import datetime
import socketserver
import socket
import os
import binascii
import logging
import queue
import hmac
from multiprocessing import Process, Queue, Event

current_time = datetime.datetime.now()
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(message)s', level=logging.INFO)

class PasswordServer(socketserver.BaseRequestHandler):
    def __init__(self, server, request, client_address):
        self.server = server
        self.request = request
        self.client_address = client_address
        self.cursor = None
        self.conn = sqlite3.connect('passwords.db')
        self.cursor = self.conn.cursor()
        self.create_table()

    def handle(self):
        try:
            current_time = datetime.datetime.now()
            client_ip = self.client_address[0]
            connection_start_time = datetime.datetime.now()
            logging.info(f"{connection_start_time} - New connection from {client_ip}")
            start_time = datetime.datetime.now()
            self.request.settimeout(5)
        except Exception as e:
            logging.info(f"ERROR - {current_time} - Exception: {e}")
            return
        
        while True:
            try:
                data = self.request.recv(1024).strip()
                if not data:
                    break
                data = data.decode("utf-8")
                if data == "close":
                    break
                elif data.startswith("register"):
                    _, identifier, email, password = data.split("=")
                    response = str(self.register_user(identifier, email, password))
                    current_time = datetime.datetime.now()
                    logging.info(f"INFO - {current_time} - Connection from {client_ip} closed. Response:  {response} Type: register")
                elif data.startswith("authenticate"):
                    _, identifier, password = data.split("=")
                    response = str(self.authenticate_user(identifier, password))
                    logging.info(f"INFO - {current_time} - Connection from {client_ip} closed. Response:  {response} Type: authenticate")
                else:
                    response = "error", "invalid command"
                    logging.info(f"INFO -  {current_time} - Connection from {client_ip} closed. Response:  {response} Type: UNknown")
                self.request.sendall(response.encode("utf-8"))
            except socket.timeout:
                break
            except Exception as e:
                logging.info(f"ERROR - {current_time} - Exception: {e}")
                break
            end_time = datetime.datetime.now()
            logging.info(f"INFO - {current_time} - User IP was {client_ip} Connection was open for  {end_time - start_time} seconds")

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                uuid TEXT PRIMARY KEY,
                                username TEXT UNIQUE,
                                email TEXT,
                                password TEXT,
                                salt TEXT,
                                creation_date TEXT,
                                last_updated TEXT)''')
        self.conn.commit()

    def hash_password(self, password, salt):
        iterations = 100000
        hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), iterations)
        return hashed_password.hex()

    def generate_salt(self):
        return binascii.hexlify(os.urandom(16)).decode()

    def generate_uuid(self):
        while True:
            uuid_val = str(uuid.uuid4())
            self.cursor.execute("SELECT COUNT(*) FROM users WHERE uuid = ?", (uuid_val,))
            count = self.cursor.fetchone()[0]
            if count == 0:
                return uuid_val

    def register_user(self, username, email, password):
        username_upper = username.upper()
        email_upper = email.upper()
    
        self.cursor.execute("SELECT COUNT(*) FROM users WHERE email = ?", (email_upper,))
        count = self.cursor.fetchone()[0]
        if count > 0:
            return "error", "email already exists", None
    
        salt = self.generate_salt()
        hashed_password = self.hash_password(password, salt)
        uuid_val = self.generate_uuid()
        creation_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            self.cursor.execute('''INSERT INTO users (uuid, username, username, email, email, password, salt, creation_date, last_updated)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (uuid_val, username_upper, username_upper, email_upper, email_upper, hashed_password, salt, creation_date, creation_date))
            self.conn.commit()
            return "success", uuid_val
        except sqlite3.IntegrityError:
            self.conn.rollback()
            return "error", "username already exists", None

    def authenticate_user(self, identifier, password):
        identifier_upper = identifier.upper()
    
        self.cursor.execute("SELECT password, salt FROM users WHERE username = ? OR email = ?", (identifier_upper, identifier_upper))
        result = self.cursor.fetchone()
        if result:
            hashed_password, salt = result
            
            if hmac.compare_digest(self.hash_password(password, salt), hashed_password):
                return "success"
            else:
                return "error", "incorrect password"
        else:
            return "error", "no account found"

def handle_connection(connection, client_address):
    try:
        password_server = PasswordServer(None, connection, client_address) 
        password_server.setup()
        password_server.handle()
    except Exception as e:
        response = "error", "Server Error - HANDLE_CONNECTION"
        connection.sendall(response.encode("utf-8"))
        response = str(e)
        logging.error(f"ERROR - {current_time} - Response: {e}")
    finally:
        connection.close()

if __name__ == "__main__":
    logging.info(f"Server started at {current_time}")
    parser = argparse.ArgumentParser(description="Password server")
    parser.add_argument("--dev", action="store_true", help="Run server on local IP")
    args = parser.parse_args()

    HOST = "127.0.0.1" if args.dev else "0.0.0.0"
    PORT = 9999
    MAX_PROCESSES = 1
    print(f"Starting server on {HOST}:{PORT}")
    print(f"Maximum number of processes: {MAX_PROCESSES}")
    print(f"server started at {current_time}")
    print("Press Ctrl+C to stop the server")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)

    processes = []

    try:
        while True:
            connection, client_address = server.accept()
            start_time = datetime.datetime.now()
            process = Process(target=handle_connection, args=(connection, client_address))
            process.start()
            processes.append(process)
            end_time = datetime.datetime.now()
            print(f"INFO - {end_time} - Connection from {client_address[0]}:{client_address[1]} was open for {end_time - start_time} seconds")
            processes = [p for p in processes if p.is_alive()]
    except KeyboardInterrupt:
        print("Terminating processes...")
        for process in processes:
            process.terminate()
            process.join() 
        server.close()
        print("Server closed.")

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
import hmac
import multiprocessing

current_time = datetime.datetime.now()
logging.basicConfig(filename='app.log', filemode='a', format='%(name)s - %(message)s', level=logging.INFO)

class PasswordLogic(socketserver.BaseRequestHandler):
    def __init__(self, server, request, client_address, queue=None):
        self.server = server
        self.request = request
        self.client_address = client_address
        self.cursor = None
        self.conn = sqlite3.connect('passwords.db')
        self.cursor = self.conn.cursor()
        self.create_table()
        self.queue = queue

    def handle(self):
        try:
            current_time = datetime.datetime.now()
            client_ip = self.client_address[0]
            connection_start_time = datetime.datetime.now()
            logging.info(f"{connection_start_time} - INFO - New connection from {client_ip}")
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





class ProcessManager(multiprocessing.Process):
    def __init__(self, max_processes, queue):
        super().__init__()
        self.max_processes = max_processes
        self.queue = queue
        self.active_processes = []

    def run(self):
        while True:
            for process in list(self.active_processes):
                if datetime.datetime.now() - process["start_time"] > datetime.timedelta(seconds=10):
                    process["process"].terminate()
                    response = ("error", "Server process timeout")
                    process["connection"].sendall(str(response).encode("utf-8"))
                    logging.info(f"KILLED - {datetime.datetime.now()} - Server process {process['process'].name} was killed by Argus Response: {response}")
                    self.active_processes.remove(process)

            while not self.queue.empty():
                if len(self.active_processes) >= self.max_processes:
                    break
                start_time, connection, client_address = self.queue.get() 
                if datetime.datetime.now() - start_time > datetime.timedelta(seconds=10):
                    response = ("error", "Server queue timeout")
                    connection.sendall(str(response).encode("utf-8"))
                    logging.info(f"KILLED - {datetime.datetime.now()} Connection from {connection.getpeername()} was killed by Argus (more than 10s in queue) Response: {response}")
                    continue
                auth_process = multiprocessing.Process(target=self.handle_connection, args=(connection, client_address))
                auth_process.start()
                self.active_processes.append({"process": auth_process, "start_time": datetime.datetime.now(), "connection": connection})


class TCPProcess:  # Corrected class name
    def __init__(self, server_address, max_processes):
        self.server_address = server_address
        self.max_processes = max_processes
        self.manager = multiprocessing.Manager()  
        self.queue = self.manager.Queue()  
        self.active_processes = []
        self.manager_process =  ProcessManager(self.max_processes, self.queue)

    def process_request(self, request, client_address):
        start_time = datetime.datetime.now()
        self.queue.put((start_time, request, client_address))

    def handle_connection(self, connection, client_address):
        try:
            password_Logic_thread = PasswordLogic(None, connection, client_address)
            password_Logic_thread.handle()
        except Exception as e:
            response = ("error", "Server Error - HANDLE_CONNECTION")
            connection.sendall(str(response).encode("utf-8"))
            logging.error(f"ERROR - {datetime.datetime.now()} - Response: {e}")
        finally:
            connection.close()
        for process in self.active_processes:
            if process["connection"] == connection:
                self.active_processes.remove(process)
                logging.info(f"INFO - {datetime.datetime.now()} - Process closed. Active processes: {len(self.active_processes)}")
                break
    
    def top_level_manager(self, connection, client_address):
        manager = ProcessManager(self.max_processes, self.queue)
        manager.handle_connection(connection, client_address)

    def serve_forever(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind(self.server_address)
            server_socket.listen()
            logging.info(f"Server started on {self.server_address[0]}:{self.server_address[1]}")
            while True:
                connection, client_address = server_socket.accept()
                logging.info(f"New connection from {client_address}")
                process = multiprocessing.Process(target=self.top_level_manager, args=(connection, client_address))
                process.start()
                self.active_processes.append(process)

    def close(self):
        for process in self.active_processes:
            process.terminate()

if __name__ == "__main__":
    logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(message)s', level=logging.INFO)
    parser = argparse.ArgumentParser(description="Password server")
    parser.add_argument("--dev", action="store_true", help="Run server on local IP")
    args = parser.parse_args()

    HOST = "127.0.0.1" if args.dev else "0.0.0.0"
    PORT = 9999
    MAX_PROCESSES = 4

    print(f"Starting server on {HOST}:{PORT}")
    print(f"Maximum number of processes: {MAX_PROCESSES}/{os.cpu_count()}")
    print(f"server started at {current_time}")
    print("Press Ctrl+C to stop the server") 

    server = TCPProcess((HOST, PORT), max_processes=MAX_PROCESSES)
    server.serve_forever()
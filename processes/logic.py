import socket
import datetime
import logging
import sys
import os
from events.register_user import register_user
from events.authenticate_user import authenticate_user
from events.database.sqlite3.database_init import create_table
filename = os.path.basename(__file__)

current_time = datetime.datetime.now()
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(message)s', level=logging.INFO)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def handle(start_time, request, client_address):
    create_table()
    try:
        current_time = datetime.datetime.now()
        client_ip = client_address[0]
        connection_start_time = datetime.datetime.now()
        logging.info(f" {filename} - {connection_start_time} - INFO - New connection from {client_ip}")
        start_time = datetime.datetime.now()
        request.settimeout(5)
    except Exception as e:
        logging.info(f" {filename} - ERROR - {current_time} - Exception: {e}")
        return
        
    while True:
        try:
            data = request.recv(1024).strip()
            if not data:
                break
            data = data.decode("utf-8")
            if data == "close":
                break
            elif data.startswith("register"):
                _, identifier, email, password = data.split("=")
                response = str(register_user(identifier, email, password))
                current_time = datetime.datetime.now()
                logging.info(f" {filename} - INFO - {current_time} - Connection from {client_ip} closed. Response:  {response} Type: register")
            elif data.startswith("authenticate"):
                _, identifier, password = data.split("=")
                response = str(authenticate_user(identifier, password))
                logging.info(f" {filename} - INFO - {current_time} - Connection from {client_ip} closed. Response:  {response} Type: authenticate")
            else:
                response = "error", "invalid command"
                logging.info(f" {filename} - INFO -  {current_time} - Connection from {client_ip} closed. Response:  {response} Type: UNknown")
            request.sendall(response.encode("utf-8"))
        except socket.timeout:
            break
        except Exception as e:
            logging.info(f" {filename} - ERROR - {current_time} - Exception: {e}")
            break
        end_time = datetime.datetime.now()
        logging.info(f" {filename} - INFO - {current_time} - User IP was {client_ip} Connection was open for  {end_time - start_time} seconds") 
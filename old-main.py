import argparse
import datetime
import socketserver
import threading
import os
import logging
import queue
from processes.logic import handle

curent_time = datetime.datetime.now()
filename = os.path.basename(__file__)

class ThreadedAuthManager(threading.Thread):

    def __init__(self, max_threads, queue, active_threads):
        super().__init__()
        self.max_threads = max_threads
        self.queue = queue
        self.active_threads = active_threads
        self.shutdown_event = threading.Event()

    def run(self):
        while not self.shutdown_event.is_set():
            for thread in list(self.active_threads):
                if (datetime.datetime.now() - thread["start_time"]).total_seconds() > 10:
                    thread["thread"].join(timeout=1)
                    if thread["thread"].is_alive():
                        thread["thread"].terminate()
                        response = "error", "Server thread timeout"
                        thread["connection"].sendall(response.encode("utf-8"))
                        logging.info(f" {filename} - KILLED - {self.current_time} - Server thread {thread['thread'].name} was killed by Argus Response: {response}")
                        self.active_threads.remove(thread)

            while not self.queue.empty():
                if len(self.active_threads) >= self.max_threads:
                    break
                start_time, connection, client_address = self.queue.get() 
                if (datetime.datetime.now() - start_time).total_seconds() > 10:
                    response = "error", "Server queue timeout"
                    response = str(response)
                    connection.sendall(response.encode("utf-8"))
                    logging.info(f" {filename} - KILLED - {self.current_time} Connection from {connection.getpeername()} was killed by Argus (more than 10s in queue) Response: {response}")
                    continue
                auth_thread = threading.Thread(target=self.handle_connection, args=(start_time, connection, client_address))
                auth_thread.daemon = True
                auth_thread.start()
                self.active_threads.append({"thread": auth_thread, "start_time": datetime.datetime.now(), "connection": connection})

    def handle_connection(self, start_time, connection, client_address):
        try:
            handle(start_time, connection, client_address)
        except Exception as e:
            response = "error", "Server Error - HANDLE_CONNECTION"
            connection.sendall(response.encode("utf-8"))
            response = str(e)
            logging.error(f"ERROR - {self.current_time} - Response: {e}")
        finally:
            connection.close()
        for thread in self.active_threads:
            if thread["connection"] == connection:
                self.active_threads.remove(thread)
                logging.info(f" {filename} - INFO - {self.current_time} - Thread closed. Active threads: {len(self.active_threads)}")
                break
            logging.info(f" {filename} - INFO - {self.current_time} - Connection closed. from {client_address}")
            logging.info(f" {filename} - INFO - {self.current_time} - Active threads: {len(self.active_threads)}")
            logging.info(f" {filename} - INFO - {self.current_time} - Server queue size: {self.queue.qsize()}")

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def __init__(self, server_address, RequestHandlerClass, max_threads):
        super().__init__(server_address, RequestHandlerClass)
        self.queue = queue.Queue()
        self.active_threads = []
        self.auth_manager = ThreadedAuthManager(max_threads, self.queue, self.active_threads)
        self.auth_manager.start()

    def process_request(self, request, client_address):
        start_time = datetime.datetime.now()
        self.queue.put((start_time, request, client_address))

    def server_close(self):
        if hasattr(self, 'auth_manager'): 
            self.auth_manager.shutdown_event.set()
        super().server_close()

if __name__ == "__main__":
    logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(message)s', level=logging.INFO)
    parser = argparse.ArgumentParser(description="Password server")
    parser.add_argument("--dev", action="store_true", help="Run server on local IP")
    args = parser.parse_args()

    HOST = "127.0.0.1" if args.dev else "0.0.0.0"
    PORT = 9999
    MAX_THREADS = 10000

    server = ThreadedTCPServer((HOST, PORT), handle, max_threads=MAX_THREADS)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    print("Server loop running in thread:", server_thread.name)
    logging.info(f" {filename} - {curent_time} - RESTARTED SERVER -- RESTARTED SERVER -- RESTARTED SERVER -- RESTARTED SERVER -- RESTARTED SERVER -- RESTARTED SERVER - {curent_time}")
    logging.info(f" {filename} - {curent_time} - Server loop running in thread: {server_thread.name}")
    logging.info(f" {filename} - {curent_time} - Server started on {HOST}:{PORT}")  

    server_thread.join()
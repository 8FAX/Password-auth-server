import socketserver
import time
from multiprocessing import Process, Queue, Manager
from processes.manager import Manager


class TCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print(f"{self.client_address[0]} wrote: {self.data}")
        self.request.sendall(self.data.upper())
        

        
class TCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def __init__(self, server_address, RequestHandlerClass, manager):
        super().__init__(server_address, RequestHandlerClass)
        self.active_threads = manager.list()
        self.idle_threads = manager.list()


if __name__ == "__main__":

    HOST, PORT = "localhost", 9999
    MAX_CORES = 4
    MIN_CORES = 1
    start_time = time.time()
    queue = Queue()
    manager = Manager()

    server = TCPServer((HOST, PORT), TCPHandler, manager)
    server_thread = server.serve_forever()
    server_thread.daemon_threads = True
    server_thread.start()
    server_thread.join()

    
    Manager = Process(target=Manager, args=(Queue, MAX_CORES, MIN_CORES))
    server_thread = server.serve_forever()
    server_thread.daemon_threads = True
    server_thread.start()
    server_thread.join()

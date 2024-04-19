import socket
import time
from multiprocessing import Process, Queue 
from processes.logic import pusher
from events.load_config import load_config
import logging as log


def start_server(host, port, num_workers):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()

    workers = []
    for i in range(NUM_WORKERS):
        worker = Process(target=pusher, args=(server_socket,))
        worker.start()
        workers.append(worker)
        print(f"Worker {i} started with PID {worker.pid}")


if __name__ == "__main__":

    print ("Starting server")
    HOST, PORT = "localhost", 9999
    NUM_WORKERS = 100
    config = load_config()
    start_time = time.time()
    queue = Queue()
    start_server(HOST, PORT, NUM_WORKERS)



    
    
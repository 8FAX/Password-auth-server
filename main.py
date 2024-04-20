import socket
import time
from multiprocessing import Process, Queue 
from processes.logic import pusher
from events.load_config import load_config
from processes.logger import logger


def start_server(config):

    host = config["ip"]
    port = config["port"]
    NUM_WORKERS = config["num_of_workers"]

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()

    workers = []
    for i in range(NUM_WORKERS):
        worker = Process(target=pusher, args=(server_socket,))
        worker.start()
        workers.append(worker)
        print(f"Worker {i} started with PID {worker.pid}")
    
    log_queue = Queue()
    logger_process = Process(target=logger, args=(log_queue, config))
    logger_process.start()
    print(f"Logger started with PID {logger_process.pid}")

    input("Press enter to shutdown server\n")
    server_socket.close()
    for worker in workers:
        if worker.is_alive():
            worker.terminate()
            workers.remove(worker)
            print(f"Worker {worker.pid} terminated")
    log_queue.put("SERVER_SHUTDOWN")
    while not log_queue.empty():
        time.sleep(0.1) 
    logger_process.terminate()
    print(f"Logger {logger_process.pid} terminated") 
    print("Server shutdown safely")


if __name__ == "__main__":

    config = load_config()
    for key, value in config.items():
        print(f"{key}: {value}")

    print ("Starting server")
    start_time = time.time()

    start_server(config)



    
    
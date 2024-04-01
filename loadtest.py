import socket
import time
from multiprocessing import Process
import random

def spam_server(host, port, num_requests_per_thread):
    for _ in range(num_requests_per_thread):
        try:
            # Create a TCP/IP socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((host, port))
                # Sending a simple message to the server
                i = random.randint(1, 10000)
                user = f"user{i}"
                email = f"user@user.com{i}"
                message = f"register={user}={email}=password"
                sock.sendall(message.encode())
                response = sock.recv(1024)
                print("Response:", response.decode())
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 9999  # Change this to the dev port you are using
    NUM_PROCESSES = 1  # Number of processes to use
    NUM_REQUESTS_PER_PROCESS = 4  # Number of requests per process

    # Spawning multiple processes to spam the server with connections
    processes = []
    for _ in range(NUM_PROCESSES):
        start = time.time()
        p = Process(target=spam_server, args=(HOST, PORT, NUM_REQUESTS_PER_PROCESS))
        processes.append(p)
        p.start()

    # Wait for all processes to finish
    for p in processes:
        p.join()
    end = time.time()
    print(f"Spamming the server with {NUM_PROCESSES * NUM_REQUESTS_PER_PROCESS} processes took {end - start} seconds.")
    print("All connections completed.")
import socket
import time
import threading
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
    NUM_THREADS = 10  # Number of threads to use
    NUM_REQUESTS_PER_THREAD = 100  # Number of requests per thread

    # Spawning multiple threads to spam the server with connections
    threads = []
    for _ in range(NUM_THREADS):
        t = threading.Thread(target=spam_server, args=(HOST, PORT, NUM_REQUESTS_PER_THREAD))
        threads.append(t)
        t.start()
        t.start()
        t.start()

    # Wait for all threads to finish
    for t in threads:
        t.join()
        t.join()
        t.join()

    print("All connections completed.")
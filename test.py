import socket

def send_data(data):
    HOST = '127.0.0.1'  # Change this to the IP address or hostname of your server
    PORT = 9999  # Change this to the port number your server is running on

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(data.encode('utf-8'))  # Ensure data is encoded as bytes before sending
        response = s.recv(1024).decode('utf-8')
    return response

def main():
    print("Welcome to the password server test client, this can be used to test the\nserver's functionality and to enter new test accounst into the database.")
    reqtype = input("Enter type call authenticate or register: ")
    if reqtype.lower() == "register" or reqtype.lower() == "1":
        username = input("Enter username: ")
        email = input("Enter email: ")
        password = input("Enter password: ")
        data = f"register={username}={email}={password}"
    elif reqtype.lower() == "authenticate" or reqtype.lower() == "2":
        username = input("Enter username: ")
        password = input("Enter password: ")
        data = f"authenticate={username}={password}"
    else:
        print("Invalid request type")
        main()

    response = send_data(data)
    print("Server response:", response)

if __name__ == "__main__":
    main()

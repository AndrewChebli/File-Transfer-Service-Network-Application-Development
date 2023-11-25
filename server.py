import socket
import os

def put_func(filename):
    pass

def get_func(filename):
    pass

def summary_func(filename):
    pass

def change_func(oldFileName, newFileName):
    pass

def help_func():
    pass

def bye():
    print("Client closed the connection.")


def fileTransferProtocol(port):
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind(('localhost', port))
    serverSocket.listen(1)
    while True:
        # Create socket for the connection
        connectionSocket, addr = serverSocket.accept()
        print(f'ip address: {addr}')

        while True:
            # Receive request from client and decode it
            message = connectionSocket.recv(1024).decode()
            
            if (message == 'bye'):
                # If no data received, client may have closed the connection
                bye()
                break
            
            # Split the HTTP request sent into lines
            group_requests = message.split("\n")
            print(group_requests)

        connectionSocket.close() 


if __name__ == '__main__':
    fileTransferProtocol(500)
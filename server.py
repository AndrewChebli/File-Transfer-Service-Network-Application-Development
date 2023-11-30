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
    while True:
        connection = input("Choose type of communication: TCP or UDP? ")

        if connection == 'TCP':
            serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serverSocket.bind(('127.0.0.1', port))
            serverSocket.listen(1)
            connectionSocket,addr = serverSocket.accept()
            connected = True
            print("TCP server launched!")
            while True:
                
                if not(connected):
                    # Create socket for the connection
                    connectionSocket, addr = serverSocket.accept()
                    print(f'accepting connection from ip address: {addr}')
                    connected = True

                message = connectionSocket.recv(1024).decode()

                if message == 'bye' :
                    # If client send bye, then server can close the connection
                    bye()
                    connectionSocket.close()
                    connected = False
                    continue 

                # Split the HTTP request sent into words
                group_requests = message.split(" ")
                print(group_requests)
                
        elif connection == 'UDP':     
            serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            serverSocket.bind(('127.0.0.1', port))
            print("UDP server launched!")
            while True:
                #no need to accept with udp we just receive
                data, addr = serverSocket.recvfrom(1024)
                data_new = data.decode()
                # Split the HTTP request sent into lines
                group_requests = data_new.split(" ")
                print(group_requests)

        else:
            continue    
    

if __name__ == '__main__':
    fileTransferProtocol(500)
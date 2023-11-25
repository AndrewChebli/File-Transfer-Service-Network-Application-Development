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
    pass

def fileTransferProtocol(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', port))
    server_socket.listen(1)
    while True:
        connection, address = server_socket.accept()
        




    


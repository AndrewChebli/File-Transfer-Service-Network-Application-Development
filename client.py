import socket
import os

def ftp_transfer_client(server_ip, server_port):
        while True:
            connection = input("Choose type of communication: TCP or UDP? ")
            if connection =='TCP':     
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((server_ip, server_port))
                print("TCP connection established")
                print(f"Connected to FTP Server at {server_ip}:{server_port}")
                break
            elif connection =='UDP':
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                print(f"sending requests via UDP to {server_ip}:{server_port} ")
                break
            else:
                continue

        # print(f"Connected to FTP Server at {server_ip}:{server_port}")

        while True:
            #ask client for input
            command = input("myftp>").split()
            
            if connection == 'TCP':
                # Send command to the server
                client_socket.send(' '.join(command).encode())
            elif connection == 'UDP':          
                # Send command to the server
                client_socket.sendto(' '.join(command).encode(),(server_ip,server_port))
            if(command[0].lower() == 'bye'):
                print('client terminated session')
                client_socket.close()
                break
               
    

if __name__ == '__main__':
    ftp_transfer_client('127.0.0.1',500)
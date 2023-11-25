import socket
import os

def ftp_transfer_client(server_ip, server_port):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_ip, server_port))

        print(f"Connected to FTP Server at {server_ip}:{server_port}")

        while True:
            #ask for input from client
            command = input("myftp>").split()

            # Send command to the server
            client_socket.send(' '.join(command).encode())
            if(command[0].lower() == 'bye'):
                print('client terminated session')
                client_socket.close()
                break
               
    

if __name__ == '__main__':
    ftp_transfer_client('localhost',500)
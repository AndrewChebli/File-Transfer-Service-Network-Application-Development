import socket
import os

put_opcode =0
get_opcode = 1
change_opcode = 2
summary_opcode = 3
help_opcode = 4
typefile = "utf-8"

def put_func(filename, client_socket):
            if not os.path.exists(filename):
                raise FileNotFoundError(f"File '{filename}' not found.")

            if len(filename)>31:
                raise("filename length should be 31 or less")
            
            
            firstByte = command_byte(put_opcode, filename) 
            client_socket.send(bytes([firstByte]))
            client_socket.send(filename.encode(typefile)) 
            filedata = open(filename, 'rb').read()
            client_socket.send(filedata)


def command_byte(opcode, filename):
     msb = opcode << 5 
     filename_length = len(filename)
     return msb | filename_length

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
                # client_socket.send(' '.join(command).encode())
                if(command[0].lower() == 'put'):
                    print('transferring file')
                    put_func(command[1], client_socket)
                    break
                elif(command[0].lower() == 'bye'):
                    print('client terminated session')
                    client_socket.close()
                    break
                
            elif connection == 'UDP':          
                # Send command to the server
                client_socket.sendto(' '.join(command).encode(),(server_ip,server_port))
            
    
       
                

               
    

if __name__ == '__main__':
    ftp_transfer_client('127.0.0.1',2005)
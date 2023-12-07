import socket
import os

put_opcode =0
get_opcode = 1
change_opcode = 2
summary_opcode = 3
help_opcode = 4
typefile = "utf-8"
client_folder = os.path.dirname(os.path.realpath(__file__))

def help_func(connection_socket):
    firstByte = command_byte(help_opcode)
    connection_socket.send(bytes([firstByte]))
    rescode, filename_length = decode_first_byte(connection_socket.recv(1))
    print(f"rescode {rescode}")
    if rescode == 6:
        print(f"commands are: {(connection_socket.recv(1024)).decode()}")

def decode_first_byte(first_byte):  # Add rescode to response message
    new = int.from_bytes(first_byte, byteorder='big') 
    rescode = new >>5
    filename_length = new & 0x1F
    return rescode, filename_length

def receive_file(connection_socket, filename_length):

   encoded_filename = connection_socket.recv(filename_length)
   print(encoded_filename)
   filename = encoded_filename.decode()
   file_path = os.path.join(client_folder, filename)
   print(f"Saving file to: {file_path}")  
   with open(file_path, 'wb') as file:
         while True:
            file_data = connection_socket.recv(1024)
            if "EOF".encode() in file_data:
                # If EOF is found, write data up to EOF and then break
                eof_index = file_data.index("EOF".encode())
                file.write(file_data[:eof_index])  # Write data before EOF
                break  # Stop reading after EOF
            else:
                file.write(file_data)

def get_func(filename, client_socket):
        if len(filename)>31:
            raise("filename length should be 31 or less")
        
        firstByte = command_byte(get_opcode, filename)
        client_socket.send(bytes([firstByte]))
        client_socket.send(filename.encode(typefile))

def put_func(filename, client_socket):
            if not os.path.exists(filename):
                raise FileNotFoundError(f"File '{filename}' not found.")

            if len(filename)>31:
                raise("filename length should be 31 or less")
            
            
            firstByte = command_byte(put_opcode, filename) 
            client_socket.send(bytes([firstByte]))
            client_socket.send(filename.encode(typefile))

            with open(filename, 'rb') as file:
                filedata = file.read(1024)
                client_socket.send(filedata)

                # Continue sending one byte at a time until the end of the file
                while filedata:
                    filedata = file.read(1024)
                    if not filedata:
                        break  # Exit the loop when no more data to send
                    client_socket.send(filedata)
                    print(filedata)

                # Send an "EOF" signal to indicate the end of the file
                eof_signal = "EOF".encode()
                client_socket.send(eof_signal)


def change_func(connectionSocket, oldFileName, newFileName):
    firstByte = command_byte(change_opcode, oldFileName)
    connectionSocket.send(bytes([firstByte]))
    connectionSocket.send(oldFileName.encode(typefile))
    #to send length of the newFileName
    newFileName_length = bytes([len(newFileName)])
    connectionSocket.send(newFileName_length)
    #send encoded newFileName
    connectionSocket.send(newFileName.encode(typefile))
    #receive response from server
    rescode, filename_length = decode_first_byte(connectionSocket.recv(1))
    if rescode == 0:
        print(f"{oldFileName} has been changed into {newFileName}. ")


def summary(filename,client_socket):
     firstByte = command_byte(summary_opcode, filename)
     client_socket.send(bytes([firstByte]))
     client_socket.send(filename.encode(typefile))
     rescode, filename_length = decode_first_byte(client_socket.recv(1))
     if rescode == 0:
        print(f"Summary request for {filename} was successful.")
        # Assuming the server sends back the name of the summary file
        summary_filename = client_socket.recv(filename_length).decode()
        print(f"Receiving summary file: {summary_filename}")
        receive_file(client_socket, filename_length)
     else:
        print("Error in summary request.")
     
     pass
     



def command_byte(opcode, filename=None):
    msb = opcode << 5
    if filename is not None:
        filename_length = len(filename)
    else:
        filename_length = 0
    return msb | filename_length

def ftp_transfer_client(server_ip, server_port):
        script_directory = os.path.dirname(os.path.realpath(__file__))
        os.chdir(script_directory)
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

        while True:
            #ask client for input
            command = input("myftp>").split()
            
            if connection == 'TCP':
                # Send command to the server
                # client_socket.send(' '.join(command).encode())
                if(command[0].lower() == 'put'):
                    print('transferring file')
                    put_func(command[1], client_socket)
                elif command[0].lower() == 'get':
                    get_func(command[1].lower(),client_socket)
                    print('waiting for server response')
                    rescode, filename_length = decode_first_byte(client_socket.recv(1))
                    print(f"answer is {rescode}, {filename_length}")
                    if rescode == 1:
                        print("get request was successful")
                        receive_file(client_socket,filename_length)
                elif(command[0].lower() == 'bye'):
                    print('client terminated session')
                    client_socket.close()
                    break
                elif(command[0].lower() == 'help'):
                     help_func(client_socket)
                elif(command[0].lower() == 'change'):
                     change_func(client_socket,command[1], command[2])
                elif command[0].lower() == 'summary':
                     summary(command[1].lower(), client_socket)

                else:
                     continue
                
            elif connection == 'UDP':          
                # Send command to the server
                client_socket.sendto(' '.join(command).encode(),(server_ip,server_port))

if __name__ == '__main__':
    port = input("enter the port you want to connect to ? ")
    port = int(port)
    ftp_transfer_client('127.0.0.1',port)
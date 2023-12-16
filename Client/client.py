import socket
import os

put_opcode =0
get_opcode = 1
change_opcode = 2
summary_opcode = 3
help_opcode = 4
error_opcode = 6
typefile = "utf-8"
client_folder = os.path.dirname(os.path.realpath(__file__))
tcp = True

def help_func(connection_socket, server_ip=None, server_port=None):
    if tcp:
        firstByte = command_byte(help_opcode)
        connection_socket.send(bytes([firstByte]))
        rescode, filename_length = decode_first_byte(connection_socket.recv(1))
        print(f"rescode {rescode}")
        if rescode == 6:
            print(f"commands are: {(connection_socket.recv(1024)).decode()}")
    else:
        firstByte = command_byte(help_opcode)
        connection_socket.sendto(bytes([firstByte]), (server_ip, server_port))
        #get first byte
        data, _ = connection_socket.recvfrom(1)
        #get the rescode and filename_length
        rescode, filename_length = decode_first_byte(data[0:1])
        if rescode == 6:
            filedata, address = connection_socket.recvfrom(1024)
            print(f"commands are: {filedata.decode()}") 
        elif rescode == 4:
            print("Error in help request.")

                
            

def decode_first_byte(first_byte):  # Add rescode to response message
    new = int.from_bytes(first_byte, byteorder='big')
    rescode = new >>5
    filename_length = new & 0x1F
    return rescode, filename_length

def receive_file(connection_socket, filename_length):
   if tcp:
        encoded_filename = connection_socket.recv(filename_length)
   else:
       encoded_filename, client_address = connection_socket.recvfrom(filename_length)
    
   filename = encoded_filename.decode()
   print(f"file name is {filename}")
   file_path = os.path.join(client_folder, filename)
   print(f"Saving file to: {file_path}")  
   with open(file_path, 'wb') as file:
         while True:
            if tcp:
                file_data = connection_socket.recv(1024)
            else:
                file_data, _ = connection_socket.recvfrom(1024)
                
            
            if "EOF".encode() in file_data:
                # If EOF is found, write data up to EOF and then break
                eof_index = file_data.index("EOF".encode())
                file.write(file_data[:eof_index])  # Write data before EOF
                break  # Stop reading after EOF
            else: 
                file.write(file_data)

def get_func(filename, client_socket, server_ip, server_port):
        
        if len(filename)>31:
            raise("filename length should be 31 or less")
        
        firstByte = command_byte(get_opcode, filename)
        server_address = (server_ip, server_port)
        if(tcp):
            
            client_socket.send(bytes([firstByte]))
            client_socket.send(filename.encode(typefile))
        else:
            client_socket.sendto(bytes([firstByte]), server_address)
            client_socket.sendto(filename.encode(typefile), server_address)

            


def put_func(filename, client_socket, server_ip,server_port):
            
        
            if not os.path.exists(filename):
                raise FileNotFoundError(f"File '{filename}' not found.")

            if len(filename)>31:
                raise("filename length should be 31 or less")
            
            
            firstByte = command_byte(put_opcode, filename) 
            
            if tcp :
                client_socket.send(bytes([firstByte]))
            else:
                server_port = int(server_port)  # Ensure server_port is an integer
                server_address = (server_ip, server_port)
                client_socket.sendto(bytes([firstByte]), server_address)

            if(tcp):   
                client_socket.send(filename.encode(typefile))
            else:
                client_socket.sendto(filename.encode(typefile), server_address )

            with open(filename, 'rb') as file:
                filedata = file.read(1024)
                if(tcp):
                    client_socket.send(filedata)
                else:
                    client_socket.sendto(filedata, server_address)

                # Continue sending one byte at a time until the end of the file
                while filedata:
                    filedata = file.read(1024)
                    if not filedata:
                        break  # Exit the loop when no more data to send
                    if(tcp):
                        client_socket.send(filedata)
                    else:
                        client_socket.sendto(filedata, server_address)
                    print(filedata)

                # Send an "EOF" signal to indicate the end of the file
                eof_signal = "EOF".encode()
                if(tcp):
                    client_socket.send(eof_signal)
                else:
                    client_socket.sendto(eof_signal, server_address)
            
            if tcp:
              rescode, filename_length = decode_first_byte(client_socket.recv(1))
            else:
                data, _ = client_socket.recvfrom(1024)
                rescode, filename_length = decode_first_byte(data[0:1])
            if(rescode == 0):
                print(f" File was downloaded succesfully" )
            else:
                print(f"Error downloading the file")    


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
    elif rescode == 3:
        print(f"File '{oldFileName}' not found.")  
    elif rescode == 5:
        print(f"Unsuccessful change request for the file {oldFileName}.")      




def summary(filename,client_socket):
     firstByte = command_byte(summary_opcode, filename)
     client_socket.send(bytes([firstByte]))
     client_socket.send(filename.encode(typefile))

     print('waiting for server response')

     rescode, filename_length = decode_first_byte(client_socket.recv(1))
     
     if rescode == 2:
        print(f"Summary request for {filename} was successful.")
        # Assuming the server sends back the name of the summary file
        
        receive_file(client_socket, filename_length)
     else:
        print("Error in summary request.")
     
     
     



def command_byte(opcode, filename=None):
    msb = opcode << 5
    if filename is not None:
        filename_length = len(filename)
    else:
        filename_length = 0
    return msb | filename_length

def ftp_transfer_client(server_ip, server_port):
        global tcp
        script_directory = os.path.dirname(os.path.realpath(__file__))
        os.chdir(script_directory)
        while True:
            connection = input("Choose type of communication: TCP or UDP? ")
            if connection =='TCP':     
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((server_ip, server_port))
                tcp = True
                print("TCP connection established")
                print(f"Connected to FTP Server at {server_ip}:{server_port}")
                break
            elif connection =='UDP':
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                tcp = False
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
                    put_func(command[1], client_socket, server_ip,server_port)
                elif command[0].lower() == 'get':
                    get_func(command[1].lower(),client_socket, server_ip = None,server_port = None)
                    print('waiting for server response')
                    rescode, filename_length = decode_first_byte(client_socket.recv(1))
                    print(f"answer is {rescode}, {filename_length}")
                    if rescode == 1:
                        print("get request was successful")
                        receive_file(client_socket,filename_length)
                    elif rescode == 3:
                        print(f"File '{command[1]}' not found.")
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
                elif command[0].lower() not in ['put', 'get', 'bye', 'help', 'change', 'summary']:
                     firstByte = command_byte(error_opcode)
                     client_socket.send(bytes([firstByte]))
                     rescode, filename_length = decode_first_byte(client_socket.recv(1))
                     if(rescode == 4): 
                         print(f"command not found")
                    
                     


                else:
                    continue
                
            elif connection == 'UDP':     

                # Send command to the server
                

                # client_socket.sendto(' '.join(command).encode(),(server_ip,server_port))
                
                if(command[0].lower() == 'put'):
                    print('transferring file UDP')
                    put_func(command[1], client_socket, server_ip,server_port)
                elif(command[0].lower() == 'get'):
                    get_func(command[1].lower(),client_socket, server_ip,server_port )

                    rescode, filename_length = decode_first_byte(client_socket.recv(1))
                    if rescode == 1:
                        print("get request was successful")
                        receive_file(client_socket,filename_length)
                    elif rescode == 3:
                        print(f"File '{command[1]}' not found.")
                    # print('waiting for server response')
                    # data, _ = client_socket.recvfrom(1024)
                    # print(f"{data}")
                    # rescode, filename_length = decode_first_byte(data[0:1])
                    # print(f'get request was successful {rescode} and {filename_length}')
                    # receive_file(client_socket,filename_length)
                elif(command[0].lower() == 'bye'):
                    print('client terminated session')
                    client_socket.close()
                    break
                elif(command[0].lower() == 'help'):
                     help_func(client_socket, server_ip, server_port)
                elif(command[0].lower() == 'change'):
                    change_func(client_socket,command[1], command[2])
                elif command[0].lower() == 'summary':
                     summary(command[1].lower(), client_socket)




if __name__ == '__main__':
    port = input("enter the port you want to connect to ? ")
    port = int(port)
    ftp_transfer_client('127.0.0.1',port)
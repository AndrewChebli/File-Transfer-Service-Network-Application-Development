from random import randint
import socket
import os

rescode_put =0 
rescode_get = 1

server_folder = os.path.dirname(os.path.realpath(__file__))

def response_byte(opcode, filename):
     msb = opcode << 5 
     filename_length = len(filename)
     return msb | filename_length

def decode_first_byte(first_byte):  # Add rescode to response message
    new = int.from_bytes(first_byte, byteorder='big') 
    rescode = new >>5
    filename_length = new & 0x1F
    return rescode, filename_length

def receive_file(connection_socket, filename_length):

   encoded_filename = connection_socket.recv(filename_length)
   filename = encoded_filename.decode()
   file_path = os.path.join(server_folder, filename)
   print(f"Saving file to: {file_path}")
   
   with open(file_path, 'wb') as file:
         while True:
            file_data = connection_socket.recv(1024)
            print(file_data)
            if len(file_data) == 0:
                # No more data to read, break out of the loop
                break
            if "EOF".encode() in file_data:
                # If EOF is found, write data up to EOF and then break
                eof_index = file_data.index("EOF".encode())
                file.write(file_data[:eof_index])  # Write data before EOF
                break  # Stop reading after EOF
            else:
                file.write(file_data)


def send_file(connection_socket,decoded_filename):
    file_path = os.path.join(server_folder,decoded_filename)

    with open(file_path,'rb') as file:
        filedata = file.read(1024)
        connection_socket.send(filedata)

        # Continue sending one byte at a time until the end of the file
        while filedata:
            filedata = file.read(1024)
            if not filedata:
                break  # Exit the loop when no more data to send
            connection_socket.send(filedata)
            print(filedata)
        # Send an "EOF" signal to indicate the end of the file
        eof_signal = "EOF".encode()
        connection_socket.send(eof_signal)

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
            #accept first connection
            connectionSocket,addr = serverSocket.accept()
            #variable to know if there is a client currently connected
            connected = True
            print("TCP server launched!")
            
            while True:
                
                if not(connected):
                    # Create socket for the connection
                    connectionSocket, addr = serverSocket.accept()
                    print(f'accepting connection from ip address: {addr}')
                    connected = True

                first_byte = connectionSocket.recv(1)
                if not first_byte:
                    connected = False 
                    continue
                rescode, filename_length = decode_first_byte(first_byte)
                
                print(f"Decoded rescode: {rescode}, filename_length: {filename_length}")
                
                if rescode == rescode_put :
                    receive_file(connectionSocket, filename_length)
                    print(f"File received successfully.")
                elif rescode == rescode_get:
                    encoded_filename = connectionSocket.recv(filename_length)
                    decoded_filename = encoded_filename.decode()
                    if os.path.exists(f"{server_folder}/{decoded_filename}"):
                        response_msg = response_byte(rescode_get,decoded_filename)
                        print(f"response_msg is {response_msg}")
                        connectionSocket.send(bytes([response_msg]))
                        connectionSocket.send(decoded_filename.encode("utf-8"))
                        send_file(connectionSocket, decoded_filename)
                        print("File sent successfully")
                            
        elif connection == 'UDP':     
            serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            serverSocket.bind(('127.0.0.1', port))
            print("UDP server launched!")
            while True:
                #no need to accept with udp we just receive
                data, addr = serverSocket.recvfrom(1024)
                data_new = data.decode()

                # Split the HTTP request sent into words
                group_requests = data_new.split(" ")
                print(group_requests)

        else:
            continue
    

if __name__ == '__main__':
    print(server_folder)
    port = randint(2000,50000)
    print(f"port for server is {port}")
    fileTransferProtocol(port)
    
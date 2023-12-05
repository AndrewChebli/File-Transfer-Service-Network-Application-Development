import socket
import os

rescode_put =0 

server_folder = os.path.dirname(os.path.realpath(__file__))

print(f"Server folder: {server_folder}")
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
            if "EOF".encode() in file_data:
                # If EOF is found, write data up to EOF and then break
                eof_index = file_data.index("EOF".encode())
                file.write(file_data[:eof_index])  # Write data before EOF
                break  # Stop reading after EOF
            else:
                file.write(file_data)

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
                     break
                rescode, filename_length = decode_first_byte(first_byte)
                
                print(f"Decoded rescode: {rescode}, filename_length: {filename_length}")
                # if message == 'bye' :
                #     # If client send bye, then server can close the connection
                #     bye()
                #     connectionSocket.close()
                #     connected = False
                #     continue
                if rescode == rescode_put :
                    receive_file(connectionSocket, filename_length)
                    print(f"File received successfully.")
                
                # Split the HTTP request sent into words
                #group_requests = message.split(" ")
                #print(group_requests)
                
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
    fileTransferProtocol(2005)
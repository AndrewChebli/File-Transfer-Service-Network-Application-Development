from random import randint
import socket
import os

rescode_summary = 2
rescode_change = 0
rescode_get = 1
rescode_put =0 
rescode_unsuccesful_change = 5 
res_file_not_found = 3
res_error_unknown_request= 4

good_request_help = 6
get_opcode =1 
summary_opcode =3
put_opcode =0
error_unknown_request= 6
help_opcode = 4

tcp = True

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
   
   if(tcp):
        encoded_filename = connection_socket.recv(filename_length)
   else:
        encoded_filename, client_address = connection_socket.recvfrom(filename_length)
   
   filename = encoded_filename.decode()
 
   file_path = os.path.join(server_folder, filename)
   print(f"Saving file to: {file_path}")
   
   with open(file_path, 'wb') as file:
         while True:
            if(tcp):
                file_data = connection_socket.recv(1024)
            else:
                file_data, _ = connection_socket.recvfrom(1024)
            
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
   msb = rescode_put << 5 
   response_msg = msb | 0
   if(tcp):
        connection_socket.send(bytes([response_msg]))
   else: 
       connection_socket.sendto(bytes([response_msg]),client_address)

def send_file(connection_socket,decoded_filename,client_address="none"):
    file_path = os.path.join(server_folder,decoded_filename)
    with open(file_path,'rb') as file:
        filedata = file.read(1024)
        if(tcp):
            connection_socket.send(filedata)
        else:
            connection_socket.sendto(filedata,client_address)
        # Continue sending one byte at a time until the end of the file
        while filedata:
            filedata = file.read(1024)
            if not filedata:
                break  # Exit the loop when no more data to send
            if(tcp):
                connection_socket.send(filedata)
            else:
                connection_socket.sendto(filedata, client_address)
            print(filedata)
        # Send an "EOF" signal to indicate the end of the file
        eof_signal = "EOF".encode()
        if(tcp) :
            connection_socket.send(eof_signal)
        else:
            connection_socket.sendto(eof_signal, client_address)

def change_func(connection_socket,oldFileName_length, client_address):
    #for old name
    if(tcp):
        encoded_oldFileName = connection_socket.recv(oldFileName_length)
    else:
        encoded_oldFileName,_ = connection_socket.recvfrom(oldFileName_length)
    
    decoded_oldFileName = encoded_oldFileName.decode()

    #for new name
    if(tcp):
        newFileByte = connection_socket.recv(1)
    else:
        newFileByte,_ = connection_socket.recvfrom(1)

    new_fileName_length = int.from_bytes(newFileByte, byteorder='big') 

    if(tcp):
        newFileName = (connection_socket.recv(new_fileName_length)).decode()
    else:
        newFile, _ = connection_socket.recvfrom(new_fileName_length)
        newFileName = (newFile).decode()

    # check if file exists
    if not os.path.isfile(os.path.join(server_folder, decoded_oldFileName)):
        print(f"File '{decoded_oldFileName}' not found.")
        msb = res_file_not_found << 5 
        response_msg = msb | 0
        if tcp:
            connection_socket.send(bytes([response_msg]))  
        else: 
             connection_socket.sendto(bytes([response_msg]), client_address)   
        return

    #change name
    os.rename(decoded_oldFileName, newFileName)
    if not os.path.isfile(os.path.join(server_folder, newFileName)):    
        print(f"Change request was a failure! ")
        msb = 5 << 5 
        response_msg = msb | 0
        if(tcp):
            connection_socket.send(bytes([response_msg]))
        else:
            connection_socket.sendto(bytes([response_msg]), client_address)
        return 
    print(f"Change request was a success! ")
    msb = rescode_change << 5 
    response_msg = msb | 0
    if(tcp):
        connection_socket.send(bytes([response_msg]))
    else:
        connection_socket.sendto(bytes([response_msg]), client_address)
    
    
def calculate_summary(filename):
    print(f"Received filename for summary: {filename}")
    file_path = os.path.join(server_folder, filename)
    
    try:
        with open(file_path, 'r') as file:
            numbers = [float(line.strip()) for line in file if line.strip()]
        return max(numbers), min(numbers), sum(numbers) / len(numbers)
    except Exception as e:
        print(f"Error calculating summary: {e}")
        return None, None, None

def summary_func(connection_socket, filename,client_address="none"):
    max_val, min_val, avg_val = calculate_summary(filename)
    if max_val is not None:
        summary_data = f"Max: {max_val}\nMin: {min_val}\nAverage: {avg_val}\n"
        summary_filename = os.path.join(server_folder, "summary_" + os.path.basename(filename))
        with open(summary_filename, 'w') as summary_file:
            summary_file.write(summary_data)       
        basename = os.path.basename(summary_filename) 
        res_message = response_byte(rescode_summary, basename)

        if tcp:
            
            connection_socket.send(bytes([res_message]))
            connection_socket.send(basename.encode())
            send_file(connection_socket, basename)
        else:
            connection_socket.sendto(bytes([res_message]),client_address)
            connection_socket.sendto(basename.encode(),client_address)
            send_file(connection_socket, basename, client_address)
        os.remove(summary_filename)
    else:
        connection_socket.send("Error in processing file.".encode())

def help_func(connection_socket,filename,client_address="none"):
    if(tcp):
        msb = good_request_help << 5 
        fileSize = os.path.getsize(f"{server_folder}/{filename}")
        response_msg = msb | fileSize
        connection_socket.send(bytes([response_msg]))
        print(response_msg)
        
        with open(filename,"rb") as file:
            filedata = file.read(1024)
            connection_socket.send(filedata)
            while filedata:
                filedata = file.read(1024)
                if not filedata:
                    break  # Exit the loop when no more data to send
                connection_socket.send(filedata)
                print(filedata)
                # Send an "EOF" signal to indicate the end of the file
                eof_signal = "EOF".encode()
                connection_socket.send(eof_signal)
    else:
        msb = good_request_help << 5 
        fileSize = os.path.getsize(f"{server_folder}/{filename}")
        response_msg = msb | fileSize
        connection_socket.sendto(bytes([response_msg]),client_address)
        print(response_msg)
        
        with open(filename,"rb") as file:
            filedata = file.read(1024)
            connection_socket.sendto(filedata,client_address)
            while filedata:
                filedata = file.read(1024)
                if not filedata:
                    break


def bye():
    print("Client closed the connection.")

def fileTransferProtocol(port):
    global tcp
    while True:
        connection = input("Choose type of communication: TCP or UDP? ")
        if connection == 'TCP':
            tcp = True
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
                
                if rescode == put_opcode :
                    receive_file(connectionSocket, filename_length)
                    print(f"File received successfully.")
                elif rescode == get_opcode:
                    encoded_filename = connectionSocket.recv(filename_length)
                    decoded_filename = encoded_filename.decode()
                    if os.path.exists(f"{server_folder}/{decoded_filename}"):
                        response_msg = response_byte(rescode_get,decoded_filename)
                        print(f"response_msg is {response_msg}")
                        connectionSocket.send(bytes([response_msg]))
                        connectionSocket.send(decoded_filename.encode("utf-8"))
                        send_file(connectionSocket, decoded_filename)
                        print("File sent successfully")
                    else:
                        print(f"File '{decoded_filename}' not found.")
                        msb = res_file_not_found << 5 
                        response_msg = msb | 0
                        connectionSocket.send(bytes([response_msg]))
                elif rescode == help_opcode:
                    help_func(connectionSocket,"help.txt")                 
                elif rescode == 2:
                    change_func(connectionSocket,filename_length)
                elif rescode == summary_opcode:
                    encoded_filename = connectionSocket.recv(filename_length)
                    decoded_filename = encoded_filename.decode()
                    summary_func(connectionSocket, decoded_filename)
                elif rescode == error_unknown_request:
                    msb = res_error_unknown_request << 5
                    response_msg = msb | 0
                    connectionSocket.send(bytes([response_msg]))




        elif connection == 'UDP':     
            tcp = False
            serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            serverSocket.bind(('127.0.0.1', port))
            print("UDP server launched!")
            while True:
                data, client_address = serverSocket.recvfrom(1024)  # Adjust buffer size as needed
                first_byte = data[0:1]
                rescode, filename_length = decode_first_byte(first_byte)
                

                

                if rescode == put_opcode:
                    receive_file(serverSocket, filename_length)
                    print(f" UDP File received successfully.")
                elif rescode == get_opcode:
                    encoded_filename, client_address = serverSocket.recvfrom(filename_length)
                    decoded_filename = encoded_filename.decode()

                    if os.path.exists(f"{server_folder}/{decoded_filename}"):
                        response_msg = response_byte(rescode_get,decoded_filename)
                        
                        serverSocket.sendto(bytes([response_msg]), client_address)
                        serverSocket.sendto(decoded_filename.encode("utf-8"),client_address)
                        send_file(serverSocket, decoded_filename, client_address)
                        print("File sent successfully")
                    else:
                        print(f"File '{decoded_filename}' not found.")
                        msb = res_file_not_found << 5 
                        response_msg = msb | 0
                        connectionSocket.sendto(bytes([response_msg]), client_address)
                

                elif rescode == help_opcode:
                    help_func(serverSocket,"help.txt",client_address)
                elif rescode == 2:
                    change_func(serverSocket,filename_length, client_address)
                elif rescode == summary_opcode:
                    encoded_filename, client_address = serverSocket.recvfrom(filename_length)
                    decoded_filename = encoded_filename.decode()
                    summary_func(serverSocket, decoded_filename, client_address)
                elif rescode == error_unknown_request:
                    msb = res_error_unknown_request << 5
                    response_msg = msb | 0
                    serverSocket.sendto(bytes([response_msg]),client_address)    

                # #no need to accept with udp we just receive
                # data, addr = serverSocket.recvfrom(1024)
                # data_new = data.decode()

                # # Split the HTTP request sent into words
                # group_requests = data_new.split(" ")
                # print(group_requests)
                

                else :
                    continue
    
if __name__ == '__main__':
    print(server_folder)
    port = randint(2000,50000)
    print(f"port for server is {port}")
    fileTransferProtocol(port)

# File Transfer Service: Network Application Development

## Overview

This repository contains a File Transfer Service network application that enables file transfer between a client and a server using both TCP and UDP communication protocols. The application supports multiple operations such as uploading (`put`), downloading (`get`), renaming files (`change`), summarizing file contents (`summary`), and retrieving help information (`help`). The client can select between TCP and UDP for communication with the server, and the server will handle the incoming requests based on the selected protocol.

## Features

- **TCP/UDP Support:** The client can choose to communicate with the server using either TCP or UDP.
- **File Transfer:** Allows the client to upload (`put`) and download (`get`) files to/from the server.
- **File Renaming:** The client can rename files on the server using the `change` command.
- **File Summary:** The client can request a summary of numerical data in a file (max, min, and average values) using the `summary` command.
- **Help Functionality:** Provides help instructions and available commands for the client using the `help` command.
- **Error Handling:** Handles various error scenarios, including invalid commands and file not found cases.
- **End of File (EOF) Handling:** Correctly identifies and processes the EOF marker when transferring files.

## How It Works

### Client

The client allows users to connect to the server via either TCP or UDP. Once connected, the user can execute various commands such as uploading, downloading, renaming, summarizing files, and requesting help. The client will handle sending requests and receiving responses from the server.

**Supported Commands:**
- `put <filename>`: Uploads the specified file to the server.
- `get <filename>`: Downloads the specified file from the server.
- `change <old_filename> <new_filename>`: Renames a file on the server.
- `summary <filename>`: Requests a summary (max, min, and average) of the contents of the file.
- `help`: Retrieves the list of available commands from the server.
- `bye`: Terminates the client-server connection.

### Server

The server listens for incoming client connections over either TCP or UDP, depending on the chosen protocol. It processes incoming requests based on the opcode provided by the client and performs the corresponding file operations. The server handles file transfer, renaming, and summary generation as requested by the client. Additionally, it sends help information and error responses when needed.

**Server Operations:**
- Handles `put`, `get`, `change`, `summary`, and `help` commands from the client.
- Sends appropriate responses for successful or failed operations.
- Processes file transfer with EOF handling to indicate the end of the file.
- Maintains separate behavior for TCP and UDP protocols.

### File Operations

- **File Transfer (Put/Get):** Files can be uploaded or downloaded between the client and server. The EOF marker is used to denote the end of the file during transmission.
- **File Renaming:** The `change` command allows renaming files on the server, with error handling in case the file does not exist or the renaming operation fails.
- **File Summary:** If a file contains numerical data, the `summary` command calculates and returns the maximum, minimum, and average of the numbers in the file.

### Error Handling

- **File Not Found:** If a file requested by the client does not exist on the server, the server responds with an appropriate error code.
- **Unknown Commands:** Invalid or unknown commands sent by the client result in an error response from the server.
- **Invalid Filename Length:** Filenames exceeding 31 characters are not allowed and will cause an error.

## Usage

1. Start the server by running the `server.py` script. The server will bind to a random port between 2000 and 50000. The server will then wait for client connections.
2. In a separate terminal, run the `client.py` script. The client will prompt you to select either TCP or UDP as the communication protocol and connect to the server using the provided IP and port.
3. Once connected, the client can issue various commands (`put`, `get`, `change`, `summary`, `help`) to interact with the server.

### Example

```bash
myftp> put example.txt
transferring file
 File was downloaded successfully

myftp> get example.txt
waiting for server response
get request was successful
file name is example.txt
Saving file to: /path/to/client/folder/example.txt

myftp> change example.txt new_example.txt
example.txt has been changed into new_example.txt.

myftp> summary new_example.txt
Summary request for new_example.txt was successful.
file name is summary_new_example.txt
Saving file to: /path/to/client/folder/summary_new_example.txt

myftp> bye
client terminated session
```

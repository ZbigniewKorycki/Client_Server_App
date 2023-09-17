import socket
import commands
import json

HOST = '192.168.0.163'
PORT = 61033

BUFFER = 1024

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(2)

while True:
    client_socket, address = server_socket.accept()

    print("Connect with the client.")

    command = client_socket.recv(BUFFER).decode("utf8")

    if command == 'help':
        output = json.dumps(commands.commands_description, indent=4)
        print(output)
        msg = f"Return message for command: {command}".encode("utf8")
        client_socket.send(msg)

    if command == 'close':
        msg = f"Return message for command: {command}".encode("utf8")
        client_socket.send(msg)
        server_socket.close()
        print("soc closed")
        break


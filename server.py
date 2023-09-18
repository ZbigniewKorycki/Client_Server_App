import socket
import commands
import json
from server_config import Server

server = Server('192.168.0.163', 61033, 1024)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((server.host, server.port))
server_socket.listen(2)
client_socket, address = server_socket.accept()
print("Connection with the client.")

while True:

    command = client_socket.recv(server.buffer).decode("utf8")

    commands_list = ['help', 'info', 'uptime', 'stop']

    if command in commands_list:
        if command == 'help':
            output = json.dumps(commands.commands_description, indent=4)
            msg = output.encode("utf8")
            client_socket.send(msg)

        elif command == 'stop':
            server_socket.close()
            break

        elif command == 'uptime':
            output = json.dumps({"server_uptime": str(server.get_server_uptime())}, indent=4)
            msg = output.encode("utf8")
            client_socket.send(msg)

        elif command == 'info':
            output = json.dumps(server.versions, indent=4)
            msg = output.encode("utf8")
            client_socket.send(msg)
    else:
        message = ("Incorrect command - try again or type "
                   "'help' for list of available commands.")
        output = json.dumps(message, indent=4)
        msg = output.encode("utf8")
        client_socket.send(msg)

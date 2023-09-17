import socket
import commands
import json
from servers import Servers

server = Servers('192.168.0.163', 61033, 1024)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((server.host, server.port))
server_socket.listen(2)

while True:
    client_socket, address = server_socket.accept()

    print("Connect with the client.")

    command = client_socket.recv(server.buffer).decode("utf8")

    if command == 'help':
        output = json.dumps(commands.command_help(), indent=4)
        msg = output.encode("utf8")
        client_socket.send(msg)

    if command == 'close':
        server_socket.close()
        break

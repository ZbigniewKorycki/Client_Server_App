from client_config import Client

import socket

client = Client('192.168.0.163', 61033, 1024)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((client.host, client.port))

while True:
    command = input('Command: ').encode("utf8")
    if command.decode("utf8") == 'stop':
        client_socket.send(command)
        client_socket.close()
        break
    else:
        client_socket.send(command)
        print(client_socket.recv(client.buffer).decode("utf8"))


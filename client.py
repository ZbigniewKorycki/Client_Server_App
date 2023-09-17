from clients import Clients

import socket

client = Clients('192.168.0.163', 61033, 1024)

while True:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((client.host, client.port))
    command = input('Command: ').encode("utf8")
    if command.decode("utf8") == 'close':
        client_socket.send(command)
        print(client_socket.recv(client.buffer).decode("utf8"))
        client_socket.close()
        break
    else:
        client_socket.send(command)
        print(client_socket.recv(client.buffer).decode("utf8"))


import socket

HOST = '192.168.0.163'
PORT = 61033

BUFFER = 1024

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

command = input('Command: ').encode("utf8")

client_socket.send(command)

print(client_socket.recv(BUFFER).decode("utf8"))
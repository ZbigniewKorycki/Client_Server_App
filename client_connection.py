from client_logic import Client
import socket


def verify_input(input_description):
    while True:
        try:
            request_input = input(input_description).encode("utf8")
            if request_input:
                return request_input
        except AttributeError:
            continue


client = Client('192.168.0.163', 61033, 1024)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((client.host, client.port))


run_client = True
while run_client:
    command = verify_input("Command: ")
    if command.decode("utf8") == 'login':
        client_socket.send(command)
        username = verify_input('Input username: ')
        password = verify_input('Input password: ')
        client_socket.send(username)
        client_socket.send(password)
        if client_socket.recv(client.buffer).decode("utf8") == '"Correct_login_and_password"':
            print(client_socket.recv(client.buffer).decode("utf8"))
            available_commands_list = client_socket.recv(client.buffer).decode("utf8")
            print(available_commands_list)
            while True:
                command = verify_input("Command: ")
                if command.decode("utf8") == 'stop' and command.decode("utf8") in available_commands_list:
                    client_socket.send(command)
                    client_socket.close()
                    run_client = False
                    break
                elif command.decode("utf8") == 'send' and command.decode("utf8") in available_commands_list:
                    client_socket.send(command)
                    recipient = verify_input("Message recipient: ")
                    client_socket.send(recipient)
                    message = verify_input('Message: ')
                    client_socket.send(message)
                    print(client_socket.recv(client.buffer).decode("utf8"))

                elif command.decode("utf8") == 'send-to-all' and command.decode("utf8") in available_commands_list:
                    client_socket.send(command)
                    message = verify_input('Message to all users: ')
                    client_socket.send(message)
                    print(client_socket.recv(client.buffer).decode("utf8"))

                elif command.decode("utf8") == 'add-user' and command.decode("utf8") in available_commands_list:
                    client_socket.send(command)
                    username = verify_input('Input username: ')
                    client_socket.send(username)
                    print(client_socket.recv(client.buffer).decode("utf8"))

                elif command.decode("utf8") == 'logout' and command.decode("utf8") in available_commands_list:
                    client_socket.send(command)
                    print(client_socket.recv(client.buffer).decode("utf8"))
                    break

                else:
                    client_socket.send(command)
                    print(client_socket.recv(client.buffer).decode("utf8"))

        else:
            print(client_socket.recv(client.buffer).decode("utf8"))

    elif command.decode("utf8") == 'add-admin':
        client_socket.send(command)
        admin_name = verify_input('Input admin name: ')
        client_socket.send(admin_name)
        print(client_socket.recv(client.buffer).decode("utf8"))

    else:
        client_socket.send(command)
        print(client_socket.recv(client.buffer).decode("utf8"))


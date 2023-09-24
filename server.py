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

    commands_list = ['help', 'info', 'uptime', 'stop', 'add-user', 'login', 'add-admin']

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

        elif command == 'add-user':
            username = client_socket.recv(server.buffer).decode("utf8")
            output = json.dumps(server.add_user(username), indent=4)
            msg = output.encode("utf8")
            client_socket.send(msg)

        elif command == 'add-admin':
            admin_name = client_socket.recv(server.buffer).decode("utf8")
            output = json.dumps(server.add_user(admin_name, privilege="admin"), indent=4)
            msg = output.encode("utf8")
            client_socket.send(msg)

        elif command == 'login':
            username = client_socket.recv(server.buffer).decode("utf8")
            password = client_socket.recv(server.buffer).decode("utf8")
            if server.login_into_system(username, password):
                current_user = server.get_user_if_exists(username)
                logged_user, inbox_info, commands_info = server.user_base_interface(current_user)
                info_after_login = {
                    "logged_user": logged_user,
                    "inbox_info": inbox_info,
                    "commands_info": commands_info
                }

                output = json.dumps(info_after_login, indent=4)
                msg = output.encode("utf8")
                client_socket.send(msg)
                while True:
                    command = client_socket.recv(server.buffer).decode("utf8")
                    commands_list_user = ['logout', 'send', 'inbox']

                    if command in commands_list_user:
                        if command == 'logout':
                            output = json.dumps(f"User {username} logged out.", indent=4)
                            msg = output.encode("utf8")
                            client_socket.send(msg)
                            break

                        elif command == 'send':
                            recipient = client_socket.recv(server.buffer).decode("utf8")
                            message = client_socket.recv(server.buffer).decode("utf8")
                            output = json.dumps(server.send_message(current_user, recipient, message), indent=4)
                            msg = output.encode("utf8")
                            client_socket.send(msg)

                        elif command == "inbox":
                            output = json.dumps(server.show_inbox(current_user), indent=4)
                            msg = output.encode("utf8")
                            client_socket.send(msg)

                    else:
                        message = f"Incorrect command, available commands: {commands_list_user}"
                        output = json.dumps(message, indent=4)
                        msg = output.encode("utf8")
                        client_socket.send(msg)

            else:
                output = json.dumps("Incorrect login or/and password", indent=4)
                msg = output.encode("utf8")
                client_socket.send(msg)


    else:
        message = ("Incorrect command - try again or type "
                   "'help' for list of available commands.")
        output = json.dumps(message, indent=4)
        msg = output.encode("utf8")
        client_socket.send(msg)

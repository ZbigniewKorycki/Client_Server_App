import socket
import commands
import json
from server_logic import Server

server = Server('192.168.0.163', 61033)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((server.host, server.port))
server_socket.listen(2)
client_socket, address = server_socket.accept()
print("Connection with the client.")

run_server = True
while run_server:

    command = client_socket.recv(server.buffer).decode("utf8")

    if command == 'login':
        username = client_socket.recv(server.buffer).decode("utf8")
        password = client_socket.recv(server.buffer).decode("utf8")
        if server.login_into_system(username, password):
            inbox_info = server.user_base_interface(username)

            output = json.dumps("Correct_login_and_password", indent=4, default=str)
            msg = output.encode("utf8")
            client_socket.send(msg)

            info_after_login = {
                "logged_user": username,
                "inbox_info": inbox_info,
            }
            output = json.dumps(info_after_login, indent=4, default=str)
            msg = output.encode("utf8")
            client_socket.send(msg)

            if server.check_if_user_has_admin_privileges(username):
                available_commands = ['send', 'send-to-all', 'inbox', 'add-user', 'help', 'info', 'uptime', 'logout',
                                      'stop', 'add-server-version', 'delete-user','change-privileges', 'delete-server-version']
            else:
                available_commands = ['send', 'inbox', 'logout']
            output = json.dumps(available_commands, indent=4)
            msg = output.encode("utf8")
            client_socket.send(msg)

            while True:
                command = client_socket.recv(server.buffer).decode("utf8")

                if command == 'logout':
                    output = json.dumps(f"User {username} logged out.", indent=4)
                    msg = output.encode("utf8")
                    client_socket.send(msg)
                    break

                elif command == "inbox":
                    output = json.dumps(server.show_inbox(username), indent=4, default=str)
                    msg = output.encode("utf8")
                    client_socket.send(msg)

                elif command == 'send':
                    recipient = client_socket.recv(server.buffer).decode("utf8")
                    message = client_socket.recv(server.buffer).decode("utf8")
                    output = json.dumps(server.send_message(username, recipient, message), indent=4, default=str)
                    msg = output.encode("utf8")
                    client_socket.send(msg)

                elif command == 'help' and server.check_if_user_has_admin_privileges(username):
                    output = json.dumps(commands.commands_description, indent=4)
                    msg = output.encode("utf8")
                    client_socket.send(msg)

                elif command == 'info' and server.check_if_user_has_admin_privileges(username):
                    output = json.dumps(server.get_server_versions(), indent=4, default=str)
                    msg = output.encode("utf8")
                    client_socket.send(msg)

                elif command == 'uptime' and server.check_if_user_has_admin_privileges(username):
                    output = json.dumps({"server_uptime": str(server.get_server_uptime())}, indent=4, default=str)
                    msg = output.encode("utf8")
                    client_socket.send(msg)

                elif command == 'send-to-all' and server.check_if_user_has_admin_privileges(username):
                    message = client_socket.recv(server.buffer).decode("utf8")
                    output = json.dumps(server.send_message_to_all(username, message), indent=4, default=str)
                    msg = output.encode("utf8")
                    client_socket.send(msg)

                elif command == 'add-user' and server.check_if_user_has_admin_privileges(username):
                    new_username = client_socket.recv(server.buffer).decode("utf8")
                    output = json.dumps(server.add_user(new_username), indent=4)
                    msg = output.encode("utf8")
                    client_socket.send(msg)

                elif command == 'delete-user' and server.check_if_user_has_admin_privileges(username):
                    username_to_delete = client_socket.recv(server.buffer).decode("utf8")
                    output = json.dumps(server.delete_user(username_to_delete), indent=4)
                    msg = output.encode("utf8")
                    client_socket.send(msg)

                elif command == 'change-privileges' and server.check_if_user_has_admin_privileges(username):
                    username_to_change_privilege = client_socket.recv(server.buffer).decode("utf8")
                    new_privileges = client_socket.recv(server.buffer).decode("utf8")
                    output = json.dumps(server.change_user_privileges(username_to_change_privilege, new_privilegenew_privileges), indent=4)
                    msg = output.encode("utf8")
                    client_socket.send(msg)

                elif command == 'stop' and server.check_if_user_has_admin_privileges(username):
                    server_socket.close()
                    run_server = False
                    break

                elif command == 'add-server-version' and server.check_if_user_has_admin_privileges(username):
                    server_version_number = client_socket.recv(server.buffer).decode("utf8")
                    output = json.dumps(server.add_server_version(server_version_number), indent=4)
                    msg = output.encode("utf8")
                    client_socket.send(msg)

                elif command == 'delete-server-version' and server.check_if_user_has_admin_privileges(username):
                    server_version_number_to_delete = client_socket.recv(server.buffer).decode("utf8")
                    output = json.dumps(server.delete_server_version(server_version_number_to_delete), indent=4)
                    msg = output.encode("utf8")
                    client_socket.send(msg)

                else:
                    message = "Incorrect command or you don't have permission to use it."
                    output = json.dumps(message, indent=4)
                    msg = output.encode("utf8")
                    client_socket.send(msg)

        else:
            output = json.dumps("Incorrect login or/and password", indent=4)
            msg = output.encode("utf8")
            client_socket.send(msg)
            client_socket.send(msg)

    elif command == 'add-admin':
        admin_name = client_socket.recv(server.buffer).decode("utf8")
        output = json.dumps(server.add_user(admin_name, privileges="admin"), indent=4)
        msg = output.encode("utf8")
        client_socket.send(msg)

    else:
        message = "Incorrect command or you don't have permission to use it."
        output = json.dumps(message, indent=4)
        msg = output.encode("utf8")
        client_socket.send(msg)

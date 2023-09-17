import json

commands_description = {
    "uptime": "returns server uptime",
    "info": "returns the version number of the server and the date it was created",
    "help": "returns the list of available commands with a short description",
    "stop": "stops the server and the client simultaneously"
}


def command_help():
    output = json.dumps(commands_description, indent=4)
    print(output)

"""
App

Last Updated: Version 0.0.1
"""

import subprocess


class Command:
    def __init__(self):
        pass

    def execute(self, str_in, managers):
        background = False
        open_new = False
        command = ["open", "-a"]
        if " -g" in str_in:
            background = True
            str_in = str_in.replace(" -g", "")
        if " -n" in str_in:
            open_new = True
            str_in = str_in.replace(" -n", "")
        query = str_in[4:]

        target = query
        command.insert(len(command), target)

        if background:
            command.append('-g')
        if open_new:
            command.append('-n')

        subprocess.call(command)

    def get_template(self, new_cmd_name):
        print("Enter base command and args: ")
        cmd_new = input()

        query_length = len(new_cmd_name)+1

        template = {
            'command': str(cmd_new.split(" ")),
            'query': 'str_in['+str(query_length)+':]',
        }

        return template

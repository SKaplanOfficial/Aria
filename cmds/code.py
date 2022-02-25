"""
Code

Last Updated: March 8, 2021
"""

import subprocess
import webbrowser


class Command:
    def __init__(self, *args, **kwargs):
        pass

    def execute(self, str_in, context):
        command = ['code']
        query = str_in[5:]

        target = query
        command.insert(len(command), target)

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

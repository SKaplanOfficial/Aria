"""
Last

Last Updated: March 14, 2021
"""

import subprocess
import webbrowser


class Command:
    def __init__(self, *args, **kwargs):
        pass

    def execute(self, str_in, context):
        command = ["open", '-a']
        target = context[1]
        
        command.insert(len(command), target)

        subprocess.call(command)

    def get_template(self, new_cmd_name):
        print("Enter base command and args: ")
        cmd_new = input()
        
        print("Enter target code: ")
        new_target = input()

        template = {
            'command': str(cmd_new.split(" ")),
            'target': new_target_code,
        }

        return template

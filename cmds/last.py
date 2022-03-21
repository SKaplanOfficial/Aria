"""
Last

Last Updated: Version 0.0.1
"""

import subprocess


class Command:
    def __init__(self):
        pass

    def execute(self, str_in, managers):
        command = ["open", '-a']

        print("current",managers["context"].current_app)
        print("previous",managers["context"].previous_apps[::-1])
        for app in managers["context"].previous_apps[::-1]:
            if app != managers["context"].current_app or len(managers["context"].previous_apps) == 1:
                command.append(app)
                subprocess.call(command)
                break

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

"""
Terminal

Last Updated: Version 0.0.1
"""

import subprocess

class Command:
    def __init__(self):
        self.aliases = [
            "term",
            "zsh",
        ]

    def execute(self, str_in, managers):
        if " " in str_in:
            command = str_in.split( )[1:]
            completion = subprocess.call(command)
        else:
            print("Please provide a terminal command and its arguments, separated by spaces")

    def get_aliases(self):
        return self.aliases

    def get_template(self, new_cmd_name):
        pass

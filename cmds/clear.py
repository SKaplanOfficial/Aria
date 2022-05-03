"""
Clear

Last Updated: Version 0.0.1
"""

import subprocess

from ariautils.command_utils import Command

class ClearScreen(Command):
    def __init__(self):
        pass

    def execute(self, query = None, origin = None):
        cmd = "clear"
        subprocess.call([cmd])
        print("Cleared.")

    def get_template(self, new_cmd_name):
        template = {
            'cmd': '"'+new_cmd_name+'"',
        }
        return template

command = ClearScreen()
"""
Clear

Last Updated: Version 0.0.1
"""

import subprocess


class Command:
    def __init__(self):
        pass

    def execute(self, str_in, managers):
        cmd = "clear"
        subprocess.call([cmd])
        print("Cleared.")

    def get_template(self, new_cmd_name):
        template = {
            'cmd': '"'+new_cmd_name+'"',
        }
        return template

"""
Clear

Last Updated: March 8, 2021
"""

import subprocess


class Command:
    def __init__(self, *args, **kwargs):
        pass

    def execute(self, str_in, context):
        cmd = "clear"
        subprocess.call([cmd])
        print("Cleared.")

    def get_template(self, new_cmd_name):
        template = {
            'cmd': '"'+new_cmd_name+'"',
        }
        return template

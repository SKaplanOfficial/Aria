"""
Note

Last Updated: February 2, 2022
"""

import subprocess
from datetime import datetime, timedelta


class Command:
    def __init__(self, *args, **kwargs):
        self.aria_path = args[0]
        print("Opening note...")

    def execute(self, str_in, context):
        target = str_in[5:]

        if target == "today":
            now = datetime.now()
            target = now.strftime("%B-%d-%Y")

        if target == "tomorrow":
            tomorrow = datetime.now() + timedelta(days=1)
            target = tomorrow.strftime("%B-%d-%Y")

        path = self.aria_path + "/docs/notes/" + target + ".txt"
        with open(path, 'a') as fp:
            pass
        subprocess.call(["open", "-a", "Textedit", path])

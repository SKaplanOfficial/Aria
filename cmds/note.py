"""
Note

Last Updated: Version 0.0.1
"""

import subprocess
from datetime import datetime, timedelta


class Command:
    def __init__(self):
        self.aliases = ["notepad", "stickynote", "sticky"]

    def execute(self, str_in, managers):
        print("Opening note...")
        target = str_in[5:]

        if target == "today":
            now = datetime.now()
            target = now.strftime("%B-%d-%Y")

        if target == "tomorrow":
            tomorrow = datetime.now() + timedelta(days=1)
            target = tomorrow.strftime("%B-%d-%Y")

        path = managers["config"].get("aria_path") + "/docs/notes/" + target + ".txt"
        with open(path, 'a') as fp:
            pass
        subprocess.call(["open", "-a", "Textedit", path])

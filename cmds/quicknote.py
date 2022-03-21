"""
Quicknote

Last Updated: Version 0.0.1
"""

import subprocess


class Command:
    def __init__(self):
        self.aliases = ["qn", "quickn"]

    def execute(self, str_in, managers):
        print("Opening quicknote file...")
        path = managers["config"].get("aria_path") + "/docs/notes/"
        with open(path+'quicknote.txt', 'a') as fp:
            pass
        subprocess.call(["open", "-a", "Textedit", path+'quicknote.txt'])

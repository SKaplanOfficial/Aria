"""
Quicknote

Last Updated: February 2, 2022
"""

import subprocess


class Command:
    def __init__(self, *args, **kwargs):
        self.aria_path = args[0]
        print("Opening quicknote file...")

    def execute(self, str_in, context):
        path = self.aria_path + "/docs/notes/"
        with open(path+'quicknote.txt', 'a') as fp:
            pass
        subprocess.call(["open", "-a", "Textedit", path+'quicknote.txt'])

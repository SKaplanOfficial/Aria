"""
Document Manager

Last Updated: March 8, 2021
"""

import subprocess
import webbrowser
import os


class DocumentManager:
    def __init__(self, *args, **kwargs):
        self.aria_path = args[0]

    def get_file_content(self, filename):
        with open(self.aria_path+"/cmds/"+filename, "r") as target_file:
            content = target_file.read()
        return content

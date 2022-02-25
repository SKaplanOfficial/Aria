"""
Command Manager

Last Updated: March 8, 2021
"""

import importlib
import subprocess
import webbrowser
import os
import re
from DocumentManager import DocumentManager


class CommandManager:
    def __init__(self, *args, **kwargs):
        self.aria_path = args[0]
        self.DM = DocumentManager(self.aria_path)

    def add_to_cmd():
        pass

    def cmd_from_template(self, str_in):
        # Determine relevant command names
        if str_in.startswith("make command "):
            new_cmd_name = str_in[13:str_in.index("from")-1]
            old_cmd_name = str_in[str_in.index("from")+5:]
        elif str_in.startswith("make"):
            new_cmd_name = str_in[5:str_in.index("from")-1]
            old_cmd_name = str_in[str_in.index("from command")+13:]
        else:
            # Some error occurred
            print("Unable to create command.")
            return

        # Check if new command already exists
        if self.get_command_filename(new_cmd_name):
            print("Target command already exists.")
            return

        # Get old cmd file path
        old_filename = self.get_command_filename(old_cmd_name)
        if (old_filename == "" or old_filename is None):
            print("Reference command does not exist.")
            return

        # Get old cmd file content
        old_file_content = self.DM.get_file_content(old_filename)

        # Modify code
        new_file_content = old_file_content.replace(old_cmd_name, new_cmd_name)
        new_file_content = new_file_content.replace(
            old_cmd_name.title(), new_cmd_name.title())

        try:
            cmd_module = importlib.import_module("cmds."+old_cmd_name)
            old_cmd = cmd_module.Command()
            template = old_cmd.get_template(new_cmd_name)

            for key in template:
                new_file_content = re.sub(
                    key+" = .*"+"\n", key+" = "+template[key]+"\n", new_file_content)

        except Exception as e:
            print("Unable to access reference command template:\n"+str(e))

        # Create new file
        with open(self.aria_path+"/cmds/"+new_cmd_name+".py", "w") as new_file:
            new_file.write(new_file_content)

        print("Command " + new_cmd_name + " created.")

    def del_cmd():
        pass

    def merge_commands():
        pass

    def get_command_filename(self, cmd_name):
        name_condensed = cmd_name.replace(" ", "")

        files = os.listdir(path=self.aria_path+"/cmds")
        for f in files:
            if f.startswith(name_condensed):
                return f

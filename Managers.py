"""
A collection of manager classes for various aspects of Aria.

Last Updated: Version 0.0.1

Typical usage example:
    ConfigManager = ConfigManager()
    DocumentManager = DocumentManager()
    TrackingManager = TrackingManager()
    CommandManager = CommandManager()
    ContextManager = ContextManager()

    managers = {
        "config": ConfigManager,
        "docs": DocumentManager,
        "tracking": TrackingManager,
        "command": CommandManager,
        "context": ContextManager
    }

    print("Hello, ", managers["config"].get("user_name"))
"""

import subprocess

from pkg_resources import require
import applescript
import termios
import importlib
import json
import os
import re
import os
import sys
import tty
import threading
from datetime import datetime
from cmds import *
from CommandTypes import Command
from tracking_tools.TrackingManager import TrackingManager


from nltk.corpus import wordnet
from contextlib import redirect_stdout
import autocomplete
import speech_recognition as sr
import markovify

managers = {}

class Manager:
    """
    An abstract class for Aria's manager objects.
    """
    def __init__(self):
        pass


class ConfigManager(Manager):
    """
    A settings/configuration manager for Aria. Only one ConfigManager should be active at a time.
    """
    def __init__(self):
        """
        Constructs a ConfigManager object.
        """
        self.cfg_file_name = "aria_config.json"
        self.cfg_version = "0.0.1"
        self.config = {}
        self.runtime_config = {}

    def create_global_config(self, initial_config):
        """
        Creates aria_config.json, overwriting if it already exists in the same location. Updates config dictionary to supplied initial config.

        Paramters:
            initial_config: dict - A dictionary of configuration settings.
        """
        with open(self.cfg_file_name, 'w') as cfg_file:
            json.dump(initial_config, cfg_file, indent = 4, sort_keys = True)

        self.config = initial_config

    def load_global_config(self):
        """
        Attempts to load configuration settings from aria_config.json. Saves loaded config to config dictionary if successful.

        Returns:
            boolean - True if aria_config.json exists and is read successfully, False otherwise.
        """
        loaded_config = {}
        try:
            with open(self.cfg_file_name, 'r') as cfg_file:
                loaded_config = json.load(cfg_file)
        except:
            return False

        if loaded_config["cfg_version"] != self.cfg_version:
            print("Your configuration file uses a different format version than expected by this version of Aria.")
            print("Expected version:", self.cfg_version)
            print("File version:", loaded_config["cfg_version"])
            print("It might be okay to proceed. Press Y to do so, or press any other key to exit.")
            input_str = input()

            if input_str != "Y" and input_str != "y":
                exit()

        self.config = loaded_config
        return True

    def save_global_config(self):
        """
        Attempts to saves the config dictionary to aria_config.json.

        Returns:
            boolean - True if aria_config.json is successfully written to, False otherwise.
        """
        try:
            with open(self.cfg_file_name, 'w') as cfg_file:
                json.dump(self.config, cfg_file, indent = 4, sort_keys = True)
        except:
            return False
        return True

    def get_config(self):
        """Returns the entire config dictionary, if a config is loaded, otherwise runs the initial setup process."""
        if not self.load_global_config():
            self.initial_setup()
        return self.config

    def get(self, key):
        """
        Returns the value associated with the specified key in the config dictionary.
        
        Parameters:
            key : str - The key to retrieve the associated value of.

        Returns:
            Object - The json-serializable object stored at the target key.
        """
        return self.config[key]

    def set(self, key, value):
        """
        Sets the key in the config dictionary to the specified key and updates aria_config.json.
        
        Paramters:
            key : str - The key to set the value of.
            value : Object - A json-serializable value to store at the target key.
        """
        self.config[key] = value
        self.save_global_config()

    def initial_setup(self):
        """
        Walks users through an initial configuration of Aria, allowing use of a default configuration.

        Notes:
            - 
        """
        default_config = {
            "cfg_version": self.cfg_version,
            "aria_path": os.getcwd(),
            "user_name": "User",
            "plugins" : {},
            "dev_mode": False,
        }

        print("Hello!\nThank you for using Aria. Press any key to answer a few configuration questions, or press X to configure settings later.")
        input_str = input()

        if input_str != "X" and input_str != "x":
            aria_path = os.getcwd()
            print("\n1. Please confirm the directory that Aria.py is located:", aria_path)
            print("Is this correct? Press Y for yes, otherwise please enter the correct directory path.")
            input_str = input()
            if input_str != "Y" and input_str != "y":
                aria_path = input_str

            print("\n2. Please tell Aria know a little about you.")
            print("What is your name?")
            name = input()

            print("\n3. Aria found the following command plugins:")
            plugins = {}
            files = os.listdir(path=aria_path+"/cmds")
            for f in files:
                if "__" not in f and ".pyc" not in f and ".DS_Store" not in f:
                    plugin_name = f.replace(".py", "")
                    print("\t", plugin_name)
                    plugins[plugin_name] = {
                        "enabled" : True
                    }
            print("Type Y to enable all (dangerous), or type a list of plugins to enable, separated by commas.")
            input_str = input()
            if input_str == "Y" or input_str == "y":
                plugins_to_enable = input_str.split(",")
                for plugin_name in plugins_to_enable:
                    plugins[plugin_name.replace(" ", "")] = {
                        "enabled" : True
                    }

            config = {
                "cfg_version": self.cfg_version,
                "aria_path": aria_path,
                "user_name": name,
                "plugins": plugins,
                "dev_mode": False
            }

            print("Creating custom config file...")
            self.create_global_config(config)
        else:
            print("Creating default config file...")
            self.create_global_config(default_config)

    def set_runtime_config(self, cfg):
        """Stores the runtime config set via commandline arguments."""
        self.runtime_config = cfg


class DocumentManager(Manager):
    """
    A document/file IO manager for Aria. Only one DocumentManager should be active at a time.
    """
    def __init__(self):
        """ Constructs a DocumentManager object. """
        self.current_file = []
        self.previous_files = []
        self.file_history_size = 10

    def set_current_file(self, new_file_path):
        """ Sets the current file. """
        self.current_file = new_file_path

        if self.previous_files == [] or self.current_file != self.previous_files[-1]:
            self.previous_files.append(self.current_file)

        if len(self.previous_files) > self.file_history_size:
            self.previous_files.pop(0)

    def open_file(self, filepath, mode = "w"):
        """ Opens a file. For writing by default. """
        self.set_current_file(filepath)
        return open(filepath, mode)

    def close_file(self, file):
        """ Closes a supplied file object. """
        file.close()

    def touch(self, filepath):
        self.write(filepath, "", "a")

    def get_file_content(self, filepath):
        """
        Returns the content within a file as a single string.

        Parameters:
            filepath: str - The full path of the file to read content from.

        Returns:
            content : str - The content of the file.
        """
        self.set_current_file(filepath)
        with open(filepath, "r") as target_file:
            content = target_file.read()
        return content

    def write(self, filepath, string, mode = "w"):
        """ Writes the provided string to a file. Write mode by default. """
        self.set_current_file(filepath)
        with open(filepath, mode) as target_file:
            if isinstance(string, str):
                target_file.write(string)
            elif isinstance(string, list):
                lines = [s+"\n" for s in string]
                target_file.writelines(lines)

    def prepend(self, filepath, string):
        """ Prepends the provided string to the beginning of a file. """
        self.set_current_file(filepath)
        content = self.get_file_content(filepath)
        new_content = string + content
        self.write(filepath, new_content, "w")

    def insert(self, filepath, string, line_num):
        """ Inserts the provided string to the end of the line at the provided line number in a file. """
        self.set_current_file(filepath)
        lines = self.get_lines(filepath)
        while len(lines) < line_num+2:
            lines.append("")
        lines[line_num] = lines[line_num] + string
        self.write(filepath, lines, "w")

    def append(self, filepath, string):
        """ Appends the provided string to the end of a file. """
        self.set_current_file(filepath)
        self.write(filepath, string, "a")

    def replace_line(self, filepath, string, line_num):
        """ Replaces the line at line num with the target string. """
        self.set_current_file(filepath)
        lines = self.get_lines(filepath)
        if line_num > len(lines):
            print("There aren't enough lines in the target file to make that replacement.")
            return
        lines[line_num] = string
        self.write(filepath, lines, "w")

    def get_lines(self, filepath):
        """ Returns lines as list. """
        self.set_current_file(filepath)
        return self.get_file_content(filepath).split("\n")

    def get_last_line(self, filepath):
        """ Returns last line of document as string. """
        self.set_current_file(filepath)
        return self.get_lines(filepath)[-1]

    def get_last_filled_line(self, filepath):
        """ Returns the last populated line of a document as a string. """
        self.set_current_file(filepath)
        lines = self.get_lines(filepath)
        for line in lines[::-1]:
            if line != "":
                return line

    def has_str(self, filepath, string, case_sensitive = False):
        """ Returns true if the target str occurs anywhere in the file. """
        self.set_current_file(filepath)
        content = self.get_file_content(filepath)

        if case_sensitive == False:
            return string.lower() in content.lower()
        return string in content

    def has_strs(self, filepath, *args):
        """ Check if all target strings occur anywhere in the file. """
        self.set_current_file(filepath)
        found_all = True
        for arg in args:
            if isinstance(arg, list):
                for string in arg:
                    if not self.has_str(filepath, string, False):
                        return False
            elif not self.has_str(filepath, arg, False):
                return False
        return True

    def has_line(self, filepath, line):
        """ Returns true if a line in the file is exactly equal to the supplied line. """
        self.set_current_file(filepath)
        lines = self.get_lines(filepath)
        return line in lines

    def find_line(self, filepath, string):
        """ Returns the line number where the target string occurs, -1 otherwise if it can't be found. """
        self.set_current_file(filepath)
        lines = self.get_lines(filepath)
        for index, line in enumerate(lines):
            if string in line:
                return index
        return -1

    def find_str(self, filepath, string):
        """ Returns the range of lines across which the target string occurs, -1 otherwise. """
        self.set_current_file(filepath)
        line_num = self.find_line(filepath, string)
        if line_num > -1:
            # String occurs in a single line; return corresponding line number
            return (line_num, line_num)

        lines = self.get_lines(filepath)
        parts = string.split()

        start_substrings = []
        end_substrings = []
        for index in range(0, len(parts)):
            start_substring = " ".join(parts[0:index+1])
            end_substring = " ".join(parts[-index:])
            start_substrings.append(start_substring)
            end_substrings.insert(0, end_substring)

        start_line = -1
        end_line = -1
        for index, line in enumerate(lines):
            for substring in start_substrings:
                if line.endswith(substring):
                    start_line = index
                else:
                    break

            for substring in end_substrings:
                if line.startswith(substring):
                    end_line = index
                else:
                    break
        return (start_line, end_line)

    def exists(self, filepath):
        return os.path.exists(filepath)

    def is_empty(self, filepath):
        return os.stat(filepath).st_size == 0


class CommandManager(Manager):
    """
    A manager for Aria command modules. Only one CommandManager should be active at a time.
    """
    def __init__(self):
        """ Constructs a CommandManager object. """
        self.plugins = dict()
        self.invocations = dict()
        self.handlers = dict()
        self.handler_checkers = dict()

        self.requirements = dict()

        Command.managers = managers.copy()

    def get_all_commands(self):
        """
        Loads all command modules enabled in aria_config.json.

        Returns:
            None
        """
        aria_path = managers["config"].get("aria_path")
        files = os.listdir(path=aria_path+"/cmds")
        for f in files:
            if "__" not in f and ".pyc" not in f and ".DS_Store" not in f:
                cmd_name = f.replace(".py", "")
                if cmd_name in managers["config"].get("plugins").keys():
                    if managers["config"].get("plugins")[cmd_name]:
                        # Add module command object
                        module = importlib.import_module("cmds."+cmd_name)
                        command_obj = getattr(module, "command", None)

                        if command_obj == None:
                            print("Error: Couldn't find command definition in " + cmd_name + ".py. Proceed with caution.")
                            continue
                        self.plugins[cmd_name] = module.command

                        # TODO: Use IDs for all entries, not as a secondary bandaid
                        self.plugins[module.command.info["id"]] = module.command

                        self.check_command_structure(cmd_name, self.plugins[cmd_name])

                        # Add invocation methods
                        self.invocations[cmd_name] = self.plugins[cmd_name].invocation

                        # Add handlers
                        self.handler_checkers[cmd_name] = self.plugins[cmd_name].handler_checker
                        self.handlers[cmd_name] = self.plugins[cmd_name].handler

                        # Add requirements
                        if "requirements" in self.plugins[cmd_name].info:
                            self.requirements.update(self.plugins[cmd_name].info["requirements"])

        for requirement in self.requirements:
            found = False
            for plugin in self.plugins:
                if self.plugins[plugin].info["id"] == requirement:
                    if self.plugins[plugin].info["version"] == self.requirements[requirement]:
                        found = True
            
            if not found:
                print("Warning: Requirement not satisfied:")
                print("  Expected: " + requirement + " @" + self.requirements[requirement])
                print("  Found: " + requirement + " @" + self.plugins[plugin].info["version"] + " instead. Proceed with caution.")
                            
        print("Loaded", len(self.plugins), "plugins.")

    def check_command_structure(self, cmd_name, command):
        """
        Checks the metadata and method definitions of a command plugin for required and recommended attributes.

        Parameters:
            cmd_name (str) - The name of the command (currently the filename).
            command (Command) - The Command object exported by the plugin module.

        Returns:
            None
        """
        required_info_keys = ["title", "id", "version", "description"]
        recommended_info_keys = ["repository", "requirements", "purposes", "targets", "example_usage"]

        required_methods = ["execute", "help"]
        recommended_methods = ["get_query_type", "handler_checker", "handler"]

        for key in required_info_keys:
            if key not in command.info:
                print("Error: Plugin '" + cmd_name + "' does not define the required '" + key + "' key. Proceed with caution.")
        
        for key in recommended_info_keys:
            if key not in command.info and (managers["config"].get("dev_mode") or managers["config"].runtime_config["debug"]):
                print("Warning: Plugin '" + cmd_name + "' does not define the recommended '" + key + "' key.")

        for method in required_methods:
            method_def = getattr(command, method, None)
            if method_def == None:
                print("Error: Plugin '" + cmd_name + "' does not define the required '" + method + "' method. Proceed with caution.")

        invocation_def = getattr(command, "invocation", None)
        if invocation_def == None:
            for method in recommended_methods:
                method_def = getattr(command, method, None)
                if method_def == None and (managers["config"].get("dev_mode") or managers["config"].runtime_config["debug"]):
                    print("Warning: Plugin '" + cmd_name + "' does define neither an invocation method nor a '" + method + "' method. At least one should be defined.")

    def cmd_from_template(self, str_in):
        """
        Creates a new command module using the template method of another command.

        Parameters:
            str_in: str - The full string that initiated this command.

        Notes:
            - The CommandManager should not be handling parsing of str_in. Check this ASAP. Use a new_command and target_command parameter instead.
        """
        aria_path = managers["config"].get("aria_path")

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
        if self.get_command_name(new_cmd_name):
            print("Target command already exists.")
            return

        # Get old cmd file path
        old_filename = self.get_command_name(old_cmd_name) + ".py"
        if (old_filename == "" or old_filename is None):
            print("Reference command does not exist.")
            return

        # Get old cmd file content
        old_file_content = managers["docs"].get_file_content(aria_path+"/cmds/"+old_filename)

        # Modify code
        new_file_content = old_file_content.replace(old_cmd_name + " ", new_cmd_name)
        new_file_content = new_file_content.replace(
            old_cmd_name.title() + " ", new_cmd_name.title())

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
        with open(aria_path+"/cmds/"+new_cmd_name+".py", "w") as new_file:
            new_file.write(new_file_content)

        print("Command " + new_cmd_name + " created.")

    def create_shortcut(self, cmd_str, cmd_name):
        """
        Removes a command plugin from the plugins dictionary and disables it in aria_config.json.

        Arguments:
            cmd_str {String} -- The full command to be saved as a shortcut, including arguments.
            cmd_name {String} -- The name of the command plugin to be saved as a shortcut; the default name of the shotcut.

        Returns:
            None
        """
        aria_path = managers["config"].get("aria_path")
        script = f"""#! /bin/zsh
        cd {aria_path}
        python Aria.py --cmd "{cmd_str}" --close
        exit
        """

        print("Where do you want the shortcut?", end="\n->")
        folder_path = input()

        print("What do you want the shorcut to be named? Leave blank to name it '" + cmd_name + ".'", end="\n->")
        name = input()
        if name == "":
            name = cmd_name

        file_path = folder_path + "/" + name
        if folder_path.endswith("/"):
            file_path = folder_path + name

        with open(file_path, 'w') as new_file:
            new_file.write(script)

        mode = os.stat(file_path).st_mode
        mode |= (mode & 0o444) >> 2    # copy R bits to X
        os.chmod(file_path, mode)
        print("Created shortcut '" + name + ".'")

    def get_command_name(self, cmd_name):
        """
        Returns the name of the file associated with a command.

        Arguments:
            cmd_name {String} -- The name of the target command.

        Returns:
            String -- the name of the file (not including .py extension)
        """
        name_condensed = cmd_name.replace(" ", "")

        files = os.listdir(path=managers["config"].get("aria_path")+"/cmds")
        for f in files:
            if f.startswith(name_condensed):
                return f[:-3]

    def get_candidate_command_names(self, input_str):
        """
        Returns a list of file where the input string is a substring of the filename.

        Arguments:
            input_str {String} -- A substring of the target command.

        Returns:
            [String] -- An array of filenames (not including .py extension)
        """
        filenames = []
        name_condensed = input_str.replace(" ", "")

        files = os.listdir(path=managers["config"].get("aria_path")+"/cmds")
        for f in files:
            if f.startswith(name_condensed):
                filenames.append(f[:-3])
        return filenames

    def enable_command_plugin(self, cmd_name):
        """Add a command plugin to the plugins dictionary and enables it in aria_config.json.

        Arguments:
            cmd_name {String} -- The name of the command plugin to be enabled.

        Returns:
            boolean -- True if a plugin is successfully enabled, False if the plugin is already enabled.
        """
        if cmd_name in managers["config"].get("plugins"):
            if managers["config"].get("plugins")[cmd_name]["enabled"] == True:
                print(cmd_name, "is already enabled.")
                return False
            else:
                managers["config"].get("plugins")[cmd_name]["enabled"] = True
        else:
            managers["config"].get("plugins")[cmd_name] = {
                "enabled": True
            }
        managers["config"].save_global_config()
        module = importlib.import_module("cmds."+cmd_name)
        aria_path = managers["config"].get("aria_path")
        self.plugins[cmd_name] = module.Command()

        print(cmd_name, "has been enabled.")
        return True

    def disable_command_plugin(self, cmd_name):
        """
        Removes a command plugin from the plugins dictionary and disables it in aria_config.json.

        Arguments:
            cmd_name {String} -- The name of the command plugin to be disabled.

        Returns:
            boolean -- True if a plugin is successfully disabled, False if the plugin is already disabled.
        """
        if cmd_name in managers["config"].get("plugins"):
            if managers["config"].get("plugins")[cmd_name]["enabled"] == False:
                print(cmd_name, "is already disabled.")
                return False
            else:
                managers["config"].get("plugins")[cmd_name]["enabled"] = False
        else:
            managers["config"].get("plugins")[cmd_name] = {
                "enabled": False
            }
        managers["config"].save_global_config()
        self.plugins.pop(cmd_name)

        print(cmd_name, "has been disabled.")
        return True

    def cmd_method(self, cmd_name, method_name):
        if (cmd_name == "" or cmd_name is None):
            print("'" + method_name + "' rountine not found (Cannot find base command '" + cmd_name + "').")
        else:
            # Attempt to show help information
            plugin = self.plugins[cmd_name]
            method = getattr(plugin, method_name, None)

            if callable(method):
                method()
            else:
                print("'" + method_name + "' rountine not found (Missing '" + method_name + "' method).")


class ContextManager(Manager):
    """
    A manager for Aria's context tracking system. Only one ContextManager should be active at a time.
    """
    def __init__(self):
        """ Constructs a ContextManager object. """
        self.mins_to_checkpoint = 0.05
        self.timer_checkpoint = -1

        item_structure = {
            "start_time" : float,
            "end_time" : float,
            "frequency" : int,
            "targets" : list,
        }

        self.context_tracker = managers["tracking"].init_tracker("context", item_structure)
        self.context_tracker.load_data()
        self.current_context = self.context_tracker.new_item([0, 0, 0, []])
        self.current_app = ""
        self.previous_apps = []
        self.previous_input = ""
        self.looping = True

    def update_context(self):
        """
        Update all context variables as necessary

        Returns:
            None
        """
        currentApp, listOfApps = self.get_context_from_AS()
        listOfApps = sorted(list(set(listOfApps)))

        # Track current app
        if currentApp is not None:
            if currentApp != "/System/Applications/Utilities/Terminal.app":
                self.current_app = currentApp

        if len(self.previous_apps) == 0 or self.current_app != self.previous_apps[-1]:
            if self.current_app != "":
                self.previous_apps.append(self.current_app)

        # Track all running apps
        if len(listOfApps) > 0:
            now = datetime.now()
            current_time = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
            self.current_context = self.context_tracker.new_item([current_time, current_time, 0, listOfApps])

            # Initialize history
            if len(self.context_tracker.items) == 0:
                self.context_tracker.add_item(self.current_context)

            # Compare against previous context
            prev_context_obj = self.context_tracker.items[-1]
            if prev_context_obj != None and listOfApps != prev_context_obj.data["targets"]:
                # Record end time of previous context, open new context
                prev_context_obj.data["end_time"] = current_time
                self.context_tracker.add_item(self.current_context)
                self.checkpoint()
            
            # Current and previous are equal at this point
            elif self.timer_checkpoint == -1 or current_time - self.timer_checkpoint > self.mins_to_checkpoint * 60:
                #print("Saving context history...")
                # Update previous end time (in case context doesn't change for a while)
                if prev_context_obj != None:
                    prev_context_obj.data["end_time"] = current_time

                if self.current_context.data["targets"] == self.context_tracker.items[-1].data["targets"]:
                    self.context_tracker.items[-1].data["frequency"] += 1

                # Export context history to context tracking csv
                self.context_tracker.save_data()
                self.checkpoint()
                self.context_tracker.load_data()

    def get_context_from_AS(self):
        """
        Runs AppleScript to find currently running applications

        Returns:
            [str, [str]] - The filepath of the currently focused application and a list of filepaths of all currently running applications.
        """
        scpt = applescript.AppleScript('''
            property _frontApp : 0
            property _frontAppName : 0
            property _ID : 0
            property _listOfApps : {}
            
            try
                with timeout of 1 second
                    tell application "System Events"
                        set frontApp to first application process whose frontmost is true
                        set frontAppName to name of frontApp
                        set currentApp to file of first application process where name is frontAppName
                        set listOfApps to (file of every process where background only is false)
                    end tell
                end timeout
                return {currentApp, listOfApps}
            on error
                -- blah
            end try
        ''')
        data = scpt.run()
        if data != None:
            return data
        return [self.current_app, self.current_context.data["targets"]]

    def checkpoint(self):
        """
        Updates the timer checkpoint to the current time.
        
        Returns:
            None
        """
        now = datetime.now()
        current_time = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
        self.timer_checkpoint = current_time

    def blank_context(self):
        """
        Closes all non-essential running apps.
        
        Returns:
            None
        """
        apps_to_close = [app for app in self.current_context.data["targets"]]
        for app in apps_to_close:
            if app != "/Applications/Visual Studio Code.app" and app != "/System/Library/CoreServices/Finder.app" and app != "/System/Applications/Utilities/Terminal.app":
                print("Closing " + app + "...")
                command = ["pkill", "-f", app]
                subprocess.call(command)


import pprint
class LanguageManager(Manager):
    """
    A language and wording manager for Aria. Only one LanguageManager should be active at a time.
    """
    def __init__(self):
        """ Constructs a LanguageManager object. """
        self.markov = None
        self.autocomplete = None

        self.loaded_markovs = []

    def load_autocomplete_data(self):
        """Loads autocomplete data from corpora."""
        folder_path = managers["config"].get("aria_path") + "/data/corpora"
        namefile = folder_path + "/names.txt"
        wordfile1 = folder_path + "/corncob_lowercase.txt"
        wordfile2 = folder_path + "/words_alpha.txt"
        skfile = folder_path + "/sk.txt"
        lyricfile = folder_path + "/lyrics.txt"
        moviefile = folder_path + "/movies.txt"

        with redirect_stdout(open(os.devnull, "w")):
            autocomplete.load()

            names = " ".join(line.strip().lower() for line in open(namefile))
            autocomplete.models.train_models(names)

            words1 = " ".join(line.strip().lower() for line in open(wordfile1))
            autocomplete.models.train_models(words1)

            words2 = " ".join(line.strip().lower() for line in open(wordfile2))
            autocomplete.models.train_models(words2)

            sk = " ".join(line.strip().lower() for line in open(skfile))
            autocomplete.models.train_models(sk)

            lyrics = " ".join(line.strip().lower().replace('"', '').replace("'","") for line in open(lyricfile))
            autocomplete.models.train_models(lyrics)

            movies = " ".join(line.strip().lower().replace('"', '').replace("'","") for line in open(moviefile))
            autocomplete.models.train_models(movies)

            autocomplete.load()
        self.autocomplete = True


    def synset(self, word):
        """Returns the first synset the given word."""
        return wordnet.synsets(word)[0]

    def lemmas(self, word):
        """Returns the list of lemmas in the first synset of the given word."""
        return self.synset(word).lemmas()

    def synonyms(self, word):
        """Returns a list of synonyms of the given word."""
        return [str(lemma.name()) for lemma in self.lemmas(word)]


    def antset(self, word):
        """Returns the set of antonyms of the given word."""
        return self.lemmas(word)[0].antonyms()


    def hyperset(self, word):
        """
        Returns the set of hypernyms of the given word.
        Hypernyms are more general terms than the supplied word.
        """
        return self.synset(word).hypernyms()

    def hyperset(self, word):
        """
        Returns a list of hypernyms of the given word.
        Hypernyms are more general terms than the supplied word.
        """
        return [str(lemma.name()) for lemma in self.hyperset(word).lemmas()]


    def hyposet(self, word):
        """
        Returns the set of hyponyms of the given word.
        Hyponyms are more specific terms than the supplied word.
        """
        return self.synset(word).hyponyms()

    def hyposet(self, word):
        """
        Returns a list of hyponyms of the given word.
        Hyponyms are more specific terms than the supplied word.
        """
        return [str(lemma.name()) for lemma in self.hyponyms(word).lemmas()]


    def holoset(self, word):
        """
        Returns the set of holonyms of the given word.
        Holonyms are terms describing concepts that the given word has membership within.
        """
        return self.synset(word).holonyms()

    def holoset(self, word):
        """
        Returns a list of holonyms of the given word.
        Holonyms are terms describing concepts that the given word has membership within.
        """
        return [str(lemma.name()) for lemma in self.holoset(word).lemmas()]


    def define(self, word):
        """Returns the definition of the given word."""
        return self.synset(word).definition()

    def complete_word(self, str):
        """Returns a list of possible completions given the current input string."""
        options = []

        str = str.lower()

        if self.autocomplete == None:
            self.load_autocomplete_data()
        
        try:
            str_parts = str.split(" ")
            if len(str_parts) >= 2:
                options = autocomplete.predict(str_parts[-2], str_parts[-1])
            else:
                options = autocomplete.predict_currword(str_parts[0])
            return [word[0] for word in options]
        except Exception as e:
            pass
        return []

    def complete_line(self, str):
        str = str.strip().lower()
        prediction = ""

        folder_path = managers["config"].get("aria_path") + "/data/corpora"
        if self.markov == None:
            # Load the base markov model -- queries
            query_file = folder_path + "/queries.txt"
            queries = "\n".join(line.strip().lower().replace('"', '').replace("'","") for line in open(query_file))
            self.markov = markovify.NewlineText(queries, retain_original=False, state_size = 40)
        
        try:
            prediction =  self.markov.make_sentence_with_start(str)
        except:
            print("\n")
            managers['output'].sprint("Please wait as I try to improve my predictive model...")
            while prediction == "":
                if "lyrics" not in self.loaded_markovs:
                    lyric_file = folder_path + "/lyrics.txt"
                    lyrics = "\n".join(line.strip().lower().replace('"', '').replace("'","") for line in open(lyric_file))
                    markov_lyrics =  markovify.NewlineText(lyrics, retain_original=False, state_size = 40)
                    self.markov = markovify.combine([ self.markov, markov_lyrics ])
                    self.loaded_markovs.append("lyrics")

                elif "movies" not in self.loaded_markovs:
                    movie_file = folder_path + "/movies.txt"
                    movies = "\n".join(line.strip().lower().replace('"', '').replace("'","") for line in open(movie_file))
                    markov_movies =  markovify.NewlineText(movies, retain_original=False, state_size = 40)
                    self.markov = markovify.combine([ self.markov, markov_movies ])
                    self.loaded_markovs.append("movies")

                else:
                    managers['output'].sprint("Sorry, I do not have a prediction for the rest of that line.")
                    break

                try:
                    prediction =  self.markov.make_sentence_with_start(str)
                except:
                    pass

        return prediction

    # def common_vocab(self):
    #     chat_vocab = text5.vocab()
    #     wsj_vocab = text7.vocab()


class InputManager(Manager):
    """
    A standard input manager for Aria. Only one InputManager should be active at a time.
    """
    def __init__(self):
        """ Constructs a InputManager object. """
        self.cmd_entered = False # True the instant the user presses Enter after typing a command
        self.last_entered = "" # The previously entered input

        self.input_buffer = "" # The current input
        self.saved_buffer = "" # A buffer to hold temporarily overwritten input
        self.autocomplete_buffer = "" # A buffer to hold pre-autocomplete input

        self.autocomplete_counter = -1 # Index of tab autocompletion array
        
        self.last_spoken_query = "" # The last input spoken by the user

        self.listener = sr.Recognizer()
        self.listener.dynamic_energy_threshold = True

        self.waitlist = [] # Inputs waiting to be parsed

    def getch(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(0)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def replace_line(self, new_line):
        print("", end="\x1b[2K")
        print("\r"+ new_line, end="")

    def sound(self):
        """Plays a blip sound to indicate inability to complete target action."""
        sys.stdout.write('\a')
        sys.stdout.flush()

    def pseudo_input(self, str_in):
        self.waitlist.append(str_in)

    def detect_spoken_input(self):
        with sr.Microphone() as source:
            print("Awaiting input...")
            self.listener.adjust_for_ambient_noise(source, duration=2)  
            audio = self.listener.listen(source)

            try:
                self.input_buffer = self.listener.recognize_sphinx(audio)
                print("You said: ", self.input_buffer)
            except sr.UnknownValueError:
                print("Sphinx could not understand audio")
                pass
            except sr.RequestError as e:
                print("Sphinx error; {0}".format(e))
                pass

        if self.input_buffer != "":
            self.cmd_entered = True

    def detect_typed_input(self):
        """
        Detects keyboard input.
        This is effectively a custom implementation of Python's input() function.
        This method enables custom logic for special keys, and it is non-blocking.
        """

        # Escape Sequence Constants
        CONTROL_C = repr('\x03')
        ENTER = repr('\r')
        ESCAPE = repr('\x1b')
        DELETE = repr('\x7f')
        TAB = repr('\t')

        input_key = self.getch()

        if repr(input_key) == CONTROL_C:
            managers["output"].dprint('Exit')
            managers["context"].looping = False

        elif repr(input_key) == ENTER:
            managers["output"].dprint('Enter')
            print("")
            self.cmd_entered = True

        elif repr(input_key) == ESCAPE:
            managers["output"].dprint('Escape')
            input_key = self.getch()
            if input_key == '[':
                # It's an arrow key of some kind
                input_key = self.getch()
                if input_key == 'A':
                    managers["output"].dprint('Up')
                    if self.last_entered != "" and self.input_buffer != self.last_entered:
                        if self.autocomplete_buffer == "":
                            self.saved_buffer = self.input_buffer
                        else:
                            self.saved_buffer = self.autocomplete_buffer
                        self.input_buffer = self.last_entered
                        self.replace_line(self.input_buffer)
                    else:
                        self.sound()

                elif input_key == 'B':
                    managers["output"].dprint('Down')
                    if self.autocomplete_buffer != "" and self.saved_buffer == "":
                        self.input_buffer = self.autocomplete_buffer
                        self.autocomplete_buffer = ""
                        self.autocomplete_counter = -1
                        self.replace_line(self.input_buffer)
                    elif self.input_buffer != self.saved_buffer:
                        self.input_buffer = self.saved_buffer
                        self.saved_buffer = ""
                        self.replace_line(self.input_buffer)
                    elif self.input_buffer != "":
                        self.input_buffer = ""
                        self.replace_line(self.input_buffer)
                    else:
                        self.sound()

                elif input_key == 'C':
                    managers["output"].dprint('Right')
                    # Try to find the most reasonable autocompletion for entire LINE
                    # Try general line autocompletion
                    markov_sentence = None

                    if self.input_buffer == "":
                        self.sound()
                        return

                    if self.autocomplete_counter != -1:
                        self.autocomplete_buffer = ""
                        self.autocomplete_counter = -1

                    if self.autocomplete_buffer == "":
                        markov_sentence = managers["lang"].complete_line(self.input_buffer)
                    else:
                        markov_sentence = managers["lang"].complete_line(self.autocomplete_buffer)

                    if markov_sentence != None:
                        if self.autocomplete_buffer == "":
                            self.autocomplete_buffer = self.input_buffer

                        self.input_buffer = markov_sentence
                        self.replace_line(self.input_buffer)
                    else:
                        self.sound()
                elif input_key == 'D':
                    managers["output"].dprint('Left')
            
            # Check if user trying to escape autocompletion
            elif self.autocomplete_buffer != "":
                self.input_buffer = self.autocomplete_buffer
                self.autocomplete_counter = -1
                self.autocomplete_buffer = ""
                self.replace_line(self.input_buffer)

        elif repr(input_key) == DELETE:
            managers["output"].dprint('Delete')
            self.autocomplete_buffer = ""
            self.autocomplete_counter = -1
            if self.input_buffer != "":
                self.input_buffer = self.input_buffer[:-1]
                self.replace_line(self.input_buffer)

        elif repr(input_key) == TAB:
            managers["output"].dprint('Tab')
            # Try to find the most reasonable autocompletion for individual WORD
            # Check commands first
            # TODO: Extract this into the CommandManager class to avoid repetition
            # Run invocation checkers for each command plugin
            if self.input_buffer == "":
                return

            candidates = []
            if self.autocomplete_buffer != "":
                self.saved_buffer = self.input_buffer
                self.input_buffer = self.autocomplete_buffer

            for (cmd, invocation_checker) in managers["command"].invocations.items():
                if invocation_checker(self.input_buffer):
                    candidates.append(cmd)

            # Try finding matching command filename
            candidates += managers["command"].get_candidate_command_names(self.input_buffer.lower())

            # Try general word autocompletion
            words = self.input_buffer.split(" ")
            finished_part = ""
            word_options = []

            if len(words) == 1:
                word_options = managers["lang"].complete_word(words[0])
            elif len(words) >= 2:
                finished_part = " ".join(words[:-1]) + " "
                word_options = managers["lang"].complete_word(self.input_buffer)

            candidates += [finished_part+word+" " for word in word_options]

            if len(candidates) > 0:
                self.autocomplete_counter = (self.autocomplete_counter + 1) % len(candidates)

                if self.autocomplete_buffer == "":
                    self.autocomplete_buffer = self.input_buffer

                self.input_buffer = candidates[self.autocomplete_counter]
                self.replace_line(self.input_buffer)
            else:
                self.sound()
        else:
            self.autocomplete_buffer = ""
            self.autocomplete_counter = -1
            self.input_buffer += input_key
            print("\r"+ self.input_buffer, end="")


class OutputManager(Manager):
    """
    A standard output manager for Aria. Only one OutputManager should be active at a time.
    """
    def __init__(self):
        """ Constructs an OutputManager object. """
        self.last_spoken_reply = ""

    def sprint(self, *arr):
        """ Speaks and prints the supplied args if the speak_reply flag is true, otherwise just prints normally. """
        arr_str = " ".join(map(str,arr))
        print(arr_str)
        if managers["config"].runtime_config["speak_reply"]:
            os.system("say "+arr_str)
            self.last_spoken_reply = arr_str

    def repeat(self):
        """ Repeats the last output. """
        self.sprint(self.last_spoken_reply)

    def dprint(self, *arr):
        """ Prints supplied args only if debug mode is enabled. """
        if managers["config"].runtime_config["debug"]:
            print(" ".join(map(str,arr)))

class AriaManager(Manager):
    """
    A manager for Aria's internal operations.
    """
    def __init__(self):
        """ Constructs an AriaManager object. """
        pass

    def _fix_broken_managers(self):
        """ Fixes broken references to the managers dictionary. """
        if Command.managers != self.managers:
            Command.managers = self.managers.copy()

    def main(self):
        """ Runs internal methods. """
        self._fix_broken_managers()

    def initialize_managers(self, runtime_config):
        CONFM = ConfigManager()
        managers["config"] = CONFM
        config = CONFM.get_config()
        managers["config"].set_runtime_config(runtime_config)

        TRACKM = TrackingManager(CONFM.get("aria_path")+"/data/")
        managers["tracking"] = TRACKM

        DOCM = DocumentManager()
        managers["docs"] = DOCM

        COMM = CommandManager()
        commands = COMM.get_all_commands()
        managers["command"] = COMM

        CONM = ContextManager()
        managers["context"] = CONM

        LANGM = LanguageManager()
        managers["lang"] = LANGM

        INM = InputManager()
        managers["input"] = INM

        OUTM = OutputManager()
        managers["output"] = OUTM

        self.managers = managers.copy()

        return managers

AriaManager = AriaManager()
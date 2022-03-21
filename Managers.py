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
import applescript
import importlib
import json
import os
import re
import os
from datetime import datetime
from cmds import *

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
    def __init__(self, debug = False):
        """
        Constructs a ConfigManager object.

        Parameters:
            managers : [Manager] - A list of references to all manager objects.
            debug : boolean - Optional setting to enable verbose feedback.
        """
        self.debug = debug
        self.cfg_file_name = "aria_config.json"
        self.cfg_version = "0.0.1"
        self.config = {}

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
            "plugins" : {}
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
                "plugins" : plugins
            }

            print("Creating custom config file...")
            self.create_global_config(config)
        else:
            print("Creating default config file...")
            self.create_global_config(default_config)


class DocumentManager(Manager):
    """
    A document/file IO manager for Aria. Only one DocumentManager should be active at a time.
    """
    def __init__(self, managers, debug = False):
        """
        Constructs a DocumentManager object.

        Parameters:
            managers : [Manager] - A list of references to all manager objects.
            debug : boolean - Optional setting to enable verbose feedback.
        """
        self.managers = managers
        self.debug = debug

    def get_file_content(self, filename):
        """
        Returns the content within a file as a single string.

        Parameters:
            filename: str - The name of the file to read content from.

        Returns:
            content : str - The content of the file.
        """
        aria_path = self.managers["config"].get("aria_path")
        with open(aria_path+"/cmds/"+filename, "r") as target_file:
            content = target_file.read()
        return content


class CommandManager(Manager):
    """
    A manager for Aria command modules. Only one CommandManager should be active at a time.
    """
    def __init__(self, managers, debug = False):
        """
        Constructs a CommandManager object.

        Parameters:
            managers : [Manager] - A list of references to all manager objects.
            debug : boolean - Optional setting to enable verbose feedback.
        """
        self.managers = managers
        self.plugins = dict()
        self.invocations = dict()
        self.handlers = dict()
        self.handler_checkers = dict()
        self.debug = debug

    def get_all_commands(self):
        """
        Loads all command modules enabled in aria_config.json.

        Returns:
            None
        """
        aria_path = self.managers["config"].get("aria_path")
        files = os.listdir(path=aria_path+"/cmds")
        for f in files:
            if "__" not in f and ".pyc" not in f and ".DS_Store" not in f:
                cmd_name = f.replace(".py", "")
                if cmd_name in self.managers["config"].get("plugins").keys():
                    if self.managers["config"].get("plugins")[cmd_name]:
                        # Add base Command object
                        module = importlib.import_module("cmds."+cmd_name)
                        self.plugins[cmd_name] = module.Command()

                        # Get aliases
                        aliases = getattr(self.plugins[cmd_name], "aliases", None)
                        if isinstance(aliases, list):
                            for alias in aliases:
                                self.plugins[alias] = self.plugins[cmd_name]

                        # Add invocation methods
                        cmd_invocation = getattr(self.plugins[cmd_name], "invocation", None)
                        if callable(cmd_invocation):
                            self.invocations[cmd_name] = cmd_invocation

                            if isinstance(aliases, list):
                                for alias in aliases:
                                    self.invocations[alias] = self.invocations[cmd_name]

                        # Add handler checking methods
                        cmd_handler_checker = getattr(self.plugins[cmd_name], "handler_checker", None)
                        cmd_handler = getattr(self.plugins[cmd_name], "handler", None)
                        if callable(cmd_handler_checker):
                            self.handler_checkers[cmd_name] = cmd_handler_checker

                            if isinstance(aliases, list):
                                for alias in aliases:
                                    self.handler_checkers[alias] = self.handler_checkers[cmd_name]

                        # Add handler methods
                        if callable(cmd_handler):
                            self.handlers[cmd_name] = cmd_handler

                            if isinstance(aliases, list):
                                for alias in aliases:
                                    self.handlers[alias] = self.handlers[cmd_name]
        if self.debug:
            print("Loaded", len(self.plugins), "plugins.")

    def cmd_from_template(self, str_in):
        """
        Creates a new command module using the template method of another command.

        Paramters:
            str_in: str - The full string that initiated this command.

        Notes:
            - The CommandManager should not be handling parsing of str_in. Check this ASAP. Use a new_command and target_command parameter instead.
        """
        aria_path = self.managers["config"].get("aria_path")

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
        old_file_content = self.managers["docs"].get_file_content(old_filename)

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
        aria_path = self.managers["config"].get("aria_path")
        script = f"""#! /bin/zsh
        cd {aria_path}
        python Aria.py --cmd "{cmd_str}" --cf
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
            String -- the name of the file (including .py extension)
        """
        name_condensed = cmd_name.replace(" ", "")

        files = os.listdir(path=self.managers["config"].get("aria_path")+"/cmds")
        for f in files:
            if f.startswith(name_condensed):
                return f[:-3]

    def enable_command_plugin(self, cmd_name):
        """Add a command plugin to the plugins dictionary and enables it in aria_config.json.

        Arguments:
            cmd_name {String} -- The name of the command plugin to be enabled.

        Returns:
            boolean -- True if a plugin is successfully enabled, False if the plugin is already enabled.
        """
        if cmd_name in self.managers["config"].get("plugins"):
            if self.managers["config"].get("plugins")[cmd_name]["enabled"] == True:
                print(cmd_name, "is already enabled.")
                return False
            else:
                self.managers["config"].get("plugins")[cmd_name]["enabled"] = True
        else:
            self.managers["config"].get("plugins")[cmd_name] = {
                "enabled": True
            }
        self.managers["config"].save_global_config()
        module = importlib.import_module("cmds."+cmd_name)
        aria_path = self.managers["config"].get("aria_path")
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
        if cmd_name in self.managers["config"].get("plugins"):
            if self.managers["config"].get("plugins")[cmd_name]["enabled"] == False:
                print(cmd_name, "is already disabled.")
                return False
            else:
                self.managers["config"].get("plugins")[cmd_name]["enabled"] = False
        else:
            self.managers["config"].get("plugins")[cmd_name] = {
                "enabled": False
            }
        self.managers["config"].save_global_config()
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
    def __init__(self, managers, debug = False):
        """
        Constructs a ContextManager object.

        Parameters:
            managers : [Manager] - A list of references to all manager objects.
            debug : boolean - Optional setting to enable verbose feedback.
        """
        self.mins_to_checkpoint = 0.05
        self.timer_checkpoint = -1
        self.debug = debug

        item_structure = {
            "start_time" : float,
            "end_time" : float,
            "frequency" : int,
            "targets" : list,
        }

        self.context_tracker = managers["tracking"].init_tracker("context", item_structure)
        self.current_context = self.context_tracker.new_item([0, 0, 0, []])
        self.current_app = ""
        self.previous_apps = []
        self.previous_input = ""

    def update_context(self):
        """
        Update all context variables as necessary

        Returns:
            None
        """
        currentApp, listOfApps = self.get_context_from_AS()
        listOfApps = list(set(listOfApps))

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
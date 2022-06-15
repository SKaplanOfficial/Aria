"""
Reload

A command plugin for Aria that reloads other command plugin modules.

Part of AriaCore in Aria 1.0.0
"""

from ariautils.command_utils import Command
from ariautils import command_utils, config_utils, file_utils, io_utils

class Reload(Command):
    info = {
        "title": "Reload",
        "repository": "https://github.com/SKaplanOfficial/Aria",
        "documentation_link": "https://github.com/SKaplanOfficial/Aria/documentation/",
        'id': "aria_core_reload",
        "version": "1.0.0",
        "description": """
            This command reloads other command plugin modules.
        """,
        "requirements": {},
        "extensions": {},
        "purposes": [
            "reload command", "reload plugin"
        ],
        "targets": [
            "aria_core_open", "aria_core_terminal", "plugin", "command"
        ],
        "keywords": [
            "aria", "command", "core", "internal", "metacommand", "automation", "utility",
        ],
        "example_usage": [
            ("reload", "Reloads all command plugins."),
            ("reload aria_core_terminal", "Reloads a specified command plugin."),
            ("reload aria_core_terminal aria_core_open", "Reloads multiple command plugins."),
            ("reload aria_core_terminal --auto", "Begins watching a command plugin for changes and reloading it when a change occurs."),
            ("reload --autoall", "Sets up autoreload for all command plugins."),
            ("reload aria_core_terminal --stop", "Stops watching a command plugin for changes."),
            ("reload --stopall", "Stops autoreload for all actively watched command plugins.")
        ],
        "help": [
            "This command reloads Python modules of other Aria commands. The reload command is intended primarily for development purposes.",
            "To reload a particular command, run `reload <plugin filename>`, where the ID is the command ID. The filename of a command can usually be found by running `help <command component>` or `help <command title>`.",
            "To reload all commands, run `reload` without any additional arguments.",
            "Set up autoreload for one or more commands using the `--auto` flag. With this flag, a separate thread will watch the plugin file for changes and reload the plugin module any time a change occurs. To set up autoreload for all plugins at once, use `reload --autoall`. To stop autoreload for a specific plugin, use `reload <plugin filename> --stop`. To stop all autoreloading, use `reload --stopall`.",
        ],
        "contact_details": {
            "author": "Stephen Kaplan",
            "email": "stephen.kaplan@maine.edu",
            "website": "http://skaplan.io",
        },
        "info_version": "0.9.0",
    }

    watched_cmds = []

    def execute(self, query, _origin):
        parts = query.split()
        num_parts = len(parts) - 1

        if num_parts == 0:
            # Reload all command plugins
            command_utils.plugins.clear()
            num_reloaded = command_utils.load_all_commands()

            if num_reloaded == 1:
                io_utils.sprint("Reloaded 1 command.")
            else:
                io_utils.sprint("Reloaded " + str(num_reloaded) + " commands.")
            
        elif parts[num_parts] == "--auto":
            # Set up autoreload upon changes to specific command file(s)
            cmd_names = parts[1:num_parts]
            for cmd_name in cmd_names:
                self.watched_cmds.append(cmd_name)
                filepath = config_utils.get("aria_path") + "/cmds/" + cmd_name + ".py"
                file_utils.watch_file_for_changes(filepath, self.reload_cmd_from_file)
            io_utils.sprint("Initialized autoreload for " + cmd_name + ".")

        elif num_parts == 1 and parts[1] == "--autoall":
            # Set up autoreload upon changes to any command file
            for cmd_name in command_utils.plugins:
                self.watched_cmds.append(cmd_name)
                filepath = config_utils.get("aria_path") + "/cmds/" + cmd_name + ".py"
                file_utils.watch_file_for_changes(filepath, self.reload_cmd_from_file)
                io_utils.sprint("Initialized autoreload for " + cmd_name + ".")

        elif num_parts == 1 and (parts[1] == "--stop" or parts[1] == "--stopall"):
            # Stop autoreload for all command plugins
            num_stopped = 0
            for cmd_name in self.watched_cmds:
                filepath = config_utils.get("aria_path") + "/cmds/" + cmd_name + ".py"
                file_utils.stop_watching(filepath)
                self.watched_cmds.remove(cmd_name)
                num_stopped += 1

            if num_stopped == 1:
                io_utils.sprint("Stopped autoreload for 1 command.")
            else:
                io_utils.sprint("Stopped autoreload for " + str(len(self.watched_cmds)) + " commands.")

            self.watched_cmds.clear()

        elif parts[num_parts] == "--stop":
            # Stop autoreload for the specified command plugins
            cmd_names = parts[1:num_parts]
            for cmd_name in cmd_names:
                if cmd_name in self.watched_cmds:
                    filepath = config_utils.get("aria_path") + "/cmds/" + cmd_name + ".py"
                    file_utils.stop_watching(filepath)
                    io_utils.sprint("Stopped autoreload for " + cmd_name + ".")
                    self.watched_cmds.remove(cmd_name)
                else:
                    io_utils.sprint(cmd_name + " was not set to autoreload.")

        else:
            # Reload the specified command plugins
            cmd_names = parts[1:]
            for cmd_name in cmd_names:
                command_utils.reload_command(cmd_name)
                io_utils.sprint("Reloaded command '" + cmd_name + "'.")

    def reload_cmd_from_file(self, filepath: str):
        """Tells Aria to reload a command plugin. Runs when a watcher thread observes a change in a command plugin file.
        """
        path_len = len(filepath)
        cmd_name = filepath[path_len - filepath[::-1].index("/"):-3]
        io_utils.sprint("Detected change in " + filepath + ".")
        command_utils.reload_command(cmd_name)
        io_utils.sprint("Reloaded command '" + cmd_name + "'.")

    def get_query_type(self, query: str) -> int:
        if query.startswith("reload"):
            return 10000

command = Reload()
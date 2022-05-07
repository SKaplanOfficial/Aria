# """
# Test

# Last Updated: Version 0.0.1
# """

from ariautils.command_utils import Command
from ariautils import command_utils, config_utils, file_utils, io_utils

class Reload(Command):
    watched_cmds = []

    def execute(self, query, origin):
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
            # Set up autoreloading upon changes to command file(s)
            cmd_names = parts[1:num_parts]
            for cmd_name in cmd_names:
                self.watched_cmds.append(cmd_name)
                filepath = config_utils.get("aria_path") + "/cmds/" + cmd_name + ".py"
                file_utils.watch_file_for_changes(filepath, self.reload_cmd_from_file, cmd_name)
                io_utils.sprint("Initalized autoreload for " + cmd_name + ".")

        elif num_parts == 1 and (parts[1] == "--stop" or parts[0] == "--stopall"):
            # Stop autoreloading for all command plugins
            num_stopped = 0
            for cmd_name in self.watched_cmds:
                filepath = config_utils.get("aria_path") + "/cmds/" + cmd_name + ".py"
                file_utils.stop_watching(filepath)
                num_stopped += 1

            if num_stopped == 1:
                io_utils.sprint("Stopped autoreload for 1 command.")
            else:
                io_utils.sprint("Stopped autoreload for " + str(len(self.watched_cmds)) + " commands.")

            self.watched_cmds.clear()

        elif parts[num_parts] == "--stop":
            # Stop autoreloading for the specified command plugins
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

    def reload_cmd_from_file(self, filepath):
        path_len = len(filepath)
        cmd_name = filepath[path_len - filepath[::-1].index("/"):-3]
        io_utils.sprint("Detected change in " + filepath + ".")
        command_utils.reload_command(cmd_name)
        io_utils.sprint("Reloaded command '" + cmd_name + "'.")

command = Reload()
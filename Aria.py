"""
Aria - A modular virtual assistant for the crazy ones.

Version 0.0.1
"""

import re
import threading
import time
import argparse
from Managers import ConfigManager
from Managers import DocumentManager
from Managers import CommandManager
from Managers import ContextManager
from tracking_tools.TrackingManager import TrackingManager

# Set up commandline argument parsing
arg_parser = argparse.ArgumentParser(description="A virtual assistant.")
arg_parser.add_argument("--cmd", type = str, help = "A command to be run when Aria starts.")
arg_parser.add_argument("--close", action = "store_true", help = "Whether Aria should close after running a command provided via --cmd.")
arg_parser.add_argument("--debug", action="store_true", help = "Enable debug features.")
args = arg_parser.parse_args()

# Set up subsystem managers
managers = {}

ConfigManager = ConfigManager(debug = args.debug)
config = ConfigManager.get_config()
managers["config"] = ConfigManager

TrackingManager = TrackingManager(managers["config"].get("aria_path")+"/data/")
managers["tracking"] = TrackingManager

DocumentManager = DocumentManager(managers, debug = args.debug)
managers["docs"] = DocumentManager

CommandManager = CommandManager(managers, debug = args.debug)
commands = CommandManager.get_all_commands()
managers["command"] = CommandManager

ContextManager = ContextManager(managers, debug = args.debug)
managers["context"] = ContextManager


def parse_input(str_in, managers):
    """
    Compares an input string against each intent checker, then runs the best fit command.

    Parameters:
        str_in : str - A command (and any arguments) to be run.
        managers : [Manager] - A list of references to all manager objects.

    Returns:
        None
    """
    global looping
    
    cmd_name = None

    # Check meta-commands
    if str_in == "q":
        exit()
    elif re.match("(make command )(\w*)( from )(\w*)", str_in) or re.match("(make )(\w*)( from command )(\w*)", str_in):
        # Make new command based on another command
        managers["command"].cmd_from_template(str_in)
    elif str_in.startswith("enable plugin "):
        cmd_name = str_in[14:]
        managers["command"].enable_command_plugin(cmd_name)
    elif str_in.startswith("disable plugin "):
        cmd_name = str_in[15:]
        managers["command"].disable_command_plugin(cmd_name)
    elif str_in.startswith("report "):
        cmd_name = managers["command"].get_command_name(str_in[7:].lower())
        managers["command"].cmd_method(cmd_name, "report")
    elif str_in.startswith("help "):
        cmd_name = managers["command"].get_command_name(str_in[5:].lower())
        managers["command"].cmd_method(cmd_name, "help")
    else:
        # Run invocation checkers for each command plugin
        for (cmd, invocation_checker) in managers["command"].invocations.items():
            if invocation_checker(str_in):
                cmd_name = cmd

        # If no invocation method has been found, try finding a matching command filename
        if cmd_name == "" or cmd_name is None:
            first_word = str_in.split(" ")[0]
            cmd_name = managers["command"].get_command_name(first_word.lower())

        # If no matching filename is found, see if any plugin wants to handle the input
        handler = None
        max_handler_score = 0
        if cmd_name == "" or cmd_name is None:
            for (cmd, handler_checker) in managers["command"].handler_checkers.items():
                handler_score = handler_checker(str_in, managers)
                if handler_score > max_handler_score:
                    max_handler_score = handler_score
                    handler = managers["command"].handlers[cmd]
        
        if handler != None:
            # If a plugin has a handler for this input, run the handler
            handler(str_in, managers, max_handler_score)
        else:
            # If there is still no command found, and the input has not been handled, report reason why
            if cmd_name == "" or cmd_name is None or cmd_name not in managers["command"].plugins.keys():
                print("Command not found.")
            elif cmd_name in managers["config"].get("plugins").keys() and managers["config"].get("plugins")[cmd_name]["enabled"] == False:
                print("Command not found (the parent plugin has been disabled).")

            # Otherwise, we found a command -- run it!
            else:
                plugin = managers["command"].plugins[cmd_name]
                data = plugin.execute(str_in, managers)

                if (type(data) is str and data.startswith("run ")):
                    # Run command from command feedback
                    run_inputs(data[4:], managers)

def aria_loop():
    """Runs the main command input loop."""
    while looping:
        str_in = input()

        if str_in == "context":
            print("-"*25, "\n", "Current Context: ", managers["context"].current_context, "\n\n")
            print("Context History: ", managers["context"].current_context, "\n", "-"*25, "\n\n")
        else:
            run_inputs(str_in, managers)

        managers["context"].previous_input = str_in


def run_inputs(str_in, managers):
    """
    Runs inputs supplied as a string.
    
    Parameters:
        str_in : str - One or more commands to be run, separated by " && ".
        managers : [Manager] - A list of references to all manager objects.

    Returns:
        None
    """
    current_str = str_in
    remaining = str_in
    while remaining:
        if " && " in remaining:
            current_str = remaining[0:remaining.index("&&")-1]
            remaining = remaining[remaining.index("&&")+3:]
        else:
            current_str = remaining
            remaining = ""
        parse_input(current_str, managers)


def context_loop():
    """Updates the context tracker once a second."""
    while looping:
        ContextManager.update_context()
        time.sleep(1)

lock = threading.Lock()  # A lock for the shared resource
context_thread = threading.Thread(target=context_loop, name="Context", daemon=True)
aria_thread = threading.Thread(target=aria_loop, name="Aria", daemon=True)


looping = True
if __name__ == '__main__':
    if args.cmd is not None:
        # Run a command supplied via commandline args
        refs = [ContextManager, TrackingManager]
        run_inputs(args.cmd, refs)

        if args.close:
            # Close after command execution
            exit()
    else:
        # Run Aria in interactive mode
        print("Hello,", managers["config"].get("user_name") + "!")

        context_thread.start()
        aria_thread.start()

        while looping:
            time.sleep(1)

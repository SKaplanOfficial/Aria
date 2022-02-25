"""
Aria

Last Updated: March 8, 2021
"""

import importlib
from multiprocessing.connection import wait
import subprocess
import os
from sys import stdin
import cmds
import re
import threading
import time
import io
import sys
from CommandManager import CommandManager
from ContextManager import ContextManager
from TrackingManager import TrackingManager

# Relative to initial start directory (User root)
aria_path = "/Users/Steven/Documents/2020/Python/Aria"

# Set up trackers
TrackM = TrackingManager(aria_path)
context_tracker = TrackM.init_tracker("context")

# Set up other subsystem managers
CM = CommandManager(aria_path)
ConM = ContextManager(aria_path, context_tracker)
looping = True


def get_command_name(str_in):
    """Attempts to identify the command within a multiparameter string.
    Use + within a command string to avoid looping through each command file.

    Arguments:
        str_in {String} -- The input command string.

    Returns:
        String -- The command name.
    """
    str_condensed = str_in.replace(" ", "")

    fast_track = str_in.split("+", 1)
    if (len(fast_track) > 1):
        print(fast_track[0])
        return fast_track[0]

    files = os.listdir(path=aria_path+"/cmds")
    for file in files:
        filename = file[:-3]
        if str_condensed.startswith(filename):
            return filename


def exit_term():
    """Closes the active terminal tab.
    """
    scpt = 'tell application "Terminal" to close (get window 1) '.encode()
    args = []
    subprocess.call(['osascript', '-e', scpt])


def parse_input(str_in, context):
    global looping
    #try:
    if str_in == "q":
        exit_term()
    elif str_in == "drop to term":
        looping = False
    elif re.match("(make command )(\w*)( from )(\w*)", str_in) or re.match("(make )(\w*)( from command )(\w*)", str_in):
        # Make new command based on another command
        CM.cmd_from_template(str_in)
    elif str_in.startswith("report"):
        # TODO: Have commands register reporters, requires commands be imported on start
        cmd_name = get_command_name(str_in[7:].lower())
        if (cmd_name == "" or cmd_name is None):
            print("Reporter not found (Cannot find base command).")
        else:
            # Attempt to run reporter
            cmd_module = importlib.import_module("cmds."+cmd_name)
            plugin = cmd_module.Command(aria_path)
            make_report = getattr(plugin, 'report', None)
            if callable(make_report):
                plugin.report(TrackM)
            else:
                print("Reporter not found (Missing report method).")
    else:
        cmd_name = get_command_name(str_in.lower())

        if (cmd_name == "" or cmd_name is None):
            print("Command not found.")
        else:
            # Run the command
            cmd_module = importlib.import_module("cmds."+cmd_name)
            plugin = cmd_module.Command(aria_path)
            data = plugin.execute(str_in, context)

            if (type(data) is str and data.startswith("run ")):
                # Run command from command feedback
                run_inputs(data[4:], context)
    # except Exception as e:
    #     print("An unknown error occurred:\n"+str(e))


def aria_loop():
    global stdin_count, msg_channel
    while looping:
        str_in = input()
        if stdin_count == 0:
            if str_in == "context":
                print("-"*25, "\n", "Current Context: ", ConM.current_context, "\n\n")
                print("Context History: ", ConM.current_context, "\n", "-"*25, "\n\n")
            else:
                refs = [ConM, TrackM]
                run_inputs(str_in, refs)
        elif stdin_count != 0:
            msg_channel = str_in


def run_inputs(str_in, context):
    current_str = str_in
    remaining = str_in
    while remaining:
        if " && " in remaining:
            current_str = remaining[0:remaining.index("&&")-1]
            remaining = remaining[remaining.index("&&")+3:]
        else:
            current_str = remaining
            remaining = ""
        parse_input(current_str, context)


def context_loop():
    while looping:
        ConM.update_context()
        time.sleep(1)

def predictor_loop():
    pass
    # global stdin_count, msg_channel
    # waitlist = []
    # waitlist_timer = 100000000

    # while looping:
    #     if waitlist_timer == 0 and len(waitlist) > 0:
    #         print("Removed ", waitlist.pop(0), " from the waitlist.")
    #         waitlist_timer = 100000000
    #     elif len(waitlist) > 0:
    #         waitlist_timer -= 1

        # if '/Applications/Visual Studio Code.app' in ConM.current_context["apps"] and '/Applications/GitHub Desktop.app' in ConM.current_context["apps"] and 'x 497' not in waitlist:
        #     if stdin_count == 0:
        #         print("[Based on you opening VSCode and GitHub Desktop] Do you want to launch the 497 context?")
        #         stdin_count += 1
            
        #     if stdin_count == 1 and msg_channel in ["Yes", "yes", "Y", "y"]:
        #         print("Launching 497 context...")
        #         context = [ConM.current_context, ConM.get_previous_context()]
        #         run_inputs("x 497", context)

        #     if stdin_count == 1 and msg_channel != "":
        #         waitlist.append('x 497')
        #         msg_channel = ""
        #         stdin_count -= 1
        # if (ConM.current_app == '/System/Applications/Calendar.app' and 'site https://calendar.google.com' not in waitlist):
        #     if stdin_count == 0:
        #         print("[Based on you opening Calendar] Do you want to open Google Calendar?")
        #         stdin_count += 1

        #     if stdin_count == 1 and msg_channel in ["Yes", "yes", "Y", "y"]:
        #         print("Opening Google Calendar...")
        #         context = [ConM.current_context, ConM.get_previous_context()]
        #         run_inputs("site https://calendar.google.com", context)

        #     if stdin_count == 1 and msg_channel != "":
        #         waitlist.append('site https://calendar.google.com')
        #         msg_channel = ""
        #         stdin_count -= 1
        # if (ConM.current_app == '/Applications/Visual Studio Code.app' and '/Applications/Safari.app' not in waitlist):
        #     if stdin_count == 0:
        #         print("[Based on you opening VSCode] Do you want to open Safari?")
        #         stdin_count += 1

        #     if stdin_count == 1 and msg_channel in ["Yes", "yes", "Y", "y"]:
        #         print("Opening Safari...")
        #         cmd_module = importlib.import_module("cmds.app")
        #         plugin = cmd_module.Command(aria_path)
        #         context = [ConM.current_context, ConM.get_previous_context()]
        #         data = plugin.execute("app Safari -g", context)
            
        #     if stdin_count == 1 and msg_channel != "":
        #         waitlist.append('/Applications/Safari.app')
        #         print("Added ", '/Applications/Safari.app', " to the waitlist")
        #         msg_channel = ""
        #         stdin_count += 1
        # if (ConM.current_app == '/Applications/Visual Studio Code.app' and '/Applications/Terminal.app' not in waitlist):
        #     if stdin_count == 2:
        #         print("[Based on you opening VSCode] Do you want to open Terminal?")
        #         stdin_count += 1

        #     if stdin_count == 3 and msg_channel in ["Yes", "yes", "Y", "y"]:
        #         print("Opening Terminal")
        #         cmd_module = importlib.import_module("cmds.app")
        #         plugin = cmd_module.Command(aria_path)
        #         context = [ConM.current_context, ConM.get_previous_context()]
        #         data = plugin.execute("app Terminal -n", context)
            
        #     if stdin_count == 3 and msg_channel != "":
        #         waitlist.append('/Applications/Terminal.app')
        #         msg_channel = ""
        #         stdin_count -= 3

stdin_count = 0
msg_channel = ""
lock = threading.Lock()  # A lock for the shared resource

context_thread = threading.Thread(
    target=context_loop, name="Context", daemon=True)
aria_thread = threading.Thread(target=aria_loop, name="Aria", daemon=True)
predictor_thread = threading.Thread(
    target=predictor_loop, name="Predictor", daemon=True)


if __name__ == '__main__':
    print("Hello.")
    context_thread.start()
    aria_thread.start()
    predictor_thread.start()

    while looping:
        time.sleep(1)

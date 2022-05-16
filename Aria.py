"""
Aria - A modular virtual assistant for the crazy ones.

Version 0.0.1
"""

import re
import threading
import time
import argparse

from datetime import datetime
from pathlib import Path

from ariautils import command_utils, config_utils, context_utils, io_utils

if __name__ == '__main__':
    # Parse commandline arguments
    arg_parser = argparse.ArgumentParser(description="A virtual assistant.")
    arg_parser.add_argument("--input", type = str, help = "Input data for Aria to analyze.")
    arg_parser.add_argument("--cmd", type = str, help = "A command to be run when Aria starts.")
    arg_parser.add_argument("--close", action = "store_true", help = "Whether Aria should close after running a command provided via --cmd.")
    arg_parser.add_argument("--debug", action="store_true", help = "Enable debug features.")
    arg_parser.add_argument("--speak_reply", action="store_true", help = "Enable spoken feedback.")
    arg_parser.add_argument("--speak_query", action="store_true", help = "Enable spoken queries.")
    args = arg_parser.parse_args()

    config_utils.runtime_config = {
        'debug' : args.debug,
        'speak_reply' : args.speak_reply,
        'speak_query' : args.speak_query,
    }

    if args.input != None:
        input_path = Path(args.input)
        print(input_path.parts)

    num_commands = command_utils.load_all_commands()
    io_utils.dprint("Loaded " + str(num_commands) + " command plugins.")

def parse_input(str_in):
    """Compares an input string against each intent checker, then runs the best fit command.

    Parameters:
        str_in : str - A command (and any arguments) to be run.

    Returns:
        None

    :Example:

    >>> another_class.foo('', AClass())        
    
    :param arg1: first argument
    :type arg1: string
    :param arg2: second argument
    :type arg2: :class:`module.AClass`
    :return: something
    :rtype: string
    :raises: TypeError
    """
    cmd_name = None

    # Check meta-commands
    if str_in == "q":
        exit()
    elif str_in == "repeat":
        io_utils.repeat()
    elif re.match("(make command )(\w*)( from )(\w*)", str_in) or re.match("(make )(\w*)( from command )(\w*)", str_in):
        # Make new command based on another command
        command_utils.cmd_from_template(str_in)
    elif str_in.startswith("enable plugin "):
        cmd_name = str_in[14:]
        command_utils.enable_command_plugin(cmd_name)
    elif str_in.startswith("disable plugin "):
        cmd_name = str_in[15:]
        command_utils.disable_command_plugin(cmd_name)
    elif str_in.startswith("report "):
        cmd_name = command_utils.get_command_name(str_in[7:].lower())
        command_utils.cmd_method(cmd_name, "report")
    elif str_in.startswith("help "):
        cmd_name = command_utils.get_command_name(str_in[5:].lower())
        command_utils.cmd_method(cmd_name, "help")
    else:
        # TODO: Extract this into the CommandManager class to avoid repetition
        # Run invocation checkers for each command plugin
        for (cmd, invocation_checker) in command_utils.invocations.items():
            if invocation_checker(str_in):
                cmd_name = cmd


        # If no matching filename is found, see if any plugin wants to handle the input
        handler = None
        max_handler_score = 0
        if cmd_name == "" or cmd_name is None:
            for (cmd, handler_checker) in command_utils.handler_checkers.items():
                try:
                    handler_score = handler_checker(str_in)
                    io_utils.dprint(cmd + " " + str(handler_score))
                except Exception as e:
                    print(e)
                    pass
                
                if handler_score != None:
                    if handler_score > max_handler_score:
                        max_handler_score = handler_score
                        handler = command_utils.handlers[cmd]
        
        if handler != None:
            # If a plugin has a handler for this input, run the handler
            handler(str_in, max_handler_score)
        else:
            # Try known files
            if cmd_name == "" or cmd_name is None:
                first_word = str_in.split(" ")[0]
                for key in command_utils.plugins.keys():
                    if key.startswith(first_word):
                        cmd_name = key
                        break

            # Try finding new plugin files -- these will probably be disabled
            if cmd_name == "" or cmd_name is None:
                first_word = str_in.split(" ")[0]
                cmd_name = command_utils.get_command_name(first_word.lower())

            if cmd_name == "" or cmd_name is None or cmd_name not in command_utils.plugins.keys():
                # No command found
                if not config_utils.runtime_config["speak_query"]:
                    io_utils.sprint("I couldn’t find that command.")
            elif cmd_name in config_utils.get("plugins").keys() and config_utils.get("plugins")[cmd_name]["enabled"] == False:
                # Command was found but is disabled
                io_utils.sprint("Sorry, that command is disabled.")

            else:
                # Enabled command has been found
                if int(time.time()) % 3 == 0:
                    # Occasional Acknowledgement
                    io_utils.sprint("Ok!")

                data = None
                if config_utils.runtime_config["debug"]:
                    # No error check when debugging -- program will crash on error & display full stacktrace
                    plugin = command_utils.plugins[cmd_name]
                    data = plugin.execute(str_in, 0)
                else:
                    try:
                        plugin = command_utils.plugins[cmd_name]
                        plugin.execute(str_in, 0)
                    except:
                        pass

def aria_loop():
    """Runs the main command input loop.
    """
    while context_utils.looping:
        if len(io_utils.query_queue) > 0 and io_utils.query_queue[0].get_exec_time() <= datetime.now():
            io_utils.query_queue.sort()
            run_query(io_utils.dequeue())
        elif io_utils.cmd_entered:
            str_in = io_utils.input_buffer
            io_utils.input_buffer = ""
            
            if str_in == "context":
                print("-"*25, "\n", "Current App: ", context_utils.current_app, "\n\n")
                print("Current Context: ", context_utils.current_context.data, "\n\n")
                print("Context History: ", context_utils.current_context.data, "\n", "-"*25, "\n\n")
            else:
                query_strings = str_in.split(",")
                for str in query_strings:
                    new_query = io_utils.Query(str)
                    io_utils.enqueue(new_query)

            context_utils.previous_input = str_in
            io_utils.last_entered = str_in
            io_utils.cmd_entered = False
        else:
            if config_utils.runtime_config['speak_query']:
                io_utils.detect_spoken_input()
            else:
                io_utils.detect_typed_input()


def run_query(query: io_utils.Query) -> None:
    """Executes a query.

    :param query: The query to be executed.
    :type query: io_utils.Query
    """
    parse_input(query.get_content())


def context_loop():
    """Updates the context tracker once a second.
    """
    while context_utils.looping:
        context_utils.update_context()
        time.sleep(1)


if __name__ == '__main__':
    lock = threading.Lock()  # A lock for the shared resource
    context_thread = threading.Thread(target=context_loop, name="Context", daemon=True)
    aria_thread = threading.Thread(target=aria_loop, name="Aria", daemon=True)

    if args.cmd is not None:
        # Run a command supplied via commandline args
        run_query(args.cmd)

        if args.close:
            # Close after command execution
            exit()
    else:
        # Run Aria in interactive mode
        io_utils.sprint("Hello, " + config_utils.get("user_name") + "!")
        io_utils.sprint("How can I help?")

        context_thread.start()
        aria_thread.start()

        while context_utils.looping:
            time.sleep(0.1)

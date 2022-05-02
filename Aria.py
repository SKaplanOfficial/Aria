"""
Aria - A modular virtual assistant for the crazy ones.

Version 0.0.1
"""

from multiprocessing import managers
import re
import threading
import time
import argparse
from Managers import AriaManager

managers = {}

if __name__ == '__main__':
    # Set up commandline argument parsing
    arg_parser = argparse.ArgumentParser(description="A virtual assistant.")
    arg_parser.add_argument("--cmd", type = str, help = "A command to be run when Aria starts.")
    arg_parser.add_argument("--close", action = "store_true", help = "Whether Aria should close after running a command provided via --cmd.")
    arg_parser.add_argument("--debug", action="store_true", help = "Enable debug features.")
    arg_parser.add_argument("--speak_reply", action="store_true", help = "Enable spoken feedback.")
    arg_parser.add_argument("--speak_query", action="store_true", help = "Enable spoken queries.")
    args = arg_parser.parse_args()

    runtime_config = {
        'debug' : args.debug,
        'speak_reply' : args.speak_reply,
        'speak_query' : args.speak_query,
    }
    managers = AriaManager.initialize_managers(runtime_config)

def parse_input(str_in):
    """
    Compares an input string against each intent checker, then runs the best fit command.

    Parameters:
        str_in : str - A command (and any arguments) to be run.
        managers : [Manager] - A list of references to all manager objects.

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
        managers["output"].repeat()
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
        # TODO: Extract this into the CommandManager class to avoid repetition
        # Run invocation checkers for each command plugin
        for (cmd, invocation_checker) in managers["command"].invocations.items():
            if invocation_checker(str_in):
                cmd_name = cmd


        # If no matching filename is found, see if any plugin wants to handle the input
        handler = None
        max_handler_score = 0
        if cmd_name == "" or cmd_name is None:
            for (cmd, handler_checker) in managers["command"].handler_checkers.items():
                try:
                    handler_score = handler_checker(str_in)
                    managers["output"].dprint(cmd, handler_score)
                except Exception as e:
                    print(e)
                    pass
                
                if handler_score != None:
                    if handler_score > max_handler_score:
                        max_handler_score = handler_score
                        handler = managers["command"].handlers[cmd]
        
        if handler != None:
            # If a plugin has a handler for this input, run the handler
            handler(str_in, max_handler_score)
        else:
            # Try known files
            if cmd_name == "" or cmd_name is None:
                first_word = str_in.split(" ")[0]
                for key in managers["command"].plugins.keys():
                    if key.startswith(first_word):
                        cmd_name = key
                        break

            # Try finding new plugin files -- these will probably be disabled
            if cmd_name == "" or cmd_name is None:
                first_word = str_in.split(" ")[0]
                cmd_name = managers["command"].get_command_name(first_word.lower())

            if cmd_name == "" or cmd_name is None or cmd_name not in managers["command"].plugins.keys():
                # No command found
                managers["output"].sprint("I couldn’t find that command.")
            elif cmd_name in managers["config"].get("plugins").keys() and managers["config"].get("plugins")[cmd_name]["enabled"] == False:
                # Command was found but is disabled
                managers["output"].sprint("Sorry, that command is disabled.")

            else:
                # Enabled command has been found
                if int(time.time()) % 3 == 0:
                    # Occasional Acknowledgement
                    managers["output"].sprint("Ok!")

                data = None
                if managers["config"].runtime_config["debug"]:
                    # No error check when debugging -- program will crash on error & display full stacktrace
                    plugin = managers["command"].plugins[cmd_name]
                    data = plugin.execute(str_in, 0)
                else:
                    try:
                        plugin = managers["command"].plugins[cmd_name]
                        plugin.execute(str_in, 0)
                    except:
                        pass

def aria_loop():
    """ Runs the main command input loop. """
    while managers["context"].looping:
        if len(managers["input"].waitlist) > 0:
            pseudo_command = managers["input"].waitlist.pop()
            run_inputs(pseudo_command)
        elif managers["input"].cmd_entered:
            str_in = managers["input"].input_buffer
            managers["input"].input_buffer = ""
            
            if str_in == "context":
                print("-"*25, "\n", "Current App: ", managers["context"].current_app, "\n\n")
                print("Current Context: ", managers["context"].current_context.data, "\n\n")
                print("Context History: ", managers["context"].current_context.data, "\n", "-"*25, "\n\n")
            else:
                run_inputs(str_in)

            managers["context"].previous_input = str_in
            managers["input"].last_entered = str_in
            managers["input"].cmd_entered = False
        else:
            if managers['config'].runtime_config['speak_query']:
                managers["input"].detect_spoken_input()
            else:
                managers["input"].detect_typed_input()


def run_inputs(str_in):
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
        parse_input(current_str)


def context_loop():
    """ Updates the context tracker once a second. """
    while managers["context"].looping:
        managers["context"].update_context()
        time.sleep(1)


if __name__ == '__main__':
    lock = threading.Lock()  # A lock for the shared resource
    context_thread = threading.Thread(target=context_loop, name="Context", daemon=True)
    aria_thread = threading.Thread(target=aria_loop, name="Aria", daemon=True)

    if args.cmd is not None:
        # Run a command supplied via commandline args
        run_inputs(args.cmd)

        if args.close:
            # Close after command execution
            exit()
    else:
        # Run Aria in interactive mode
        managers["output"].sprint("Hello, " + managers["config"].get("user_name") + "!")
        managers["output"].sprint("How can I help?")

        context_thread.start()
        aria_thread.start()

        while managers["context"].looping:
            AriaManager.main()
            time.sleep(0.1)

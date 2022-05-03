"""A standard input manager for Aria. Only one InputManager should be active at a time.
"""

import speech_recognition as sr
import os, sys, termios, tty

from . import command_utils, config_utils, context_utils, lang_utils

cmd_entered = False # True the instant the user presses Enter after typing a command
last_entered = "" # The previously entered input

input_buffer = "" # The current input
saved_buffer = "" # A buffer to hold temporarily overwritten input
autocomplete_buffer = "" # A buffer to hold pre-autocomplete input

autocomplete_counter = -1 # Index of tab autocompletion array

last_spoken_query = "" # The last input spoken by the user
last_spoken_reply = ""

listener = sr.Recognizer()
listener.dynamic_energy_threshold = True

waitlist = [] # Inputs waiting to be parsed

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(0)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def replace_line(new_line):
    print("", end="\x1b[2K")
    print("\r"+ new_line, end="")

def sound():
    """Plays a blip sound to indicate inability to complete target action."""
    sys.stdout.write('\a')
    sys.stdout.flush()

def pseudo_input(str_in):
    waitlist.append(str_in)

def detect_spoken_input():
    global cmd_entered
    with sr.Microphone() as source:
        print("Awaiting input...")
        listener.adjust_for_ambient_noise(source, duration=2)  
        audio = listener.listen(source)

        try:
            input_buffer = listener.recognize_sphinx(audio)
            print("You said: ", input_buffer)
        except sr.UnknownValueError:
            print("Sphinx could not understand audio")
            pass
        except sr.RequestError as e:
            print("Sphinx error; {0}".format(e))
            pass

    if input_buffer != "":
        cmd_entered = True

def detect_typed_input():
    """
    Detects keyboard input.
    This is effectively a custom implementation of Python's input() function.
    This method enables custom logic for special keys, and it is non-blocking.
    """
    global input_buffer, cmd_entered, autocomplete_buffer, autocomplete_counter, saved_buffer
    # Escape Sequence Constants
    CONTROL_C = repr('\x03')
    ENTER = repr('\r')
    ESCAPE = repr('\x1b')
    DELETE = repr('\x7f')
    TAB = repr('\t')

    input_key = getch()

    if repr(input_key) == CONTROL_C:
        dprint('Exit')
        context_utils.looping = False

    elif repr(input_key) == ENTER:
        dprint('Enter')
        print("")
        cmd_entered = True

    elif repr(input_key) == ESCAPE:
        dprint('Escape')
        input_key = getch()
        if input_key == '[':
            # It's an arrow key of some kind
            input_key = getch()
            if input_key == 'A':
                dprint('Up')
                if last_entered != "" and input_buffer != last_entered:
                    if autocomplete_buffer == "":
                        saved_buffer = input_buffer
                    else:
                        saved_buffer = autocomplete_buffer
                    input_buffer = last_entered
                    replace_line(input_buffer)
                else:
                    sound()

            elif input_key == 'B':
                dprint('Down')
                if autocomplete_buffer != "" and saved_buffer == "":
                    input_buffer = autocomplete_buffer
                    autocomplete_buffer = ""
                    autocomplete_counter = -1
                    replace_line(input_buffer)
                elif input_buffer != saved_buffer:
                    input_buffer = saved_buffer
                    saved_buffer = ""
                    replace_line(input_buffer)
                elif input_buffer != "":
                    input_buffer = ""
                    replace_line(input_buffer)
                else:
                    sound()

            elif input_key == 'C':
                dprint('Right')
                # Try to find the most reasonable autocompletion for entire LINE
                # Try general line autocompletion
                markov_sentence = None

                if input_buffer == "":
                    sound()
                    return

                if autocomplete_counter != -1:
                    autocomplete_buffer = ""
                    autocomplete_counter = -1

                if autocomplete_buffer == "":
                    markov_sentence = lang_utils.complete_line(input_buffer)
                else:
                    markov_sentence = lang_utils.complete_line(autocomplete_buffer)

                if markov_sentence != None:
                    if autocomplete_buffer == "":
                        autocomplete_buffer = input_buffer

                    input_buffer = markov_sentence
                    replace_line(input_buffer)
                else:
                    sound()
            elif input_key == 'D':
                dprint('Left')
        
        # Check if user trying to escape autocompletion
        elif autocomplete_buffer != "":
            input_buffer = autocomplete_buffer
            autocomplete_counter = -1
            autocomplete_buffer = ""
            replace_line(input_buffer)

    elif repr(input_key) == DELETE:
        dprint('Delete')
        autocomplete_buffer = ""
        autocomplete_counter = -1
        if input_buffer != "":
            input_buffer = input_buffer[:-1]
            replace_line(input_buffer)

    elif repr(input_key) == TAB:
        dprint('Tab')
        # Try to find the most reasonable autocompletion for individual WORD
        # Check commands first
        # TODO: Extract this into the CommandManager class to avoid repetition
        # Run invocation checkers for each command plugin
        if input_buffer == "":
            return

        candidates = []
        if autocomplete_buffer != "":
            saved_buffer = input_buffer
            input_buffer = autocomplete_buffer

        for (cmd, invocation_checker) in command_utils.invocations.items():
            if invocation_checker(input_buffer):
                candidates.append(cmd)

        # Try finding matching command filename
        candidates += command_utils.get_candidate_command_names(input_buffer.lower())

        # Try general word autocompletion
        words = input_buffer.split(" ")
        finished_part = ""
        word_options = []

        if len(words) == 1:
            word_options = lang_utils.complete_word(words[0])
        elif len(words) >= 2:
            finished_part = " ".join(words[:-1]) + " "
            word_options = lang_utils.complete_word(input_buffer)

        candidates += [finished_part+word+" " for word in word_options]

        if len(candidates) > 0:
            autocomplete_counter = (autocomplete_counter + 1) % len(candidates)

            if autocomplete_buffer == "":
                autocomplete_buffer = input_buffer

            input_buffer = candidates[autocomplete_counter]
            replace_line(input_buffer)
        else:
            sound()
    else:
        autocomplete_buffer = ""
        autocomplete_counter = -1
        input_buffer += input_key
        print("\r"+ input_buffer, end="")



"""A standard output manager for Aria. Only one OutputManager should be active at a time.
"""

def sprint(*arr):
    """ Speaks and prints the supplied args if the speak_reply flag is true, otherwise just prints normally. """
    global last_spoken_reply
    arr_str = " ".join(map(str,arr))
    print(arr_str)
    if config_utils.runtime_config["speak_reply"]:
        os.system("say "+arr_str)
        last_spoken_reply = arr_str

def repeat():
    """ Repeats the last output. """
    sprint(last_spoken_reply)

def dprint(*arr):
    """ Prints supplied args only if debug mode is enabled. """
    if config_utils.runtime_config["debug"]:
        print(" ".join(map(str,arr)))
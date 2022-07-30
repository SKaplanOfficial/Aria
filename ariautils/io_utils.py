"""A standard input manager for Aria. Only one InputManager should be active at a time.
"""

import os, sys
import speech_recognition as sr
from datetime import datetime, timedelta
from typing import Any

import platform
current_os = platform.system()

if current_os == "Windows":
    import msvcrt
else:
    import termios, tty

from . import command_utils, config_utils, lang_utils

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

query_queue = [] # Inputs waiting to be parsed

class Query:
    """Represents a query to some controller.
    """
    def __init__(self, content: Any = None, delay: timedelta = None):
        self.content: Any = content
        self.creation_time: datetime = datetime.now()
        self.exec_time: datetime = datetime.now()
        if delay != None:
            self.exec_time += delay

    ### Getters
    def get_content(self) -> Any:
        return self.content

    def get_creation_time(self) -> datetime:
        return self.creation_time

    def get_exec_time(self) -> datetime:
        return self.exec_time


    ### Setters
    def set_content(self, content: Any) -> None:
        self.content = content

    def set_exec_time(self, exec_time: datetime) -> None:
        self.exec_time = exec_time

    
    ### Basic Operations
    def delay(self, duration: timedelta) -> None:
        """Delay execution of this query by the specified duration.

        :param duration: The amount of time to delay this query's execution.
        :type duration: timedelta
        """
        self.exec_time += duration

    ### Magic Operations
    def __add__(self, other: 'Query') -> 'Query':
        if isinstance(self.content, list):
            new_content = [x for x in self.content]
            if isinstance(other.get_content(), list):
                new_content.extend([x for x in other.get_content])
            else:
                new_content.append(other.get_content())
            return Query(new_content)
        return Query(self.content + other.get_content())

    def __add__(self, other: Any) -> 'Query':
        try:
            return Query(self.content + other)
        except:
            if isinstance(self.content, list):
                new_content = [x for x in self.content]
                new_content.append(other)
                return Query(new_content)
            return Query([x for x in self.content], other)

    def __sub__(self, other: 'Query') -> 'Query':
        return Query(self.content - other.get_content())

    def __sub__(self, other: Any) -> 'Query':
        return Query(self.content - other)

    def __mul__(self, other: 'Query') -> 'Query':
        return Query(self.content * other.get_content())

    def __mul__(self, other: Any) -> 'Query':
        return Query(self.content * other)

    def __eq__(self, other: 'Query') -> bool:
        if not isinstance(other, Query):
            return False
        return self.content == other.get_content()

    def __lt__(self, other: 'Query') -> bool:
        if not isinstance(other, Query):
            return False
        return self.exec_time < other.exec_time

    def __le__(self, other: 'Query') -> bool:
        if not isinstance(other, Query):
            return False
        return self.exec_time <= other.exec_time

    def __gt__(self, other: 'Query') -> bool:
        if not isinstance(other, Query):
            return False
        return self.exec_time > other.exec_time

    def __ge__(self, other: 'Query') -> bool:
        if not isinstance(other, Query):
            return False
        return self.exec_time >= other.exec_time

    def __contains__(self, item):
        return item in self.content

    def __getitem__(self, index):
        return self.content[index]

    def __setitem__(self, index, item):
        self.content[index] = item

    def __len__(self):
        return len(self.content)

    def __str__(self) -> str:
        return str(self.content)

    def __repr__(self) -> str:
        return str({
            "content": self.content,
            "creation_time": self.creation_time,
        })

def enqueue(query: Query) -> None:
    query_queue.append(query)

def dequeue() -> Query:
    return query_queue.pop(0)

class Response:
    """Represents a response to a Query.
    """
    def __init__(self, content: Any = None, delay: timedelta = None):
        self.content: Any = content
        self.creation_time: datetime = datetime.now()
        self.exec_time: datetime = datetime.now()
        if delay != None:
            self.exec_time += delay

    ### Getters
    def get_content(self) -> Any:
        return self.content

    def get_creation_time(self) -> datetime:
        return self.creation_time

    def get_exec_time(self) -> datetime:
        return self.exec_time


    ### Setters
    def set_content(self, content: Any) -> None:
        self.content = content

    def set_exec_time(self, exec_time: datetime) -> None:
        self.exec_time = exec_time

    
    ### Basic Operations
    def delay(self, duration: timedelta) -> None:
        """Delay execution of this query by the specified duration.

        :param duration: The amount of time to delay this query's execution.
        :type duration: timedelta
        """
        self.exec_time += duration

    ### Magic Operations
    def __add__(self, other: 'Query') -> 'Query':
        if isinstance(self.content, list):
            new_content = [x for x in self.content]
            if isinstance(other.get_content(), list):
                new_content.extend([x for x in other.get_content])
            else:
                new_content.append(other.get_content())
            return Query(new_content)
        return Query(self.content + other.get_content())

    def __add__(self, other: Any) -> 'Query':
        try:
            return Query(self.content + other)
        except:
            if isinstance(self.content, list):
                new_content = [x for x in self.content]
                new_content.append(other)
                return Query(new_content)
            return Query([x for x in self.content], other)

    def __sub__(self, other: 'Query') -> 'Query':
        return Query(self.content - other.get_content())

    def __sub__(self, other: Any) -> 'Query':
        return Query(self.content - other)

    def __mul__(self, other: 'Query') -> 'Query':
        return Query(self.content * other.get_content())

    def __mul__(self, other: Any) -> 'Query':
        return Query(self.content * other)

    def __eq__(self, other: 'Query') -> bool:
        if not isinstance(other, Query):
            return False
        return self.content == other.get_content()

    def __lt__(self, other: 'Query') -> bool:
        if not isinstance(other, Query):
            return False
        return self.exec_time < other.exec_time

    def __le__(self, other: 'Query') -> bool:
        if not isinstance(other, Query):
            return False
        return self.exec_time <= other.exec_time

    def __gt__(self, other: 'Query') -> bool:
        if not isinstance(other, Query):
            return False
        return self.exec_time > other.exec_time

    def __ge__(self, other: 'Query') -> bool:
        if not isinstance(other, Query):
            return False
        return self.exec_time >= other.exec_time

    def __contains__(self, item):
        return item in self.content

    def __getitem__(self, index):
        return self.content[index]

    def __setitem__(self, index, item):
        self.content[index] = item

    def __len__(self):
        return len(self.content)

    def __str__(self) -> str:
        return str(self.content)

    def __repr__(self) -> str:
        return str({
            "content": self.content,
            "creation_time": self.creation_time,
        })

def getch():
    fd = sys.stdin.fileno()
    ch = None
    if current_os == "Windows":
        ch = msvcrt.getch().decode()
    else:
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(0)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def replace_line(new_line):
    print("", end="\x1b[2K")
    print("\r" + new_line, end="")

def sound():
    """Plays a blip sound to indicate inability to complete target action."""
    sys.stdout.write('\a')
    sys.stdout.flush()

def pseudo_input(input_str: str) -> None:
    pseudo_query = Query(input_str)
    enqueue(pseudo_query)

def detect_spoken_input():
    global cmd_entered, input_buffer
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
        dprint('\nExit')
        command_utils.plugins["aria_core_context"].looping = False

    elif repr(input_key) == ENTER:
        dprint('\nEnter')
        print("\n", end="")
        cmd_entered = True

    elif repr(input_key) == ESCAPE:
        dprint('\nEscape')
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
        print("\r" + input_buffer, end="")



"""A standard output manager for Aria. Only one OutputManager should be active at a time.
"""

def sprint(string):
    """ Speaks and prints the supplied args if the speak_reply flag is true, otherwise just prints normally. """
    global last_spoken_reply
    print("\r" + string)
    if config_utils.runtime_config["speak_reply"]:
        os.system("say " + string)
        last_spoken_reply = string

def repeat():
    """ Repeats the last output. """
    sprint(last_spoken_reply)

def dprint(string):
    """ Prints supplied args only if debug mode is enabled. """
    if config_utils.runtime_config["debug"]:
        print("\r" + string)
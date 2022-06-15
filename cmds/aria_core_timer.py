"""
Timer

A command plugin for Aria that provides the ability to create and manage timers.

Part of AriaCore in Aria 1.0.0
"""

import threading
import re
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable, Iterable, List, Literal, Mapping, Union, Any, Tuple, Dict

from ariautils.command_utils import Command
from ariautils import io_utils
from ariautils.misc_utils import any_in_str
from ariautils.types import RunningState
from ariautils.notifications import DesktopNotification, Alert, TimedNotification

class TimerCommand(Command):
    """An Aria Command for timers, reminders, and management thereof.
    """
    info = {
        "title": "Timers",
        "repository": "https://github.com/SKaplanOfficial/Aria",
        "documentation_link": "https://github.com/SKaplanOfficial/Aria/documentation",
        'id': "aria_core_timer",
        "version": "1.0.0",
        "description": """
            This command offers various timer-related functionalities such as starting, pausing, stopping, extending, and listing timers.
        """,
        "requirements": {},
        "extensions": {},
        "purposes": [
            "set timer", "pause timer", "stop timer", "extend timer", "list timers", "display timers"
        ],
        "targets": [
            "timer", "reminder", "10 minutes", "an hour", "several miutes", "named TimerA", "about TimerSubject",
        ],
        "keywords": [
            "aria", "command", "core", "timing", "reminders", "timers", "utility", "productivity",
        ],
        "example_usage": [
            ("start a timer for 30 seconds", "Create a new timer with a duration of 30 seconds."),
            ("remind me to do homework in 10 minutes", "Create a new named timer/reminder with a duration of 10 minutes."),
            ("set a timer for half an hour", "Create a new timer with a duration of 30 minutes."),
            ("cancel that timer", "Cancel the most recently created timer."),
            ("pause the timer for cake", "Pause the timer with the specified name."),
            ("stop all timers", "Stop all currently running timers."),
            ("extend the reminder for homework by 20 minutes", "Add 20 minutes to an existing timer/reminder."),
            ("list all timers", "Display a list of timers, organized by state."),
        ],
        "help": [
            "This command is designed to accomodate a large amount of variety in the structure and content of its inputs. Use the provided example usages only as rough guidelines. If the command does not support an input format that you beleive to be intuitive, please submit it in a bug report.",
        ],
        "contact_details": {
            "author": "Stephen Kaplan",
            "email": "stephen.kaplan@maine.edu",
            "website": "http://skaplan.io",
        },
        "info_version": "0.9.0",
    }

    # Stores information about each timer and tracks their status
    timers = {}

    # Stacks of timer IDs to simplify actions acting on "last" timer of given state
    stacks = {
        RunningState.RUNNING: [],
        RunningState.PAUSED: [],
        RunningState.STOPPED: [],
        RunningState.FINISHED: [],
    }

    def execute(self, query: str, _origin: int) -> None:
        # Operate on query using method specified for the query type
        query_type = self.get_query_type(query, True)
        query_type[1]["func"](query, query_type[1]["args"])

    def __parse_name_reminder_args(self, name_args: List[str], reminder_args: List[Tuple[str, ...]]) -> str:
        """Internal method to obtain the name string of a timer or reminder from the pasrsed data of an input query.

        :param name_args: A list of strings making up the direct name of a timer. Not all timers will have a name string specified via the input query, or they may have an implicit name specified in the form of a reminder. Thus, name_args may be an empty list.
        :type name_args: List[str]
        :param reminder_args: A list of tuples that define the name of a reminder-type timer. The first value in the tuple indicates the phrasing of the query (e.g. reminder 'about' vs. 'for'), while the remaining values form the name of the timer.
        :type reminder_args: List[Tuple[str, ...]]
        :return: The timer name specified in the input query.
        :rtype: str
        """
        if reminder_args != []:
            return reminder_args[0][1]
        elif name_args != []:
            return name_args[0]
        return "Unnamed Timer"

    def __get_target_timers(self, target: Literal["last", "all", "named"], of_state: RunningState, parsed_args: Dict[str, List[Union[str, Tuple[str, ...]]]]) -> List[Dict[int, Dict[str, Any]]]:
        """Internal method to obtain a list of timers in the specified state, adjusted based on the value of target.

        :param target: Specifier for which timer(s) are desired, directs this method where to obtain timers from. The value of this must be "last", "all", or "named". A value of "last" indicates that the last timer that entered the state specified by of_state should be returned. A value of "all" indicates that all timers in the specified state should be returned. A value of "named" indicates that the user provided a name in their query, explicitly or implicitly, and the timer with that name should be returned.
        :type target: Literal["last", "all", "named"]
        :param of_state: The state that all returned timer(s) are currently in.
        :type of_state: RunningState
        :param parsed_args: A dictionary of lists containing parsed information from the query. Parsing occurs in self.get_query_type().
        :type parsed_args: Dict[str, List[Union[str, Tuple[str, ...]]]]
        :return: A list of timers in dictionary form.
        :rtype: List[Dict[int, Dict[str, Any]]]
        """
        timers = []
        if target == "last":
            id = self.stacks[of_state][-1]
            timers.append(self.get_timer_by_id(id))
        elif target == "all":
            timers = self.get_timers_by_state(of_state)
        elif target == "named":
            print(parsed_args["name"])
            print(parsed_args["reminder"])
            if parsed_args["name"] != []:
                name = parsed_args["name"][0]
            elif parsed_args["reminder"] != []:
                name = parsed_args["reminder"][0][1]
            named_timer = self.get_timer_by_name(name)
            if named_timer != None:
                timers.append(named_timer)
        return timers

    def __new_timer(self, _query: str, args: Dict[str, List[Union[str, Tuple[str, ...]]]]) -> None:
        """Internal method that interfaces between query types aiming to create new timers and the public start_timer method. This method calls the start_timer method after extracting data from the query and providing feedback to users; it does not create a new timer itself.
 
        :param query: The raw text of the user's query. Not currently used, but kept for future purposes.
        :type query: str
        :param args: A dictionary of lists containing parsed information from the query. Parsing occurs in self.get_query_type().
        :type args: Dict[str, List[Union[str, Tuple[str, ...]]]]
        """
        duration = self.__parse_duration_args(args["duration"])
        name = self.__parse_name_reminder_args(args["name"], args["reminder"])
        id = len(self.timers)

        if args["reminder"] != []:
            io_utils.sprint("Alright, I'll remind you " + args["reminder"][0][0] + " " + args["reminder"][0][1] + " in " + self.timedelta_str(duration))
        elif args["name"] != []:
            io_utils.sprint("Alright, I made a new timer with the name '" + args["name"][0] + "' and ID " + str(id) + ". It's scheduled to go off in " + self.timedelta_str(duration))
        else:
            io_utils.sprint("Starting a new timer for " + self.timedelta_str(duration))

        self.start_timer(duration = duration, name = name, function = self.__on_timer_finish, args = (id, ), track = True)

    def __pause_timer(self, _query: str, args: List[Union[Dict[str, List[Union[str, Tuple[str, ...]]]], str]]) -> None:
        """Wraps the public pause_timer method. This method calls the pause_timer method after extracting data from the query, then provides feedback to the user; it does not pause running timers itself.

        :param _query: The raw text of the user's query. Not currently used, but kept for future purposes.
        :type _query: str
        :param args: A list containing a dictionary of parsed values and a specifier for the type of target this command should act on.
        :type args: List[Union[Dict[str, List[Union[str, Tuple[str, ...]]]], str]]
        """
        timers = self.__get_target_timers(args[1], RunningState.RUNNING, args[0])
        for timer in timers:
            self.pause_timer(timer)
            time_remaining = self.timedelta_str(timer["duration"] - timer["elapsed"])
            io_utils.sprint("Paused timer with ID " + str(timer["id"]) + "  and name '" + timer["name"] + "'. It has " + time_remaining + " remaining.")

    def __continue_timer(self, _query: str, args: List[Union[Dict[str, List[Union[str, Tuple[str, ...]]]], str]]) -> None:
        """Wraps the public continue_timer method. This method calls the continue_timer method after extracting data from the query, then provides feedback to the user; it does not continue paused timers itself.

        :param _query: The raw text of the user's query. Not currently used, but kept for future purposes.
        :type _query: str
        :param args: A list containing a dictionary of parsed values and a specifier for the type of target this command should act on.
        :type args: List[Union[Dict[str, List[Union[str, Tuple[str, ...]]]], str]]
        """
        timers = self.__get_target_timers(args[1], RunningState.PAUSED, args[0])
        for timer in timers:
            self.continue_timer(timer)
            time_remaining = self.timedelta_str(timer["duration"] - timer["elapsed"])
            io_utils.sprint("Resumed timer with ID " + str(timer["id"]) + "  and name '" + timer["name"] + "'. It has " + time_remaining + " remaining.")

    def __stop_timer(self, _query: str, args: List[Union[Dict[str, List[Union[str, Tuple[str, ...]]]], str]]) -> None:
        """Wraps the public stop_timer method. This method calls the stop_timer method after extracting data from the query, then provides feedback to the user; it does not stop running timers itself.

        :param _query: The raw text of the user's query. Not currently used, but kept for future purposes.
        :type _query: str
        :param args: A list containing a dictionary of parsed values and a specifier for the type of target this command should act on.
        :type args: List[Union[Dict[str, List[Union[str, Tuple[str, ...]]]], str]]
        """
        timers = self.__get_target_timers(args[1], RunningState.RUNNING, args[0])
        for timer in timers:
            self.stop_timer(timer)
            if "elapsed" in timer:
                time_remaining = self.timedelta_str(timer["duration"] - timer["elapsed"])
            else:
                time_remaining = self.timedelta_str(timer["duration"] - (datetime.now() - timer["start_time"]))
            io_utils.sprint("Stopped timer with ID " + str(timer["id"]) + "  and name '" + timer["name"] + "'. It had " + time_remaining + " remaining.")

    def __repeat_timer(self, _query: str, args: List[Union[Dict[str, List[Union[str, Tuple[str, ...]]]], str]]) -> None:
        """Repeats a finished timer by creating a new timer with the same information (i.e. duration, name, function, and args) as the previous one.

        :param _query: The raw text of the user's query. Not currently used, but kept for future purposes.
        :type _query: str
        :param args: A list containing a dictionary of parsed values and a specifier for the type of target this command should act on.
        :type args: List[Union[Dict[str, List[Union[str, Tuple[str, ...]]]], str]]
        """
        timers = self.__get_target_timers(args[1], RunningState.FINISHED, args[0])
        for timer in timers:
            if timer["state"] == RunningState.FINISHED:
                self.stacks[RunningState.FINISHED].remove(timer["id"])
                self.start_timer(duration = timer["duration"], name = timer["name"], function = timer["function"], args = (id, ), track = True)
                time_remaining = self.timedelta_str(timer["duration"])
                io_utils.sprint("Restarted timer with ID " + str(timer["id"]) + "  and name '" + timer["name"] + "'. It has " + time_remaining + " remaining.")

    def __extend_timer(self, _query: str, args: List[Union[Dict[str, List[Union[str, Tuple[str, ...]]]], str]]) -> None:
        """Wraps the public extend_timer method. This method calls the extend_timer method after extracting data from the query, then provides feedback to the user; it does not extend running timers itself.

        :param _query: The raw text of the user's query. Not currently used, but kept for future purposes.
        :type _query: str
        :param args: A list containing a dictionary of parsed values and a specifier for the type of target this command should act on.
        :type args: List[Union[Dict[str, List[Union[str, Tuple[str, ...]]]], str]]
        """
        extension_duration = self.__parse_duration_args(args[0]["duration"])
        timers = self.__get_target_timers(args[1], RunningState.RUNNING, args[0])
        for timer in timers:
            if timer["state"] == RunningState.RUNNING:
                self.extend_timer(timer, extension_duration)
                time_remaining = self.timedelta_str(timer["duration"])
                io_utils.sprint("Extended timer with ID " + str(timer["id"]) + "  and name '" + timer["name"] + "'. It has " + time_remaining + " remaining.")
        
    def __list_timers(self, _query: str, args: List[Union[Dict[str, List[Union[str, Tuple[str, ...]]]], str]]) -> None:
        """Lists all timers, organized by their running state.

        :param _query: The raw text of the user's query. Not currently used, but kept for future purposes.
        :type _query: str
        :param args: A list containing a dictionary of parsed values and a specifier for the type of target this command should act on.
        :type args: List[Union[Dict[str, List[Union[str, Tuple[str, ...]]]], str]]
        """
        for state in RunningState:
            timers = self.get_timers_by_state(state)
            if timers == []:
                io_utils.sprint("You don't have any " + state.name.lower() + " timers.")
            elif len(timers) == 1:
                io_utils.sprint("You have one " + state.name.lower() + " timer: " + timers[0]["name"] + " with ID " + str(timers[0]["id"]) + ".")
            else:
                io_utils.sprint("You have " + len(timers) + " " + state.name.lower() + " timers:")
                for timer in timers:
                    io_utils.sprint(timer["name"] + " with ID " + str(timer["id"]) + ".")

    def __parse_duration_args(self, duration_args: List[Tuple[str, ...]]) -> timedelta:
        """Constructs a timedelta object from the values and units mentioned in the user's query.

        :param duration_args: A list of tuples specifying amounts and units of time. The first value is a number (as a string), followed by some representation of a unit of time. Each tuple represents one pair of number and time unit in the user's query. The total duration is the sum of the durations specified by each tuple.
        :type duration_args: List[Tuple[str, ...]]
        :return: A timedelta object representing the duration of time represented in the user's query.
        :rtype: timedelta
        """
        print(duration_args)
        s = m = h = d = w = 0
        for re_match in duration_args:
            for index, group in enumerate(re_match):
                if "y" in group:
                    d += 365 * float(re_match[index - 1])
                elif "mon" in group:
                    w += 4 * float(re_match[index - 1])
                elif "w" in group:
                    w += float(re_match[index - 1])
                elif "day" in group:
                    d += float(re_match[index - 1])
                elif "h" in group:
                    h += float(re_match[index - 1])
                elif "m" in group:
                    m += float(re_match[index - 1])
                elif "second" in group:
                    s += float(re_match[index - 1])
                elif "d" in group:
                    print(duration_args, group, re_match[index - 1])
                    d += float(re_match[index - 1])
                elif "s" in group:
                    s += float(re_match[index - 1])

        return timedelta(seconds=s, minutes=m, hours=h, days=d, weeks=w)

    def timedelta_str(self, timedelta: timedelta) -> str:
        """Creates a string from a timedelta object of the form "A days, B hours, C minutes, and D seconds" where D may be an integer or a float. If the full duration of the timedelta can be captured by one unit, then the string will be of the form "A days" or "C minutes", and so on.

        :param timedelta: The timedelta to create a string representation of.
        :type timedelta: timedelta
        :return: The string representing of the timedelta duration.
        :rtype: str
        """
        string = str(timedelta).replace(":", " hour ", 1).replace(":", " minute ", 1) + " second "
        parts = string.split()

        index = 0
        while index < len(parts):
            if parts[index] == "0" or parts[index] == "00":
                parts.pop(index)
                parts.pop(index)
                continue
            elif parts[index].startswith("0"):
                parts[index] = parts[index][1]

            try:
                if float(parts[index]) > 1:
                    parts[index + 1] = parts[index + 1].rstrip() + "s"
            except:
                pass
            index += 1

        if len(parts) > 2:
            parts.insert(-2, "and")

        string = " ".join(parts)
        return string

    def get_timer_by_id(self, id: int) -> Dict[int, Dict[str, Any]]:
        """Gets the information for the timer whose ID matches the specified id.

        :param id: The ID of the timer to obtain the information of.
        :type id: int
        :return: The dictionary representation of the timer with the specified ID.
        :rtype: Dict[int, Dict[str, Any]]
        """
        return self.timers[id]

    def get_timer_by_name(self, name, require_exact = False) -> Dict[int, Dict[str, Any]]:
        """Gets the information for the timer whose name matches the specified name.

        :param name: The name of the timer to obtain the information of.
        :type name: str
        :param require_exact: Whether to require an exact match or accept a partial match to the timer's true name, defaults to False.
        :type require_exact: bool, optional
        :return: The dictionary representation of the timer with the specified ID.
        :rtype: Dict[int, Dict[str, Any]]
        """
        for timer in self.timers.values():
            if require_exact:
                if name == timer["name"]:
                    return timer
            else:
                if name in timer["name"]:
                    return timer

    def get_timers_by_state(self, state: RunningState) -> List[Dict[int, Dict[str, Any]]]:
        """Gets a list of timers in the specified state.

        :param state: The state that timers must be in to be included in the returned list.
        :type state: RunningState
        :return: A list of dictionary representation of all timers currently in the specified state.
        :rtype: List[Dict[int, Dict[str, Any]]]
        """
        return [self.timers[t] for t in self.timers if self.timers[t]["state"] is state]

    def start_timer(self, duration: timedelta, name: str = "New Timer", function: Callable[..., Any] = None, args: Union[Iterable, None] = (), kwargs: Union[Mapping[str, Any], None] = {}, track: bool = False) -> threading.Timer:
        """Creates a new timer and starts it in a separate Timer thread.

        :param duration: The interval of the Timer thread before its target function is called.
        :type duration: timedelta
        :param name: The name of the timer, defaults to "New Timer".
        :type name: str, optional
        :param function: The function that the Timer thread will call upon completion, defaults to None.
        :type function: Callable[..., Any], optional
        :param args: The arguments to pass to the Timer thread's target function upon completion of the timer, defaults to ().
        :type args: Union[Iterable, None], optional
        :param kwargs: The keyword arguments to pass to the Timer thread's target function, defaults to {}.
        :type kwargs: Union[Mapping[str, Any], None], optional
        :param track: Whether to track this timer in the aria_core_timer command's list of timers, defaults to False. Only timers that users are aware of should be tracked.
        :type track: bool, optional
        :return: A reference to the Timer thread.
        :rtype: threading.Timer
        """
        timer_thread = threading.Timer(interval = duration.total_seconds(), function = function, args = args, kwargs = kwargs)
        if track:
            id = len(self.timers)
            self.timers[id] = {
                    "id": id,
                    "thread": timer_thread,
                    "start_time": datetime.now(),
                    "duration": duration,
                    "name": name,
                    "callback": function,
                    "args": args,
                    "kwargs": kwargs,
                    "state": RunningState.RUNNING,
            }
            self.stacks[RunningState.RUNNING].append(id)
        timer_thread.start()
        return timer_thread

    def pause_timer(self, timer: Dict[int, Dict[str, Any]]) -> None:
        """Pauses a currently running timer.

        :param timer: The dictionary object of the timer to pause.
        :type timer: Dict[int, Dict[str, Any]]
        """
        if timer["state"] == RunningState.RUNNING:
            if "elapsed" in timer:
                timer["elapsed"] = timer["elapsed"] + (datetime.now() - timer["start_time"])
            else:
                timer["elapsed"] = datetime.now() - timer["start_time"]
            timer["state"] = RunningState.PAUSED
            timer["thread"].cancel()
            timer["thread"].join()
            self.stacks[RunningState.RUNNING].remove(timer["id"])
            self.stacks[RunningState.PAUSED].append(timer["id"])

    def continue_timer(self, timer: Dict[int, Dict[str, Any]]) -> None:
        """Resumes a currently paused timer.

        :param timer: The dictionary object of the timer to resume.
        :type timer: Dict[int, Dict[str, Any]]
        """
        if timer["state"] == RunningState.PAUSED:
            remaining_duration = (timer["duration"] - timer["elapsed"])
            new_thread = threading.Timer(interval = remaining_duration.total_seconds(), function = timer["callback"], args = timer["args"], kwargs = timer["kwargs"])
            timer["thread"] = new_thread
            timer["start_time"] = datetime.now()
            timer["state"] = RunningState.RUNNING
            new_thread.start()
            self.stacks[RunningState.PAUSED].remove(timer["id"])
            self.stacks[RunningState.RUNNING].append(timer["id"])

    def extend_timer(self, timer: Dict[int, Dict[str, Any]], extension_duration: timedelta) -> None:
        """Extends the duration of a currently running timer.

        :param timer: The dictionary object of the timer to extend.
        :type timer: Dict[int, Dict[str, Any]]
        :param extension_duration: The duration to extend the timer by.
        :type extension_duration: timedelta
        """
        total_duration = timer["duration"] + extension_duration
        elapsed_time = datetime.now() - timer["start_time"]
        remaining_duration = total_duration - elapsed_time
        timer["thread"].cancel()
        timer["thread"].join()
        new_thread = threading.Timer(interval = remaining_duration.total_seconds(), function = timer["callback"], args = timer["args"], kwargs = timer["kwargs"])
        timer["thread"] = new_thread
        timer["duration"] = total_duration
        new_thread.start()

    def stop_timer(self, timer: Dict[int, Dict[str, Any]]) -> None:
        """Stops a timer.

        :param timer: The dictionary object of the timer to stop.
        :type timer: Dict[int, Dict[str, Any]]
        """
        if timer["state"] in [RunningState.RUNNING, RunningState.PAUSED]:
            timer["state"] = RunningState.STOPPED
            timer["thread"].cancel()
            timer["thread"].join()

            if timer["id"] in self.stacks[RunningState.RUNNING]:
                self.stacks[RunningState.RUNNING].remove(timer["id"])
            if timer["id"] in self.stacks[RunningState.PAUSED]:
                self.stacks[RunningState.PAUSED].remove(timer["id"])
            if timer["id"] in self.stacks[RunningState.STOPPED]:
                self.stacks[RunningState.STOPPED].append(timer["id"])

    def __on_timer_finish(self, timer_id: int) -> None:
        """Runs on completion of timers/reminders created via queries to the Timer command. This method does not run for timers created by external calls to this command's public methods; a separate callback method must be specified.

        :param timer_id: The ID of the timer.
        :type timer_id: int
        """
        timer = self.timers[timer_id]
        io_utils.sprint("Timer complete: " + timer["name"])
        self.stacks[RunningState.RUNNING].remove(timer["id"])
        self.stacks[RunningState.FINISHED].append(timer["id"])
        #DesktopNotification(content = timer["name"] + " is done!", title = "Aria - Timer Complete").show()
        #Alert("This is an alert!", "Alerted", "warning").show()
        future_time = datetime.now() + timedelta(seconds = 5)
        TimedNotification(future_time, "Hi", "How are you?")

        #(class) Alert(title="Alert!", message="Action complete!", type="informational", buttons=["Ok", "Cancel"], default_button="Ok", cancel_button="Cancel", wait=-1)

    def get_query_type(self, query: str, get_tuple: bool = False) -> Union[int, Tuple[int, Dict[str, Any]]]:
        # Replace natural language time specifiers with corresponding amounts and time units
        current_time = datetime.now()
        if "the morn" in query:
            if current_time.hour < 6:
                query = re.sub(r' morn[ ]?', " " + str(8 - datetime.now().hour) + " hours ", query)
            else:
                query = re.sub(r' morn[ ]?', " " + str(32 - datetime.now().hour) + " hours ", query)

        if "tonight" in query:
            if current_time.hour < 14:
                query = re.sub(r' tonight[ ]?', " " + str(19 - datetime.now().hour) + " hours ", query)
            else:
                query = re.sub(r' tonight[ ]?', " " + str(24 - datetime.now().hour) + " hours ", query)

        if "tomor" in query and "morn" in query:
            if current_time.hour < 3:
                query = re.sub(r' morn[ ]?', " " + str(8 - datetime.now().hour) + " hours ", query)
            else:
                query = re.sub(r' morn[ ]?', " " + str(32 - datetime.now().hour) + " hours ", query)

        if "a bit " in query or "little bit " in query:
            if current_time.hour < 3:
                query = re.sub(r' bit ', " 2 hours ", query)

        query = re.sub(r' me | in | by ', " ", query)
        query = re.sub(r'(a )? half (of )?(an | a )?| 1/2 (of )?(a | an )?', " 0.5 ", query)
        query = re.sub(r'( a)? third (of )?(an | a )?| 1/3 (of )?(a | an )?', " 0.33 ", query)
        query = re.sub(r'( a)? quarter (of )?(an | a )?| 1/4 (of )?(a | an )?', " 0.25 ", query)
        query = re.sub(r' an | a ', " 1 ", query)
        query = re.sub(r' couple (of )?', " 2 ", query)
        query = re.sub(r' few ', " 3 ", query)
        query = re.sub(r' several ', " 7 ", query)

        # Compute result of conditions used in multiple query types
        low_conf_time = any_in_str(["s", "m", "h", "d", "w", "y"], query)
        low_conf_extend = any_in_str(["add", "increase", "increment"], query)
        high_conf_time = any_in_str(["sec", "min", "mom", "hour", "hr", "day", "week", "mon", "year", "yr"], query)
        high_conf_start = any_in_str(["start", "begin", "set", "create", "new"], query)
        high_conf_pause = any_in_str(["pause", "halt", "adjourn", "suspend"], query)
        high_conf_continue = any_in_str(["continue", "commence", "resume", "play", "restore"], query)
        high_conf_stop = any_in_str(["stop", "cancel", "end", "terminate", "kill", "destroy"], query)
        high_conf_extend = any_in_str(["extend", "prolong", "lengthen"], query)
        high_conf_restart = any_in_str(["restart", "start over", "start again", "run again", "redo", "reset", "repeat", "rerun", "replay"], query)
        high_conf_list = re.search(r'(?:(list|enumerat|display|show)[a-z ]*(timer))|(?:(what|which)[a-z ]*(timer))', query) != None
        high_conf_last = any_in_str(["last", "previous", "prev", "recent", "latest", "that"], query)

        # Extract duration, name, and reminder information from query
        duration_args = re.compile(r' ([0-9]*\.?[0-9]+)[ ]?(second|sec|minute|min|moment|mom|hour|hr|day|week|month|mon|year|yr|s|m|h|d|w|y)').findall(query)
        name_args = re.compile(r' (?:called|call|named|name|titled|title|labelled|label|designated|designation)(?: it | )([a-z0-9]+)(?: |$)').findall(query)
        reminder_args = re.compile(r'(?:remind|tell|prompt|for)[a-z0-9 ]*(to|about|for) ([a-z ]*)(?: |$)').findall(query)
        parsed_args = {
            "duration": duration_args,
            "name": name_args,
            "reminder": reminder_args,
        }

        # Define conditions and associated method for each execution pathway
        __query_type_map = {
            ### List
            7000: { # List timers
                "conditions": [high_conf_list, "timer" in query],
                "func": self.__list_timers,
                "args": parsed_args,
            },

            ### Extend
            6200: { # Extend Named/Reminder Timer
                "conditions": [high_conf_extend, "timer" in query or "remind" in query, name_args != [] or reminder_args != []],
                "func": self.__extend_timer,
                "args": [parsed_args, "named"]
            },
            6000: { # Extend Last Timer
                "conditions": [high_conf_extend, high_conf_last, "timer" in query],
                "func": self.__extend_timer,
                "args": [parsed_args, "last"]
            },

            ### Repeat
            5200: { # Repeat Named/Reminder Timer
                "conditions": [high_conf_restart, "timer" in query, name_args != [] or reminder_args != []],
                "func": self.__repeat_timer,
                "args": [parsed_args, "named"]
            },
            5100: { # Repeat All Stopped Timers
                "conditions": [high_conf_restart, any_in_str(["all", "stopped", "paused", "halted", "suspended"], query), "timers" in query],
                "func": self.__repeat_timer,
                "args": [parsed_args, "all"]
            },
            5000: { # Repeat Last Timer
                "conditions": [high_conf_restart, high_conf_last, "timer" in query],
                "func": self.__repeat_timer,
                "args": [parsed_args, "last"]
            },

            ### Stop
            4200: { # Stop Named/Reminder Timer
                "conditions": [high_conf_stop, "timer" in query, name_args != [] or reminder_args != []],
                "func": self.__stop_timer,
                "args": [parsed_args, "named"]
            },
            4100: { # Stop All Timers
                "conditions": [high_conf_stop, any_in_str(["current", "active", "the", "all", "every", "each", "my"], query), "timer" in query],
                "func": self.__stop_timer,
                "args": [parsed_args, "all"]
            },
            4000: { # Stop Last Timer
                "conditions": [high_conf_stop, high_conf_last, "timer" in query],
                "func": self.__stop_timer,
                "args": [parsed_args, "last"]
            },

            ### Continue
            3200: { # Continue Paused Named/Reminder Timer
                "conditions": [high_conf_continue, "timer" in query, name_args != [] or reminder_args != []],
                "func": self.__continue_timer,
                "args": [parsed_args, "named"]
            },
            3100: { # Continue All Paused Timers
                "conditions": [high_conf_stop, any_in_str(["all", "paused", "halted", "suspended"], query), "timers" in query],
                "func": self.__continue_timer,
                "args": [parsed_args, "all"]
            },
            3000: { # Continue Last Paused Timer
                "conditions": [high_conf_continue, high_conf_last, "timer" in query],
                "func": self.__continue_timer,
                "args": [parsed_args, "last"]
            },

            ### Pause
            2200: { # Pause Named/Reminder Timer
                "conditions": [high_conf_pause, "timer" in query, name_args != [] or reminder_args != []],
                "func": self.__pause_timer,
                "args": [parsed_args, "named"]
            },
            2100: { # Pause All Timers
                "conditions": [high_conf_pause, any_in_str(["current", "active", "the", "all", "every", "each", "my"], query), "timers" in query],
                "func": self.__pause_timer,
                "args": [parsed_args, "all"]
            },
            2000: { # Pause Last Timer
                "conditions": [high_conf_pause, high_conf_last, "timer" in query],
                "func": self.__pause_timer,
                "args": [parsed_args, "last"]
            },

            ### Start
            1200: { # Start Named Timer
                "conditions": ["timer" in query, high_conf_time, name_args != []],
                "func": self.__new_timer,
                "args": parsed_args
            },
            1100: { # Set Reminder
                "conditions": [high_conf_time, reminder_args != []],
                "func": self.__new_timer,
                "args": parsed_args
            },
            1000: { # Start Unnamed Timer
                "conditions": [high_conf_start, "timer" in query, high_conf_time],
                "func": self.__new_timer,
                "args": parsed_args
            },



            ### Extend
            600: { # Extend Last Timer
                "conditions": [low_conf_extend, high_conf_last, "timer" in query],
                "func": self.__extend_timer,
                "args": [parsed_args, "last"]
            },

            ### Stop
            410: { # Stop All Timers
                "conditions": [high_conf_stop, "timers" in query],
                "func": self.__stop_timer,
                "args": [parsed_args, "all"]
            },
            400: { # Stop Last Timer
                "conditions": [high_conf_stop, "timer" in query],
                "func": self.__stop_timer,
                "args": [parsed_args, "last"]
            },

            ### Pause
            210: { # Pause All Timers
                "conditions": [high_conf_pause, "timers" in query],
                "func": self.__pause_timer,
                "args": [parsed_args, "all"],
            },
            200: { # Pause Last Timer
                "conditions": [high_conf_pause, "timer" in query],
                "func": self.__pause_timer,
                "args": [parsed_args, "last"],
            },

            ### Start
            100: { # Start Unnamed Timer
                "conditions": ["timer" in query, high_conf_time],
                "func": self.__new_timer,
                "args": parsed_args,
            },



            ### Start
            12: { # Start Named Timer
                "conditions": ["timer" in query, low_conf_time, name_args != [], len(query.replace("timer ", "")) > 1],
                "func": self.__new_timer,
                "args": parsed_args,
            },
            11: { # Set Reminder
                "conditions": [low_conf_time, reminder_args != []],
                "func": self.__new_timer,
                "args": parsed_args,
            },
            10: { # Start Unnamed Timer
                "conditions": ["timer" in query, low_conf_time, len(query.replace("timer ", "")) > 1],
                "func": self.__new_timer,
                "args": parsed_args,
            },
        }

        # Obtain query type and associated execution data
        for key, query_type in __query_type_map.items():
            if all(query_type["conditions"]):
                if get_tuple:
                    return (key, query_type)
                return key
        return 0

command = TimerCommand()
"""This module provides timer and timer-related functionalities, including creating, pausing, stopping, extending, and listing timers, for use in Aria.
"""
import threading
import re
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable, Iterable, List, Mapping, Union, Any

from ariautils.command_utils import Command
from ariautils import io_utils
from ariautils.misc_utils import any_in_str, display_notification

class RunningStates(Enum):
    """Levels of running states for timers in Aria.
    """
    RUNNING = 1
    PAUSED = 2
    STOPPED = 3
    FINISHED = 4

class TimerCommand(Command):
    """An Aria Command for timers, reminders, and management thereof.
    """
    info = {
        "title": "Timers",
        "repository": "https://github.com/SKaplanOfficial/Aria",
        "documentation_link": "https://github.com/SKaplanOfficial/Aria",
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
        RunningStates.RUNNING: [],
        RunningStates.PAUSED: [],
        RunningStates.STOPPED: [],
        RunningStates.FINISHED: [],
    }

    def execute(self, query, _origin):
        query_type = self.get_query_type(query, True)
        query_type[1]["func"](query, query_type[1]["args"])

    def run(self, query, operation, args):
        operation(query, args)

    def __parse_name_reminder_args(self, name_args, reminder_args):
        if reminder_args != []:
            return reminder_args[0][1]
        elif name_args != []:
            return name_args[0]
        return "Unnamed Timer"

    def __new_timer(self, query, args):
        duration = self.__parse_duration_args(args["duration"])
        name = self.__parse_name_reminder_args(args["name"], args["reminder"])
        id = len(self.timers)

        if args["reminder"] != []:
            io_utils.sprint("Alright, I'll remind you " + args["reminder"][0][0] + " " + args["reminder"][0][1] + " in " + self.timedelta_str(duration))
        elif args["name"] != []:
            io_utils.sprint("Alright, I made a new timer with the name '" + args["name"][0] + "' and ID " + str(id) + ". It's scheduled to go off in " + self.timedelta_str(duration))
        else:
            io_utils.sprint("Starting a new timer for " + self.timedelta_str(duration))

        self.start_timer(duration = duration, name = name, function = self.on_timer_finish, args = (id, ), track = True)

    def __get_target_timers(self, target_str, of_state, parsed_args):
        timers = []
        if target_str == "last":
            id = self.stacks[of_state][-1]
            timers.append(self.get_timer_by_id(id))
        elif target_str == "all":
            timers = self.get_timers_by_state(of_state)
        elif target_str == "named":
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

    def __pause_timer(self, query, args):
        timers = self.__get_target_timers(args[1], RunningStates.RUNNING, args[0])
        for timer in timers:
            self.pause_timer(timer)
            time_remaining = self.timedelta_str(timer["duration"] - timer["elapsed"])
            io_utils.sprint("Paused timer with ID " + str(timer["id"]) + "  and name '" + timer["name"] + "'. It has " + time_remaining + " remaining.")

    def __continue_timer(self, query, args):
        timers = self.__get_target_timers(args[1], RunningStates.PAUSED, args[0])
        for timer in timers:
            self.continue_timer(timer)
            time_remaining = self.timedelta_str(timer["duration"] - timer["elapsed"])
            io_utils.sprint("Resumed timer with ID " + str(timer["id"]) + "  and name '" + timer["name"] + "'. It has " + time_remaining + " remaining.")

    def __stop_timer(self, query, args):
        timers = self.__get_target_timers(args[1], RunningStates.RUNNING, args[0])
        for timer in timers:
            self.stop_timer(timer)
            if "elapsed" in timer:
                time_remaining = self.timedelta_str(timer["duration"] - timer["elapsed"])
            else:
                time_remaining = self.timedelta_str(timer["duration"] - (datetime.now() - timer["start_time"]))
            io_utils.sprint("Stopped timer with ID " + str(timer["id"]) + "  and name '" + timer["name"] + "'. It had " + time_remaining + " remaining.")

    def __repeat_timer(self, query, args):
        timers = self.__get_target_timers(args[1], RunningStates.FINISHED, args[0])
        for timer in timers:
            if timer["state"] == RunningStates.FINISHED:
                self.stacks[RunningStates.FINISHED].remove(timer["id"])
                self.start_timer(duration = timer["duration"], name = timer["name"], function = timer["function"], args = (id, ), track = True)
                time_remaining = self.timedelta_str(timer["duration"])
                io_utils.sprint("Restarted timer with ID " + str(timer["id"]) + "  and name '" + timer["name"] + "'. It has " + time_remaining + " remaining.")

    def __extend_timer(self, query, args):
        extension_duration = self.__parse_duration_args(args[0]["duration"])
        timers = self.__get_target_timers(args[1], RunningStates.RUNNING, args[0])
        for timer in timers:
            if timer["state"] == RunningStates.RUNNING:
                self.extend_timer(timer, extension_duration)
                time_remaining = self.timedelta_str(timer["duration"])
                io_utils.sprint("Extended timer with ID " + str(timer["id"]) + "  and name '" + timer["name"] + "'. It has " + time_remaining + " remaining.")
        
    def __list_timers(self, query, args):
        for state in RunningStates:
            timers = self.get_timers_by_state(state)
            if timers == []:
                io_utils.sprint("You don't have any " + state.name.lower() + " timers.")
            elif len(timers) == 1:
                io_utils.sprint("You have one " + state.name.lower() + " timer: " + timers[0]["name"] + " with ID " + str(timers[0]["id"]) + ".")
            else:
                io_utils.sprint("You have " + len(timers) + " " + state.name.lower() + " timers:")
                for timer in timers:
                    io_utils.sprint(timer["name"] + " with ID " + str(timer["id"]) + ".")

    def __parse_duration_args(self, duration_args):
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

    def timedelta_str(self, timedelta):
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

    def get_timer_by_id(self, id):
        return self.timers[id]

    def get_timer_by_name(self, name, require_exact = False):
        for timer in self.timers.values():
            if require_exact:
                if name == timer["name"]:
                    return timer
            else:
                if name in timer["name"]:
                    return timer

    def get_timers_by_state(self, state):
        return [self.timers[t] for t in self.timers if self.timers[t]["state"] is state]

    def start_timer(self, duration: timedelta, name: str = "New Timer", function: Callable[..., Any] = None, args: Union[Iterable, None] = (), kwargs: Union[Mapping[str, Any], None] = {}, track: bool = False) -> threading.Timer:
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
                    "state": RunningStates.RUNNING,
            }
            self.stacks[RunningStates.RUNNING].append(id)
        timer_thread.start()
        return timer_thread

    def pause_timer(self, timer) -> None:
        if timer["state"] == RunningStates.RUNNING:
            if "elapsed" in timer:
                timer["elapsed"] = timer["elapsed"] + (datetime.now() - timer["start_time"])
            else:
                timer["elapsed"] = datetime.now() - timer["start_time"]
            timer["state"] = RunningStates.PAUSED
            timer["thread"].cancel()
            timer["thread"].join()
            self.stacks[RunningStates.RUNNING].remove(timer["id"])
            self.stacks[RunningStates.PAUSED].append(timer["id"])

    def continue_timer(self, timer) -> None:
        if timer["state"] == RunningStates.PAUSED:
            remaining_duration = (timer["duration"] - timer["elapsed"])
            new_thread = threading.Timer(interval = remaining_duration.total_seconds(), function = timer["callback"], args = timer["args"], kwargs = timer["kwargs"])
            timer["thread"] = new_thread
            timer["start_time"] = datetime.now()
            timer["state"] = RunningStates.RUNNING
            new_thread.start()
            self.stacks[RunningStates.PAUSED].remove(timer["id"])
            self.stacks[RunningStates.RUNNING].append(timer["id"])

    def extend_timer(self, timer, extension_duration) -> None:
        total_duration = timer["duration"] + extension_duration
        elapsed_time = datetime.now() - timer["start_time"]
        remaining_duration = total_duration - elapsed_time
        timer["thread"].cancel()
        timer["thread"].join()
        new_thread = threading.Timer(interval = remaining_duration.total_seconds(), function = timer["callback"], args = timer["args"], kwargs = timer["kwargs"])
        timer["thread"] = new_thread
        timer["duration"] = total_duration
        new_thread.start()

    def stop_timer(self, timer) -> None:
        if timer["state"] in [RunningStates.RUNNING, RunningStates.PAUSED]:
            timer["state"] = RunningStates.STOPPED
            timer["thread"].cancel()
            timer["thread"].join()

            if timer["id"] in self.stacks[RunningStates.RUNNING]:
                self.stacks[RunningStates.RUNNING].remove(timer["id"])
            if timer["id"] in self.stacks[RunningStates.PAUSED]:
                self.stacks[RunningStates.PAUSED].remove(timer["id"])
            if timer["id"] in self.stacks[RunningStates.STOPPED]:
                self.stacks[RunningStates.STOPPED].append(timer["id"])

    def on_timer_finish(self, timer_id):
        timer = self.timers[timer_id]
        io_utils.sprint("Timer complete: " + timer["name"])
        self.stacks[RunningStates.RUNNING].remove(timer["id"])
        self.stacks[RunningStates.FINISHED].append(timer["id"])
        display_notification(content = "Hey")

    def get_query_type(self, query, get_tuple = False):
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

        duration_args = re.compile(r' ([0-9]*\.?[0-9]+)[ ]?(second|sec|minute|min|moment|mom|hour|hr|day|week|month|mon|year|yr|s|m|h|d|w|y)').findall(query)
        name_args = re.compile(r' (?:called|call|named|name|titled|title|labelled|label|designated|designation)(?: it | )([a-z0-9]+)(?: |$)').findall(query)
        reminder_args = re.compile(r'(?:remind|tell|prompt|for)[a-z0-9 ]*(to|about|for) ([a-z ]*)(?: |$)').findall(query)
        parsed_args = {
            "duration": duration_args,
            "name": name_args,
            "reminder": reminder_args,
        }

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
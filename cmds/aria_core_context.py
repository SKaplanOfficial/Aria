"""An Aria plugin for tracking context changes in a users' system.
"""

import os
from pathlib import Path
import subprocess
import PyXA
import re
import threading
from datetime import datetime
from time import sleep
from typing import Any, Dict, List, Tuple, Union

from ariautils import command_utils
from ariautils.tracking_utils import TrackingManager


class CoreContext(command_utils.Command):
    info = {
        "title": "Run Shortcuts",
        "repository": "https://github.com/SKaplanOfficial/Aria",
        'id': "aria_core_context",
        "version": "1.0.0",
        "description": """
            This plugin allows users to execute Siri Shortcuts.
        """,
        "requirements": {},
        "extensions": {},
        "purposes": [
            "run shortcut", "run shortcut with input"
        ],
        "targets": [
            "shortcut",
        ],
        "keywords": [
            "aria", "command", "shortcut", "shortcuts.app", "macOS"
        ],
        "example_usage": [
            ("run shortcut open maps", "Runs the Shortcut titled 'Open Maps'."),
            ("run the shortcut called Open Maps", "Runs the Shortcut titled 'Open Maps'."),
            ("run shortcut open maps with input test", "Runs the Shortcut titled 'Open Maps' and pass the string 'test' as input to it."),
        ],
        "contact_details": {
            "author": "Stephen Kaplan",
            "email": "stephen.kaplan@maine.edu",
            "website": "http://skaplan.io",
        },
        "info_version": "0.9.0",
    }

    def __init__(self):
        super().__init__()
        self.looping = True #: Whether the context loop is running
        self.current_application = None #: The non-Terminal application that was most recently active
        self.current_applications = [] #: A list of currently running applications
        self.previous_applications = [] #: A list of the last 10 closed applications
        self.previous_input = None #: The previously entered input

        self.timer = 0
        self.seconds_to_checkpoint = 3

        self.context_tracker = TrackingManager.init_tracker(
            title="context",
            item_structure={

                "start_time" : float,
                "end_time" : float,
                "frequency" : int,
                "targets" : list,
            },
            data_folder_path="./data"
        )
        self.context_tracker.load_data()
        self.current_context = self.context_tracker.new_item([0, 0, 0, []])

        context_thread = threading.Thread(target=self.__context_loop, name="Context", daemon=True)
        context_thread.start()

        print(self.get_selected_items())

    def execute(self, query: str, _origin: int) -> None:
        query_type = self.get_query_type(query, True)
        query_type[1]["func"](query, query_type[1]["args"])

    def __context_loop(self):
        """Updates the context tracker once a second.
        """
        while self.looping:
            self.__update_context()
            sleep(1)

    def __update_context(self):
        current_application = PyXA.current_application().executable_url.path()
        current_applications = PyXA.running_applications().executable_url()
        current_applications = [x.path() for x in current_applications]

        # Track current application
        if current_application != "/System/Applications/Utilities/Terminal.app":
            self.current_application = current_application

        # Track previous application
        if len(self.previous_applications) == 0 or self.current_application != self.previous_applications[-1]:
            self.previous_applications.append(self.current_application)

        # Track running apps
        now = datetime.now()
        current_time = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
        self.current_context = self.context_tracker.new_item([current_time, current_time, 0, current_applications])

        # Initialize history
        if len(self.context_tracker.items) == 0:
            self.context_tracker.add_item(self.current_context)

        # Compare against previous context
        prev_context_obj = self.context_tracker.items[-1]
        if prev_context_obj != None and current_applications != prev_context_obj.data["targets"]:
            # Record end time of previous context, open new context
            prev_context_obj.data["end_time"] = current_time
            self.context_tracker.add_item(self.current_context)
            self.checkpoint()
        
        # Current and previous are equal at this point
        elif self.timer == -1 or current_time - self.timer > self.seconds_to_checkpoint:
            #print("Saving context history...")
            # Update previous end time (in case context doesn't change for a while)
            if prev_context_obj != None:
                prev_context_obj.data["end_time"] = current_time

            if self.current_context.data["targets"] == self.context_tracker.items[-1].data["targets"]:
                self.context_tracker.items[-1].data["frequency"] += 1

            # Export context history to context tracking csv
            self.context_tracker.save_data()
            self.checkpoint()
            self.context_tracker.load_data()

    def checkpoint(self):
        """
        Updates the timer checkpoint to the current time.
        
        Returns:
            None
        """
        now = datetime.now()
        current_time = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
        self.timer = current_time

    def blank_context(self):
        apps_to_close = [app for app in self.current_context.data["targets"]]
        for app in apps_to_close:
            if app != "/Applications/Visual Studio Code.app" and app != "/System/Library/CoreServices/Finder.app" and app != "/System/Applications/Utilities/Terminal.app":
                print("Closing " + app + "...")
                command = ["pkill", "-f", app]
                subprocess.call(command)

    def get_selected_items(self):
        print(PyXA.application("Finder").selection.url())

    def get_app_list(self):
        home_dir = str(Path.home()) 
        apps = ["/Applications/" + a for a in os.listdir("/Applications")]
        apps.extend([home_dir + "/" + a for a in os.listdir(home_dir + "/Applications")])
        apps = [a for a in apps if a.endswith(".app") and not a.startswith(".")]
        return apps

    def get_query_type(self, query: str, get_tuple: bool = False) -> Union[int, Tuple[int, Dict[str, Any]]]:
        shortcut_target = ""
        input = ""
        shortcut_name_cmd = re.search(r'(run|execute|exec)( the)? shortcut (named |name |called |titled |title )?', query)
        has_shortcut_name_cmd = shortcut_name_cmd != None
        if has_shortcut_name_cmd:
            shortcut_target = query[shortcut_name_cmd.span()[1]:]

        # Define conditions and associated method for each execution pathway
        query_type_map = {

            5000: { # Run shortcut by name - High Confidence
                "conditions": [has_shortcut_name_cmd],
                "func": self.run_shortcut,
                "args": [shortcut_target],
            },

        }

        # Obtain query type and associated execution data
        for key, query_type in query_type_map.items():
            if all(query_type["conditions"]):
                if get_tuple:
                    return (key, query_type)
                return key
        return 0

command = CoreContext()
core_context = command

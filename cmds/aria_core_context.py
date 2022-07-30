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
        "title": "Core Context",
        "repository": "https://github.com/SKaplanOfficial/Aria",
        'id': "aria_core_context",
        "version": "1.0.0",
        "description": """
            This plugin tracks context changes as users interact with a macOS system.
        """,
        "requirements": {},
        "extensions": {},
        "purposes": [
            "track context",
        ],
        "targets": [
            "shortcut",
        ],
        "keywords": [
            "aria", "command", "context", "applescript", "pyxa", "automation",
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

    looping = True #: Whether the context loop is running
    current_application = None #: The non-Terminal application that was most recently active
    current_applications = [] #: A list of currently running applications
    previous_applications = [] #: A list of the last 10 closed applications
    previous_input = None #: The previously entered input

    timer = 0
    seconds_to_checkpoint = 3

    context_tracker = TrackingManager.init_tracker(
        title="context",
        item_structure={

            "start_time" : float,
            "end_time" : float,
            "frequency" : int,
            "targets" : list,
        },
        data_folder_path="./data"
    )
    context_tracker.load_data()
    current_context = context_tracker.new_item([0, 0, 0, []])

    context_thread = None

    def __init__(self):
        super().__init__()

        if CoreContext.context_thread is None:
            CoreContext.context_thread = threading.Thread(target=self.__context_loop, name="Context", daemon=True)
            CoreContext.context_thread.start()

            self.__response = None #: The previously returned response object

    def execute(self, query: str, _origin: int) -> None:
        query_type = self.get_query_type(query, True)
        query_type[1]["func"](query, query_type[1]["args"])

    def __context_loop(self):
        """Updates the context tracker once a second.
        """
        while CoreContext.looping:
            self.__update_context()
            sleep(1)

    def __update_context(self):
        current_applications = PyXA.running_applications()

        current_application = None
        for x in current_applications:
            if x.frontmost and x.localized_name != "Terminal":
                current_application = x
                break

        # Track current application
        if current_application != None and current_application.localized_name != "Terminal":
            CoreContext.current_application = current_application

        # Track previous application
        if len(CoreContext.previous_applications) == 0 or CoreContext.current_application != CoreContext.previous_applications[-1]:
            CoreContext.previous_applications.append(CoreContext.current_application)

        # Track running apps
        now = datetime.now()
        current_time = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
        current_apps = [x.bundle_url.path() for x in current_applications]
        CoreContext.current_context = CoreContext.context_tracker.new_item([current_time, current_time, 0, current_apps])

        # Initialize history
        if len(CoreContext.context_tracker.items) == 0:
            CoreContext.context_tracker.add_item(CoreContext.current_context)

        # Compare against previous context
        prev_context_obj = CoreContext.context_tracker.items[-1]
        if prev_context_obj != None and current_apps != prev_context_obj.data["targets"]:
            # Record end time of previous context, open new context
            prev_context_obj.data["end_time"] = current_time
            CoreContext.context_tracker.add_item(CoreContext.current_context)
            self.checkpoint()
        
        # Current and previous are equal at this point
        elif CoreContext.timer == -1 or current_time - CoreContext.timer > CoreContext.seconds_to_checkpoint:
            #print("Saving context history...")
            # Update previous end time (in case context doesn't change for a while)
            if prev_context_obj != None:
                prev_context_obj.data["end_time"] = current_time

            if CoreContext.current_context.data["targets"] == CoreContext.context_tracker.items[-1].data["targets"]:
                CoreContext.context_tracker.items[-1].data["frequency"] += 1

            # Export context history to context tracking csv
            CoreContext.context_tracker.save_data()
            self.checkpoint()
            CoreContext.context_tracker.load_data()
                    
    def checkpoint(self):
        """
        Updates the timer checkpoint to the current time.
        
        Returns:
            None
        """
        now = datetime.now()
        current_time = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
        CoreContext.timer = current_time

    def blank_context(self):
        apps_to_close = [app for app in CoreContext.current_context.data["targets"]]
        for app in apps_to_close:
            if app != "Code" and app != "Finder" and app != "Terminal":
                print("Closing " + app + "...")
                command = ["pkill", "-f", app]
                subprocess.call(command)

    def set_response(self, response):
        self.__response = response

    def get_response(self, command_id: str, _token = None):
        permissions = command_utils.plugins[command_id].info.get("permissions")
        if isinstance(permissions, list) and "retrieve_previous_response" in permissions:
            return self.__response

    def get_selected_items(self, app: str = "Finder"):
        current_selection = PyXA.application(app).selection
        if not hasattr(CoreContext, "selected_items") or current_selection.xa_elem != CoreContext.selection.xa_elem:
            CoreContext.selection = current_selection
        return CoreContext.selection if CoreContext.selection is not None else []

    def get_app_list(self):
        home_dir = str(Path.home()) 
        apps = ["/Applications/" + a for a in os.listdir("/Applications")]
        apps.extend([home_dir + "/" + a for a in os.listdir(home_dir + "/Applications")])
        apps = [a for a in apps if a.endswith(".app") and not a.startswith(".")]
        return apps

    def get_query_type(self, query: str, get_tuple: bool = False) -> Union[int, Tuple[int, Dict[str, Any]]]:
        # Define conditions and associated method for each execution pathway
        query_type_map = {

            # 1: { # Run shortcut by name - High Confidence
            #     "conditions": [],
            #     "func": self.blank_context,
            #     "args": [],
            # },

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

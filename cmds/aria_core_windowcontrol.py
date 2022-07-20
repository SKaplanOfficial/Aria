"""An Aria plugin for interacting with the macOS Notes application.
"""

from typing import Any, Dict, List, Tuple, Union
import PyXA
import re

from ariautils import command_utils

class WindowControl(command_utils.Command):
    info = {
        "title": "Window Control",
        "repository": "https://github.com/SKaplanOfficial/Aria",
        'id': "aria_core_windowcontrol",
        "version": "1.0.0",
        "description": """
            This plugin allows macOS users to interact with and manage application windows.
        """,
        "requirements": {},
        "extensions": {},
        "purposes": [
            "move window", "minimize window", "maximize window", "maximize application",
        ],
        "targets": [
            "window", "app"
        ],
        "keywords": [
            "aria", "command", "window", "application", "macOS", "interface",
        ],
        "example_usage": [
            ("minimize this window", "Minimizes the current window."),
            ("maximize Maps", "Maximizes the all windows currently open for Maps.app."),
            ("align this window right", "Aligns the current window to the right."),
        ],
        "contact_details": {
            "author": "Stephen Kaplan",
            "email": "stephen.kaplan@maine.edu",
            "website": "http://skaplan.io",
        },
        "info_version": "0.9.0",
    }

    def execute(self, query: str, _origin: int) -> None:
        query_type = self.get_query_type(query, True)
        query_type[1]["func"](query, query_type[1]["args"])

    def minimize_current_window(self, _query: str, _args: List[Any]):
        """Minimizes the current window.

        .. versionadded:: 1.0.0
        """
        command_utils.plugins["aria_core_context"].current_application.front_window().collapse()

    def minimize_target_app(self, _query: str, args: List[Any]):
        """Minimizes the windows of the specified application.

        :param args: A list of arguments; the first argument is the name of the application to minimize the windows of
        :type args: List[Any]

        .. versionadded:: 1.0.0
        """
        PyXA.application(args[0]).windows().collapse()

    def maximize_target_app(self, _query: str, args: List[Any]):
        """Maximizes the windows of the specified application.

        :param args: A list of arguments; the first argument is the name of the application to maximize the windows of
        :type args: List[Any]

        .. versionadded:: 1.0.0
        """
        PyXA.application(args[0]).activate()

    def align_current_window_left(self, _query: str, args: List[Any]):
        """Positions the current window's origin at the top left of the screen, (0, 0).

        .. versionadded:: 1.0.0
        """
        PyXA.application(command_utils.plugins["aria_core_context"].current_application).front_window().set_property("position", (0, 0))

    def align_current_window_right(self, _query: str, args: List[Any]):
        """Positions the current window's origin at the top right of the screen, (screen_width - window_width, 0).

        .. versionadded:: 1.0.0
        """
        window = PyXA.application(command_utils.plugins["aria_core_context"].current_application).front_window()
        screen_width = PyXA.application("Finder").desktop.xa_elem.window().bounds().size.width
        window_width = window.xa_elem.size().get()[0]
        window.set_property("position", (screen_width - window_width, 0))

    def get_current_tab(self, _query: str, args: List[Any]):
        command_utils.plugins["aria_core_context"].current_application.front_window().current_tab

    def close_tab(self, _query: str, args: List[Any]):
        command_utils.plugins["aria_core_context"].current_application.front_window().tabs()[args[0]].close()

    def close_current_tab(self, query: str, args: List[Any]):
        command_utils.plugins["aria_core_context"].current_application.front_window().current_tab.close()

    def close_current_window(self, query: str, args: List[Any]):
        command_utils.plugins["aria_core_context"].current_application.front_window().close()

    def get_query_type(self, query: str, get_tuple: bool = False) -> Union[int, Tuple[int, Dict[str, Any]]]:
        window_target = ""
        minimize_cmd = re.search(r'(minimize|collapse|shrink) ', query)
        has_minimize_cmd = minimize_cmd != None
        if has_minimize_cmd:
            window_target = query[minimize_cmd.span()[1]:]

        maximize_cmd = re.search(r'(maximize|unminimize|uncollapse|expand) ', query)
        has_maximize_cmd = maximize_cmd != None
        if has_maximize_cmd:
            window_target = query[maximize_cmd.span()[1]:]

        has_left_align_cmd = re.search(r'(align|position|move).*left', query) != None
        has_right_align_cmd = re.search(r'(align|position|move).*right', query) != None

        # Define conditions and associated method for each execution pathway
        query_type_map = {
            5000: { # Minimize this window - High Confidence
                "conditions": [("this" in query or "current" in query) and "window" in query and has_minimize_cmd],
                "func": self.minimize_current_window,
                "args": [],
            },

            4050: { # Close current tab - High Confidence
                "conditions": [("this" in query or "current" in query) and "tab" in query],
                "func": self.close_current_tab,
                "args": [],
            },

            4040: { # Close current window - High Confidence
                "conditions": [("this" in query or "current" in query) and "window" in query],
                "func": self.close_current_window,
                "args": [],
            },

            4001: { # Send this window to right - High Confidence
                "conditions": [("this" in query or "current" in query) and "window" in query and has_right_align_cmd],
                "func": self.align_current_window_right,
                "args": [],
            },

            4000: { # Send this window to left - High Confidence
                "conditions": [("this" in query or "current" in query) and "window" in query and has_left_align_cmd],
                "func": self.align_current_window_left,
                "args": [],
            },

            502: { # Maximize target app - Medium Confidence
                "conditions": [has_maximize_cmd],
                "func": self.maximize_target_app,
                "args": [window_target],
            },

            501: { # Minimize target app - Medium Confidence
                "conditions": [has_minimize_cmd],
                "func": self.minimize_target_app,
                "args": [window_target],
            },
        }

        # Obtain query type and associated execution data
        for key, query_type in query_type_map.items():
            if all(query_type["conditions"]):
                if get_tuple:
                    return (key, query_type)
                return key
        return 0

command = WindowControl()
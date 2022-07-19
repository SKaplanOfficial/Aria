"""An Aria plugin for interacting with the macOS Shortcuts application.
"""

from typing import Any, Dict, List, Tuple, Union
import PyXA
import re

from ariautils.command_utils import Command
from ariautils import command_utils, context_utils

class ShortcutsApp(Command):
    info = {
        "title": "Run Shortcuts",
        "repository": "https://github.com/SKaplanOfficial/Aria",
        'id': "aria_extra_shortcutsapp",
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

    def execute(self, query: str, _origin: int) -> None:
        query_type = self.get_query_type(query, True)
        query_type[1]["func"](query, query_type[1]["args"])

    def run_shortcut(self, _query: str, args: List[Any]):
        """Runs the specified shortcut.

        :param args: The arguments to the command; the first arg is the name of the shortcut to run
        :type args: List[Any]

        .. versionadded:: 1.0.0
        """
        PyXA.application("Shortcuts").shortcuts().by_name(args[0]).run()

    def run_shortcut_with_input(self, _query: str, args: List[Any]):
        """Runs the specified shortcut with the provided input.

        :param args: The arguments to the command; the first arg is the name of the shortcut to run, the second arg is the input to pass to the shortcut.
        :type args: List[Any]

        .. versionadded:: 1.0.0
        """
        PyXA.application("Shortcuts").shortcuts().by_name(args[0]).run(args[1])

    def get_query_type(self, query: str, get_tuple: bool = False) -> Union[int, Tuple[int, Dict[str, Any]]]:
        shortcut_target = ""
        input = ""
        shortcut_name_cmd = re.search(r'(run|execute|exec)( the)? shortcut (named |name |called |titled |title )?', query)
        has_shortcut_name_cmd = shortcut_name_cmd != None
        if has_shortcut_name_cmd:
            shortcut_target = query[shortcut_name_cmd.span()[1]:]

        if "with input" in query:
            input = shortcut_target[shortcut_target.index("with input ")+11:]
            shortcut_target = shortcut_target[:shortcut_target.index("with")-1]
            print(input)
        elif "with" in query:
            input = shortcut_target[shortcut_target.index("with")+5:]
            shortcut_target = shortcut_target[:shortcut_target.index("with")-1]

        # Define conditions and associated method for each execution pathway
        query_type_map = {

            5001: { # Run shortcut by name with input - High Confidence
                "conditions": [has_shortcut_name_cmd and "with" in query],
                "func": self.run_shortcut_with_input,
                "args": [shortcut_target, input],
            },

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

command = ShortcutsApp()
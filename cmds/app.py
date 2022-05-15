"""
App

Last Updated: Version 0.0.2
"""

from ariautils.command_utils import Command
from ariautils import command_utils

from .terminal import Command

class OpenApp(Command):
    info = {
        "title": "App",
        "repository": "https://github.com/SKaplanOfficial/Aria",
        "documentation_link": "https://github.com/SKaplanOfficial/Aria/documentation/",
        'id': "aria_app",
        "version": "1.0.0",
        "description": """
            This command opens applications from the system Applications folder.
        """,
        "requirements": {
            "aria_open": "1.0.0",
        },
        "extensions": {},
        "purposes": [
            "open app", "open website"
        ],
        "targets": [
            "calendar", "calculator.app", "https://example.com"
        ],
        "keywords": [
            "aria", "command", "navigation", "shortcut",
        ],
        "example_usage": [
            ("app calendar", "Opens the calendar app."),
        ],
        "help": [
            "A full application name must be provided.",
        ],
        "contact_details": {
            "author": "Stephen Kaplan",
            "email": "stephen.kaplan@maine.edu",
            "website": "http://skaplan.io",
        },
        "info_version": "0.9.0",
    }

    def execute(self, query, origin):
        target = " ".join(query.split()[1:])

        g = n = ""

        if "-g" in target:
            g = "-g"
            target = target.replace(" -g", "")

        if "-n" in query:
            n = " -n"
            target = target.replace(" -n", "")

        command_utils.plugins["aria_open"].execute("open" + g + n + " -a " + target.strip(), 2)

    def get_query_type(self, query):
        parts = query.split()
        if parts[0] in ["app"]:
            return 1000
        if parts[0] in ["open"]:
            if parts[1].find("/") != -1:
                # The target is a path -- leave it for aria_open
                return 0
            elif parts[1].find(".") != -1 and not parts[1].endswith(".app"):
                # The target is a file -- leave it for aria_open
                return 0
            elif parts[1].find("://") != -1:
                # The target is a URL -- leave it for aria_open
                return 0
            else:
                # The target is probably an app -- handle it
                return 20
        return 0

    def get_template(self, new_cmd_name):
        print("Enter base command and args: ")
        cmd_new = input()

        query_length = len(new_cmd_name)+1

        template = {
            'command': str(cmd_new.split(" ")),
        }

        return template

command = OpenApp()
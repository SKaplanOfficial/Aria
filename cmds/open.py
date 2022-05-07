"""
App

Last Updated: Version 0.0.2
"""

from ariautils.command_utils import Command
from ariautils import command_utils

class OpenApp(Command):
    info = {
        "title": "Open",
        "repository": "https://github.com/SKaplanOfficial/Aria",
        "documentation_link": "https://github.com/SKaplanOfficial/Aria/documentation/",
        'id': "aria_open",
        "version": "1.0.0",
        "description": """
            This command opens applications, folders, files, and websites.
        """,
        "requirements": {
            "aria_jump": "1.0.0",
        },
        "extensions": {
            "aria_app": "1.0.0",
        },
        "purposes": [
            "open application", "open website"
        ],
        "targets": [
            "calendar", "calculator.app", "https://example.com"
        ],
        "keywords": [
            "aria", "command", "navigation", "shortcut",
        ],
        "example_usage": [
            ("open /applications/calendar.app", "Opens the calendar app."),
            ("open ~/Documents/example.pdf", "Opens a PDF file."),
            ("open https://example.com", "Opens example.com in the default browser."),
        ],
        "help": [
            "An exact path or complete URL (including http://) must be supplied.",
        ],
        "contact_details": {
            "author": "Stephen Kaplan",
            "email": "stephen.kaplan@maine.edu",
            "website": "http://skaplan.io",
        },
        "info_version": "0.9.0",
    }

    def execute(self, query, origin):
        cmd_args = " ".join(query.split()[1:])

        print("open " + cmd_args)
        command_utils.plugins["aria_terminal"].execute("open " + cmd_args, 2)

        target = []
        parts = cmd_args.split()
        print(parts)
        quote_open = False
        for index, part in enumerate(parts):
            if "-" not in part:
                target.append(part)
                if not quote_open:
                    parts[index] = "'"+part
                    quote_open = True
                if quote_open and index == len(parts) - 1:
                    parts[index] = part+"'"
            else:
                if quote_open:
                    parts[index] = part+"'"


        target = "\ ".join(parts)
        print(target)
        # Pseudo-jump to target to track the app usage
        command_utils.plugins["aria_jump"].execute("j "+target.strip(), 3)

    def get_query_type(self, query):
        parts = query.split()
        if parts[0] in ["open"]:
            return 10
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
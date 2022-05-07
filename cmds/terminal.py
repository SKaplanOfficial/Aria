"""
Terminal

Last Updated: Version 0.0.1
"""

import subprocess

from ariautils.command_utils import Command

class Terminal(Command):
    info = {
        "title": "Run In Terminal",
        "repository": "https://github.com/SKaplanOfficial/Aria",
        'id': "aria_terminal",
        "version": "1.0.0",
        # Description is required, but has no length limit.
        "description": """
            This is an example of a custom command class for Aria.
            All custom command classes should extend the base Command class and implement its required methods.
        """,
        "requirements": {

        },
        "extensions": {
            # Optional.
            # List of other Aria commands that extend the features of this command.
            # If one of these commands is installed and enabled, then this command utilizes it. Otherwise, this command still works with limited functionality.
            # Use the same format as with requirements.
        },
        "purposes": [
            "run terminal command", "execute bash script"
        ],
        "targets": [
            "note", "file", "doc", "example.txt", "./docs/notes/example.txt", "file named example", "todays note"
        ],
        "keywords": [
            "aria", "command", "terminal", "command prompt"
        ],
        "example_usage": [
            ("make a new note", "Request an example response."),
            ("todays note", "Open today's daily note."),
            ("note for tomorrow", "Open the daily note for tomorrow."),
            ("show me yesterdays note", "Open the daily note from yesterday."),
            ("open example.txt", "Open a note called example.txt."),
        ],
        "contact_details": {
            "author": "Stephen Kaplan",
            "email": "stephen.kaplan@maine.edu",
            "website": "http://skaplan.io",
        },
        "info_version": "0.9.0",
    }
    
    def __init__(self):
        self.aliases = [
            "term",
            "zsh",
        ]

    def execute(self, query, origin):
        index = 1 if origin in [0, 1] else 0
        if " " in query:
            command = query.split()[index:]
            for index, arg in enumerate(command):
                if "&" in arg:
                    command[index] = arg.replace("&", " ")
            completion = subprocess.call(command)
        else:
            print("Please provide a terminal command and its arguments, separated by spaces.")

    def invocation(self, query):
        parts = query.split()
        aliases = [
            "term",
            "zsh",
            "bash",
        ]
        return parts[0] in aliases

command = Terminal()
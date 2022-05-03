"""
Note

Last Updated: Version 0.0.1
"""

import re
from datetime import datetime, timedelta

from ariautils.command_utils import Command
from ariautils import command_utils, config_utils, file_utils

class Note(Command):
    info = {
        "title": "Note Management for Aria",
        "repository": "https://github.com/SKaplanOfficial/Aria",
        'id': "aria_note",
        "version": "1.0.0",
        # Description is required, but has no length limit.
        "description": """
            This is an example of a custom command class for Aria.
            All custom command classes should extend the base Command class and implement its required methods.
        """,
        "requirements": {
            # Optional, but preferred.
            # List of identifiers of other Aria commands needed in order to run this command.
            #
            # Example:
            # 'aria_exec': '0.1.0',
            # 'aria_jump': '0.1.0',
            #
            # Aria current checks for exact match versions and displays warnings when the versions are at all different.
            # Support for Semantic Versioning and associated control mechanisms will be added in a future release.
            # Custom commands should still utilize SemVer despite it not being enforced currently.
            'aria_terminal': '1.0.0',
        },
        "extensions": {
            # Optional.
            # List of other Aria commands that extend the features of this command.
            # If one of these commands is installed and enabled, then this command utilizes it. Otherwise, this command still works with limited functionality.
            # Use the same format as with requirements.
        },
        "purposes": [
            "create notes", "manage notes", "edit files", "write documents", "update daily note"
        ],
        "targets": [
            "note", "file", "doc", "example.txt", "./docs/notes/example.txt", "file named example", "todays note"
        ],
        "keywords": [
            "aria", "command", "note", "text editing", "textedit"
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
        }
    }

    def __init__(self):
        self.sessions = {}
        self.min_session_duration = 3 # Minutes

    def execute(self, query, origin):
        parts = query.split()
        targets = (" ".join(parts[1:])).split(",")

        query_types = []
        if len(targets) > 1:
            for target in targets:
                query_types.append(self.get_query_type(parts[0] + " " + target.strip()))
        else:
            query_types = [self.get_query_type(query)]

        filename = ""
        log_time = False
        new_session = False

        for index, query_type in enumerate(query_types):
            print(query_type)
            targets[index] = targets[index].strip()
            if query_type in [1, 3, 5, 8, 9]:
                if targets[index].startswith("a ") or targets[index] == "note":
                    now = datetime.now()
                    filename = now.strftime("%B-%d-%Y at %-I-%M-%S %p") + ".txt"
                else:
                    filename = targets[index] + ".txt"

            elif query_type in [34, 36, 40]:
                if "today" in query:
                    now = datetime.now()
                    filename = now.strftime("%B-%d-%Y") + ".txt"
                    log_time = True
                elif "tomorrow" in query:
                    tomorrow = datetime.now() + timedelta(days=1)
                    filename = tomorrow.strftime("%B-%d-%Y") + ".txt"
                elif "yesterday" in query:
                    yesterday = datetime.now() + timedelta(days=-1)
                    filename = yesterday.strftime("%B-%d-%Y") + ".txt"

            elif query_type in [65, 99, 101, 105, 145, 264, 393]:
                # Note with a given name
                filename = parts[-1]
                if not filename[-4:].startswith("."):
                    # No extension provided
                    filename += ".txt"

            elif query_type in [256, 257]:
                # Quicknote
                filename = "quicknote.txt"
                log_time = True

            path = config_utils.get("aria_path") + "/docs/notes/" + filename

            if query_type in [193, 291, 293, 297]:
                # Full path provided
                path = targets[index]

            file_utils.touch(path)

            if log_time == True:
                if path not in self.sessions:
                    self.sessions[path] = datetime.now()
                    new_session = True
                else:
                    if datetime.now() - self.sessions[path] > timedelta(minutes=self.min_session_duration):
                        self.sessions[path] = datetime.now()
                        new_session = True

            if new_session == True:
                if not file_utils.is_empty(path):
                    file_utils.append(path, "\n\n")
                file_utils.append(path, "-- " + datetime.now().strftime("%-I:%M %p") + " Note Session --\n")

            path = path.replace(" ", "&")

            command_utils.plugins["aria_terminal"].execute("open -a Textedit " + path, 2)


    def invocation(self, query):
        parts = query.split()

        aliases = [
            "notepad",
            "textedit",
            "textfile",
        ]

        return parts[0] in aliases

    def get_query_type(self, query):
        type_map = {
            "shortcuts": {
                "regex": r'(quicknote|qn|quickn|(quick note)|(quick notepad))$',
                "type": 256,
            },
            "actions": {
                "regex": r'create |edit |new |make |open ',
                "type": 1,
                "modifiers": ["name", "days", "file_target", "path_target"]
            },
            "tertiary": {
                "regex": r'entry|doc|worddoc',
                "type": 2,
                "modifiers": ["name", "days", "file_target", "path_target"]
            },
            "secondary": {
                "regex": r'file',
                "type": 4, 
                "modifiers": ["name", "days", "file_target", "path_target"]
            },
            "primary": {
                "regex": r'note|textfile|record|memo',
                "type": 8,
                "modifiers": ["name", "days", "file_target", "path_target"]
            },
            "days": {
                "regex": r'today|tomorrow|yesterday',
                "type": 16,
            },
            "file_target": {
                "regex": r'(.*)\.(txt|rtf|html|htm|js|jsx|md|css|csv)',
                "type": 32, 
            },
            "path_target": {
                "regex": r'(.*/)+(.*)\.(txt|rtf|html|htm|js|jsx|md|css|csv)',
                "type": 64, 
            },
            "name": {
                "regex": r'called|named|by the name of|with the name',
                "type": 128,
            },
        }

        return self.apply_type_map(type_map, query)

    def apply_type_map(self, type_map, query):
        query_type = 0
        for key in type_map:
            if re.findall(type_map[key]["regex"], query) != []:
                query_type += type_map[key]["type"]

                if "modifiers" in type_map[key]:
                    sub_dict = {modifier:type_map[modifier] for modifier in type_map[key]["modifiers"]}
                    query_type += self.apply_type_map(sub_dict, query)

        return query_type

    def handler_checker(self, query):
        query_type = self.get_query_type(query)
        return query_type

command = Note()
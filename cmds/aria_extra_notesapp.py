"""An Aria plugin for interacting with the macOS Notes application.
"""

from typing import Any, Dict, List, Tuple, Union
import PyXA
import re

from ariautils.command_utils import Command
from ariautils import command_utils, context_utils

class NotesApp(Command):
    info = {
        "title": "Notes.app Control",
        "repository": "https://github.com/SKaplanOfficial/Aria",
        'id': "aria_extra_notesapp",
        "version": "1.0.0",
        "description": """
            This plugin allows users to create and manage notes in the macOS Notes application.
        """,
        "requirements": {
            'aria_core_terminal': '1.0.0',
        },
        "extensions": {},
        "purposes": [
            "create new note", "update note", "append to note", "prepend to note"
        ],
        "targets": [
            "note",
        ],
        "keywords": [
            "aria", "command", "note", "notes.app", "macOS"
        ],
        "example_usage": [
            ("make a new note", "Create a new note."),
            ("find the note containing Test", "Shows the first note containing the term 'Test'."),
            ("find the note called Test", "Shows the first note with the name 'Test'."),
            ("speak the selected note", "Speaks the text of the currently selected note."),
        ],
        "contact_details": {
            "author": "Stephen Kaplan",
            "email": "stephen.kaplan@maine.edu",
            "website": "http://skaplan.io",
        },
        "info_version": "0.9.0",
    }

    def __init__(self):
        self.sessions = {}

    def execute(self, query: str, _origin: int) -> None:
        query_type = self.get_query_type(query, True)
        query_type[1]["func"](query, query_type[1]["args"])

    def new_note(self, _query: str, args: List[Any]):
        """Creates a new note with the given text content.

        _extended_summary_

        :param args: The arguments to the command; the first arg is the string content of the note
        :type args: List[Any]

        .. versionadded:: 1.0.0
        """
        PyXA.application("Notes").new_note(*args).show()

    def show_note_with_name(self, _query: str, args: List[any]):
        """Shows the note with the specified name.

        :param args: The arguments to the command; the first arg is the string to search notes for
        :type args: List[Any]

        .. versionadded:: 1.0.0
        """
        PyXA.application("Notes").notes().by_name(args[0]).show()

    def show_note_containing(self, _query: str, args: List[Any]):
        """Shows the note containing the specified string.

        :param args: The arguments to the command; the first arg is the string to search notes for
        :type args: List[Any]

        .. versionadded:: 1.0.0
        """
        notes = PyXA.application("Notes").notes()
        note = PyXA.XABase.XAPredicate.evaluate_with_format(notes.xa_elem, f"body CONTAINS '{args[0]}'")[0]
        note.showSeparately_(False)

    def speak_selected_notes(self, _query: str, _args: List[Any]):
        """Speaks the text of each selected note sequentially.

        .. versionadded:: 1.0.0
        """
        notes = PyXA.application("Notes").selection.plaintext()
        for note in notes:
            command_utils.plugins["aria_core_terminal"].run_command(["say", note.replace("\n", "").replace("\t", "")], shell=False)

    def get_query_type(self, query: str, get_tuple: bool = False) -> Union[int, Tuple[int, Dict[str, Any]]]:
        has_create_cmd = re.search(r'(create|make|add|write)', query) != None

        find_target = ""
        find_name_cmd = re.search(r'(find|show|reveal|open).*(titled|title|called|named|name) ', query)
        has_find_name_cmd = find_name_cmd != None
        if has_find_name_cmd:
            find_target = query[find_name_cmd.span()[1]:]

        find_cmd = re.search(r'(find|show|reveal|open).*(with|containing|contain|has|saying|says|reads) ', query)
        has_find_cmd = find_cmd != None
        if has_find_cmd:
            find_target = query[find_cmd.span()[1]:]

        # Define conditions and associated method for each execution pathway
        query_type_map = {
            5000: { # New Note - High Confidence
                "conditions": [("Notes.app" in context_utils.current_app or query.endswith("in notes") or query.endswith("with notes")) and has_create_cmd and "note" in query],
                "func": self.new_note,
                "args": [""],
            },

            4001: { # Find Note by Name - High Confidence
                "conditions": [("Notes.app" in context_utils.current_app or "note" in query) and has_find_name_cmd],
                "func": self.show_note_with_name,
                "args": [find_target],
            },

            4000: { # Find Note Containing - High Confidence
                "conditions": [("Notes.app" in context_utils.current_app or "note" in query) and has_find_cmd],
                "func": self.show_note_containing,
                "args": [find_target],
            },

            3000: { # Speak Selected Note - High Confidence
                "conditions": [("Notes.app" in context_utils.current_app or "note" in query) and "speak" in query and ("selection" in query or "selected" in query)],
                "func": self.speak_selected_notes,
                "args": [],
            },
        }

        # Obtain query type and associated execution data
        for key, query_type in query_type_map.items():
            if all(query_type["conditions"]):
                if get_tuple:
                    return (key, query_type)
                return key
        return 0

command = NotesApp()
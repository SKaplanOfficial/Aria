"""
Example

Last Updated: Version 0.0.1
"""

from CommandTypes import Command

class ExampleCommand(Command):
    info = {
        "title": "Example Custom Command for Aria",
        "repository": "https://github.com/SKaplanOfficial/Aria",
        "documentation_link": "https://github.com/SKaplanOfficial/Aria",
        'id': "aria_example_cmd",
        "version": "1.0.0",
        "description": """
            This is an example of a custom command class for Aria.
            All custom command classes should extend the base Command class and implement its required methods.
        """,
        "requirements": {},
        "extensions": {},
        "purposes": [],
        "targets": [],
        "keywords": [
            "aria", "command", "example"
        ],
        "example_usage": [
            ("give me an example", "Request an example response."),
            ("example query", "Query for an example acknowledgement."),
        ],
        "help": [], # TODO: This
        "contact_details": {
            "author": "Stephen Kaplan",
            "email": "stephen.kaplan@maine.edu",
            "website": "http://skaplan.io",
        }
    }

    def execute(self, query, origin):
        print("Testing...")

        if "test" in Command.managers["config"].get_config().keys():
            print(Command.managers["config"].get("test"))
        else:
            Command.managers["config"].set("test", 123)
            print("Added config entry.")

# Init object for export
command = ExampleCommand()
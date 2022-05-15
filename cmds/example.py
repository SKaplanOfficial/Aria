"""
Example

Last Updated: Version 0.0.1
"""

from ariautils.command_utils import Command
from ariautils import config_utils, io_utils

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
        },
        "info_version": "0.9.0",
    }

    def execute(self, query, origin):
        print("Testing...")

        if "test" in config_utils.get_config().keys():
            print(config_utils.get("test"))
        else:
            config_utils.set("test", 123)
            print("Added config entry.")

        print(config_utils.get(self.info["id"])["my_var"])

    def configure(self):
        if self.info["id"] not in config_utils.get_config():
            io_utils.sprint("Please configure this")
            config_utils.set(self.info["id"], {})

        plugin_config = config_utils.get(self.info["id"])
        if "my_var" not in config_utils.get(self.info["id"]):
            print("Enter a value for my_var: ", end="")
            plugin_config["my_var"] = input()

        config_utils.set(self.info["id"], plugin_config)

# Init object for export
command = ExampleCommand()
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

from ariautils import command_utils, io_utils
from ariautils.tracking_utils import TrackingManager


class ExitCommand(command_utils.Command):
    info = {
        "title": "Exit Aria",
        "repository": "https://github.com/SKaplanOfficial/Aria",
        'id': "aria_core_control_exit",
        "version": "1.0.0",
        "description": """
            Exits the Aria commandline interface.
        """,
        "requirements": {},
        "extensions": {},
        "purposes": [
            "Quit Aria",
        ],
        "targets": [],
        "keywords": [
            "aria", "core", "command", "exit", "quit", "terminate",
        ],
        "example_usage": [
            ("quit", "Exits Aria."),
            ("q", "Exits Aria."),
        ],
        "contact_details": {
            "author": "Stephen Kaplan",
            "email": "stephen.kaplan@maine.edu",
            "website": "http://skaplan.io",
        },
        "info_version": "0.9.0",
    }

    def __init__(self):
        super().__init__()

    def execute(self, query, origin) -> None:
        exit()

    def invocation(self, query):
        return query.content in ["q", "exit", "quit", "terminate", "stop"]


class EnableCommand(command_utils.Command):
    info = {
        "title": "Enable Plugin",
        "repository": "https://github.com/SKaplanOfficial/Aria",
        'id': "aria_core_control_enable_plugin",
        "version": "1.0.0",
        "description": """
            Enables an Aria command plugin
        """,
        "requirements": {},
        "extensions": {},
        "purposes": [
            "Enable command plugin",
        ],
        "targets": [],
        "keywords": [
            "aria", "core", "command", "plugin", "plugin management",
        ],
        "example_usage": [
            ("enable plugin aria_core_open", "Enables the aria_core_open command plugin."),
        ],
        "contact_details": {
            "author": "Stephen Kaplan",
            "email": "stephen.kaplan@maine.edu",
            "website": "http://skaplan.io",
        },
        "info_version": "0.9.0",
    }

    def __init__(self):
        super().__init__()

    def execute(self, query, origin) -> None:
        command_id = query.content[14:]
        command_utils.enable_command_plugin(command_id)
        return command_utils.plugins[command_id]

    def invocation(self, query):
        return query.content.startswith("enable plugin ")

class DisableCommand(command_utils.Command):
    info = {
        "title": "Disable Plugin",
        "repository": "https://github.com/SKaplanOfficial/Aria",
        'id': "aria_core_control_disable_plugin",
        "version": "1.0.0",
        "description": """
            Disables an Aria command plugin
        """,
        "requirements": {},
        "extensions": {},
        "purposes": [
            "Disable command plugin",
        ],
        "targets": [],
        "keywords": [
            "aria", "core", "command", "plugin", "plugin management",
        ],
        "example_usage": [
            ("disable plugin aria_core_open", "Disables the aria_core_open command plugin."),
        ],
        "contact_details": {
            "author": "Stephen Kaplan",
            "email": "stephen.kaplan@maine.edu",
            "website": "http://skaplan.io",
        },
        "info_version": "0.9.0",
    }

    def __init__(self):
        super().__init__()

    def execute(self, query, origin) -> None:
        command_id = query.content[15:]
        command_utils.disable_command_plugin(command_id)

    def invocation(self, query):
        return query.content.startswith("disable plugin ")

command_exports = [
    ExitCommand(),
    EnableCommand(),
    DisableCommand(),
]

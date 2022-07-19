"""
Site

A command plugin for Aria that opens websites.

Part of AriaCore in Aria 1.0.0
"""

import re
from typing import Any, Dict, Tuple, Union
import webbrowser

from ariautils.command_utils import Command
from ariautils import command_utils

class Site(Command):
    info = {
        "title": "Site",
        "repository": "https://github.com/SKaplanOfficial/Aria",
        "documentation_link": "https://github.com/SKaplanOfficial/Aria/documentation/",
        'id': "aria_core_site",
        "version": "1.0.0",
        "description": """
            Opens websites.
        """,
        "requirements": {
            'aria_core_open': '1.0.0',
        },
        "extensions": {},
        "purposes": [
            "open website", "goto URL", "visit site",
        ],
        "targets": [
            "google.com", "https://youtube.com"
        ],
        "keywords": [
            "aria", "command", "core", "web", "websites", "internet", "safari", "edge", "chrome", "firefox", "browser"
        ],
        "example_usage": [
            ("site https://www.google.com", "Open a website using its full URL."),
            ("site google.com", "Open a website using its top-level domain only."),
        ],
        "help": [
            "This command opens a website in the default browser given a URL or the top-level domain of a website.",
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

    def open(self, query: str, *args):
        url = self.get_url_term(query)
        if not url.startswith("http"):
            url = "http://" + url
        if not "." in url:
            url = url + ".com"
        command_utils.plugins["aria_core_terminal"].run_command(["open", url], shell = False)

    def get_url_term(self, query: str) -> str:
        ignored_terms = {
            "or", "of", "by", "for", "um", "something", "like", "ish", "name", "named", "call", "called"
        }

        parts = query.split(" ")
        for part in parts:
            if part in ignored_terms:
                query = query.replace(part, "")
            if "http" in part or (len(part) > 3 and part[-4] == "."):
                return part

        for part in parts:
            if part[-2] == ".":
                return part

        query = query.replace("  ", " ").strip()
        return query.split(" ")[-1]

    def get_query_type(self, query: str, get_tuple: bool = False) -> Union[int, Tuple[int, Dict[str, Any]]]:
        has_site_specifier = re.search(r'(site|website|url|web)', query) != None
        has_tld = re.search(r'(\.com|\.net|\.org|\.io|\.tk|\.edu|\.gov|\.xyz|\.nl|\.uk|\.ca)', query) != None

        query_type_map = {
            2400: {
                "conditions": ["open" in query, "http" in query or has_tld],
                "func": self.open,
                "args": [],
            },

            2300: {
                "conditions": [has_site_specifier, "http" in query or has_tld],
                "func": self.open,
                "args": [],
            },

            1000: {
                "conditions": [has_site_specifier, len(query.split(" ")) > 2],
                "func": self.open,
                "args": [],
            },

            100: {
                "conditions": [has_site_specifier],
                "func": self.open,
                "args": [],
            },

            10: {
                "conditions": ["http" in query or has_tld],
                "func": self.open,
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

command = Site()
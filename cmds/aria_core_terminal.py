"""
Terminal

Last Updated: Version 0.0.1
"""

import re, subprocess
from typing import Any, Union, Dict, Tuple

from ariautils.command_utils import Command
from ariautils.misc_utils import any_in_str

class Terminal(Command):
    info = {
        "title": "Run In Terminal",
        "repository": "https://github.com/SKaplanOfficial/Aria",
        'id': "aria_core_terminal",
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

    def execute(self, query, origin):
        query_type = self.get_query_type(query, True)
        query_type[1]["func"](query, query_type[1]["args"])

    def default_shell(self, query, args):
        if args != []:
            for tuple in args:
                query = query[:tuple[0]] + tuple[1] + query[tuple[0]:]
                print(query)
        query = query.replace("terminal ", "")
        subprocess.call(query, shell=True)

    def zsh(self, query, args):
        query = query.replace("zsh ", "")
        subprocess.call(query, shell=True, executable='/bin/zsh')

    def bash(self, query, args):
        query = query.replace("bash ", "")
        subprocess.call(query, shell=True, executable='/bin/bash')

    def get_query_type(self, query: str, get_tuple: bool = False) -> Union[int, Tuple[int, Dict[str, Any]]]:
        has_macos_cmd = re.search(r'^(clear|cd|ls|du|df|mkdir|rm|rmdir|touch|cp|mv|history|chmod|chown|ps|top|kill|ping|whois|ssh|curl|scp|arp|ifconfig|traceroute|printenv|echo|export|grep|cat|less|head|nano|man|open|vim|afplay|cron|cmp|diff|diskutil|env|fdisk|ftp|groups|users|ipconfig|killall|launchctl|logout|md5|mkfile|mtree|net|netstat|openssl|pbcopy|pbs|pkill|pkgutil|reboot|shutdown|screen|sleep|softwareupdate|tail|vi|whoami|pwd|afconvert|apachectl|sftp|ffplay|flac|zip|unzip|xargs|wall)', query) != None

        has_third_party_cmd = re.search(r'^(git|brew|python|pip|ffmpeg|ffplay|python3|pydoc|black|pylint|autopep8|django|django-admin|mysql|docker|docker-compose|node|npm|php|perl|ruby|rust|rustc|gcc|cpp|c\+\+|f90|aws|code|emacs|youtube-dl)', query) != None

        # Define conditions and associated method for each execution pathway
        __query_type_map = {
            2001: { # Bash
                "conditions": [query.startswith("bash "), len(query) > 5],
                "func": self.bash,
                "args": [],
            },
            2000: { # Zsh
                "conditions": [query.startswith("zsh "), len(query) > 4],
                "func": self.zsh,
                "args": [],
            },

            1000: { # Direct Ref to This Command
                "conditions": [query.startswith("terminal "), len(query) > 9],
                "func": self.default_shell,
                "args": [],
            },

            2: { # Third Party Command
                "conditions": [has_third_party_cmd],
                "func": self.default_shell,
                "args": [],
            },
            1: { # MacOS Command
                "conditions": [has_macos_cmd],
                "func": self.default_shell,
                "args": [],
            },
        }

        # Obtain query type and associated execution data
        for key, query_type in __query_type_map.items():
            if all(query_type["conditions"]):
                if get_tuple:
                    return (key, query_type)
                return key
        return 0

command = Terminal()
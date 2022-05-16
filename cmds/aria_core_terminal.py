"""
Terminal command for Aria.

API
===
TerminalCommand: A class for executing terminal commands in Aria.
"""

import os
import re, subprocess
from typing import Any, List, Union, Dict, Tuple

from ariautils import config_utils
from ariautils.command_utils import Command
from ariautils.io_utils import sprint

class Terminal(Command):
    """An Aria Command for executing terminal commands.
    """
    info = {
        "title": "Run In Terminal",
        "repository": "https://github.com/SKaplanOfficial/Aria",
        'id': "aria_core_terminal",
        "version": "1.0.0",
        "description": """
            This command interfaces between Aria and the Unix terminal, allowing users to directly execute terminal commands.
        """,
        "requirements": {},
        "extensions": {
            "aria_core_open": "1.0.0",
        },
        "purposes": [
            "run terminal command", "execute bash script"
        ],
        "targets": [
            "terminal", "bash" "/bin/zsh"
        ],
        "keywords": [
            "aria", "command", "terminal", "command prompt"
        ],
        "example_usage": [
            ("clear", "Clear the terminal window."),
            ("python", "Open an interactive shell program such as Python."),
            ("terminal echo example", "Run a terminal command in the default shell."),
            ("bash echo example", "Run a terminal command in a specified shell such as Bash."),
            ("zsh echo example", "Open a note called example.txt."),
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

    def run_command(self, command_string: str, shell: bool = True, stdin: subprocess._FILE = None, stdout: subprocess._FILE = None, stderr: subprocess._FILE = None, cwd: Union[str, bytes, os.PathLike] = None, env: subprocess._ENV = None) -> int:
        completion_status = subprocess.call(command_string, shell = shell, stdin = stdin, stdout = stdout, stderr = stderr, cwd = cwd, env = env)
        return completion_status

    def __default_shell(self, query: str, args: List[Union[Tuple[Union[str, Any], ...], Tuple[int, int]]]) -> None:
        """Runs a command in the default shell, or opens the shell in interactive mode.

        :param query: The raw text of the user's query. Not currently used, but kept for future purposes.
        :type query: str
        :param args: Either an empty list or a list containing two entries: the group(0) of a REGEX match and the associated span.
        :type args: List[Union[Tuple[Union[str, Any], ...], Tuple[int, int]]]
        """
        if args != []:
            for tuple in args:
                query = query[:tuple[0]] + tuple[1] + query[tuple[0]:]
                print(query)
        query = query.replace("terminal ", "")
        subprocess.call(query, shell=True)

    def __specified_shell(self, query: str, args: List[Union[Tuple[Union[str, Any], ...], Tuple[int, int]]]) -> None:
        """Runs a command in a specified shell, or opens the shell in interactive mode. The shell is specified by index 0 of the REGEX match span tuple at index 1 of args.

        :param query: The raw text of the user's query. Not currently used, but kept for future purposes.
        :type query: str
        :param args: A list containing two entries: the group(0) of a REGEX match and the associated span.
        :type args: List[Union[Tuple[Union[str, Any], ...], Tuple[int, int]]]
        """
        query = query.replace(args[0] + " ", "")
        subprocess.call(query, shell=True, executable='/bin/'+args[0])
        if len(query) == args[1][1]:
            # User exited interactive shell, welcome them back to Aria
            sprint("Hello again, " + config_utils.get("user_name") + "!")

    def get_query_type(self, query: str, get_tuple: bool = False) -> Union[int, Tuple[int, Dict[str, Any]]]:
        has_macos_cmd = re.search(r'^(clear|cd|ls|du|df|mkdir|rm|rmdir|touch|cp|mv|history|chmod|chown|ps|top|kill|ping|whois|ssh|curl|scp|arp|ifconfig|traceroute|printenv|echo|export|grep|cat|less|head|nano|man|open|vim|afplay|cron|cmp|diff|diskutil|env|fdisk|ftp|groups|users|ipconfig|killall|launchctl|logout|md5|mkfile|mtree|net|netstat|openssl|pbcopy|pbs|pkill|pkgutil|reboot|shutdown|screen|sleep|softwareupdate|tail|vi|whoami|pwd|afconvert|apachectl|sftp|ffplay|flac|zip|unzip|xargs|wall)', query) != None

        has_third_party_cmd = re.search(r'^(git|brew|python|pip|ffmpeg|ffplay|python3|pydoc|black|pylint|autopep8|django|django-admin|mysql|docker|docker-compose|node|npm|php|perl|ruby|rust|rustc|gcc|cpp|c\+\+|f90|aws|code|emacs|youtube-dl)', query) != None

        match_shell = re.search(r'(csh|ksh|tcsh|bash|dash|zsh)', query)
        shell_args = [match_shell.group(0), match_shell.span()] if match_shell != None else []

        # Define conditions and associated method for each execution pathway
        __query_type_map = {
            3000: { # Specified Shell - High Confidence
                "conditions": [match_shell != None and match_shell.span()[0] == 5, query.startswith("/bin/")],
                "func": self.__specified_shell,
                "args": shell_args,
            },

            1000: { # Direct Ref to This Command
                "conditions": [query.startswith("terminal "), len(query) > 9],
                "func": self.__default_shell,
                "args": [],
            },

            30: { # Specified Shell - Medium Confidence
                "conditions": [match_shell != None and match_shell.span()[0] == 0],
                "func": self.__specified_shell,
                "args": shell_args,
            },

            2: { # Third Party Command
                "conditions": [has_third_party_cmd],
                "func": self.__default_shell,
                "args": [],
            },
            1: { # MacOS Command
                "conditions": [has_macos_cmd],
                "func": self.__default_shell,
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
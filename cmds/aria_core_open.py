"""
App

Last Updated: Version 0.0.2
"""

from ariautils.command_utils import Command
from ariautils import command_utils, context_utils, io_utils

import shlex
import platform
current_os = platform.system()

class OpenApp(Command):
    info = {
        "title": "Open",
        "repository": "https://github.com/SKaplanOfficial/Aria",
        "documentation_link": "https://github.com/SKaplanOfficial/Aria/documentation/",
        'id': "aria_core_open",
        "version": "1.0.0",
        "description": """
            This command opens applications, folders, files, and websites.
        """,
        "requirements": {
            "aria_core_terminal": "1.0.0",
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
        query = self.__cleanse(query)
        query_type = self.get_query_type(query)
        app_target = ""
        if query_type in [22, 220, 2200]:
            # Selected Files, query is along the lines of "open these"
            if query_type == 2200:
                # Query is along the lines of "open these in ___"
                app = query[query.index("in") + 3:]
                app = self.__expand_app_ref(app)
                app_target = app
                print("Opening", app_target + "...")

            selected_items = context_utils.get_selected_items()
            if selected_items != None:
                for item in selected_items:
                        self.open(item, app_target)
        else:
            parts = shlex.split(query)
            app_target = self.__expand_app_ref(" ".join(parts[1:]))
            print("Opening", app_target + "...")
            self.open_item(app_target)

        # Pseudo-jump to target to track the app usage
        command_utils.plugins["aria_jump"].execute("j " + app_target, 3)

    def __cleanse(self, query: str) -> str:
        query = query.replace("\\", "\\\\")
        query = query.replace("\"", "\\\"")
        query = query.replace('\'', '\\\'')
        query = query.replace('\ ', '\\\ ')
        return query

    def __expand_app_ref(self, app_ref):
        ref_map = {}
        if current_os == "Windows":
            ref_map = {
                "vscode": "C:\\Users\\fryei\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
                "visual studio code": "C:\\Users\\fryei\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
            }
        elif current_os == "Linux":
            ref_map = {}
        elif current_os == "Darwin":
            ref_map = {
                "vscode": "Visual Studio Code", "code": "Visual Studio Code",
                "msg": "Messages", "msgs": "Messages",
                "mc": "Minecraft",
                "browser": "Safari",
                "acrobat": "Adobe Acrobat",
                "msw": "Microsoft Word",
                "mse": "Microsoft Excel",
                "msp": "Microsoft Powerpoint",
                "ps": "Adobe Photoshop 2022",
                "ind": "Adobe InDesign 2022",
                "ai": "Adobe Illustrator 2022",
                "qt": "QuickTime Player",
                "gitdesk": "Github Desktop",
                "git": "Github Desktop",
            }

        # Exact match to known shorthand form
        if app_ref in ref_map:
            return ref_map[app_ref]

        # Partial match to app name
        values = list(ref_map.values())
        if current_os == "Darwin":
            values.extend(context_utils.get_app_list())
        for value in values:
            if app_ref in value.lower():
                return value

        # No match, keep the ref as-is
        return app_ref

    def get_query_type(self, query):
        parts = query.split()
        if parts[0] in ["open"]:
            if ("/") in query:
                # File path
                return 11

            # Query contains a direct reference to vscode
            # TODO: Add 20
            if "that" in query:
                # Query is along the lines of "open that in vscode"
                return 21

            if "this" in query or "these" in query:
                # Query is along the lines of "open this/these in vscode"
                if "Finder" in context_utils.previous_apps or "Finder" in context_utils.current_app or current_os != "Darwin":
                    # Finder is open
                    if "in" in query:
                        return 2200
                    return 220
                return 22
            return 10 # App
        return 0

    def open_item(self, item: str, app: str = None) -> None:
        if app is None:
            # No app specified, open in default app
            if current_os == "Windows":
                self.__open_file_windows(item)
            elif current_os == "Linux":
                self.__open_file_linux(item)
            elif current_os == "Darwin":
                self.__open_file_darwin(item)
        else:
            if current_os == "Windows":
                self.__open_app_windows(app, item)
            elif current_os == "Linux":
                self.__open_app_linux(app, item)
            elif current_os == "Darwin":
                self.__open_app_darwin(app, item)

    def open_app() -> None:
        pass

    # Windows
    def __open_app_windows(self, app: str, file: str = None):
        if ".exe" in app:
            status = command_utils.plugins["aria_core_terminal"].run_command([app, file])
        else:
            status = command_utils.plugins["aria_core_terminal"].run_command(["start", app, file])
            if status == 1:
                io_utils.sprint("Let me try again...")
                status = command_utils.plugins["aria_core_terminal"].run_command(["start", file + ":"])
                if status == 1:
                    io_utils.sprint("Sorry, I was unable to find that file or application.")
                    
    def __open_file_windows(self, file: str):
        if ".exe" in file:
            status = command_utils.plugins["aria_core_terminal"].run_command([file])
        else:
            status = command_utils.plugins["aria_core_terminal"].run_command(["start", file])
            if status == 1:
                io_utils.sprint("Let me try again...")
                status = command_utils.plugins["aria_core_terminal"].run_command(["start", file + ":"])
                if status == 1:
                    io_utils.sprint("Sorry, I was unable to find that file or application.")

    # Linux
    def __open_app_linux(self, app: str, file: str = None):
        command_utils.plugins["aria_core_terminal"].run_command(["gio", "open", app, file])

    def __open_file_linux(self, file: str):
        command_utils.plugins["aria_core_terminal"].run_command(["gio", "open", file])

    # Darwin
    def __open_app_darwin(self, app: str, file: str = None):
        command_utils.plugins["aria_core_terminal"].run_command(["open", "-a", app, file])

    def __open_file_darwin(self, file: str):
        command_utils.plugins["aria_core_terminal"].run_command(["open", file])

    def get_template(self, new_cmd_name):
        print("Enter base command and args: ")
        cmd_new = input()

        query_length = len(new_cmd_name)+1

        template = {
            'command': str(cmd_new.split(" ")),
        }

        return template

command = OpenApp()
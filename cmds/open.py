"""
App

Last Updated: Version 0.0.2
"""

from ariautils.command_utils import Command
from ariautils import command_utils, context_utils, io_utils

import platform
current_os = platform.system()

class OpenApp(Command):
    info = {
        "title": "Open",
        "repository": "https://github.com/SKaplanOfficial/Aria",
        "documentation_link": "https://github.com/SKaplanOfficial/Aria/documentation/",
        'id': "aria_open",
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
        query_type = self.get_query_type(query)
        app_target = ""
        if query_type in [22, 220, 2200]:
            print("\nOpening...")
            # "open these"
            if query_type == 2200:
                # "open these in ___"
                app = query.split()[-1]
                app = self.__expand_app_ref(app)

            selected_items = context_utils.get_selected_items()
            if selected_items != None:
                for item in selected_items:
                    if current_os == "Darwin":
                        app_target = " -a " + app.replace(" ", "&")
                        command_utils.plugins["aria_core_terminal"].execute("open" + app_target + " " + item.replace(" ", "&"), 2)
                    elif current_os == "Linux":
                        app_target = app.replace(" ", "&")
                        command_utils.plugins["aria_core_terminal"].execute("cmd.exe /C start" + app_target + " " + item.replace(" ", "&"), 2)
        elif query_type == 10:
            if "-a" not in query and current_os == "Darwin":
                query = query[:5] + "-a " + query[5:]
            else:
                io_utils.sprint("Opening " + query[8:] + "...")
                # TODO: Should base this ^ on last space, use split()
            cmd_args = " ".join(query.split()[1:])
            if current_os == "Darwin":
                command_utils.plugins["aria_core_terminal"].execute("open " + cmd_args, 2)
            elif current_os == "Linux":
                command_utils.plugins["aria_core_terminal"].execute("cmd.exe /C start " + cmd_args, 2)
        else:
            cmd_args = " ".join(query.split()[1:])
            if current_os == "Darwin":
                command_utils.plugins["aria_core_terminal"].execute("open " + cmd_args, 2)
            elif current_os == "Linux":
                command_utils.plugins["aria_core_terminal"].execute("cmd.exe /C start " + cmd_args, 2)

        target = []
        parts = cmd_args.split()
        quote_open = False
        for index, part in enumerate(parts):
            if "-" not in part and current_os == "Darwin":
                target.append(part)
                if not quote_open:
                    parts[index] = "'"+part
                    quote_open = True
                if quote_open and index == len(parts) - 1:
                    parts[index] = part+"'"
            else:
                if quote_open:
                    parts[index] = part+"'"


        target = "\ ".join(parts)
        # Pseudo-jump to target to track the app usage
        command_utils.plugins["aria_jump"].execute("j "+target.strip(), 3)

    def __expand_app_ref(self, app_ref):
        ref_map = {
            "vscode": "Visual Studio Code",
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
            "qt": "Quicktime Player",
        }

        # Exact match to known shorthand form
        if app_ref in ref_map:
            return ref_map[app_ref]

        # Partial match to app name
        values = list(ref_map.values())
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
                if "Finder" in context_utils.previous_apps or "Finder" in context_utils.current_app:
                    # Finder is open
                    if "in" in query:
                        return 2200
                    return 220
                return 22
            return 10 # App
        return 0

    def get_template(self, new_cmd_name):
        print("Enter base command and args: ")
        cmd_new = input()

        query_length = len(new_cmd_name)+1

        template = {
            'command': str(cmd_new.split(" ")),
        }

        return template

command = OpenApp()
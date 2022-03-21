"""
Close

Last Updated: Version 0.0.1
"""

import applescript
import subprocess


class Command:
    def __init__(self):
        pass

    def execute(self, str_in, managers):
        optional = ""

        if str_in.endswith(" tab") or str_in.endswith( "window"):
            if str_in.endswith(" tab"):
                if "Safari" in managers["context"].current_app:
                    optional = "current tab of the "

                str_in = str_in[:str_in.index(" tab")]

            elif str_in.endswith( "window"):
                str_in = str_in[:str_in.index(" window")]

            scpt = applescript.AppleScript('''try
                tell application "''' + managers["context"].current_app + '''"
                    close ''' + optional + '''front window
                end tell
                return tabURL
            on error
                -- blah
            end try
            ''')
            scpt.run()

            if managers["context"].current_app != managers["context"].previous_apps[-1]:
                managers["context"].previous_apps.append(managers["context"].current_app)
        else:
            query = str_in[6:]
            command = ['pkill', '-ix']
            command.insert(len(command), query)
            subprocess.call(command)

    def get_template(self, new_cmd_name):
        print("Enter base command and args: ")
        cmd_new = input()

        query_length = len(new_cmd_name)+1

        template = {
            'command': str(cmd_new.split(" ")),
            'query': 'str_in['+str(query_length)+':]',
        }

        return template

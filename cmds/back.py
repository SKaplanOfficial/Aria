"""
Back

Last Updated: Version 0.0.1
"""

import applescript


class Command:
    def __init__(self):
        self.aliases = ["prev", "previous"]

    def execute(self, str_in, managers):
        scpt = applescript.AppleScript('''
            try
                tell application "''' + managers["context"].current_app + '''"
                    activate
                    delay 0.1
                    tell application "System Events" to keystroke "[" using command down
                end tell
            on error
                -- blah
            end try
        ''')
        scpt.run()

    def get_template(self, new_cmd_name):
        print("Enter base command and args: ")
        cmd_new = input()
        
        print("Enter target code: ")
        new_target = input()

        template = {
            'command': str(cmd_new.split(" ")),
            'target': new_target_code,
        }

        return template

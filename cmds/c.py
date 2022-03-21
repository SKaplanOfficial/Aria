"""
Jump to context

Last Updated: Version 0.0.1
"""

import subprocess
from datetime import datetime


class Command:
    def __init__(self):
        pass

    def execute(self, str_in, managers):
        target_names = str_in[2:].split(" ")

        context_tracker = managers["context"].context_tracker
        current_context = managers["context"].current_context

        now = datetime.now()
        current_time = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()

        print("Finding context match...")
        candidates = context_tracker.get_entries_containing(target_names)
        target_context = context_tracker.entry_obj(current_time, current_time, 1, target_names)

        best_candidate = context_tracker.get_best_match(target_context, candidates, 0)

        if best_candidate == None:
            best_candidate = context_tracker.entry_obj(current_time, current_time, 0, target_names)
            context_tracker.add_entry(best_candidate)

        # Close running apps
        apps_to_close = [app for app in current_context["targets"] if app not in best_candidate["targets"]]
        for app in apps_to_close:
            if app != "/Applications/Visual Studio Code.app" and app != "/System/Library/CoreServices/Finder.app" and app != "/System/Applications/Utilities/Terminal.app":
                print("Closing " + app + "...")
                command = ["pkill", "-f", app]
                subprocess.call(command)
        
        # Run apps
        apps_to_open = [app for app in best_candidate["targets"] if app not in current_context["targets"]]
        for app in apps_to_open:
            print("Opening " + app + "...")
            command = ["open", app]
            subprocess.call(command)

    def get_template(self, new_cmd_name):
        # TODO: Fix this or remove it
        print("Enter base command and args: ")
        cmd_new = input()

        query_length = len(new_cmd_name)+1

        template = {
            'command': str(cmd_new.split(" ")),
            'query': 'str_in['+str(query_length)+':]',
            'data_file_name': "",
        }

        return template

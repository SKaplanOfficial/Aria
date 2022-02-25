"""
Conx - open applications relevant to the current context

Last Updated: February 22, 2022
"""

import subprocess


class Command:
    def __init__(self, *args, **kwargs):
        self.aria_path = args[0]

    def execute(self, str_in, refs):
        ConM = refs[0]

        current_context = ConM.current_context
        context_data = ConM.context_tracker.entries

        print("Finding context match...")
        max_score = 0
        best_candidates = []
        for context_candidate in context_data:
            # Award points for context delta
            score = 100 - ConM.context_tracker.entry_delta(context_candidate, current_context)

            # Award points for having some job to do (otherwise why would the user enter this command?)
            num_apps_diff = max(0, len(context_candidate["targets"]) - len(current_context["targets"]))
            score += -(num_apps_diff-3) * (num_apps_diff-3) + num_apps_diff + 16

            if score > max_score:
                max_score = score
                best_candidates = context_candidate["targets"]

        best_candidates = [app for app in best_candidates if app not in current_context["targets"]]
        
        # Run apps
        for app in best_candidates:
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

    def get_help(self):
        return ""

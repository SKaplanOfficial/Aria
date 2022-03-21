"""
Jump

Last Updated: Version 0.0.1
"""

import subprocess
from datetime import datetime


class Command:
    def __init__(self):
        self.aliases = ["jump", "goto"]

    def execute(self, str_in, managers):
        jump_tracker = managers["tracking"].init_tracker("jump")
        jump_tracker.load_data()

        target_destinations = str_in[2:].split(" ")
        candidates = jump_tracker.get_items_containing("targets", target_destinations)

        now = datetime.now()
        current_time = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
        target_jump = jump_tracker.new_item([current_time, current_time, 1, target_destinations])

        max_freq = 0
        for item in jump_tracker.items:
            if item.data["frequency"] > max_freq:
                max_freq = item.data["frequency"]

        def weigh_freq(item_1, item_2):
            score = jump_tracker.default_compare_method(item_1, item_2)
            if score < 0.8:
                score -= (item_2.data["frequency"]) / max_freq
            return score

        best_candidate = jump_tracker.get_best_match(target_jump, candidates, 0.3, ignored_cols = ["frequency"], compare_method = weigh_freq)

        if best_candidate == None:
            best_candidate = jump_tracker.new_item([current_time, current_time, 0, target_destinations])
            jump_tracker.add_item(best_candidate)

        # Run apps
        for dest in best_candidate.data["targets"]:
            print("Jumping to " + dest + "...")
            command = ["open", dest]
            completion = subprocess.call(command)

            if completion == 0:
                # If successful, update the CSV with new frequencies
                best_candidate.data["start_time"] += (current_time - best_candidate.data["start_time"]) * 0.01
                best_candidate.data["end_time"] += (current_time - best_candidate.data["end_time"]) * 0.01
                best_candidate.data["frequency"] += 1
            else:
                if (best_candidate.data["frequency"] != 0):
                    print("Found broken jump point, removing.")
                jump_tracker.items.remove(best_candidate)
        
        jump_tracker.save_data()

    def handler_checker(self, str_in, managers):
        if "Finder" in managers["context"].current_app:
            return 1
        return 0

    def handler(self, str_in, managers, score):
        self.execute("j " + str_in, managers)

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

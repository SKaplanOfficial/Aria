"""
Jump

Last Updated: February 2, 2022
"""

import subprocess
import os
import csv
from datetime import datetime
from pathlib import Path


class Command:
    def __init__(self, *args, **kwargs):
        self.aria_path = args[0]

    def execute(self, str_in, refs):
        ConM = refs[0]
        TrackM = refs[1]

        target_destinations = str_in[2:].split(" ")

        jump_tracker = TrackM.init_tracker("jump")
        jump_tracker.load_data()

        now = datetime.now()
        current_time = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()

        print("Finding jump match...")
        candidates = jump_tracker.get_entries_containing(target_destinations)
        target_jump = jump_tracker.entry_obj(current_time, current_time, 1, [""])
        best_candidate = jump_tracker.get_best_match(target_jump, candidates, 1)

        if best_candidate == None:
            best_candidate = jump_tracker.entry_obj(current_time, current_time, 3, target_destinations)
            jump_tracker.add_entry(best_candidate)

        # Run apps
        for dest in best_candidate["targets"]:
            print("Jumping to " + dest + "...")
            command = ["open", dest]
            completion = subprocess.call(command)

            if completion == 0:
                # If successful, update the CSV with new frequencies
                # TODO: Make the tracker object handle this?
                best_candidate["start_time"] += (current_time - best_candidate["start_time"]) * 0.01
                best_candidate["end_time"] += (current_time - best_candidate["end_time"]) * 0.01
                best_candidate["frequency"] += 1
            else:
                if (best_candidate["frequency"] != 0):
                    print("Found broken jump point, removing.")
                jump_tracker.entries.remove(best_candidate)
        
        jump_tracker.save_data()

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

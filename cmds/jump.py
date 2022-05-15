"""
Jump

Last Updated: Version 0.0.1
"""

import subprocess
from datetime import datetime

from ariautils import io_utils, context_utils
from ariautils.tracking_utils import TrackingManager
from ariautils.command_utils import Command

class Jump(Command):
    info = {
        "title": "Jump",
        "repository": "https://github.com/SKaplanOfficial/Aria",
        "documentation_link": "https://github.com/SKaplanOfficial/Aria/documentation/",
        'id': "aria_jump",
        "version": "1.0.0",
        "description": """
            Jumps to a destination application, file, folder, or website.
            Tracks jumps to better infer destinations from shorthand notations over time.
        """,
        "requirements": {},
        "extensions": {
            "aria_exec": "1.0.0",
            "aria_open": "1.0.0",
        },
        "purposes": [
            "jump to", "go to",
        ],
        "targets": [
            "http://example.com", "google", "documents", "doc", "Applications/Notes.app", "notes",
        ],
        "keywords": [
            "aria", "command", "navigation", "shortcut"
        ],
        "example_usage": [
            ("j downloads", "Opens the downloads folder in the file explorer application (Finder)."),
            ("j down", "(Likely) Opens the downloads folder."),
            ("jump google", "Opens google.com."),
            ("goto goog", "(Likely) Opens google.com."),
        ],
        "contact_details": {
            "author": "Stephen Kaplan",
            "email": "stephen.kaplan@maine.edu",
            "website": "http://skaplan.io",
        },
        "info_version": "0.9.0",
    }

    def execute(self, query, origin):
        # Extract targets from query
        query_type = self.get_query_type(query)
        target_destinations = query.split()
        if query_type != 1:
            target_destinations = target_destinations[1:]
        
        target_destinations = (" ".join(target_destinations)).split(",")

        # Get list of relevant candidates
        jump_tracker = TrackingManager.init_tracker("jump")
        jump_tracker.load_data()
        candidates = jump_tracker.get_items_containing("targets", target_destinations)

        # Create an object for the target jump(s)
        now = datetime.now()
        current_time = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
        target_jump = jump_tracker.new_item([current_time, current_time, 1, target_destinations])

        # Find the best candidate, if one exists
        best_candidate = self.__get_best_candidate(target_jump, candidates, jump_tracker)
        if best_candidate == None:
            best_candidate = jump_tracker.new_item([current_time, current_time, 0, target_jump.data["targets"]])
            jump_tracker.add_item(best_candidate)

        # Attempt to make jump(s)
        completion_status = self.__jump(best_candidate, origin)

        # Report status and update tracker items as necessary
        if completion_status[0] == 0:
            # The jump was entirely successful, update the frequency and time of the item
            if origin in [0, 1]:
                io_utils.sprint("Here you go!")
            self.__update_jump(best_candidate, current_time)
        elif completion_status[0] == -1 and origin in [0, 1]:
            # Some parts of the jump failed
            self.__report_failures(completion_status[2])
        else:
            # The entire jump failed, remove the broken item
            if origin in [0, 1]:
                self.__report_failures(completion_status[2])
            self.__remove_broken_jump(best_candidate, jump_tracker)
        
        jump_tracker.save_data()

    def __get_best_candidate(self, target_jump, candidates, jump_tracker):
        """ Gets the best candidate jump with matching or near-matching targets, if one exists. Returns None otherwise. """
        max_freq = jump_tracker.get_max_of_col("frequency")

        def weigh_freq(item_1, item_2):
            score = jump_tracker.default_compare_method(item_1, item_2)

            for target_1 in item_1.data["targets"]:
                for target_2 in item_2.data["targets"]:
                    if target_1.lower() in target_2.lower():
                        score /= 1.1
                    else:
                        score *= 1.01

            score -= (item_2.data["frequency"]) / max_freq
            return score

        best_candidate = jump_tracker.get_best_match(target_jump, candidates, 0.1, compare_method = weigh_freq)
        return best_candidate

    def __jump(self, best_candidate, origin):
        """ Attempts to open the destinations associated with the best candidate. Returns 0 if all jumps succeeded, -1 if some jumps failed while others succeeded, and 1 if all jumps failed. """
        successes = []
        failures = []

        for dest in best_candidate.data["targets"]:
            if origin in [0, 1]:
                print("Attempting jump to " + dest + "...")
            command = ["open", dest]

            status = 0
            if origin != 3:
                status = subprocess.call(command)

            if status == 0:
                successes.append(dest)
            else:
                failures.append(dest)

        overall_status = 0 # Assume all successes
        if len(successes) > 0 and len(failures) > 0:
            # Mix of successes and failures
            overall_status = -1
        elif len(successes) == 0:
            # All failures
            overall_status = 1
        
        return overall_status, successes, failures

    def __update_jump(self, jump_item, current_time):
        """ Updates the jump item's time range and frequency. """
        jump_item.data["start_time"] += (current_time - jump_item.data["start_time"]) * 0.01
        jump_item.data["end_time"] += (current_time - jump_item.data["end_time"]) * 0.01
        jump_item.data["frequency"] += 1

    def __report_failures(self, failures):
        """ Reports the destinations that could not be jumped to. """
        if len(failures) > 1:
            io_utils.sprint("I was unable to complete jumps to " + str(len(failures)) + " destinations:")
            for dest in failures:
                print("\t" + dest)
        else:
            io_utils.sprint("I was unable to complete the jump to " + failures[0] + ".")

    def __remove_broken_jump(self, jump_item, jump_tracker):
        """ Removes jump entries that are no longer functional. """
        if (jump_item.data["frequency"] != 0):
            print("Found broken jump point, removing.")
        else:
            # Item is the temporary item created when no candidate is found
            io_utils.dprint("Removing jump item '" + " ".join(jump_item.data["targets"]) + "'")
        jump_tracker.items.remove(jump_item)

    def get_query_type(self, query):
        parts = query.split()
        if parts[0] in ["j", "goto", "jto"]:
            return 1000

        if "Finder" in context_utils.current_app:
            return 1
        return 0

    def get_template(self, new_cmd_name):
        print("Enter base command and args: ")
        cmd_new = input()

        query_length = len(new_cmd_name)+1

        template = {
            'command': str(cmd_new.split(" ")),
            'query': 'query['+str(query_length)+':]',
        }

        return template

command = Jump()
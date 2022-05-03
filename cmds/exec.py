"""
x

Last Updated: Version 0.0.1
"""

from datetime import datetime
from time import sleep

from ariautils import context_utils, io_utils
from ariautils.command_utils import Command
from ariautils.tracking_utils import TrackingManager

class Execute(Command):
    info = {
        "title": "Execute",
        "repository": "https://github.com/SKaplanOfficial/Aria",
        "documentation_link": "https://github.com/SKaplanOfficial/Aria/documentation/",
        'id': "aria_exec",
        "version": "1.0.0",
        "description": """
            Executes a set of commands.
            Tracks executions to better infer targets from shorthand notations over time.
        """,
        "requirements": {},
        "extensions": {
            'aria_exec': '1.0.0',
        },
        "purposes": [
            "execute tasks", "run commands",
        ],
        "targets": [
            "j google", "app calendar", "note today",
        ],
        "keywords": [
            "aria", "command", "navigation", "shortcut",
        ],
        "example_usage": [
            ("x example", "Runs the execution sequences named 'example'."),
            ("x app calendar & app contacts --name events", "Creates a new execution sequence named 'events'."),
        ],
        "help": [
            "This command executes a set of commands.",
            "Run that",
        ],
        "contact_details": {
            "author": "Stephen Kaplan",
            "email": "stephen.kaplan@maine.edu",
            "website": "http://skaplan.io",
        }
    }

    def __init__(self, ):
        self.force_context = False

    def execute(self, query, origin):
        # Extract targets from query
        query_type = self.get_query_type(query)
        target_destinations = query.split()
        if query_type != 1:
            target_destinations = target_destinations[1:]

        # Initialize execution tracker object
        item_structure = {
            "name" : str,
            "time" : float,
            "frequency" : int,
            "targets" : list,
        }

        exec_tracker = TrackingManager.tracker(
            "exec",
            item_structure = item_structure,
            data_source = self.parse_target,
            merge_method = self._increment_freq
        )
        exec_tracker.load_data()

        # Get list of relevant candidates
        candidates = exec_tracker.get_items_containing("targets", target_destinations)

        # Create an object for the target jump(s)
        data = self.parse_target(query)
        exec_target = exec_tracker.new_item(data)
        candidates += exec_tracker.get_items_containing("name", data[0])

        # Find the best candidate, if one exists
        best_candidate = self._get_best_candidate(exec_target, candidates, exec_tracker)
        if best_candidate == None:
            best_candidate = exec_target
            print("New exec pathway:", best_candidate.data["name"], "->", best_candidate.data["targets"])
            exec_tracker.add_item(best_candidate)
        else:
            print("Existing exec pathway:", best_candidate.data["name"], "->", best_candidate.data["targets"])
        
        exec_tracker.save_data()

        if self.force_context:
            context_utils.blank_context()

        commands = best_candidate.data["targets"].split("|")
        for command in commands:
            print("Running", command)
            io_utils.pseudo_input(command)
            sleep(0.1)

    def _get_best_candidate(self, exec_target, candidates, exec_tracker):
        """ Gets the best exec candidate with matching or near-matching targets, if one exists. Returns None otherwise. """
        max_freq = exec_tracker.get_max_of_col("frequency")

        def compare_method(item_1, item_2):
            if item_1.data["name"] == item_2.data["name"]:
                return 0

            score = exec_tracker.default_compare_method(item_1, item_2)
            for target_1 in item_1.data["targets"]:
                for target_2 in item_2.data["targets"]:
                    if target_1.lower() in target_2.lower():
                        score /= 1.1
                    else:
                        score *= 1.01

            score -= (item_2.data["frequency"]) / max_freq
            return score

        best_candidate = exec_tracker.get_best_match(exec_target, candidates, 0.1, compare_method = compare_method)
        return best_candidate

    def _increment_freq(self, item_1, item_2):
        """ Updates the exec item's frequency. """
        item_1.data["frequency"] += 1
        return item_1

    def parse_target(self, target):
        targets = target.split()[1:]

        self.force_context = False
        if "-fc" in targets:
            self.force_context = True
            targets.remove("-fc")

        # Name
        name = targets[0]
        if "--name" in targets:
            name_index = targets.index("--name") + 1
            name = targets[name_index]
            targets.pop(name_index)
            targets.remove("--name")

        # Time
        now = datetime.now()
        current_time = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()

        targets_str = (" ".join(targets)).split(" & ")
        return [name, current_time, 1, targets_str]

    def get_query_type(self, query):
        parts = query.split()
        if parts[0] in ["x", "exec", "run"]:
            return 1000
        return 0

    def get_template(self, new_cmd_name):
        print("Enter base command and args: ")
        cmd_new = input()

        query_length = len(new_cmd_name)+1

        template = {
            'command': str(cmd_new.split(" ")),
            'targets': 'query['+str(query_length)+':]',
            'data_file_name': "'"+str(cmd_new.split(" ")[0])+"'",
            'return_cmd': "'"+str(cmd_new.split(" ")[1])+"'"
        }

        return template

command = Execute()
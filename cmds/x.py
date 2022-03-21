"""
x

Last Updated: Version 0.0.1
"""

from datetime import datetime

class Command:
    def __init__(self, ):
        self.force_context = False
        self.exec_tracker = None

    def execute(self, str_in, managers):
        item_structure = {
            "name" : str,
            "time" : float,
            "frequency" : int,
            "targets" : list,
        }

        self.exec_tracker = managers["tracking"].tracker(
            "exec",
            item_structure = item_structure,
            data_source = self.parse_target,
            merge_method = self.increment_freq
        )

        self.exec_tracker.load_data()

        targets = str_in[2:].split(" ")
        data = self.parse_target(str_in)

        candidates = self.exec_tracker.get_items_containing("targets", targets)
        candidates += self.exec_tracker.get_items_containing("name", data[0])

        target = self.exec_tracker.new_item(data)
        best_candidate = self.exec_tracker.get_best_match(target, candidates, 0, compare_method = self.compare_method)

        if best_candidate == None:
            best_candidate = target
            print("New exec pathway:", best_candidate.data["name"], "->", best_candidate.data["targets"])
            self.exec_tracker.add_item(best_candidate)
        else:
            print("Existing exec pathway:", best_candidate.data["name"], "->", best_candidate.data["targets"])
        
        self.exec_tracker.save_data()

        if self.force_context:
            managers["context"].blank_context()

        return_cmd = "run"
        return return_cmd + " " + best_candidate.data["targets"].replace("|", " && ")

    def increment_freq(self, item_1, item_2):
        item_1.data["frequency"] += 1
        return item_1

    def compare_method(self, item_1, item_2):
        if item_1.data["name"] == item_2.data["name"]:
            return 0
        return self.exec_tracker.default_compare_method(item_1, item_2)

    def parse_target(self, target):
        cmd_target = target[2:]

        if " -fc" in cmd_target:
            self.force_context = True
            cmd_target = cmd_target.replace(" -fc", "")

        # Name
        name = cmd_target
        if " " in name:
            name = name.split(" ")[0]
        if " --name=" in cmd_target:
            name = cmd_target[cmd_target.index("--name=")+7:]

        # Time
        now = datetime.now()
        current_time = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()

        # Targets
        targets_new = [cmd_target]
        if " & " in cmd_target:
            targets_new = cmd_target.split(" & ")
        if " --name=" in cmd_target:
            if " & " in cmd_target:
                targets_new = cmd_target.replace(" --name="+name, "").split(" & ")
            else:
                targets_new = [cmd_target.replace(" --name="+name, "")]
        
        return [name, current_time, 1, targets_new]

    def get_template(self, new_cmd_name):
        print("Enter base command and args: ")
        cmd_new = input()

        query_length = len(new_cmd_name)+1

        template = {
            'command': str(cmd_new.split(" ")),
            'targets': 'str_in['+str(query_length)+':]',
            'data_file_name': "'"+str(cmd_new.split(" ")[0])+"'",
            'return_cmd': "'"+str(cmd_new.split(" ")[1])+"'"
        }

        return template

    def get_help(self):
        return "x [cmd 1] & [cmd 2] & ... --name=[name] -fc"

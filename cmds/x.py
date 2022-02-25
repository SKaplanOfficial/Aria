"""
Jump

Last Updated: February 2, 2022
"""

import os
import csv
import datetime
from pathlib import Path


class Command:
    def __init__(self, *args, **kwargs):
        self.aria_path = args[0]

    def execute(self, str_in, context):
        (target, target_name) = self.parse_target(str_in)

        # Get current hour
        target_time = datetime.datetime.now().hour

        # Data file path
        folder_path = self.aria_path+"/data/"
        data_file_name = "exec_tracking.csv"
        file_path = folder_path + "/" + data_file_name

        # Create jump-tracking csv if it's missing
        if not os.path.isfile(file_path):
            if not target:
                print(
                    "Since this is your first time jumping, please provide a full command.")
                return

            self.create_csv(
                folder_path,
                file_path,
                [target_name, target, target_time, 0])

        # Compare target against csv
        best_candidate = (None, None)  # path, index
        rows = []
        with open(file_path, 'r') as data_file:
            csv_reader = csv.reader(data_file, delimiter=",")
            best_score = 0
            for index, row in enumerate(csv_reader):
                rows.append(row)
                # Check if target name is a substring of the row folder name
                if target_name.lower() in row[0].lower():
                    time_difference = max(target_time, float(
                        row[2])) - min(target_time, float(row[2]))
                    if time_difference < 0:
                        time_difference = 24 + time_difference

                    if time_difference == 0:
                        time_difference = 0.01

                    score = float(row[3]) / time_difference

                    # Award bonus score if target time is + or - 3 hours of row time
                    if time_difference < 4:
                        score *= 1.5

                    if score > best_score:
                        # Set row folder path as current best candidate
                        best_candidate = (row[1], index)
                        best_score = score
        # New entry
        if best_candidate == (None, None):
            best_candidate = (target, -1)
            rows.append([target_name, target, target_time, 1])
        else:
            current_best_time = float(rows[best_candidate[1]][2])
            current_freq = float(rows[best_candidate[1]][3])
            new_best_time = ((current_best_time * current_freq) +
                             target_time) / (current_freq + 1)
            rows[best_candidate[1]][2] = new_best_time
            rows[best_candidate[1]][3] = current_freq + 1

        # Update csv
        with open(file_path, 'w') as data_file:
            for row in rows:
                csv_writer = csv.writer(
                    data_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
                csv_writer.writerow(row)

        return "run " + best_candidate[0]

    def parse_target(self, str_in):
        # Get the actual name of the target folder
        target = str_in[2:]
        target_name = target
        if " &&& " in target:
            target = target.replace(" &&& ", " && ")
        if " --name=" in target:
            target_name = target[target.index("--name=")+7:]
            target = target[0:target.index(" --name=")]
        if " " in target_name:
            target_name = target_name[target_name.rfind(" ")+1:]
        return (target, target_name)

    def create_csv(self, folder_path, file_path, initial_row_content):
        Path(folder_path).mkdir(parents=True, exist_ok=True)
        with open(file_path, 'a') as new_csv:
            csv_writer = csv.writer(
                new_csv, delimiter=",",
                quotechar='"',
                quoting=csv.QUOTE_NONNUMERIC)
            csv_writer.writerow(initial_row_content)

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
        return "x [cmd 1] &&& [cmd 2] &&& ... --name=[name]"

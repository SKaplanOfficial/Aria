from .Trackers import Tracker
from pathlib import Path
from datetime import datetime

class TrackingManager:
    def __init__(self, data_folder_path):
        self.data_folder_path = data_folder_path
        self.trackers = {}

        Path(self.data_folder_path).mkdir(parents = True, exist_ok = True)
    
    def init_tracker(self, title, item_structure = None):
        """ Create a tracker. """
        data_file_name = title+"_tracking.csv"
        data_file_path = self.data_folder_path + "/" + data_file_name

        if item_structure == None:
            item_structure = {
                "start_time" : float,
                "end_time" : float,
                "frequency" : float,
                "targets" : list
            }

        new_tracker = Tracker(title, data_file_path, item_structure)
        return new_tracker

    def tracker(self, name = None, data_file_path = None, item_structure = {},
                 data_source = None, allow_duplicate_entries = False,
                 allow_near_duplicates = False, compare_method = None,
                 merge_method = None, use_csv = False):

        if (name != None or use_csv == True) and data_file_path == None:
            if name == None:
                now = datetime.now()
                current_time = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
                name = "tracker"+hash(current_time)
            data_file_name = name+"_tracking.csv"
            data_file_path = self.data_folder_path + "/" + data_file_name

        return Tracker(name, data_file_path, item_structure,
                 data_source, allow_duplicate_entries,
                 allow_near_duplicates, compare_method,
                 merge_method, use_csv)

    def keep_alive(self, Tracker):
        """ Keep Tracker in memory via this TrackingManager's list of trackers. """
        self.trackers.append(Tracker)

    def run_frequency_tracker(self, title, data_source):
        data_file_name = title+"_tracking.csv"

        def check_targets(item_1, item_2):
            if item_1.data["target"] == item_2.data["target"]:
                return 1
            return 0

        def increment_freq(item_1, item_2):
            item_1.data["frequency"] += 1
            return item_1

        item_structure = {
            "time" : float,
            "frequency" : int,
            "target" : str,
        }

        my_tracker = Tracker(
            title,
            data_file_path = self.data_folder_path + "/" + data_file_name,
            item_structure = item_structure,
            data_source = data_source,
            compare_method = check_targets,
            merge_method = increment_freq
        )

        my_tracker.run()
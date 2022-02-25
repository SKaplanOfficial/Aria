import csv
import math
import os
from pathlib import Path
from datetime import datetime, timedelta

class Tracker:
    def __init__(self, title, data_file_path):
        self.title = title
        self.data_file_path = data_file_path

        self.create_csv = self.default_create_csv
        self.update_csv = self.default_update_csv
        self.save_data = self.default_save_data
        self.load_data = self.default_load_data
        self.new_entry = self.default_new_entry

        self.entries = []

    def default_create_csv(self, first_entry = []):
        """ Create tracking.csv if it doesn't already exist """
        print("Creating " + self.data_file_path + "...")
        with open(self.data_file_path, 'a') as new_csv:
            csv_writer = csv.writer(
                new_csv,
                delimiter=",",
                quotechar='"',
                quoting=csv.QUOTE_NONNUMERIC)
            csv_writer.writerow(first_entry)

    def default_update_csv(self, entries):
        """ Update tracking.csv with data from csv_row parameter """
        with open(self.data_file_path, 'w') as data_file:
            for entry in entries:
                csv_writer = csv.writer(
                    data_file,
                    delimiter=",",
                    quotechar='"',
                    quoting=csv.QUOTE_NONNUMERIC)
                csv_writer.writerow(entry)

    def default_save_data(self):
        """ Export all objects to tracking.csv """
        # Check whether tracking.csv needs to be made
        if not os.path.isfile(self.data_file_path):
            initial_entry = self.entry_obj()
            self.create_csv()
        
        # Load old data to preserve history
        self.load_data()

        # Prepare entries for export
        entries_to_export = []
        for entry in self.entries:
            entries_to_export.append(self.entry_to_list(entry))

        # Update csv with modified rows
        self.update_csv(entries_to_export)

    def get_stored_entries(self):
        """ Get data from tracking.csv """
        # Check whether tracking.csv needs to be made
        if not os.path.isfile(self.data_file_path):
            initial_entry = self.entry_obj()
            self.create_csv()

        # Extract entries from csv
        entries = []
        with open(self.data_file_path, 'r') as data_file:
            csv_reader = csv.reader(data_file, delimiter=",")
            for _, row in enumerate(csv_reader):
                if row == []:
                    continue
                entries.append([
                    float(row[0]),
                    float(row[1]),
                    float(row[2]),
                    row[3:]]
                )
        return entries

    def default_load_data(self):
        """ Load data from tracking.csv, compute insights, then store for later use """
        # Extract entries from csv
        entries = self.get_stored_entries()

        # Add new entries from current session
        # Check if entry already exists
        entries_to_remove = []
        for new_entry in self.entries:
            if new_entry == []:
                continue

            for old_entry in entries:
                if old_entry == []:
                    continue

                new_targets = new_entry["targets"]
                old_targets = old_entry[3]

                old_targets.sort()
                new_targets.sort()

                if self.check_entry_similarity(self.entry_obj(*old_entry), new_entry):
                    new_entry["frequency"] = max(new_entry["frequency"], old_entry[2])

                    if new_targets != old_targets:
                        new_entry["targets"] = new_entry["targets"] + old_entry[3]
                    entries_to_remove.append(old_entry)
        
            entries.append(list(new_entry.values()))

        # Remove duplicate entries
        for entry in entries_to_remove:
            if entry in entries:
                entries.remove(entry)

        self.clear_entries()

        # Map each row to a tracked object
        for entry in entries:
            tracked_obj = self.new_entry(*entry)

    def default_new_entry(self, *args):
        self.entries.append(self.entry_obj(*args))

    def entry_to_list(self, entry):
        return [entry["start_time"], entry["end_time"], entry["frequency"]] + entry["targets"]

    def add_entry(self, entry):
        self.entries.append(entry)

    def entry_obj(self, *args):
        if len(args) > 0:
            targets = args[3]
            targets.sort()
            return {
                "start_time" : args[0],
                "end_time" : args[1],
                "frequency" : args[2],
                "targets" : targets
            }
        else:
            return {
                "start_time" : 0,
                "end_time" : 0,
                "frequency" : 1,
                "targets" : []
            }
    
    def clear_entries(self):
        self.entries = []

    def check_entry_similarity(self, entry_1, entry_2):
        """ Check if two entries are reasonably similar based on delta between them and frequencies """
        def fprint(*str):
            #if entry_1["targets"] != entry_2["targets"]:
            #    print(*str)
            return
            
        fprint("\n\n", "-"*25)
        delta = self.entry_delta(entry_1, entry_2)
        fprint("DELTA:", delta)
    
        freq = max(entry_1["frequency"], entry_2["frequency"])
        freq_weight = 1 - (freq / math.sqrt(freq * freq + 50))

        similarity = max(delta, freq_weight * delta)

        fprint("FREQ:", freq)
        fprint("WEIGHT:", freq_weight)
        fprint("SIM:", similarity)
        return similarity < 5

    def entry_delta(self, entry_1, entry_2):
        """ Calculate weighted difference between two entries based on time and target, 0-100 (inverse) """
        start_1 = entry_1["start_time"]
        end_1 = entry_1["end_time"]
        targets_1 = entry_1["targets"]

        start_2 = entry_2["start_time"]
        end_2 = entry_2["end_time"]
        targets_2 = entry_2["targets"]

        delta = 100

        # Time Difference
        start_start_diff = abs(start_1 - start_2)
        end_end_diff = abs(end_1 - end_2)
        diff_from_same_bound = min(start_start_diff, end_end_diff)

        diff_from_opposite_bound = diff_from_same_bound
        if start_1 < start_2 and end_1 > end_2:
            # entry_2 occurs entirely during entry_1
            # Don't care about opposite bounds here
            pass
        elif start_1 < start_2 and end_1 < end_2:
            # entry_2 begins during entry_1, ends after
            diff_from_opposite_bound = abs(end_1 - start_2)
        elif start_1 > start_2 and end_1 > end_2:
            # entry_2 begins before entry_1, ends during
            diff_from_opposite_bound = abs(start_1 - end_2)
        elif start_1 > start_2 and end_1 < end_2:
            # entry_1 occurs entirely during entry_2
            # Don't care about opposite bounds here
            pass

        weighted_time_diff = min(diff_from_same_bound, diff_from_opposite_bound)
        scaled_time_diff = 50 - (50 * weighted_time_diff / math.sqrt((weighted_time_diff + 3600) * (weighted_time_diff + 60) + 1))

        # Target Similarity
        scaled_similarity = 50
        if targets_1 != targets_2:
            num_similar = 0
            num_diff = 0
            max_consec = 0
            num_consec_similar = 0
            for target_1 in targets_1:
                found = False
                for target_2 in targets_2:
                    if target_1 == target_2 and not found:
                        found = True

                if found:
                    num_similar += 1
                    num_consec_similar += 1
                    if num_consec_similar > max_consec:
                        max_consec = num_consec_similar
                else:
                    num_diff += 1
                    num_consec_similar = 0

            weighted_target_similarity = max(0, num_similar * 1 + max_consec * 2 - abs(len(targets_1) - len(targets_2)) * 2 - num_diff * 3)
            scaled_similarity = 50 * weighted_target_similarity / math.sqrt((weighted_target_similarity + 2) * (weighted_target_similarity + 2) + 1)

        # TODO: Make this not inversed?
        delta -= scaled_time_diff + scaled_similarity
        return max(0, delta)

    def get_entries_containing(self, targets):
        """ Get a list of entries containing all members of the target array """
        if isinstance(targets, str):
            targets = [targets]

        candidates = []
        for entry in self.entries:
            all_targets_present = True
            for target in targets:
                missing = True
                for entry_target in entry["targets"]:
                    if target.lower() in entry_target.lower():
                        # TODO: Make this check use some approximation logic, e.g. to accept minceraft instead of minecraft
                        missing = False

                if missing:
                    all_targets_present = False

            if all_targets_present:
                candidates.append(entry)

        return candidates

    def get_best_match(self, target_entry, candidates = None, base_score = 0, custom_score_func = None, custom_compare_func = None, ignored_cols = []):
        """ Get the entry with the smallest delta from the target entry """
        
        if candidates == None:
            candidates = self.entries

        best_score = base_score
        best_candidate = None
        for candidate in candidates:
            for column in ignored_cols:
                target_entry[column] = candidate[column]

            score = 100 - self.entry_delta(candidate, target_entry)

            if callable(custom_score_func):
                score = custom_score_func(candidate, target_entry, score)

            if callable(custom_compare_func):
                if custom_compare_func(score, best_score):
                    best_score = score
                    best_candidate = candidate

            else:
                if score > best_score:
                    best_score = score
                    best_candidate = candidate

        return best_candidate

    def get_entries(self, sort = None):
        if callable(sort):
            return sorted(self.entries, key=sort)
        else:
            return self.entries


class TrackingManager:
    def __init__(self, *args, **kwargs):
        self.aria_path = args[0]
        self.data_folder_path = self.aria_path+"/data/"
        self.trackers = {}

        Path(self.data_folder_path).mkdir(parents = True, exist_ok = True)
    
    def init_tracker(self, title):
        """ Create a tracker """
        data_file_name = title+"_tracking.csv"
        data_file_path = self.data_folder_path + "/" + data_file_name
        new_tracker = Tracker(title, data_file_path)

        return new_tracker

    def run_basic_tracker(self, title, data, tracking_method = None):
        tracker = self.init_tracker(title)
        tracker.load_data()

        now = datetime.now()
        current_time = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()

        relevant_entries = tracker.get_entries_containing(data)
        target_entry = tracker.entry_obj(current_time, current_time, 1, [data])

        best_candidate = tracker.get_best_match(target_entry, relevant_entries, 0, custom_score_func = tracking_method)
        if relevant_entries == [] or best_candidate["targets"][0] != data:
            # Not an exact match, so add new article
            tracker.add_entry(target_entry)

        tracker.save_data()
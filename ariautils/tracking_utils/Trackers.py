import csv
import math
import os

class TrackerItem:
    def __init__(self):
        self.data = {}

    def __init__(self, data):
        self.data = data

    def get(self, key):
        pass

    def set(self, key, value):
        pass

    def format(self, structure):
        if isinstance(structure, list):
            # Make list of values corresponding to supplied keys
            new_data_list = []
            for key in structure:
                new_data_list.append(self.data[key])
            return new_data_list
                
        elif isinstance(structure, dict):
            # Convert data to a dictionary with supplied keys and types
            new_data_dict = {}
            index = 0
            for key, value in structure.items():
                new_data_dict[key] = value(self.data[key])
                index += 1
            return new_data_dict

    def as_list(self):
        new_data_list = []
        for key in self.data.keys():
            new_data_list.append(self.data[key])
        return new_data_list

    def __str__(self):
        pass

class Tracker:
    def __init__(self, name = None, data_file_path = None, item_structure = {},
                 data_source = None, allow_duplicate_items = False,
                 allow_near_duplicates = False, compare_method = None,
                 merge_method = None, use_csv = False):
        self.name = name
        self.items = []
        self.cols = []
        self.coltypes = []
        self.item_structure = item_structure
        self.data_file_path = data_file_path
        if self.data_file_path == None and use_csv == True:
            self.data_file_path = "./" + self.name + "-tracker.csv"

        for key, value in item_structure.items():
            self.cols.append(key)
            self.coltypes.append(value)

        self.data_source = data_source
        self.allow_duplicate_items = allow_duplicate_items
        self.allow_near_duplicates = allow_near_duplicates
        self.compare_method = compare_method
        self.merge_method = merge_method

    def run(self):
        if self.data_file_path is not None:
            self.load_data()

        if self.data_source is not None:
            if callable(self.data_source):
                new_item = self.new_item(self.data_source())
            else:
                new_item = self.new_item(self.data_source)
            self.add_item(new_item)
        else:
            print("You are running a track without specifying a data source. Did you mean to do this?")

        if not self.allow_near_duplicates:
                self.remove_near_duplicates(compare_method = self.compare_method, merge_method = self.merge_method)
        elif not self.allow_duplicate_items:
            self.remove_duplicates(merge_method = self.merge_method)

        if self.data_file_path is not None:
            self.save_data()

    def new_empty_item(self):
        """ Create an empty TrackerItem object with 0-out fields. """
        new_item_data = {}
        for key, value in self.item_structure.items():
            new_item_data[key] = value("0")

        new_item = TrackerItem(new_item_data)
        return new_item

    def new_item(self, data):
        """ Create a new TrackerItem object from the supplied data. """
        new_item_data = {}
        for index, key in enumerate(self.cols):
            if isinstance(data, list):
                new_item_data[key] = self.coltypes[index](data[index])
            elif isinstance(data, dict):
                new_item_data[key] = self.coltypes[index](data[key])

        new_item = TrackerItem(new_item_data)
        return new_item

    def add_item(self, item):
        """ Adds a TrackerItem object to this Tracker's items list. """
        self.items.append(item)

    def clear_items(self):
        """ Remove all TrackerItems from this Tracker's items list. Leave csv file unchanged. """
        self.items = []

    def create_csv(self, first_item = []):
        """ Create tracking.csv if it doesn't already exist. """
        print("Creating " + self.data_file_path + "...")
        with open(self.data_file_path, 'a') as new_csv:
            csv_writer = csv.writer(
                new_csv,
                delimiter=",",
                quotechar='"',
                quoting=csv.QUOTE_NONNUMERIC)
            csv_writer.writerow(first_item)

    def update_csv(self, items):
        """ Update tracking.csv with data from csv_row parameter. """
        with open(self.data_file_path, 'w') as data_file:
            for item in items:
                csv_writer = csv.writer(
                    data_file,
                    delimiter=",",
                    quotechar='"',
                    quoting=csv.QUOTE_NONNUMERIC)
                csv_writer.writerow(item)

    def purge_csv(self):
        """ Delete all rows in this Tracker's csv data file. """
        with open(self.data_file_path, 'w') as data_file:
            csv_writer = csv.writer(
                    data_file,
                    delimiter=",",
                    quotechar='"',
                    quoting=csv.QUOTE_NONNUMERIC)
            csv_writer.writerow([])

    def save_data(self):
        """ Export all objects to tracking.csv. """
        # Check whether tracking.csv needs to be made
        if not os.path.isfile(self.data_file_path):
            initial_item = self.new_empty_item()
            self.create_csv(initial_item.as_list())

        # Prepare items for export
        items_to_export = []
        for item in self.items:
            # Convert python list object to string list expression
            for index, key in enumerate(self.cols):
                if self.coltypes[index] == list:
                    item.data[key] = "|".join(item.data[key])

            items_to_export.append(item.format([*self.cols]))

        # Update csv with modified rows
        self.update_csv(items_to_export)

    def load_data(self, append = False):
        """ Get data from tracking.csv. """
        # Check whether tracking.csv needs to be made
        if not os.path.isfile(self.data_file_path):
            initial_item = self.new_empty_item()
            self.create_csv(initial_item.as_list())

        # Extract items from csv
        items = []
        with open(self.data_file_path, 'r') as data_file:
            csv_reader = csv.reader(data_file, delimiter=",")
            for _, row in enumerate(csv_reader):
                if row == []:
                    continue

                # Convert string list expression to python list object
                for index, element in enumerate(row):
                    if self.coltypes[index] == list:
                        if "|" in str(element):
                            row[index] = element.split("|")
                        else:
                            row[index] = [element]

                new_item = self.new_item(row)
                items.append(new_item)

        # Add old items to current items list
        if append:
            self.items = self.items + items
        else:
            self.items = items

    def remove_duplicates(self, merge_values = True, merge_method = None):
        """ Remove items that are exact duplicates, leaving one in the items array. """
        items_to_remove = []
        for index_1, item_1 in enumerate(self.items):
            for index_2, item_2 in enumerate(self.items[index_1+1:]):
                if item_1.data == item_2.data:
                    if merge_values or merge_method is not None:
                        if callable(merge_method):
                            self.items[index_1] = merge_method(item_1, item_2)
                        else:
                            if callable(self.merge_method):
                                self.items[index_1] = self.merge_method(item_1, item_2)
                            else:
                                self.items[index_1] = self.default_merge_method(item_1, item_2)
                    items_to_remove.append(index_2+index_1+1)

        for item_index in items_to_remove:
            self.items.pop(item_index)

    def remove_near_duplicates(self, compare_method = None, threshold = 0.5, merge_values = True, merge_method = None):
        """ Remove items that are near duplicates, leaving one in the items array. """
        items_to_remove = []
        for index_1, item_1 in enumerate(self.items):
            for index_2, item_2 in enumerate(self.items[index_1+1:]):
                similar = False
                if callable(compare_method):
                    similar = compare_method(item_1, item_2) > threshold
                else:
                    if callable(self.compare_method):
                        similar = self.compare_method(item_1, item_2) > threshold
                    else:
                        similar = self.default_compare_method(item_1, item_2) > threshold

                if similar:
                    if merge_values or merge_method is not None:
                        if callable(merge_method):
                            self.items[index_1] = merge_method(item_1, item_2)
                        else:
                            if callable(self.merge_method):
                                self.items[index_1] = self.merge_method(item_1, item_2)
                            else:
                                self.items[index_1] = self.default_merge_method(item_1, item_2)
                    items_to_remove.append(index_2+index_1+1)

        for item_index in items_to_remove:
            self.items.pop(item_index)

    def remove_empty_items(self):
        items_to_remove = []
        for index_1, item_1 in enumerate(self.items):
            all_zero = True
            for column in self.cols:
                if item_1.data[column] != "0":
                    all_zero = False

            if all_zero:
                items_to_remove.append(index_1)

        for item_index in items_to_remove:
            self.items.pop(item_index)

    def default_merge_method(self, item_1, item_2):
        """ Combine the values of two items into one item's data dictionary. """
        for index, key in enumerate(self.cols):
            if self.coltypes[index] == bool:
                item_1.data[key] = item_1.data[key] or item_2.data[key]
            
            elif self.coltypes[index] == int or self.coltypes[index] == float:
                item_1.data[key] += (item_2.data[key] - item_1.data[key]) * 0.5
                
            elif self.coltypes[index] == str:
                item_1.data[key] += item_2.data[key]

            elif self.coltypes[index] == list:
                item_1.data[key] = item_1.data[key] + item_2.data[key]
        return item_1

    def default_compare_method(self, item_1, item_2):
        diff = 0
        for index, key in enumerate(self.cols):
            if self.coltypes[index] == bool:
                diff += 2 * abs(item_1.data[key] - item_2.data[key]) # Max 2
            
            elif self.coltypes[index] == int or self.coltypes[index] == float:
                num_diff = abs(item_2.data[key] - item_1.data[key])
                diff += 16 * num_diff / math.sqrt((num_diff + 2) * (num_diff + 2) + 1) # Max 16
                
            elif self.coltypes[index] == str:
                # Length diff
                len_diff = abs(len(item_1.data[key]) - len(item_2.data[key]))

                # Number of letters diff
                num_eq = 0
                num_diff = 0
                num_consec = 0
                max_consec = 0
                for letter1 in item_1.data[key]:
                    found = False
                    for letter2 in item_2.data[key]:
                        if letter1 == letter2 and not found:
                            found = True

                    if found:
                        num_eq += 1
                        num_consec += 1
                        if num_consec > max_consec:
                            max_consec = num_consec
                    else:
                        num_diff += 1
                        num_consec = 0

                sim_diff = max(0, num_diff * 3 - num_eq**2 - max_consec**2 + len_diff * 2)
                diff += 16 * sim_diff / math.sqrt((sim_diff + 2) * (sim_diff + 2) + 1) # Max 16


            elif self.coltypes[index] == list:
                # No restrictions on list types, so just compare length and equality
                len_diff = abs(len(item_1.data[key]) - len(item_2.data[key]))

                num_eq = 0
                num_diff = 0
                for item1 in item_1.data[key]:
                    found = False
                    for item2 in item_2.data[key]:
                        if item1 == item2 and not found:
                            found = True

                    if found:
                        num_eq += 1
                    else:
                        num_diff += 1

                sim_diff = max(0, num_eq - num_diff - len_diff * 2)
                diff += 16 * sim_diff / math.sqrt((sim_diff + 2) * (sim_diff + 2) + 1) # Max 16
        return diff / 50 # 0-1, 0 = min. diff, 1 = max. diff

    def get_items_containing(self, column, target_values):
        """ Get a list of items containing all members of the target array """
        if isinstance(target_values, str):
            target_values = [target_values]

        candidates = []
        for item in self.items:
            all_targets_present = True
            for value in target_values:
                missing = True

                if value in item.data[column]:
                    # TODO: Make this check use some approximation logic, e.g. to accept minceraft instead of minecraft
                    missing = False

                if isinstance(item.data[column], list):
                    for word in item.data[column]:
                        if value.lower() in word.lower():
                            missing = False

                if missing:
                    all_targets_present = False

            if all_targets_present:
                candidates.append(item)

        return candidates

    def get_best_match(self, target_item, candidates = None, threshold = 0, compare_method = None, ignored_cols = []):
        """ Get the item with the smallest delta from the target item """
        
        if candidates == None:
            candidates = self.items

        best_score = threshold
        best_candidate = None
        for candidate in candidates:
            for column in ignored_cols:
                target_item.data[column] = candidate.data[column]

            score = 0
            if compare_method is not None and callable(compare_method):
                score = 1 - compare_method(target_item, candidate)
            else:
                score = 1 - self.default_compare_method(target_item, candidate)

            if score > best_score:
                best_score = score
                best_candidate = candidate

        return best_candidate
    
    def get_max_of_col(self, column):
        """ Gets the maximum value of the target column across all tracked items. """
        max = 0
        for item in self.items:
            if item.data[column] > max:
                max = item.data[column]
        return max

    def get_min_of_col(self, column):
        """ Gets the minimum value of the target column across all tracked items. """
        min = math.inf
        for item in self.items:
            if item.data[column] < min:
                min = item.data[column]
        return min

class SimpleFrequencyTracker(Tracker):
    def __init__(self, name, data_file_path = None, item_structure = {},
        data_source = None, allow_near_duplicates = True, compare_method = None,
        merge_method = None, use_csv = True):
        
        super()

    def check_equal_cols(self,):
        pass

    def increment_freq(self,):
        pass

    def run():
        pass
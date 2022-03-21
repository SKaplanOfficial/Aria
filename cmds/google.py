"""
Google

Last Updated: Version 0.0.1
"""

from datetime import datetime, timedelta
import applescript
import webbrowser


class Command:
    def __init__(self):
        pass

    def execute(self, str_in, managers):
        url = "https://www.google.com/search?q="
        query = str_in[7:]
        print("Opening " + url+query + "...")

        # Open url in new tab (1=window, 2=tab)
        #webbrowser.open(url+query, new=2)

        self.track_searches(managers["tracking"], query)


    def track_searches(self, TrackingManager, query):
        google_tracker = TrackingManager.init_tracker("google")
        google_tracker.load_data()

        now = datetime.now()
        current_time = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()

        relevant_searches = google_tracker.get_items_containing("targets", query)
        target_search = google_tracker.new_item([current_time, current_time, 1, [query]])
        best_candidate = google_tracker.get_best_match(target_search, relevant_searches, ignored_cols = ["start_time", "end_time"])
        
        if relevant_searches == [] or best_candidate.data["targets"] != query:
            # Not an exact match, so add new article
            google_tracker.add_item(target_search)

        def check_targets(item_1, item_2):
            score = 0
            if item_1.data["targets"] == item_2.data["targets"]:
                score = 1

            return score

        def increment_freq(item_1, item_2):
            now = datetime.now()
            current_time = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
            item_1.data["frequency"] += 1
            item_1.data["start_time"] = current_time
            item_1.data["end_time"] = current_time
            return item_1

        google_tracker.remove_near_duplicates(compare_method = check_targets, merge_method = increment_freq)

        # Increment queries more general than the search term with matching words
        for item in google_tracker.items:
            for word in target_search.data["targets"]:
                if item.data["targets"] != [word] and (item.data["targets"][0]+" " in word or " "+item.data["targets"][0] in word):
                    item.data["frequency"] += 1

        google_tracker.save_data()

    def report(self, TrackingManager):
        google_tracker = TrackingManager.init_tracker("google")
        google_tracker.load_data()

        print("\n--Common Searches--")
        print("Your 10 most common (exact) searches:")
        common_searches = google_tracker.get_entries(sort=lambda item: -item["frequency"])

        for index, search in enumerate(common_searches):
            print("[" + str(search.data["frequency"]) + " times]", search.data["targets"][0])
            if index > 9:
                break

        print("\nFrequent search terms")
        terms = {}
        for search in google_tracker.entries:
            for word in search["targets"][0].split(" "):
                if word in terms:
                    terms[word] += search.data["frequency"]
                else:
                    terms[word] = search.data["frequency"]

        common_terms = sorted(terms.items(), key=lambda item: -item[1])
        for index, term in enumerate(common_terms):
            print("[" + str(term[1]) + " times]", term[0])
            if index > 9:
                break


        print("\n\n--Averages--")
        num_searches = 0
        times = []
        query_lengths = []

        for search in google_tracker.entries:
            num_searches += int(search.data["frequency"])
            times.append(float(search.data["start_time"]) * int(search.data["frequency"]))
            query_lengths.append(len(search.data["targets"][0].split(" ")) * int(search.data["frequency"]))
        
        average_search_time = sum(times) / num_searches
        print("Average search time:", timedelta(seconds=average_search_time))

        average_query_length = sum(query_lengths) / num_searches
        print("Average query length:", average_query_length)


        print("\n\n--Search History--")
        for search in google_tracker.entries:
            start_time = search.data["start_time"]
            end_time = search.data["end_time"]
            frequency = search.data["frequency"]
            targets = search.data["targets"]

            print("Search query:", targets[0])
            print("Searched between", timedelta(seconds=start_time), "and", timedelta(seconds=end_time))
            print("Frequency:", frequency, "\n")

    def handler_checker(self, str_in, managers):
        if "Safari" in managers["context"].current_app:
            if "http" in str_in or ".com" in str_in or ".net" in str_in or ".io" in str_in:
                return 5

            scpt = applescript.AppleScript('''try
                tell application "Safari"
                    set tabURL to URL of current tab of the front window
                end tell
                return tabURL
            on error
                -- blah
            end try
            ''')
            tabURL = scpt.run()
            if tabURL is not None:
                if "google" in tabURL:
                    return 2
            return 1
        return 0

    def handler(self, str_in, managers, score):
        print("Handling input in Safari...")

        url = "https://www.google.com/search?q="
        if score == 1:
            # Safari is open, might not be on Google tab
            webbrowser.open(url+str_in, new=2)
        elif score == 2: 
            # Safari is on Google tab
            webbrowser.open(url+str_in, new=0)
        elif score == 5:
            # User specified a URL to go to
            if not str_in.startswith("http"):
                str_in = "http://" + str_in
            webbrowser.open(str_in, new=2)

        self.track_searches(managers["tracking"], str_in)

    def help(self):
        print("This is the help text for the google plugin.")
"""
Google

Last Updated: February 24, 2022
"""

import subprocess
import webbrowser
from datetime import datetime, timedelta


class Command:
    def __init__(self, *args, **kwargs):
        pass

    def execute(self, str_in, refs):
        url = "https://www.google.com/search?q="
        query = str_in[7:]
        print("Opening " + url+query + "...")

        # Open url in new tab (1=window, 2=tab)
        # webbrowser.open(url+query, new=2)

        self.track_searches(refs[1], query)


    def track_searches(self, TrackingManager, query):
        google_tracker = TrackingManager.init_tracker("google")
        google_tracker.load_data()

        now = datetime.now()
        current_time = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()

        relevant_searches = google_tracker.get_entries_containing(query)
        target_search = google_tracker.entry_obj(current_time, current_time, 1, [query])
        best_candidate = google_tracker.get_best_match(target_search, relevant_searches, ignored_cols = ["start_time", "end_time"])
        
        if relevant_searches == [] or best_candidate["targets"][0] != query:
            # Not an exact match, so add new article
            google_tracker.add_entry(target_search)

        incremented = []
        for word in query.split(" "):
            searches_containing_word = google_tracker.get_entries_containing(word)
            target_search = google_tracker.entry_obj(current_time, current_time, 1, [word])

            def custom_score(search, target_search, current_score):
                if search not in custom_score.incremented:
                    custom_score.incremented.append(search)
                    if search["targets"][0] in custom_score.query:
                        search["frequency"] += 1
                return current_score
            custom_score.incremented = incremented
            custom_score.query = query

            google_tracker.get_best_match(target_search, searches_containing_word, custom_score_func = custom_score, ignored_cols = ["start_time", "end_time"])

        google_tracker.save_data()

    def report(self, TrackingManager):
        google_tracker = TrackingManager.init_tracker("google")
        google_tracker.load_data()

        print("\n--Common Searches--")
        print("Your 10 most common (exact) searches:")
        common_searches = google_tracker.get_entries(sort=lambda item: -item["frequency"])

        for index, search in enumerate(common_searches):
            print("[" + str(search["frequency"]) + " times]", search["targets"][0])
            if index > 9:
                break

        print("\nFrequent search terms")
        terms = {}
        for search in google_tracker.entries:
            for word in search["targets"][0].split(" "):
                if word in terms:
                    terms[word] += search["frequency"]
                else:
                    terms[word] = search["frequency"]

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
            num_searches += int(search["frequency"])
            times.append(float(search["start_time"]) * int(search["frequency"]))
            query_lengths.append(len(search["targets"][0].split(" ")) * int(search["frequency"]))
        
        average_search_time = sum(times) / num_searches
        print("Average search time:", timedelta(seconds=average_search_time))

        average_query_length = sum(query_lengths) / num_searches
        print("Average query length:", average_query_length)


        print("\n\n--Search History--")
        for search in google_tracker.entries:
            start_time = search["start_time"]
            end_time = search["end_time"]
            frequency = search["frequency"]
            targets = search["targets"]

            print("Search query:", targets[0])
            print("Searched between", timedelta(seconds=start_time), "and", timedelta(seconds=end_time))
            print("Frequency:", frequency, "\n")

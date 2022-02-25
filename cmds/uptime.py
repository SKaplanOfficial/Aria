"""
Update

Last Updated: February 24, 2022
"""

import subprocess
import webbrowser
from datetime import datetime, timedelta
import urllib.request


class Command:
    def __init__(self, *args, **kwargs):
        pass

    def execute(self, str_in, refs):
        query = str_in[7:]
        if "http://" not in query:
            query = "http://" + query

        status = 0
        try:
            status = urllib.request.urlopen(query).getcode()
        except Exception as e:
            pass

        if status == 200:
            print(query, "is UP")
        else:
            print(query, "is DOWN")

        # Track uptime
        def tracking_method(site, target_site, current_score):
            uptime_freq = int(site["frequency"])
            num_decimal_places = 0
            total_freq = 2

            if site["targets"][0] == query and site["frequency"] != 1:
                num_decimal_places = len(str(site["frequency"]).split(".")[1])
                total_freq = int(round(site["frequency"] % 1, num_decimal_places) * 10 ** num_decimal_places) + 1

            if site["targets"][0] == query:
                # Exact match
                if status == 200:
                    uptime_freq += 1
                percent = uptime_freq / total_freq * 100
                print("The site has been up " + str(percent) + "% of the time.\n")
                tracking_method.first_check = 0

            if status != 200:
                target_site["frequency"] = 0.1

            if tracking_method.first_check == 1:
                print("This site has not been checked before.\n")
                tracking_method.first_check = 0

            updated_freq = float(str(uptime_freq) + "." + str(total_freq))
            site["frequency"] = updated_freq
            tracking_method.first_iter = 0
            return current_score

        tracking_method.first_check = 1

        TrackM = refs[1]
        TrackM.run_basic_tracker("uptime", query, tracking_method)
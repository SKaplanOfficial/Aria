"""
Wikipedia

Last Updated: February 24, 2022
"""

import subprocess
import webbrowser
from datetime import datetime


class Command:
    def __init__(self, *args, **kwargs):
        pass
        
    def execute(self, str_in, refs):
        url = "https://en.wikipedia.org/w/index.php?search="
        query = str_in[10:]
        print("Opening " + url+query + "...")

        # Open url in new tab (1=window, 2=tab)
        webbrowser.open(url+query, new=2)

        # Track wiki searches
        def tracking_method(article, target_article, current_score):
            # If the article is relevant, increase its freq
            article["frequency"] += 1
            return current_score

        TrackM = refs[1]
        TrackM.run_basic_tracker("wiki", query, tracking_method)

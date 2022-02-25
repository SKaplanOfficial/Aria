"""
Site

Last Updated: March 8, 2021
"""

import subprocess
import webbrowser


class Command:
    def __init__(self, *args, **kwargs):
        print("Opening website...")

    def execute(self, str_in, context):
        url = str_in[5:]

        if url is None or url == "":
            url = "https://www.google.com"

        if not url.startswith("http") and not url.startswith("https"):
            url = "https://"+url

        # Open url in new tab (1=window, 2=tab)
        webbrowser.open(url, new=2)

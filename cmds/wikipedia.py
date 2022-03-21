"""
Wikipedia

Last Updated: Version 0.0.1
"""

import webbrowser
import time

class Command:
    def __init__(self):
        pass
        
    def execute(self, str_in, managers):
        cmd_args = str_in.split(" ")
        url = "https://en.wikipedia.org/w/index.php?search="

        query = ""
        if cmd_args[0] == "wikipedia":
            query = str_in[10:]
        elif cmd_args[0] == "wiki":
            query = str_in[5:]

        print("Opening " + url+query + "...")

        # Open url in new tab (1=window, 2=tab)
        webbrowser.open(url+query, new=2)

        managers["tracking"].run_frequency_tracker("wiki", [time.time(), 1, query])

    def get_template(self, new_cmd_name):
        print("Enter search URL: ")
        url_new = input()

        query_length = len(new_cmd_name)+1

        template = {
            'url': '"'+url_new+'"',
            'query': 'str_in['+str(query_length)+':]',
        }

        return template
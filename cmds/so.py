"""
So

Last Updated: March 8, 2021
"""

import subprocess
import webbrowser


class Command:
    def __init__(self, *args, **kwargs):
        print("Opening so...")

    def execute(self, str_in, context):
        url = "https://stackoverflow.com/search?q="
        query = str_in[3:]

        # Open url in new tab (1=window, 2=tab)
        webbrowser.open(url+query, new=2)

    def get_template(self, new_cmd_name):
        print("Enter search URL: ")
        url_new = input()

        query_length = len(new_cmd_name)+1

        template = {
            'url': '"'+url_new+'"',
            'query': 'str_in['+str(query_length)+':]',
        }

        return template

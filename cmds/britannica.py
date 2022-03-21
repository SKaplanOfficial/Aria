"""
Britannica

Last Updated: Version 0.0.1
"""

import webbrowser


class Command:
    def __init__(self):
        pass

    def execute(self, str_in, managers):
        print("Opening britannica...")
        url = "https://www.britannica.com/search?query="
        query = str_in[11:]

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

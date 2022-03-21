"""
News

Last Updated: Version 0.0.1
"""

import webbrowser
import random
import pdfkit
from datetime import datetime


class Command:
    def __init__(self):
        self.sources = [
            "https://www.nytimes.com",
            "https://www.huffpost.com",
            "https://news.yahoo.com",
            "https://news.google.com",
            "https://www.bbc.co.uk",
            "https://www.thestar.com",
            "https://www.reddit.com/r/news",
            "https://www.cnn.com",
            "https://www.msnbc.com",
            "https://www.nbcnews.com",
            "https://www.cbsnews.com",
            "https://www.reuters.com",
            "https://abcnews.go.com",
            "https://www.usnews.com",
            "https://news.sky.com",
        ]

        self.search_urls = [
            "https://www.nytimes.com/search?query=",
            "https://www.huffpost.com/search?keywords=",
            "https://news.search.yahoo.com/search?p=",
            "https://news.google.com/search?q=",
            "https://www.bbc.co.uk/search?q=",
            "https://www.thestar.com/search.html?q=",
            "https://www.reddit.com/r/news/search/?q=",
            "https://www.cnn.com/search?q=",
            "https://www.msnbc.com/search/?q=",
            "https://www.nbcnews.com/search/?q=",
            "https://www.cbsnews.com/search/?q=",
            "https://www.reuters.com/site-search/?query=",
            "https://abcnews.go.com/search?searchtext=",
            "https://www.usnews.com/search?q=",
            "https://news.sky.com/topic/",
        ]

    def execute(self, str_in, managers):
        cmd_args = str_in[5:].split(" ")

        export = False
        if "export" in cmd_args:
            export = True
            cmd_args.remove("export")

        if "latest" in cmd_args:
            if len(cmd_args) == 2 and cmd_args[1] == "all":
                for source in self.sources:
                    # Open url in new tab (1=window, 2=tab)
                    self.open_url(source, 2, export, managers)

            if len(cmd_args) == 2 and cmd_args[1].isdigit():
                # Open x number of random sources
                selected = []
                for x in range(0, int(cmd_args[1])):
                    selection = random.choice(self.sources)
                    while selection in selected:
                        selection = random.choice(self.sources)
                    selected.append(selection)

                    self.open_url(selection, 2, export, managers)

            elif len(cmd_args) > 1:
                # Open all provided sources
                for source in self.sources:
                    for arg in cmd_args:
                        if arg in source:
                            self.open_url(source, 2, export, managers)

            else:
                # Open a random site for latest news
                self.open_url(random.choice(self.sources), 2, export, managers)

        else:
            if len(cmd_args) == 1:
                # Search a random news url
                query = cmd_args[0]
                self.open_url(random.choice(self.search_urls)+query, 2, export, managers)

            elif len(cmd_args) > 1:
                topics = []
                urls = []

                for arg in cmd_args:
                    if "http" in arg and "://" in arg:
                        urls.append(arg)
                    else:
                        topics.append(arg)

                if len(urls) > 0:
                    # Search all topics on each supplied url
                    for url in urls:
                        for topic in topics:
                            self.open_url(url+topic, 2, export, managers)

                else:
                    # Search all topics on a random url
                    url = random.choice(self.search_urls)
                    for topic in topics:
                        self.open_url(url+topic, 2, export, managers)

    def open_url(self, url, tabmode, export, managers):
        if export:
            now = datetime.now()
            filename = "NEWS-"+now.strftime("%B-%d-%Y")
            file_path = managers["config"].get("aria_path")+"/docs/"+filename+".pdf"
            pdfkit.from_url(url, file_path)
        else:
            webbrowser.open(url, new=tabmode)

    def handler_checker(self, str_in, managers):
        if str_in.endswith("news"):
            return 3
        return 0

    def handler(self, str_in, managers, score):
        query = "news " + str_in[:str_in.index(" news")]
        self.execute(query, managers)

    def get_template(self, new_cmd_name):
        print("Enter search URL: ")
        url_new = input()

        query_length = len(new_cmd_name)+1

        template = {
            'url': '"'+url_new+'"',
            'query': 'str_in['+str(query_length)+':]',
        }

        return template

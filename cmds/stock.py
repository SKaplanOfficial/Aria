"""
Stocks

Last Updated: Version 0.0.1
"""

import applescript
import webbrowser


class Command:
    def __init__(self):
        self.favorite_stocks = ["AAPL", "GOOG", "GOOGL", "MSFT", "AMZN", "NTFX"]

    def execute(self, str_in, managers):
        url = "https://finance.yahoo.com/quote/"
        cmd_args = str_in[6:].split(" ")

        if cmd_args[0] == "favorites":
            for stock in self.favorite_stocks:
                # Open url in new tab (1=window, 2=tab)
                webbrowser.open(url+stock, new=2)
        else:
            stock = cmd_args[0]
            webbrowser.open(url+stock, new=2)

    def handler_checker(self, str_in, managers):
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

        score = 0
        if "Stocks" in managers["context"].current_app:
            score = 2

        if "Safari" in managers["context"].current_app:
            if tabURL is not None and "finance.yahoo" in tabURL:
                score = 4

        for stock in self.favorite_stocks:
            if str_in == stock:
                score += 1
            break
        
        return score

    def handler(self, str_in, managers, score):
        print("Handling stock lookup...")

        url = "https://finance.yahoo.com/quote/"
        if score == 2:
            # User supplied a favorite stock symbol 
            webbrowser.open(url + str_in, new=2)
        elif score == 3: 
            # Stock app is open
            webbrowser.open(url+str_in, new=2)
        elif score == 4:
            # User supplied a favorite stock symbol & the stocks app is open
            webbrowser.open(url+str_in, new=2)
        elif score == 5:
            # Yahoo finance is open
            webbrowser.open(url+str_in, new=0)
        elif score == 6:
            # User supplied a favorite stock symbol & Yahoo finance is open
            webbrowser.open(url+str_in, new=0)

    def get_template(self, new_cmd_name):
        print("Enter search URL: ")
        url_new = input()

        query_length = len(new_cmd_name)+1

        template = {
            'url': '"'+url_new+'"',
            'query': 'str_in['+str(query_length)+':]',
        }

        return template
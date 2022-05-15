"""
Search

Last Updated: Version 0.0.1
"""

import webbrowser, re, math

from ariautils.command_types import WebAction
from ariautils.tracking_utils import TrackingManager
from ariautils import command_utils, io_utils

from ariautils.misc_utils import get_json

class Search(WebAction):
    def __init__(self):
        pass

    def execute(self, str_in, origin):
        # Expected input structure: search [url] [query] OR [url] query OR search [query] on/in/with [url]

        # Get input
        strs = str_in.split()

        site_name = None
        url = None
        url_type = None

        # io_utils.dprint("Checking term '" + term + "'")
        matched_url, match_type = self.get_web_target(strs[1])

        if matched_url != None:
            # Term is a web target (URL or shortname of site)
            # Use first web target occurrence
            # TODO: Add support for multiple web targets?
            if url == None:
                site_name = strs[1]
                url = matched_url
                url_type = match_type

        queries = strs[2:]

        if url == None:
            # No web target found -- default to Google
            # TODO: Inferencing? Prediction? idk
            io_utils.dprint("No URL provided, defaulting to Google")
            url = "https://www.google.com/search?q="
        else:
            io_utils.dprint("Search url: " + url)

        if queries == []:
            # Not query provided -- just open the search link
            io_utils.dprint("No query provided, opening search link")
            queries.append(" ")
        else:
            # One or more queries are present
            queries__str = " ".join(queries)
            queries = queries__str.split(",")
            io_utils.dprint(str(len(queries)) + " queries found:")

        if (site_name == url or url_type == "custom") and url != None:
            # Site name is not short, shorten it
            site_name = self.name_from_url(url)

        if url_type == "custom":
            # Try to make search url
            if "/search" in url or "?" in url:
                # It's already a search URL, don't change anything
                pass
            else:
                search_url = self.find_search_url(url)
                if search_url != None:
                    print("Identified URL:", search_url)
                    url = search_url
                else:
                    url = url+"/search?q=&s=&search=&query=&term="
                    search_url = self.find_search_url(url)
                    if search_url != None:
                        print("Identified URL:", search_url)
                        url = search_url

        json_response = None
        try:
            json_response = get_json(url)
        except:
            pass

        # Open each query
        for query in queries:
            if query != " ":
                io_utils.dprint("\t"+query)
            if json_response != None:
                self.links_from_json(url, query)
            else:
                self.search(url, query.strip())

        if url != None and site_name != None:
            self.track_urls(url, site_name)

        # search_url = self.find_search_url(site)
        # print(search_url)

    def links_from_json(self, url, query):
        base_url = url

        query = query.replace(" ", "%20")
        
        if "=" in url:
            url = url.replace("=", "=" + query)
        else:
            url = url + query

        json_response = get_json(url)

        links = []
        self.traverse_json_obj(json_response, base_url, links)

        links.sort()
        if len(links) == 0:
            print("I couldn't find any links matching '" + query + "' via " + base_url)
        elif len(links) == 1:
            print("I found this link: " + links[0])
            webbrowser.open(links[0], new=2)
        else:
            print("I found " + str(len(links)) + " links:")
            for index, link in enumerate(links):
                print("  " + str(index + 1) + ": " + link)

    def traverse_json_obj(self, obj, base_url, links):
        for key in obj:
            if isinstance(obj[key], dict):
                self.print_json_obj(obj[key], base_url, links)
            else:
                if command_utils.plugins["tokenize"].url_target(str(obj[key]))[0]:
                    links.append(str(obj[key]))
                else:
                    components = str(obj[key]).split()
                    for item in components:
                        if "href=" in item:
                            if not item.startswith(base_url):
                                item = base_url + item
                            links.append(item.replace("href=", "").replace('"', ''))

    def name_from_url(self, url):
        new_url = url[url.index("://")+3:]

        if "/" in new_url:
            new_url = new_url[:new_url.index("/")]

        parts = new_url.split(".")
        name = parts[-2]

        io_utils.dprint("Shortened " + url + " to '" + name + "'")
        return name


    def search(self, url, query):
        # Open url in new tab (1=window, 2=tab)
        if "=" in url:
            populated_url = url
            print(url)
            p = re.compile(r'(=)(&|$)')
            m = p.finditer(url)
            if (m is not None):
                for index, match in enumerate(m):
                    populated_url = populated_url[:match.span()[0] + index * len(query)] + "=" + query + populated_url[match.span()[0] + 1 + index * len(query):]
                    print(populated_url)
            webbrowser.open(populated_url, new=2)
        else:
            print(url)
            webbrowser.open(url + query, new=2)
        #pass

    def get_web_target(self, term):
        item_structure = {
            "url" : str,
            "shortname" : str,
        }
        url_tracker = TrackingManager.init_tracker("search_urls", item_structure = item_structure)
        url_tracker.load_data()

        relevant_urls = url_tracker.get_items_containing("url", term)
        relevant_urls += url_tracker.get_items_containing("shortname", term)

        if relevant_urls == [] and not self.check_if_url(term):
            relevant_urls = url_tracker.items

        target_url = url_tracker.new_item([term, term])

        # Check for matching shortname in history
        best_candidate = url_tracker.get_best_match(target_url, relevant_urls, threshold = 0.15, ignored_cols=["url"], compare_method = self.check_similarity)
        if best_candidate != None:
            io_utils.dprint("Found matching shortname in history")
            return best_candidate.data["url"], "shortname"

        # No match, check for matching URL in history
        best_candidate = url_tracker.get_best_match(target_url, relevant_urls, threshold = 0.15, ignored_cols=["shortname"], compare_method = self.check_similarity)
        if best_candidate != None:
            io_utils.dprint("Found matching URL in history")
            return best_candidate.data["url"], "url"

        # Still no match, check if the term itself is a URL
        if self.check_if_url(term):
            io_utils.dprint("Found URL in input")
            if not "http" in term:
                term = "http://"+term
            return term, "custom"

        # No web target
        io_utils.dprint("No web target in input")
        return None, None

    def check_if_url(self, term):
        if "http" in term or "www." in term:
            return True

        tlds = [".com", ".net", ".org", ".io", ".de", ".uk", ".xyz", ".gov", ".tk", ".nl", ".ca", ".uk"]

        for tld in tlds:
            if tld in term:
                return True
        return False

    # def find_search_url(self, base_site):
    #     # html_text = requests.get(base_site).text
    #     # soup = BeautifulSoup(html_text, 'html.parser')

    #     # print(html_text)

    #     # input_fields = soup.find_all('form')

    #     # for field in input_fields:
    #     #     print(field.action)

    #     # return 'hi'
    #     pass

    def get_template(self, new_cmd_name):
        # TODO: Fix this or remove it
        print("Enter base command and args: ")
        cmd_new = input()

        query_length = len(new_cmd_name)+1

        template = {
            'command': str(cmd_new.split(" ")),
            'query': 'str_in['+str(query_length)+':]',
            'data_file_name': "",
        }

        return template

    # def report(self, TrackingManager):
    #     google_tracker = TrackingManager.init_tracker("google")
    #     google_tracker.load_data()

    #     print("\n--Common Searches--")
    #     print("Your 10 most common (exact) searches:")
    #     common_searches = google_tracker.get_entries(sort=lambda item: -item["frequency"])

    #     for index, search in enumerate(common_searches):
    #         print("[" + str(search.data["frequency"]) + " times]", search.data["targets"][0])
    #         if index > 9:
    #             break

    #     print("\nFrequent search terms")
    #     terms = {}
    #     for search in google_tracker.entries:
    #         for word in search["targets"][0].split(" "):
    #             if word in terms:
    #                 terms[word] += search.data["frequency"]
    #             else:
    #                 terms[word] = search.data["frequency"]

    #     common_terms = sorted(terms.items(), key=lambda item: -item[1])
    #     for index, term in enumerate(common_terms):
    #         print("[" + str(term[1]) + " times]", term[0])
    #         if index > 9:
    #             break


    #     print("\n\n--Averages--")
    #     num_searches = 0
    #     times = []
    #     query_lengths = []

    #     for search in google_tracker.entries:
    #         num_searches += int(search.data["frequency"])
    #         times.append(float(search.data["start_time"]) * int(search.data["frequency"]))
    #         query_lengths.append(len(search.data["targets"][0].split(" ")) * int(search.data["frequency"]))
        
    #     average_search_time = sum(times) / num_searches
    #     print("Average search time:", timedelta(seconds=average_search_time))

    #     average_query_length = sum(query_lengths) / num_searches
    #     print("Average query length:", average_query_length)


    #     print("\n\n--Search History--")
    #     for search in google_tracker.entries:
    #         start_time = search.data["start_time"]
    #         end_time = search.data["end_time"]
    #         frequency = search.data["frequency"]
    #         targets = search.data["targets"]

    #         print("Search query:", targets[0])
    #         print("Searched between", timedelta(seconds=start_time), "and", timedelta(seconds=end_time))
    #         print("Frequency:", frequency, "\n")

    # def handler_checker(self, str_in, managers):
    #     if "Safari" in managers["context"].current_app:
    #         if "http" in str_in or ".com" in str_in or ".net" in str_in or ".io" in str_in:
    #             return 5

    #         scpt = applescript.AppleScript('''try
    #             tell application "Safari"
    #                 set tabURL to URL of current tab of the front window
    #             end tell
    #             return tabURL
    #         on error
    #             -- blah
    #         end try
    #         ''')
    #         tabURL = scpt.run()
    #         if tabURL is not None:
    #             if "google" in tabURL:
    #                 return 2
    #         return 1
    #     return 0

    # def handler(self, str_in, managers, score):
    #     print("Handling input in Safari...")

    #     url = "https://www.google.com/search?q="
    #     if score == 1:
    #         # Safari is open, might not be on Google tab
    #         webbrowser.open(url+str_in, new=2)
    #     elif score == 2: 
    #         # Safari is on Google tab
    #         webbrowser.open(url+str_in, new=0)
    #     elif score == 5:
    #         # User specified a URL to go to
    #         if not str_in.startswith("http"):
    #             str_in = "http://" + str_in
    #         webbrowser.open(str_in, new=2)

    #     self.track_searches(managers["tracking"], str_in)

    def track_urls(self, url, shortname):
        item_structure = {
            "url" : str,
            "shortname" : str,
        }
        url_tracker = TrackingManager.init_tracker("search_urls", item_structure = item_structure)
        url_tracker.load_data()

        relevant_urls = url_tracker.get_items_containing("url", url)
        relevant_urls += url_tracker.get_items_containing("shortname", shortname)

        target_url = url_tracker.new_item([url, shortname])
        best_candidate = url_tracker.get_best_match(target_url, relevant_urls, compare_method = self.check_similarity)
        
        if relevant_urls == [] or best_candidate.data["url"] != url:
            # Not an exact match, so add new url
            url_tracker.add_item(target_url)

        url_tracker.remove_duplicates(merge_values = False)
        url_tracker.remove_empty_items()

        url_tracker.save_data()

    def check_similarity(self, item_1, item_2):
        diff = 0
        for key in ["url", "shortname"]:
            len_diff = abs(len(item_1.data[key]) - len(item_2.data[key]))

            # Number of letters diff
            num_eq = 0
            num_diff = 0
            num_consec = 0
            max_consec = 0

            word_len = min(len(item_1.data[key]), len(item_2.data[key]))
            for i in range(0, word_len):
                letter1 = item_1.data[key][i]
                letter2 = item_2.data[key][i]

                if letter1 == letter2:
                    i += 1
                    num_eq += 1
                    num_consec += 1
                    if num_consec > max_consec:
                        max_consec = num_consec
                else:
                    num_diff += 1
                    num_consec = 0

            sim_diff = max(0, (num_diff + 1) / (len_diff + 1) - num_eq * - max_consec)
            diff += sim_diff / math.sqrt((sim_diff + 2) * (sim_diff + 2) + 1) # Max 1
        return 1 - diff/2

command = Search()
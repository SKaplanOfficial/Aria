"""
Jump

Last Updated: March 10, 2021
"""

import os
import csv
import datetime
import requests
from bs4 import BeautifulSoup
from pathlib import Path


class Command:
    def __init__(self, *args, **kwargs):
        self.aria_path = args[0]

    def execute(self, str_in, context):
        print("Finding search link...")

        strs = str_in.split()
        site = strs[1]

        search_url = self.find_search_url(site)
        print(search_url)

    def find_search_url(self, base_site):
        html_text = requests.get(base_site).text
        soup = BeautifulSoup(html_text, 'html.parser')

        print(html_text)

        input_fields = soup.find_all('form')

        for field in input_fields:
            print(field.action)

        return 'hi'

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

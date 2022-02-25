"""
Newfile

Last Updated: March 8, 2021
"""

import subprocess
import datetime


class Command:
    def __init__(self, *args, **kwargs):
        print("Opening new file...")

    def execute(self, str_in, context):
        path = "/Users/steven/Documents/2020/Python/Aria.3/docs/"

        current_time = datetime.datetime.now()
        time_string = current_time.strftime("%d-%B-%Y-%I.%M.%S-%p")
        filename = 'file-'+time_string+'.txt'

        with open(path+filename, 'a') as fp:
            pass
        subprocess.call(["open", "-a", "Textedit", path+filename])

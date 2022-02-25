"""
NETT

Last Updated: March 8, 2021
"""

import os
import time
import subprocess
import webbrowser
from appscript import *


class Command:
    def __init__(self, *args, **kwargs):
        print("Connecting to NETT...")

    def execute(self, str_in, context):
        os.system("eval $(ssh-agent)")
        os.system("ssh-add -K /Users/steven/Documents/2021/pem/nett-dev.pem")

        app('Terminal').do_script(
            "ssh -L 5000:localhost:80 -L 4000:localhost:22 -J ec2-user@18.191.145.107 ubuntu@10.0.4.201").run()

        time.sleep(2)
        os.system('open /Applications/FileZilla.app --args -c "0/NETT VPC"')

        # Open url in new tab (1=window, 2=tab)
        webbrowser.open(
            "https://drive.google.com/drive/u/0/folders/0AKpYnFS065NiUk9PVA", new=2)
        time.sleep(0.5)
        webbrowser.open("https://nettsl.org", new=2)
        time.sleep(0.5)
        webbrowser.open("http://localhost:5000", new=2)

        os.system(
            'cd "/Users/steven/Documents/2021/Servant Heart/Projects/nett_dev" && code .')

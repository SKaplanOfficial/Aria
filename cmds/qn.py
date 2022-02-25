"""
Quicknote Alias

Last Updated: February 2, 2022
"""

import subprocess
from . import quicknote


class Command:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs;

    def execute(self, str_in, context):
        qn = quicknote.Command(*self.args, **self.kwargs)
        qn.execute(str_in, context)

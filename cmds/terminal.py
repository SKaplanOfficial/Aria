"""
Terminal

Last Updated: March 8, 2021
"""


class Command:
    def __init__(self, *args, **kwargs):
        print("Dropping to terminal...")

    def execute(self, str_in, context):
        return "run drop to term"

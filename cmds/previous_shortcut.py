"""
Previous Shortcut

Last Updated: Version 0.0.1
"""


class Command:
    def __init__(self):
        pass

    def execute(self, str_in, managers):
        previous_input = managers["context"].previous_input
        if previous_input == "":
            print("There is no previous input to make a shortcut from.")
        else:
            cmd_str = previous_input
            cmd_name = cmd_str.split(" ")[0]
            managers["command"].create_shortcut(cmd_str, cmd_name)

    def report(self):
        pass

    def help(self):
        pass

    def invocation(self, str_in):
        """
        Checks whether user intends to create a shortcut of the previously executed command.

        Parameters:
            str_in : str - The full text of the current command.

        Returns:
            boolean - True if the user has this intent, False otherwise.
        """
        
        verbs = [
            "shortcut",
            "make",
            "create",
            "build",
            "construct",
            "turn that into",
        ]

        subjects = [
            "a shortcut",
            "the shortcut",
            "an shortcut",
            "shortcut",
            "that"
        ]

        targets = [
            "it",
            "that",
            "a shortcut",
            "for that",
            "with that",
            "of that",
            "from that",
            "for it",
            "with it",
            "of it",
            "from it",
            "for last",
            "of last",
            "from last"
            "with last",
            "for the last command",
            "with the last command",
            "of the last command",
            "from the last command"
            "for the previous command",
            "with the previous command",
            "of the previous command",
            "from the previous command",
        ]

        found_verb = False
        for verb in verbs:
            if verb in str_in:
                found_verb = True

        found_subject = False
        for subject in subjects:
            if subject in str_in:
                found_subject = True

        found_target = False
        for target in targets:
            if target in str_in:
                found_target = True

        return found_verb and found_subject and found_target
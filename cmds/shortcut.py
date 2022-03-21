"""
Previous Shortcut

Last Updated: Version 0.0.1
"""


class Command:
    def __init__(self):
        self.aliases = ["save"]

    def execute(self, str_in, managers):
        if self.invocation(str_in):
            # Command was executed via invocation
            loc_for = str_in.find("for") + 3
            loc_of = str_in.find("of") + 2
            loc_with = str_in.find("with") + 4
            loc_subject = max(loc_for, loc_of, loc_with)

            cmd_str = str_in[loc_subject:]

        elif str_in.startswith("shortcut"):
            # Command was executed via filename
            cmd_str = str_in[9:]

        else:
            for alias in self.aliases:
                if str_in.startswith(alias):
                    # Command was executed via alias
                    cmd_str = str_in[len(alias)+1:]
                    break

        cmd_name = cmd_str.split(" ")[0]
        managers["command"].create_shortcut(cmd_str, cmd_name)

    def report(self):
        pass

    def help(self):
        pass

    def invocation(self, str_in):
        """
        Checks whether user intends to create a shortcut of the entered command string.

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
            "save",
        ]

        objects = [
            "a shortcut",
            "the shortcut",
            "shortcut",
        ]

        subjects = [
            "for",
            "of",
            "with",
        ]

        found_verb = False
        for verb in verbs:
            if verb in str_in:
                found_verb = True

        found_object = False
        for object in objects:
            if object in str_in:
                found_object = True

        found_subject = False
        for subject in subjects:
            if subject in str_in:
                found_subject = True

        return found_verb and found_object and found_subject
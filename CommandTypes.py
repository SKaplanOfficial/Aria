from textwrap import dedent

managers = None

class Command:
    """This is the base Command class for all Aria commands.

    - **parameters**, **types**, **return** and **return types**::
          :param arg1: description
          :param arg2: description
          :type arg1: type description
          :type arg1: type description
          :return: return description
          :rtype: the return type description
    """
    info = {
        "title": "", # Required.
        "repository": "", # Optional, but preferred.
        "documentation_link": "", # Optional, but preferred for non-trivial commands
        'id': "", # Required. All default Aria commands are prefixed with aria_. Custom commands should use a unique prefix.
        "version": "", # Required. SemVer is preferred, but not enforced.
        # Description is required, but has no length limit.
        "description": """""",
        "requirements": {
            # Optional, but preferred.
            # List of identifiers of other Aria commands needed in order to run this command.
            #
            # Example:
            # "aria_exec": "0.1.0",
            # "aria_jump": "0.1.0",
            #
            # Aria current checks for exact match versions and displays warnings when the versions are at all different.
            # Support for Semantic Versioning and associated control mechanisms will be added in a future release.
            # Custom commands should still utilize SemVer despite it not being enforced currently.
        },
        "extensions": {
            # Optional.
            # List of other Aria commands that extend the features of this command.
            # If one of these commands is installed and enabled, then this command utilizes it. Otherwise, this command still works with limited functionality.
            # Use the same format as with requirements.
        },
        "purposes": [
            # Optional, but highly recommended.
            # List of words/phrases capturing the general purpose of this command.
            # Aria uses these to compare query intent against the command's intended usage, specifically when there is no other known way to handle the query.
            # The weighting for this is not enough to offset direct usage of this command or override direct usage of another.
            #
            # Example 1 - For a file creation command:
            # "make file", "save content to file"
            #
            # Example 2 - For a social media command:
            # "go to social media website", "post on social media", "draft social media post", "share content on social media"
        ],
        "targets": [
            # Optional, but recommended.
            # List of examples of relevant targets for your command.
            # Targets may include:
            #   - Parts of queries that appear in the command's output in some way.
            #   - Parts of queries that the command directly acts upon, i.e. mutates, the result of which appears in the command's output.
            #   - Parts of queries that directly influence branches of the command, i.e. signals used in conditions and other control statements.
            # This improves the accuracy of Aria's comparison between query intent and the command's purpose.
            #
            # Example 1 - For a file creation command:
            # "new_file.txt", "./docs/notes", "that text", "http://example.com/example_text", "file", "document", "csv"
            #
            # Example 2 - For a social media command:
            # "www.website.com", "post", "message", "image", "my friends"
        ],
        "keywords": [
            # Optional.
            # List of words that describe this command.
            # These are used by Aria to compare query intent against the command's overall identity.
            # Keyword comparison is weighted very lightly and is mainly intended as a back-up.
        ],
        "commands": {
            # Optional.
            # List of words that describe this command.
            # These are used by Aria to compare query intent against the command's overall identity.
            # Keyword comparison is weighted very lightly and is mainly intended as a back-up.
        },
        "example_usage": [
            # Optional, but recommended.
            # List of tuples of queries that this command handles and associated descriptions.
            # Displays as past of the command's self.help() method.
        ],
        "help": [], # Optional, but preferred for non-trivia commands.
        "contact_details": { # Optional, but useful for users of the command.
            "author": "",
            "email": "",
            "website": "",
        }
    }

    def __init__(self):
        """Constructs a Command object.
        """
        self.managers = None    # A dictionary of Aria's manager objects
        pass

    def execute(self, query, origin):
        """Executes the command. This is the entrypoint for the command where all queries passed to the command are routed through, by default.
        It is possible to configure self.handler() to forgo calling self.execution(). This method is called directly by Aria when a query exactly
        satisfies the command's invocation conditions specified in self.invocation().

        Params:
        :param query: The current inputted query to evaluate and base execution on.
        :type query: str
        :param origin: An integer representing the entity calling this command's execute() method. 0 - Default exec from Aria's main loop; 1 - The command's handler method; 2 - Another command.
        :type origin: int
        """
        pass

    def get_query_type(self, query):
        """Returns a number representing the type of the supplied query. The exact meaning of the type is defined on a per-command basis, however:
        1) higher return values should indicate greater specificity of the query, and
        2) a return value of 0 or lower should indicate that the command is unable to handle the query.

        Works in combination with self.handler_checker(). The values returned by this method do not need to reflect confidence in handler suitability, but can.
        Queries that share the same type may differ in format and level of confidence in handler suitability.
        
        Runs in self.handler_checker() by default and can be used manually elsewhere to branch command execution based on query type.

        :param query: The current inputted query to evaluate.
        :type query: str

        :return: A number representing the query's type.
        :rtype: int
        """
        return 0

    def handler_checker(self, query):
        """Checks whether this command can handle a given query and returns a number representing the level of confidence that this command is a suitable handler.

        Works in combination with self.get_query_type(). The values returned by this method must reflect confidence in handler suitability,
        but that is not necessarily an ideal indication of the query's type.
        Queries that share the same type may differ in format and level of confidence in handler suitability.
        
        Runs on input of a query that does not exactly match any command's invocation conditions.

        :param query: The current inputted query to evaluate.
        :type query: str

        :return: A number representing the type of query and the level of confidence that it should be handled by this command.
        :rtype: int
        """
        return self.get_query_type(query)

    def handler(self, query, query_type):
        """Handles a query after it is tranferred to this command's control. Calls self.execute() by default. Use this method to adjust the command's flow based on the type of query that is being handled. In combindation with self.handler_checker(), this can be used to customize which queries the command responds to and how it responds to them.

        :param query: The current inputted query to be handled.
        :type query: str
        :param query_type: A number reprenting the type of query and level of confidence that it should be handled by this command.
        :type query_type: int
        """
        self.execute(query, 1)

    def help(self):
        """Displays instructions for how to use this command. Called when users input 'help [command name]'. This method does not need to be overwritten unless additional information is desired. By default, the help message contains the description of the command, the items in the specified in the 'help' section of the command's info dictionary, and the examples specified in the info dictionary.
        """
        print("-- Help for '" + self.info["title"] + "' --")
        print(dedent(self.info["description"]) + "\n")
        for item in self.info["help"]:
            print(item + "\n")

        print("\n-- Examples --")
        for tuple in self.info["example_usage"]:
            print(tuple[0], end="")
            print(" - " + tuple[1] +"\n")
    
    def invocation(self, query):
        """Checks whether the inputted query invokes this command via its syntax/structure or content, and returns True if it does. Otherwise, returns False.
        It is recommended to supply multiple ways to invoke a command in case of overlap with other command plugins. Control of the query is handed to the
        first command that the query satisfies the invocation conditions of.

        :param query: The current inputted query to analyze.
        :type query: str

        :return: True if the query satisfied invocation conditions, false 
        :rtype: bool
        """
        pass

    def prepare(self):
        """Initializes objects and resources to be used in an upcoming execution of this command.
        Children of the Command class are not required to implement this method, and there is often no need to call it. It is not automatically called.
        An implemention should be provided when all of the following conditions are true: other commands are likely to call this command, the preparation procedure
        for this command takes a nontrivial amount of time, and the preparation must necessarily be done upon each execution
        instead of upon initialization of the command object.

        If applicable, manually run this before or at the start of self.execute().
        """
        pass

    def cleanup(self):
        """Removes any unneeded references and resources but keeps resources beneficial to subsequent executions of this command.
        Children of the Command class are not required to implement this method, however, it is automatically called at the end of each execution.
        An implementation should be provided when the data and references stored at the object- or class-level are of nontrivial size,
        or when object- or class-level variables are used for temporary data storage. In the latter case, consider whether storage at that scope is
        necessary or beneficial to your command. That tactic is, in fact, useful in some cases, such as when storing data while handling a query before execution.

        Runs automatically after self.execute().
        """
        pass

    def standdown(self):
        """Removes all in-memory references and resources, saving data to disk where appropriate. Children of the Command class are not required to implement this method, and it is not automatically called. Similar to the cleanup method, this method is unnecessary in most circumstances but is recommended in particular circumstances. The primary beneficiaries of this method are Commands that handle a significant amount of data, store that data in memory throughout their execution, and need to preserve the data between Aria sessions.

        If applicable, manually run this at the end of or after self.execute()
        """
        pass

    def get_template(self, new_cmd_name):
        """Models this command for use in automatic/spontaneous command creation. Returns a template in the form of a dictionary where the keys are variable names used in this command and the values are the initial assignment values that those variables will have in the newly created command. All instances of the form var = x\n, where var is a key specified in the template, will have x replaced by the corresponding value. Children of the Command class are not required to implement this method, but developers are encouraged to design their commands in a templatable way to help simplify creation of unique commands that share the same underlying process.

        :param new_cmd_name: The name of the new file containing the new command.
        :type new_cmd_name: str

        :return: A dictionary of variables and values to re-assign when generating the new command.
        :rtype: dict
        """
        pass



# Blah
class _API:
    def __init__(self, base_url, api_key, structure = None):
        self.base_url = base_url
        self.api_key = api_key
        self.api_structure = structure

    def make_query(self, ):
        pass

    def call(self, query):
        #get_json(self.api_key)
        pass

    def add_route():
        pass


### High-level Action Classes
class WebAction(Command):
    def find_api(base_url):
        pass


class SystemAction(Command):
    pass


class InputAction(Command):
    pass



### Action Subclasses
class APIAction(WebAction):
    
    def __init__(self):
        pass

    def get_response(self, ):
        pass


class TerminalCommand(SystemAction):
    pass


class AppAction(SystemAction):
    pass


class FileAction(SystemAction):
    pass


class KeyboardAction(InputAction):
    # Text input, keystrokes
    pass


class ClickAction(SystemAction, InputAction):
    # Mouse click sequence
    pass
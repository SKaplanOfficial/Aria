"""A manager for Aria command modules. Only one CommandManager should be active at a time.
"""

from calendar import c
import importlib, os, re, threading, sys
from json import load
from . import command_utils, config_utils, io_utils, file_utils

plugins = dict()
invocations = dict()
handlers = dict()
handler_checkers = dict()

requirements = dict()

def load_command(cmd_name):
    """Loads a command from a command plugin file.

    :param cmd_name: The name of the command to load; the name of a file in the cmds subdirectory (without the .py extension).
    :type cmd_name: str
    """
    # Add module command object
    module = None
    module = importlib.import_module("cmds."+cmd_name)
    command_obj = getattr(module, "command", None)

    if command_obj == None:
        print("Error: Couldn't find command definition in " + cmd_name + ".py. Proceed with caution.")
        return
    plugins[cmd_name] = module.command

    # TODO: Use IDs for all entries, not as a secondary bandaid
    plugins[module.command.info["id"]] = module.command

    check_command_structure(cmd_name, plugins[cmd_name])

    # Add invocation methods
    invocations[cmd_name] = plugins[cmd_name].invocation

    # Add handlers
    handler_checkers[cmd_name] = plugins[cmd_name].handler_checker
    handlers[cmd_name] = plugins[cmd_name].handler

    # Add requirements
    if "requirements" in plugins[cmd_name].info:
        requirements.update(plugins[cmd_name].info["requirements"])

    # Run plugin configuration if necessary
    if "configure" in vars(plugins[cmd_name].__class__):
        plugins[cmd_name].configure()

    # Preload plugin resources if necessary
    if "preload" in vars(plugins[cmd_name].__class__):
        preload_thread = threading.Thread(target=plugins[cmd_name].preload, name="preload_"+cmd_name)
        preload_thread.start()

def unload_command(cmd_name):
    """Removes a command from Aria's active plugin dictionaries.

    :param cmd_name: The name of the command to unload.
    :type cmd_name: str
    """
    handlers.pop(cmd_name)
    handler_checkers.pop(cmd_name)
    invocations.pop(cmd_name)
    plugins.pop(cmd_name)

def reload_command(cmd_name):
    """Reloads the module associated with the specified command name, loads the command back into Aria, and re-checks the requirements of all plugins.

    :param cmd_name: The name of the command to reload.
    :type cmd_name: str
    """
    importlib.reload(sys.modules[plugins[cmd_name].__module__])
    load_command(cmd_name)
    check_requirements()

def check_requirements():
    """Checks that the plugins and versions of plugins required by each loaded command plugin are installed and loaded.
    """
    for requirement in requirements:
        found = False
        for plugin in plugins:
            if plugins[plugin].info["id"] == requirement:
                if plugins[plugin].info["version"] == requirements[requirement]:
                    found = True

        if not found:
            print("Warning: Requirement not satisfied:")
            print("  Expected: " + requirement + " @" + requirements[requirement])
            print("  Found: " + requirement + " @" + plugins[plugin].info["version"] + " instead. Proceed with caution.")

def load_all_commands():
    """
    Loads all command modules enabled in aria_config.json.

    Returns:
        None
    """
    aria_path = config_utils.get("aria_path")
    files = os.listdir(path=aria_path+"/cmds")
    num_commands = 0
    for f in files:
        if "__" not in f and ".pyc" not in f and ".DS_Store" not in f:
            cmd_name = f.replace(".py", "")
            if cmd_name in config_utils.get("plugins").keys():
                if config_utils.get("plugins")[cmd_name]:
                    load_command(cmd_name)
                    num_commands += 1
    check_requirements()
    return num_commands

def check_command_structure(cmd_name, command):
    """
    Checks the metadata and method definitions of a command plugin for required and recommended attributes.

    Parameters:
        cmd_name (str) - The name of the command (currently the filename).
        command (Command) - The Command object exported by the plugin module.

    Returns:
        None
    """
    info_def = getattr(command, "info", None)
    if info_def == command_utils.Command.info:
        print("Warning: Plugin '" + cmd_name + "' does not define its own info dictionary. Proceed with caution.")

    required_info_keys = ["title", "id", "version", "description"]
    recommended_info_keys = ["repository", "requirements", "purposes", "targets", "example_usage"]

    required_methods = ["execute", "help"]
    recommended_methods = ["get_query_type", "handler_checker", "handler"]

    for key in required_info_keys:
        if key not in command.info:
            print("Error: Plugin '" + cmd_name + "' does not define the required '" + key + "' key. Proceed with caution.")
    
    for key in recommended_info_keys:
        if key not in command.info and (config_utils.get("dev_mode") or config_utils.runtime_config["debug"]):
            print("Warning: Plugin '" + cmd_name + "' does not define the recommended '" + key + "' key.")

    for method in required_methods:
        method_def = getattr(command, method, None)
        if method_def == None:
            print("Error: Plugin '" + cmd_name + "' does not define the required '" + method + "' method. Proceed with caution.")

    invocation_def = getattr(command, "invocation", None)
    if invocation_def == None:
        for method in recommended_methods:
            method_def = getattr(command, method, None)
            if method_def == None and (config_utils.get("dev_mode") or config_utils.runtime_config["debug"]):
                print("Warning: Plugin '" + cmd_name + "' does not define either an invocation method nor a '" + method + "' method. At least one should be defined.")

    if "info_version" in command.info:
        if command.info["info_version"] != command_utils.Command.info["info_version"]:
            print("Warning: Plugin '" + cmd_name + "' uses the Version " + command.info["info_version"] + " command structure, but Aria expected Version " + command_utils.Command.info["info_version"] + ". Proceed with caution.")
    else:
        print("Warning: Could not determine the command structure version of plugin '" + cmd_name + "'. Proceed with caution.")

def cmd_from_template(str_in):
    """
    Creates a new command module using the template method of another command.

    Parameters:
        str_in: str - The full string that initiated this command.

    Notes:
        - The CommandManager should not be handling parsing of str_in. Check this ASAP. Use a new_command and target_command parameter instead.
    """
    aria_path = config_utils.get("aria_path")

    # Determine relevant command names
    if str_in.startswith("make command "):
        new_cmd_name = str_in[13:str_in.index("from")-1]
        old_cmd_name = str_in[str_in.index("from")+5:]
    elif str_in.startswith("make"):
        new_cmd_name = str_in[5:str_in.index("from")-1]
        old_cmd_name = str_in[str_in.index("from command")+13:]
    else:
        # Some error occurred
        print("Unable to create command.")
        return

    # Check if new command already exists
    if get_command_name(new_cmd_name):
        print("Target command already exists.")
        return

    # Get old cmd file path
    old_filename = get_command_name(old_cmd_name) + ".py"
    if (old_filename == "" or old_filename is None):
        print("Reference command does not exist.")
        return

    # Get old cmd file content
    old_file_content = file_utils.get_file_content(aria_path+"/cmds/"+old_filename)

    # Modify code
    new_file_content = old_file_content.replace(old_cmd_name + " ", new_cmd_name)
    new_file_content = new_file_content.replace(
        old_cmd_name.title() + " ", new_cmd_name.title())

    try:
        cmd_module = importlib.import_module("cmds."+old_cmd_name)
        old_cmd = cmd_module.Command()
        template = old_cmd.get_template(new_cmd_name)

        for key in template:
            new_file_content = re.sub(
                key+" = .*"+"\n", key+" = "+template[key]+"\n", new_file_content)

    except Exception as e:
        print("Unable to access reference command template:\n"+str(e))

    # Create new file
    with open(aria_path+"/cmds/"+new_cmd_name+".py", "w") as new_file:
        new_file.write(new_file_content)

    print("Command " + new_cmd_name + " created.")

def create_shortcut(cmd_str, cmd_name):
    """
    Removes a command plugin from the plugins dictionary and disables it in aria_config.json.

    Arguments:
        cmd_str {String} -- The full command to be saved as a shortcut, including arguments.
        cmd_name {String} -- The name of the command plugin to be saved as a shortcut; the default name of the shotcut.

    Returns:
        None
    """
    aria_path = config_utils.get("aria_path")
    script = f"""#! /bin/zsh
    cd {aria_path}
    python Aria.py --cmd "{cmd_str}" --close
    exit
    """

    print("Where do you want the shortcut?", end="\n->")
    folder_path = input()

    print("What do you want the shorcut to be named? Leave blank to name it '" + cmd_name + ".'", end="\n->")
    name = input()
    if name == "":
        name = cmd_name

    file_path = folder_path + "/" + name
    if folder_path.endswith("/"):
        file_path = folder_path + name

    with open(file_path, 'w') as new_file:
        new_file.write(script)

    mode = os.stat(file_path).st_mode
    mode |= (mode & 0o444) >> 2    # copy R bits to X
    os.chmod(file_path, mode)
    print("Created shortcut '" + name + ".'")

def get_command_name(cmd_name):
    """
    Returns the name of the file associated with a command.

    Arguments:
        cmd_name {String} -- The name of the target command.

    Returns:
        String -- the name of the file (not including .py extension)
    """
    name_condensed = cmd_name.replace(" ", "")

    files = os.listdir(path=config_utils.get("aria_path")+"/cmds")
    for f in files:
        if f.startswith(name_condensed):
            return f[:-3]

def get_candidate_command_names(input_str):
    """
    Returns a list of file where the input string is a substring of the filename.

    Arguments:
        input_str {String} -- A substring of the target command.

    Returns:
        [String] -- An array of filenames (not including .py extension)
    """
    filenames = []
    name_condensed = input_str.replace(" ", "")

    files = os.listdir(path=config_utils.get("aria_path")+"/cmds")
    for f in files:
        if f.startswith(name_condensed):
            filenames.append(f[:-3])
    return filenames

def enable_command_plugin(cmd_name):
    """Add a command plugin to the plugins dictionary and enables it in aria_config.json.

    Arguments:
        cmd_name {String} -- The name of the command plugin to be enabled.

    Returns:
        boolean -- True if a plugin is successfully enabled, False if the plugin is already enabled.
    """
    if cmd_name in config_utils.get("plugins"):
        if config_utils.get("plugins")[cmd_name]["enabled"] == True:
            print(cmd_name, "is already enabled.")
            return False
        else:
            config_utils.get("plugins")[cmd_name]["enabled"] = True
    else:
        config_utils.get("plugins")[cmd_name] = {
            "enabled": True
        }
    config_utils.save_global_config()
    module = importlib.import_module("cmds."+cmd_name)
    aria_path = config_utils.get("aria_path")
    plugins[cmd_name] = module.Command()

    print(cmd_name, "has been enabled.")
    return True

def disable_command_plugin(cmd_name):
    """
    Removes a command plugin from the plugins dictionary and disables it in aria_config.json.

    Arguments:
        cmd_name {String} -- The name of the command plugin to be disabled.

    Returns:
        boolean -- True if a plugin is successfully disabled, False if the plugin is already disabled.
    """
    if cmd_name in config_utils.get("plugins"):
        if config_utils.get("plugins")[cmd_name]["enabled"] == False:
            print(cmd_name, "is already disabled.")
            return False
        else:
            config_utils.get("plugins")[cmd_name]["enabled"] = False
    else:
        config_utils.get("plugins")[cmd_name] = {
            "enabled": False
        }
    config_utils.save_global_config()
    plugins.pop(cmd_name)

    print(cmd_name, "has been disabled.")
    return True

def cmd_method(cmd_name, method_name):
    if (cmd_name == "" or cmd_name is None):
        print("'" + method_name + "' rountine not found (Cannot find base command '" + cmd_name + "').")
    else:
        # Attempt to show help information
        plugin = plugins[cmd_name]
        method = getattr(plugin, method_name, None)

        if callable(method):
            method()
        else:
            print("'" + method_name + "' rountine not found (Missing '" + method_name + "' method).")

from textwrap import dedent

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
        },
        "info_version": "0.9.0",
    }

    def __init__(self):
        """Constructs a Command object.
        """
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
        An implemention should be provided when all of the following conditions are true: 1) other commands are likely to call this command, 2) the preparation procedure for this command takes a nontrivial amount of time, and 3) the preparation procedure must occur upon most (but not necessary every) execution of the command instead.

        In cases where preparation cannot be done asychronously or otherwise without significantly impacting Aria's performance, the self.preload() method is preferred.

        If applicable, manually run this before or at the start of self.execute().
        """
        pass

    def cleanup(self):
        """Removes any unneeded references and resources but keeps resources beneficial to subsequent executions of this command. Children of the Command class are not required to implement this method, however, it is automatically called at the end of each execution. An implementation should be provided when the data and references stored at the object- or class-level are of nontrivial size, or when object- or class-level variables are used for temporary data storage. In the latter case, consider whether storage at that scope is necessary or beneficial to your command. That tactic is, in fact, useful in some cases, such as when storing data while handling a query before execution.

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

    def configure(self):
        """Checks for entries in aria_config.json, updates config entries, and adds missing config entries. Children of the Command class are not required to implement this method. This method should be implemented in cases where persistent configuration settings offer useful benefits to users. This method should not be used to store regularly changing data or track data over time (a Tracker object is more suitable to such scenarios). Command developers should strive to uphold the semi-static nature of configuration files -- essentially meaning that the aria_config.json should change only when users expect or request it to be changed.

        Runs automatically at the end of self.get_all_commands(), before self.preload().
        """
        pass

    def preload(self):
        """Runs custom code when this command plugin is loaded into Aria's plugin dictionary. Children of the Command class are not required to implement this method. Commands should implement this method when the following conditions are met: 1) the command relies on resources that take a nontrivial amount of time to retrieve, 2) the resources are necessary for the majority of the command's execution branches, 3) it is not possible or desirable to store and retrieve the resources in a more efficient way, and 4) the resources can be loaded one time instead of upon each execution of the command.

        In cases where resources can be obtained or configured asynchronously, the self.prepare() method is preferred.
        
        Runs automatically in a separate thread beginning at the end of self.get_all_commands(), after self.configure(). Command developers looking to implement this method should be mindful of its threaded execution.
        """
        pass
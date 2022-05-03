"""A settings/configuration manager for Aria. Only one ConfigManager should be active at a time.
"""

import os, json

cfg_file_name = "aria_config.json"
cfg_version = "0.0.1"
config = {}
runtime_config = {}

def create_global_config(initial_config):
    """
    Creates aria_config.json, overwriting if it already exists in the same location. Updates config dictionary to supplied initial config.

    Paramters:
        initial_config: dict - A dictionary of configuration settings.
    """
    global config
    with open(cfg_file_name, 'w') as cfg_file:
        json.dump(initial_config, cfg_file, indent = 4, sort_keys = True)

    config = initial_config

def load_global_config():
    """
    Attempts to load configuration settings from aria_config.json. Saves loaded config to config dictionary if successful.

    Returns:
        boolean - True if aria_config.json exists and is read successfully, False otherwise.
    """
    global config
    loaded_config = {}
    try:
        with open(cfg_file_name, 'r') as cfg_file:
            loaded_config = json.load(cfg_file)
    except:
        return False

    if loaded_config["cfg_version"] != cfg_version:
        print("Your configuration file uses a different format version than expected by this version of Aria.")
        print("Expected version:", cfg_version)
        print("File version:", loaded_config["cfg_version"])
        print("It might be okay to proceed. Press Y to do so, or press any other key to exit.")
        input_str = input()

        if input_str != "Y" and input_str != "y":
            exit()

    config = loaded_config
    return True

def save_global_config():
    """
    Attempts to saves the config dictionary to aria_config.json.

    Returns:
        boolean - True if aria_config.json is successfully written to, False otherwise.
    """
    try:
        with open(cfg_file_name, 'w') as cfg_file:
            json.dump(config, cfg_file, indent = 4, sort_keys = True)
    except:
        return False
    return True

def get_config():
    """Returns the entire config dictionary, if a config is loaded, otherwise runs the initial setup process."""
    if not load_global_config():
        initial_setup()
    return config

def get(key):
    """
    Returns the value associated with the specified key in the config dictionary.
    
    Parameters:
        key : str - The key to retrieve the associated value of.

    Returns:
        Object - The json-serializable object stored at the target key.
    """
    if not load_global_config():
        return
    return config[key]

def set(key, value):
    """
    Sets the key in the config dictionary to the specified key and updates aria_config.json.
    
    Paramters:
        key : str - The key to set the value of.
        value : Object - A json-serializable value to store at the target key.
    """
    if not load_global_config():
        initial_setup()
    config[key] = value
    save_global_config()

def initial_setup():
    """
    Walks users through an initial configuration of Aria, allowing use of a default configuration.

    Notes:
        - 
    """
    global config
    
    default_config = {
        "cfg_version": cfg_version,
        "aria_path": os.getcwd(),
        "user_name": "User",
        "plugins" : {},
        "dev_mode": False,
    }

    print("Hello!\nThank you for using Aria. Press any key to answer a few configuration questions, or press X to configure settings later.")
    input_str = input()

    if input_str != "X" and input_str != "x":
        aria_path = os.getcwd()
        print("\n1. Please confirm the directory that Aria.py is located:", aria_path)
        print("Is this correct? Press Y for yes, otherwise please enter the correct directory path.")
        input_str = input()
        if input_str != "Y" and input_str != "y":
            aria_path = input_str

        print("\n2. Please tell Aria know a little about you.")
        print("What is your name?")
        name = input()

        print("\n3. Aria found the following command plugins:")
        plugins = {}
        files = os.listdir(path=aria_path+"/cmds")
        for f in files:
            if "__" not in f and ".pyc" not in f and ".DS_Store" not in f:
                plugin_name = f.replace(".py", "")
                print("\t", plugin_name)
                plugins[plugin_name] = {
                    "enabled" : True
                }
        print("Type Y to enable all (dangerous), or type a list of plugins to enable, separated by commas.")
        input_str = input()
        if input_str == "Y" or input_str == "y":
            plugins_to_enable = input_str.split(",")
            for plugin_name in plugins_to_enable:
                plugins[plugin_name.replace(" ", "")] = {
                    "enabled" : True
                }

        config = {
            "cfg_version": cfg_version,
            "aria_path": aria_path,
            "user_name": name,
            "plugins": plugins,
            "dev_mode": False
        }

        print("Creating custom config file...")
        create_global_config(config)
    else:
        print("Creating default config file...")
        create_global_config(default_config)
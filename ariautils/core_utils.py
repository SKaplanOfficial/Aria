"""A manager for Aria's internal operations.
"""

# def initialize_managers(runtime_config):
#     CONFM = ConfigManager()
#     managers["config"] = CONFM
#     config = CONFM.get_config()
#     managers["config"].set_runtime_config(runtime_config)

#     TRACKM = TrackingManager(CONFM.get("aria_path")+"/data/")
#     managers["tracking"] = TRACKM

#     DOCM = DocumentManager()
#     managers["docs"] = DOCM

#     COMM = CommandManager()
#     commands = COMM.get_all_commands()
#     managers["command"] = COMM

#     CONM = ContextManager()
#     managers["context"] = CONM

#     LANGM = LanguageManager()
#     managers["lang"] = LANGM

#     INM = InputManager()
#     managers["input"] = INM

#     OUTM = OutputManager()
#     managers["output"] = OUTM

#     managers = managers.copy()

#     return managers

# AriaManager = AriaManager()
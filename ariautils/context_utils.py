"""A manager for Aria's context tracking system. Only one ContextManager should be active at a time.
"""

import subprocess, os
from datetime import datetime
from .tracking_utils import TrackingManager
from pathlib import Path
from . import file_utils

import platform
current_os = platform.system()
if current_os == "Darwin":
    import applescript

mins_to_checkpoint = 0.05
timer_checkpoint = -1

item_structure = {
    "start_time" : float,
    "end_time" : float,
    "frequency" : int,
    "targets" : list,
}

context_tracker = TrackingManager.init_tracker("context", item_structure, "/mnt/c/Users/fryei/Documents/GitHub/Aria/data")
context_tracker.load_data()
current_context = context_tracker.new_item([0, 0, 0, []])
current_app = ""
current_apps = []
previous_apps = []
previous_input = ""
looping = True

def update_context():
    """
    Update all context variables as necessary

    Returns:
        None
    """
    global current_app, current_apps, current_context
    currentApp, current_apps = get_context_from_AS()
    current_apps = sorted(list(set(current_apps)))

    # Track current app
    if currentApp is not None:
        if currentApp != "/System/Applications/Utilities/Terminal.app":
            current_app = currentApp

    if len(previous_apps) == 0 or current_app != previous_apps[-1]:
        if current_app != "":
            previous_apps.append(current_app)

    # Track all running apps
    if len(current_apps) > 0:
        now = datetime.now()
        current_time = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
        current_context = context_tracker.new_item([current_time, current_time, 0, current_apps])

        # Initialize history
        if len(context_tracker.items) == 0:
            context_tracker.add_item(current_context)

        # Compare against previous context
        prev_context_obj = context_tracker.items[-1]
        if prev_context_obj != None and current_apps != prev_context_obj.data["targets"]:
            # Record end time of previous context, open new context
            prev_context_obj.data["end_time"] = current_time
            context_tracker.add_item(current_context)
            checkpoint()
        
        # Current and previous are equal at this point
        elif timer_checkpoint == -1 or current_time - timer_checkpoint > mins_to_checkpoint * 60:
            #print("Saving context history...")
            # Update previous end time (in case context doesn't change for a while)
            if prev_context_obj != None:
                prev_context_obj.data["end_time"] = current_time

            if current_context.data["targets"] == context_tracker.items[-1].data["targets"]:
                context_tracker.items[-1].data["frequency"] += 1

            # Export context history to context tracking csv
            context_tracker.save_data()
            checkpoint()
            context_tracker.load_data()

def get_context_from_AS():
    """
    Runs AppleScript to find currently running applications

    Returns:
        [str, [str]] - The filepath of the currently focused application and a list of filepaths of all currently running applications.
    """
    scpt = applescript.AppleScript('''
        property _frontApp : 0
        property _frontAppName : 0
        property _ID : 0
        property _listOfApps : {}
        
        try
            with timeout of 1 second
                tell application "System Events"
                    set frontApp to first application process whose frontmost is true
                    set frontAppName to name of frontApp
                    set currentApp to file of first application process where name is frontAppName
                    set listOfApps to (file of every process where background only is false)
                end tell
            end timeout
            return {currentApp, listOfApps}
        on error
            -- blah
        end try
    ''')
    data = scpt.run()
    if data != None:
        return data
    return [current_app, current_context.data["targets"]]

def checkpoint():
    """
    Updates the timer checkpoint to the current time.
    
    Returns:
        None
    """
    global timer_checkpoint
    now = datetime.now()
    current_time = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    timer_checkpoint = current_time

def blank_context():
    """
    Closes all non-essential running apps.
    
    Returns:
        None
    """
    apps_to_close = [app for app in current_context.data["targets"]]
    for app in apps_to_close:
        if app != "/Applications/Visual Studio Code.app" and app != "/System/Library/CoreServices/Finder.app" and app != "/System/Applications/Utilities/Terminal.app":
            print("Closing " + app + "...")
            command = ["pkill", "-f", app]
            subprocess.call(command)

def get_tab_title():
    """Gets the title of the front tab (or only tab) of the current applications.

    Finder -> Path to current directory
    Safari -> URL of current website
    Contacts -> Name of current contact
    Notes -> Name of current note
    Music -> Name of current playlist / current area of the application
    Maps -> Current location in view
    News -> Current category or article
    Stocks -> Name of current stock
    Books -> Name of current book
    Other -> Name of current tab or window
    """
    # Finder, Messages, Preview
    app_script = '''tell application "''' + current_app + '''" to set targetName to the (name of front window) as text'''
    if "Safari" in current_app:
        app_script = '''tell application "Safari" to set targetName to the URL of the current tab of the front window'''
    elif "Contacts" in current_app or "Notes" in current_app:
        app_script = '''tell application "''' + current_app + '''" to set targetName to the name of item 1 of (selection as list)'''
    elif "Music" in current_app:
        app_script = '''tell application "Music" to set targetName to the name of the view of the front window'''
    elif "Maps" in current_app or "News" in current_app or "Stocks" in current_app or "News" in current_app or "Books" in current_app or "":
        app_script = '''tell application "System Events" to tell application process "''' + current_app + '''" to set targetName to name of its window'''

    scpt = applescript.AppleScript('''
        try
            ''' + app_script + '''
            return targetName
        on error
            -- Do nothing
        end try
    ''')
    data = scpt.run()
    return data

def get_tab_target():
    """Gets the target of the front tab (or only tab) of the current application. The target is always a string, but it may represent different resources across different applications. A map between applications and their resource types is provided below.

    Finder -> Name of current directory
    Safari -> URL of current website
    Contacts -> 
    Notes -> 
    Music ->
    Maps ->
    News ->
    Stocks ->
    Books ->
    Other ->
    """
    # # Maps, News, Stocks, Books, Stickies, Home, QuickTime Player, Slack, Processing, Arduino
    # app_script = '''tell application "''' + current_app + '''" to set targetName to the (name of front window) as text'''
    # app_script = '''tell application "System Events" to tell application process "''' + current_app + '''" to set targetName to name of its window'''
    # if any([x in current_app for x in ["Contacts", "Notes"]]):
    #     app_script = '''tell application "''' + current_app + '''" to set targetName to the name of item 1 of (selection as list)'''
    # elif "Music" in current_app:
    #     app_script = '''tell application "Music" to set targetName to the name of the view of the front window'''
    # elif any([x in current_app for x in ["Finder", "Safari", "Firefox", "Microsoft Edge", "Google Chrome", "Opera", "Messages", "Preview", "TextEdit", "Pages", "Numbers", "Keynote", "System Preferences", "Script Editor", "Automator", "Font Book"]):
    #     app_script = '''tell application "''' + current_app + '''" to set targetName to the (name of front window) as text'''

    # scpt = applescript.AppleScript('''
    #     try
    #         ''' + app_script + '''
    #         return targetName
    #     on error
    #         -- Do nothing
    #     end try
    # ''')

    scpt = applescript.AppleScript('''
        tell application "Notes"
            set targetContent to {}
            set itemList to selection
            repeat with i in itemList
                copy properties of i to end of targetContent
            end repeat
        end tell
        return targetContent
    ''')

    scpt = applescript.AppleScript('''
        tell application "Keynote"
            set targetContent to {}
            set docItem to the front item of the document of the front window
            copy properties of docItem to docProps
            set selectedItems to selection of docProps
            repeat with i in selectedItems
                copy properties of i to end of targetContent
            end repeat
        end tell
        return targetContent
    ''')

    scpt = applescript.AppleScript('''
        tell application "''' + current_app + '''"
            set targetContent to {}
            set itemList to selection
            repeat with i in itemList
                copy properties of i to end of targetContent
            end repeat
        end tell
        return targetContent
    ''')

    data = scpt.run()
    return data

def get_current_folder():
    """Gets the path of the current directory open in Finder. Finder does not need to be the current app for this to work, but it does need to be open.
    """
    scpt = applescript.AppleScript('''
        try
            tell application "Finder" to set folderPath to the (target of front window) as text
            return folderPath
        on error
            -- Do nothing
        end try
    ''')
    data = scpt.run()
    return data

def get_current_file():
    """Gets the path of the currently open file. The file can be open in any application.
    """
    scpt = applescript.AppleScript('''
        try
            tell application "''' + current_app + '''" to set filePath to the path of the front document
            return filePath
        on error
            -- Do nothing
        end try
    ''')
    data = scpt.run()
    return data

def get_selected_items():
    scpt = applescript.AppleScript('''
        try
            set itemNames to {}
            tell application "''' + current_app + '''"
                set selectedItems to selection
                
                if selectedItems is not {} then
                    set first_item to item 1 of selectedItems
                    set basePath to the container of first_item as alias
                    
                    repeat with itemRef in selectedItems
                        copy (name of itemRef) to the end of itemNames
                    end repeat
                end if
            end tell
            return {itemNames, basePath}
        on error
            -- Do nothing
        end try
    ''')
    data = scpt.run()

    selected_items = []
    if data != None:
        base_path = data[1]
        for target in data[0]:
            selected_items.append(base_path + "/" + target)
    return selected_items

def get_app_list():
    home_dir = str(Path.home()) 
    apps = ["/Applications/" + a for a in os.listdir("/Applications")]
    apps.extend([home_dir + "/" + a for a in os.listdir(home_dir + "/Applications")])
    apps = [a for a in apps if a.endswith(".app") and not a.startswith(".")]
    return apps
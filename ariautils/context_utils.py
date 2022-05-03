"""A manager for Aria's context tracking system. Only one ContextManager should be active at a time.
"""

import applescript, subprocess
from datetime import datetime
from .tracking_utils import TrackingManager

mins_to_checkpoint = 0.05
timer_checkpoint = -1

item_structure = {
    "start_time" : float,
    "end_time" : float,
    "frequency" : int,
    "targets" : list,
}

context_tracker = TrackingManager.init_tracker("context", item_structure)
context_tracker.load_data()
current_context = context_tracker.new_item([0, 0, 0, []])
current_app = ""
previous_apps = []
previous_input = ""
looping = True

def update_context():
    """
    Update all context variables as necessary

    Returns:
        None
    """
    global current_app, current_context
    currentApp, listOfApps = get_context_from_AS()
    listOfApps = sorted(list(set(listOfApps)))

    # Track current app
    if currentApp is not None:
        if currentApp != "/System/Applications/Utilities/Terminal.app":
            current_app = currentApp

    if len(previous_apps) == 0 or current_app != previous_apps[-1]:
        if current_app != "":
            previous_apps.append(current_app)

    # Track all running apps
    if len(listOfApps) > 0:
        now = datetime.now()
        current_time = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
        current_context = context_tracker.new_item([current_time, current_time, 0, listOfApps])

        # Initialize history
        if len(context_tracker.items) == 0:
            context_tracker.add_item(current_context)

        # Compare against previous context
        prev_context_obj = context_tracker.items[-1]
        if prev_context_obj != None and listOfApps != prev_context_obj.data["targets"]:
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
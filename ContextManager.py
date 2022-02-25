"""
Context Manager

Last Updated: March 13, 2021
"""

import applescript
import os
import csv
from datetime import datetime
from pathlib import Path

from TrackingManager import TrackingManager

class ContextManager:
    def __init__(self, *args, **kwargs):
        # Settings
        self.mins_to_checkpoint = 0.05
        self.data_file_name = "context_tracking.csv"

        self.aria_path = args[0]

        self.context_tracker = args[1]

        self.current_context = self.context_tracker.entry_obj(0, 0, 0, [])
        self.current_app = ""
        self.timer_checkpoint = -1

    def update_context(self):
        """ Update all context variables as necessary """
        currentApp, listOfApps = self.get_context_from_AS()

        # Track current app
        if currentApp is not None:
            self.current_app = currentApp

        # Track all running apps
        if len(listOfApps) > 0:
            now = datetime.now()
            current_time = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
            self.current_context = self.context_tracker.entry_obj(current_time, current_time, 0, listOfApps)

            # Initialize history
            if len(self.context_tracker.entries) == 0:
                self.context_tracker.add_entry(self.current_context)

            # Compare against previous context
            prev_context_obj = self.context_tracker.entries[-1]
            if prev_context_obj != None and listOfApps != prev_context_obj["targets"]:
                # Record end time of previous context, open new context
                prev_context_obj["end_time"] = current_time
                self.context_tracker.add_entry(self.current_context)
                self.checkpoint()
            
            # Current and previous are equal at this point
            elif self.timer_checkpoint == -1 or current_time - self.timer_checkpoint > self.mins_to_checkpoint * 60:
                #print("Saving context history...")
                # Update previous end time (in case context doesn't change for a while)
                if prev_context_obj != None:
                    prev_context_obj["end_time"] = current_time

                if self.current_context["targets"] == self.context_tracker.entries[-1]["targets"]:
                    self.context_tracker.entries[-1]["frequency"] += 1

                # Export context history to context tracking csv
                self.context_tracker.save_data()
                self.checkpoint()

    def get_context_from_AS(self):
        """ Run AppleScript to find currently running applications """
        scpt = applescript.AppleScript('''
            property _frontApp : 0
            property _frontAppName : 0
            property _ID : 0
            property _listOfApps : {}
            
            try
                with timeout of 2 seconds
                    tell application "System Events"
                        set frontApp to first application process whose frontmost is true
                        set frontAppName to name of frontApp
                        set currentApp to file of (application processes where name is frontAppName)
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
        return [self.current_app, self.current_context["targets"]]

    def checkpoint(self):
        """ Update the timer checkpoint to the current time """
        now = datetime.now()
        current_time = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
        self.timer_checkpoint = current_time
    
    # def get_previous_context(self):
    #     """ Get the context object directly preceeding the current one, if it exists """
    #     if len(self.context_history) > 1:
    #         return self.context_history[-2]
    #     return None

    def context_delta(self, base_context, target_context):
        """ Calculate a delta between to contexts, larger value means smaller difference """
        target_start = target_context["start_time"]
        target_end = target_context["end_time"]
        target_apps = target_context["targets"]

        base_start = base_context["start_time"]
        base_end = base_context["end_time"]
        base_apps = base_context["targets"]
        base_frequency = base_context["frequency"]

        delta = 0

        # Award points for time similarity
        start_start_diff = abs(target_start - base_start)
        start_end_diff = abs(target_start - base_end)
        end_end_diff = abs(target_end - base_end)
        end_start_diff = abs(target_end - base_start)

        avg_time_diff = (start_start_diff + start_end_diff + end_end_diff + end_start_diff) / 4

        delta += 0.1 * base_frequency / avg_time_diff

        # Award points for app list similarity
        num_similar = 0
        max_consec = 0
        num_consec_similar = 0
        for app_1 in target_apps:
            found = False
            for app_2 in base_apps:
                if app_1 == app_2 and not found:
                    found = True

            if found:
                num_similar += 1
                num_consec_similar += 1
                if num_consec_similar > max_consec:
                    max_consec = num_consec_similar
            else:
                num_consec_similar = 0

        delta += num_similar
        delta += max_consec * 10

        return delta
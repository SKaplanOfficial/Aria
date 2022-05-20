"""Notification system for Aria.

API
===
"""

import os, applescript
from datetime import datetime
from typing import Any
import threading

class Notification():
    def __init__(self, content: Any = None, title: str = "New Notification"):
        self.content: Any = content
        self.title: str = title
        self.__creation_time: datetime = datetime.now()

    ### Properties
    @property
    def title(self):
        return self.__title

    @property
    def content(self):
        return self.__content

    @property
    def creation_time(self):
        return self.__creation_time

    
    ### Setters
    @title.setter
    def title(self, title):
        self.__title = title

    @content.setter
    def content(self, content):
        self.__content = content

    ### General Methods
    def show(self):
        width = os.get_terminal_size()[0]
        print("\n" + "=" * width + "\n")
        print("  " + self.title + "\n")
        print("  " + self.content)
        print("\n" + "=" * width + "\n")


class DesktopNotification(Notification):
    def __init__(self, content: Any = None, title: str = "New Notification", subtitle: str = None, sound = "Glass"):
        super().__init__(content, title)
        self.subtitle = subtitle
        self.sound = sound

    ### Properties
    @property
    def subtitle(self):
        return self.__subtitle

    @property
    def sound(self):
        return self.__sound

    
    ### Setters
    @subtitle.setter
    def subtitle(self, subtitle):
        self.__subtitle = subtitle

    @sound.setter
    def sound(self, sound):
        self.__sound = sound

    ### General Methods
    def show(self):
        subtitle_text = f'subtitle "{self.subtitle}" ' if self.subtitle != None else ''
        notification_text = f"""
            try
                beep
                delay 0.3
                display notification "{self.content}" with title "{self.title}" {subtitle_text}sound name "{self.sound}"
            on error
                -- do nothing
            end try
        """
        os.system(f"osascript -e '{notification_text}'")

class Alert(DesktopNotification):
    def __init__(self, title = "Alert!", message = "Action complete!", type = "informational", buttons = ["Ok", "Cancel"], default_button = "Ok", cancel_button = "Cancel", wait = -1):
        super().__init__(message, title, type)
        self.type = type
        self.buttons = buttons
        self.default_button = default_button
        self.cancel_button = cancel_button
        self.wait = wait

    ### Properties
    @property
    def subtitle(self):
        return self.__subtitle

    @property
    def sound(self):
        return self.__sound

    
    ### Setters
    @subtitle.setter
    def subtitle(self, subtitle):
        self.__subtitle = subtitle

    @sound.setter
    def sound(self, sound):
        self.__sound = sound

    ### General Methods
    def show(self) -> int:
        buttons = str(self.buttons).replace("'", '"').replace("[", "{").replace("]", "}")
        type = f'as {self.type} ' if self.type != None else ''
        buttons = f'buttons {buttons} ' if self.type != None else ''
        default_button = f'default button "{self.default_button}" ' if self.default_button != None else ''
        cancel_button = f'cancel button "{self.cancel_button}" ' if self.cancel_button != None else ''
        wait = f'giving up after "{self.wait}" ' if self.wait != -1 else ''
        notification_text = f"""
            try
                do shell script "afplay /System/Library/Sounds/Glass.aiff" & " > /dev/null 2>&1 &"
                display alert "{self.title}" message "{self.content}" {type}{buttons}{default_button}{cancel_button}{wait}
            on error
                -- do nothing
            end try
        """
        response = os.system(f"osascript -e '{notification_text}'")
        if "Ok" in response:
            return 0
        return 1

class TimedNotification(Notification):
    def __init__(self, arrival_time: datetime, content: Any = None, title: str = "New Notification"):
        super().__init__(content, title)
        self.arrival_time: datetime = arrival_time

        new_thread = threading.Timer(interval = (arrival_time - datetime.now()).total_seconds(), function = self.show)
        new_thread.start()

    def show(self) -> None:
            super().show()

class TimedDesktopNotification(TimedNotification, DesktopNotification):
    def __init__(self, arrival_time: datetime, content: Any = None, title: str = "New Notification", subtitle: str = None, sound = "Glass"):
        super().__init__(content, title, subtitle, sound)
        self.content: Any = content
        self.title: str = title
        #self.arrival_time: datetime = arrival_time

        new_thread = threading.Timer(interval = (arrival_time - datetime.now()).total_seconds(), function = self.show)
        new_thread.start()

    def show(self) -> None:
        super().show()
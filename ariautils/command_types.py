from typing import Callable, Iterable, Union, Mapping, Any, Type
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException

import threading

from time import sleep

from .command_utils import Command

class DaemonSpawner(Command):
    def __init__(self, DaemonClass = Type[threading.Thread]):
        self.daemons = {}
        self.DaemonClass = DaemonClass

    def new_daemon(self, target: Callable, prefix: str = "daemon", args: Iterable = ..., start = True):
        id = len(self.daemons)
        name = prefix + "_" + str(id)
        new_daemon = self.DaemonClass(target=target, args=args, name=name, daemon=True)
        self.daemons[id] = new_daemon
        if start == True:
            self.start(id)
        return new_daemon

    def add_daemon(self, thread, start: bool = False):
        id = len(self.daemons)

        if id not in thread.getName():
            thread.setName(thread.getName() + "_" + str(id))
        self.daemons[id] = thread
        if start == True:
            self.start(id)

    def start(self, daemon_id):
        self.daemons[id].start()

    def stop(self, daemon_id):
        self.daemons[id].stop()

### High-level Action Classes
class WebAction(Command):
    def find_api(self, base_url):
        pass


    def find_search_url(self, base_url):
        driver = webdriver.Safari()
        driver.set_window_size(1512, 900)

        if not base_url.startswith("http"):
            base_url = "http://" + base_url

        driver.get(base_url)

        names = ["search", "query", "q", "s", "term", "search_query", "searchString"]
        selectors = ["input[type='search' i]", "input[placeholder*='search' i]", "input[type='text' i]", "input[aria-label*='search' i]"]

        search_url = None
        search_box = None

        for name in names:
            search_url = None
            try:
                search_box = driver.find_element_by_name(name)
                search_box.clear()
                search_box.send_keys("test")
                search_box.send_keys(Keys.RETURN)
                sleep(0.35)
                search_url = driver.current_url

                if "test" in search_url:
                    search_url = search_url[:search_url.index("test")]
                else:
                    pass
                break

            except NoSuchElementException as e:
                # Could not find named element
                pass
            except ElementNotInteractableException as e:
                # Named element is not interactable
                pass

        if search_box == None:
            for selector in selectors:
                search_url = None
                try:
                    search_box = driver.find_elements_by_css_selector(selector)[0]
                    search_box.clear()
                    search_box.send_keys("test")
                    search_box.send_keys(Keys.RETURN)
                    sleep(0.35)
                    search_url = driver.current_url

                    if "test" in search_url:
                        search_url = search_url[:search_url.index("test")]
                    else:
                        pass
                    break

                except Exception as e:
                    # Could not find named element
                    pass

        if search_box == None:
            search_button = None
            try:
                search_button = driver.find_element_by_partial_link_text("search")
                if search_button == None:
                    search_button = driver.find_elements_by_css_selector("button[aria-label*='search' i]")[0]

                if search_button != None:
                    search_button.click()
            except:
                pass

            # Do it all again...
            for name in names:
                search_url = None
                try:
                    search_box = driver.find_element_by_name(name)
                    search_box.clear()
                    search_box.send_keys("test")
                    search_box.send_keys(Keys.RETURN)
                    sleep(0.35)
                    search_url = driver.current_url

                    if "test" in search_url:
                        search_url = search_url[:search_url.index("test")]
                    else:
                        pass
                    break

                except NoSuchElementException as e:
                    # Could not find named element
                    pass
                except ElementNotInteractableException as e:
                    # Named element is not interactable
                    pass

            if search_box == None:
                for selector in selectors:
                    search_url = None
                    try:
                        search_box = driver.find_elements_by_css_selector(selector)[0]
                        search_box.clear()
                        search_box.send_keys("test")
                        search_box.send_keys(Keys.RETURN)
                        sleep(0.35)
                        search_url = driver.current_url

                        if "test" in search_url:
                            search_url = search_url[:search_url.index("test")]
                        else:
                            pass
                        break

                    except Exception as e:
                        # Could not find named element
                        pass

        driver.close()
        return search_url


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
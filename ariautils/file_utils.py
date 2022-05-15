"""A document/file IO manager for Aria. Only one DocumentManager should be active at a time.
"""

import os, threading
from time import sleep
from pathlib import Path
from typing import List, Union

current_file = []
previous_files = []
file_history_size = 10

daemons = []

def set_current_file(new_file_path):
    """ Sets the current file. """
    current_file = new_file_path

    if previous_files == [] or current_file != previous_files[-1]:
        previous_files.append(current_file)

    if len(previous_files) > file_history_size:
        previous_files.pop(0)

def open_file(filepath, mode = "w"):
    """ Opens a file. For writing by default. """
    set_current_file(filepath)
    return open(filepath, mode)

def close_file(file):
    """Closes a supplied file object.
    """
    file.close()

def touch(filepath):
    """Creates an empty file.
    """
    write(filepath, "", "a")

def watch_file_for_changes(filepath, on_change):
    """Initializes a daemon thread that detects changes in the hash of the specified file.

    :param filepath: The full path of the file to observe changes in.
    :type filepath: str
    :param on_change: A method to be executed when changes are detected. Must accept the file path as an argument.
    :type on_change: func(str)
    :return: None
    """
    id = len(daemons)

    watcher_thread = threading.Thread(target=_watch_file_daemon, args=(filepath, id, on_change), name="watcher_" + str(id), daemon=True)
    daemons.append((watcher_thread, True, filepath))
    watcher_thread.start()

def watch_folder_for_changes(folder_path, on_change, watch_files = False):
    """Initializes a daemon thread that detect changes in the specified folder's content.

    :param folder_path: The full path of the folder to observe changes in.
    :type folder_path: str
    :param on_change: A method to be executed when changes are detected. Must accept the folder path as an argument.
    :type on_change: func(str)
    :param watch_files: Whether to check for changes in the content of files instead of just the number of files in the folder, defaults to False.
    :type watch_files: bool, optional
    :return: None
    """
    id = len(daemons)

    watcher_thread = threading.Thread(target=_watch_folder_daemon, args=(folder_path, id, on_change, watch_files), name="watcher_" + str(id), daemon=True)
    daemons.append((watcher_thread, True, folder_path))
    watcher_thread.start()

def stop_watching(path):
    """Tells the daemon watching for changes to the given path to stop.

    :param path: A path currently being watched for changes.
    :type path: str
    """
    for index, daemon_tuple in enumerate(daemons):
        if daemon_tuple[2] == path:
            daemons[index] = (daemon_tuple[0], False, daemon_tuple[1])
            daemon_tuple[0].join()

def stop_watching_all():
    """Tells all daemons watching for changes to stop.

    :return: The number of daemons stopped.
    :rtype: int
    """
    for index, daemon_tuple in enumerate(daemons):
        daemons[index] = (daemon_tuple[0], False, daemon_tuple[1])
        daemon_tuple[0].join()
    return len(daemons)

def _watch_file_daemon(filepath, id, on_change):
    """The daemon that watches for changes to an individual file.

    :param filepath: The full path of the file to observe changes in.
    :type filepath: str
    :param id: The index of the daemon in the list of daemons.
    :type id: int
    :param on_change: A method to be executed when changes are detected. Must take the file path as an argument.
    :type on_change: func(str)
    """
    old_hash = None
    while daemons[id][1]:
        file = open(filepath, 'r')
        new_hash = hash(file.read())

        if old_hash == None:
            hash = hash(content)
        elif old_hash != new_hash:
            old_hash = new_hash
            on_change(filepath)

        file.close()
        sleep(1)

def _watch_folder_daemon(folder_path, id, on_change, watch_files = False):
    """The daemon that watches for changes to a folder and the files within it.

    :param filepath: The full path of the folder to observe changes in.
    :type filepath: str
    :param id: The index of the daemon in the list of daemons.
    :type id: int
    :param on_change: A method to be executed when changes are detected. Must take the folder path as an argument.
    :type on_change: func(str)
    :param watch_files: Whether to check for changes in the content of files instead of just the number of files in the folder, defaults to False
    :type watch_files: bool, optional
    """
    files = os.listdir(folder_path)
    files.sort()

    file_hashes = []
    if watch_files:
        for filename in files:
            file = open(folder_path + "/" + filename, "r")

            if filename == ".DS_Store":
                file_hashes.append(None)
            else:
                content = file.read()
                file_hashes.append(hash(content))
            file.close()

    while daemons[id][1]:
        current_files = os.listdir(folder_path)
        current_files.sort()
        
        if files != current_files:
            files = current_files
            on_change(folder_path)
            file_hashes.clear()
            if watch_files:
                for filename in files:
                    file = open(folder_path + "/" + filename, "r")

                    try:
                        content = file.read()
                        file_hashes.append(hash(content))
                    except:
                        file_hashes.append(None)

                    file.close()

        elif watch_files:
            found_changes = False
            for index, filename in enumerate(current_files):
                file = open(folder_path + "/" + filename, "r")

                new_hash = None
                try:
                    new_hash = hash(file.read())
                except:
                    pass

                file.close()

                if file_hashes[index] != new_hash:
                    found_changes = True
                    file_hashes[index] = new_hash

            if found_changes:
                on_change(folder_path)
                    
        sleep(1)

def get_file_content(filepath):
    """
    Returns the content within a file as a single string.

    Parameters:
        filepath: str - The full path of the file to read content from.

    Returns:
        content : str - The content of the file.
    """
    set_current_file(filepath)
    with open(filepath, "r") as target_file:
        content = target_file.read()
    return content

def write(filepath, string, mode = "w"):
    """ Writes the provided string to a file. Write mode by default. """
    set_current_file(filepath)
    with open(filepath, mode) as target_file:
        if isinstance(string, str):
            target_file.write(string)
        elif isinstance(string, list):
            lines = [s+"\n" for s in string]
            target_file.writelines(lines)

def prepend(filepath, string):
    """ Prepends the provided string to the beginning of a file. """
    set_current_file(filepath)
    content = get_file_content(filepath)
    new_content = string + content
    write(filepath, new_content, "w")

def insert(filepath, string, line_num):
    """ Inserts the provided string to the end of the line at the provided line number in a file. """
    set_current_file(filepath)
    lines = get_lines(filepath)
    while len(lines) < line_num+2:
        lines.append("")
    lines[line_num] = lines[line_num] + string
    write(filepath, lines, "w")

def append(filepath, string):
    """ Appends the provided string to the end of a file. """
    set_current_file(filepath)
    write(filepath, string, "a")

def replace_line(filepath, string, line_num):
    """ Replaces the line at line num with the target string. """
    set_current_file(filepath)
    lines = get_lines(filepath)
    if line_num > len(lines):
        print("There aren't enough lines in the target file to make that replacement.")
        return
    lines[line_num] = string
    write(filepath, lines, "w")

def get_lines(filepath):
    """ Returns lines as list. """
    set_current_file(filepath)
    return get_file_content(filepath).split("\n")

def get_last_line(filepath):
    """ Returns last line of document as string. """
    set_current_file(filepath)
    return get_lines(filepath)[-1]

def get_last_filled_line(filepath):
    """ Returns the last populated line of a document as a string. """
    set_current_file(filepath)
    lines = get_lines(filepath)
    for line in lines[::-1]:
        if line != "":
            return line

def has_str(filepath, string, case_sensitive = False):
    """ Returns true if the target str occurs anywhere in the file. """
    set_current_file(filepath)
    content = get_file_content(filepath)

    if case_sensitive == False:
        return string.lower() in content.lower()
    return string in content

def has_strs(filepath, *args):
    """ Check if all target strings occur anywhere in the file. """
    set_current_file(filepath)
    found_all = True
    for arg in args:
        if isinstance(arg, list):
            for string in arg:
                if not has_str(filepath, string, False):
                    return False
        elif not has_str(filepath, arg, False):
            return False
    return True

def has_line(filepath, line):
    """ Returns true if a line in the file is exactly equal to the supplied line. """
    set_current_file(filepath)
    lines = get_lines(filepath)
    return line in lines

def find_line(filepath, string):
    """ Returns the line number where the target string occurs, -1 otherwise if it can't be found. """
    set_current_file(filepath)
    lines = get_lines(filepath)
    for index, line in enumerate(lines):
        if string in line:
            return index
    return -1

def find_str(filepath, string):
    """ Returns the range of lines across which the target string occurs, -1 otherwise. """
    set_current_file(filepath)
    line_num = find_line(filepath, string)
    if line_num > -1:
        # String occurs in a single line; return corresponding line number
        return (line_num, line_num)

    lines = get_lines(filepath)
    parts = string.split()

    start_substrings = []
    end_substrings = []
    for index in range(0, len(parts)):
        start_substring = " ".join(parts[0:index+1])
        end_substring = " ".join(parts[-index:])
        start_substrings.append(start_substring)
        end_substrings.insert(0, end_substring)

    start_line = -1
    end_line = -1
    for index, line in enumerate(lines):
        for substring in start_substrings:
            if line.endswith(substring):
                start_line = index
            else:
                break

        for substring in end_substrings:
            if line.startswith(substring):
                end_line = index
            else:
                break
    return (start_line, end_line)

def exists(filepath):
    return os.path.exists(filepath)

def is_empty(filepath):
    return os.stat(filepath).st_size == 0

def list_files(dir_path: Union[str, os.PathLike], ignored_extensions: List[str] = [".pyc"], ignored_strings: List[str] = ["__"],
               recursive: bool = False, show_dot_files: bool = False) -> List[Path]:
    """Get a list of files in a directory.

    :param path: The path of a directory to list the files of.
    :type path: str or PathLike
    :param ignored_extensions: A list of file extensions; files with those extensions will be excluded from the returned list of files, defaults to [".pyc"]
    :type ignored_extensions: list, optional
    :param ignored_strings: A list of strings; files containing any of those strings in their name will be excluded from the returned list of files, defaults to ["__"]
    :type ignored_strings: list, optional
    :param recursive: Whether to recursively include files in all subdirectories, defaults to False
    :type recursive: bool, optional
    :param show_dot_files: Whether to include dot files (such as .env) in the returned list of files, defaults to False
    :type show_dot_files: bool, optional
    :return: A list of files as Path objects.
    :rtype: list[Path]
    """
    dir_path = Path(dir_path)
    if not dir_path.is_dir():
        return []

    file_list = []
    for sub_path in dir_path.iterdir():
        if recursive and sub_path.is_dir:
            file_list.extend(list_files(sub_path, ignored_extensions, ignored_strings, True, show_dot_files))

        if show_dot_files == False and sub_path.suffix == "":
            continue

        if sub_path.suffix in ignored_extensions or any([string in sub_path.stem for string in ignored_strings]):
            continue

        file_list.append(sub_path)
    return file_list
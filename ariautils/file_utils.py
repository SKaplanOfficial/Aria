"""A document/file IO manager for Aria. Only one DocumentManager should be active at a time.
"""

import os

current_file = []
previous_files = []
file_history_size = 10

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
    """ Closes a supplied file object. """
    file.close()

def touch(filepath):
    write(filepath, "", "a")

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
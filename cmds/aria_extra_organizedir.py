import os
from pathlib import Path

from ariautils import command_utils, io_utils
from ariautils.misc_utils import any_in_str

class OrganizeCommand(command_utils.Command):
    info = {
        "title": "Directory Organizer",
        "repository": "https://github.com/SKaplanOfficial/Aria-Commands/Aria-Extras",
        "documentation_link": "https://github.com/SKaplanOfficial/Aria-Commands/Aria-Extras/",
        'id': "aria_extra_organizedir",
        "version": "1.0.0",
        "description": """
            This command cleans up directories by organizing files into folders based on their extension.
        """,
        "requirements": {},
        "extensions": {},
        "purposes": [
            "organize this folder", "clean up this folder"
        ],
        "targets": [
            "this", "these"
        ],
        "keywords": [
            "aria", "command", "extra", "filesystem", "directories", "files", "macos", "contextual", "utility", "productivity"
        ],
        "example_usage": [
            ("organize this directory", "Organize the selected directory recursively."),
            ("sort this", "Organize the selected directory recursively."),
            ("sort these", "Organize all of the selected directories recursively")
        ],
        "help": [
            "As of now, you must select a directory in Finder for this command's functions to work.",
        ],
        "contact_details": {
            "author": "Stephen Kaplan",
            "email": "stephen.kaplan@maine.edu",
            "website": "http://skaplan.io",
        },
        "info_version": "0.9.0",
    }

    # Map of file extensions to high-level categories
    filetypes = {
        "Apps": [".app", ".exe", ".command", ".msi"],
        "Archives": ['.zip', '.rar', '.tar', '.gz', '.bz2', '.xz', ".deb", ".whl", ".zipx", ".jar", ".apk", ".7z"],
        "Audio": ['.mp3', '.wav', ".ogg", ".flv", ".mp4", ".wma", ".aac", ".aiff", ".flac"],
        "Books": [".mobi", ".epub", ".ebook"],
        "Dev": [".json", ".sql", ".csv", ".htm", '.html', '.css', ".less", ".wasm", '.js', ".mustache", ".scss", ".php", ".jsx", '.py', '.c', ".h", '.cpp', '.java', ".r", ".rustc", ".rs", ".pde", ".cpp", ".bat", ".bash", ".c++", ".f90", ".go", ".lisp", ".lua", ".rb", ".swift", ".vb", ".xcodeproj", ".zsh", ".sh"],
        "Disk Images": [".img", ".dmg", ".bundle", ],
        "Documents": ['.log', '.doc', '.docx', '.pdf', '.wps', ".pages", ".numbers", ".txt", ".rtf", ".md", ".tex", ".key", ".pptx", ".odp", ".xlsx", ".xls", ".numbers"],
        "Fonts": [".otf", ".ttf", ".woff", ".woff2"],
        "Pictures": ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', ".raw", ".svg", ".heif, .heic", ".gif", ".webp"],
        "Purgable": [".bin", ".bib", ".download"],
        "Videos": ['.3gp', '.mov', '.mp4', '.mkv', '.srt', '.avi', ".wemb", ".f4v", ".ogg", ".gifv", ".qt", ".wmv", ".amv", ".m4p", ".m4v", ".mpg", ".mp2", ".mpeg", ".mpe", ".mpv", ".m2v", ".flv"],
        "Other": [".br"],
    }

    def execute(self, query, _origin):
        # Get list of selected folders
        selected_items = command_utils.plugins["aria_core_context"].get_selected_items()
        query_type = self.get_query_type(query, get_tuple = True)

        if query_type[0] in [100, 200]:
            # Operate on the selected folders.
            for item in selected_items:
                self.__run(Path(item), query_type[1]["func"], query_type[1]["args"])

    def __run(self, path, operation, args):
        """Wraps execution of the supplied operation and reports completion status.

        :param path: The path of the directory to operate on.
        :type path: PosixPath or WindowsPath
        :param operation: The method to invoke with the supplied path and arguments.
        :type operation: func
        :param args: A list of values to pass as arguments to the supplied operation.
        :type args: list
        """
        operation(path, *args)
        io_utils.sprint("Organized " + str(path))

    def __flatten(self, path):
        """Flattens a directory, making all files of all subdirectories the direct children of the initial (parent) directory. No further attempt at organization is made.

        :param path: The path of the current directory to organize.
        :type path: PosixPath or WindowsPath
        """
        dirs_to_rm = []
        for subpath in path.glob('**/*'):
            if subpath.is_file():
                # Avoid overwriting files 
                new_path = Path(str(path) + "/" + subpath.name)
                while new_path.exists():
                    new_path = Path(str(path) + "/" + new_path.stem + "_" + new_path.suffix)
                subpath.rename(new_path)
            else:
                dirs_to_rm.append(subpath)

        for dir in dirs_to_rm[::-1]:
            dir.rmdir()

    def __quick_organize(self, path, max_recurse = -1, current_depth = 0):
        """Organizes a directory recursively by sorting files into folders based on their extension.

        This organization method balances speed and utility by using the same sorting scheme for all directories and subdirectories. This method makes no attempt to merge similar subdirectories or create subcategory folders for categories with many files.

        :param path: The path of the current directory to organize.
        :type path: PosixPath or WindowsPath
        :param max_recurse: Maximum depth of subdirectories that will be organized, defaults to -1 (No maximum)
        :type max_recurse: int, optional
        :param current_depth: The number of directories in the hierarchy between the current one and the original, defaults to 0
        :type current_depth: int, optional
        """
        # Organize child directories (depth-first)
        if path.is_dir():
            if max_recurse == -1 or current_depth < max_recurse:
                for subpath in path.iterdir():
                    self.__quick_organize(subpath, max_recurse, current_depth + 1)

        if not path.name.startswith("."):
            # Try to identify the appropriate parent category
            ext = path.suffix
            category = None
            for filetype, extensions in self.filetypes.items():
                if ext.lower() in extensions:
                    category = filetype
                    break

            if category != None:
                # Create the category directory if needed
                dest = str(path.parent) + "/" + category
                dest_dir = Path(dest)
                dest_dir.mkdir(parents=True, exist_ok=True)

                # Avoid overwriting files 
                dest_file = Path(str(dest_dir) + "/" + path.name)
                while dest_file.exists():
                    dest_file = Path(str(dest_dir) + "/" + dest_file.stem + "_" + dest_file.suffix)

                path.rename(dest_file)

    def get_query_type(self, query, get_tuple = False):
        # Check that selected items are directories
        selected_items = command_utils.plugins["aria_core_context"].get_selected_items()
        has_dir_targets = all([Path(item.url).is_dir() for item in selected_items]) if selected_items is not None else False
        has_dir_targets = False

        current_application = command_utils.plugins["aria_core_context"].current_application
        localized_name = current_application.localized_name if current_application is not None else ""

        # Define conditions and associated method for each execution pathway
        __query_type_map = {
            100: { # Flatten
                "conditions": [has_dir_targets, "Finder" in localized_name, ("these" in query or "this" in query), any_in_str(["flatten", "unnest", "crush", "squash"], query)],
                "func": self.__flatten,
                "args": [],
            },
            200: { # Primary command - Organize/Sort
                "conditions": [has_dir_targets, "Finder" in localized_name, ("these" in query or "this" in query), any_in_str(["organize", "sort"], query)],
                "func": self.__quick_organize,
                "args": [],
            },
        }

        # Obtain query type and associated execution data
        for key, query_type in __query_type_map.items():
            if all(query_type["conditions"]):
                if get_tuple:
                    return (key, query_type)
                return key
        return 0

command = OrganizeCommand()
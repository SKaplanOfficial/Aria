"""An Aria plugin for determining the semantic meaning of content.
"""

import re
from ariautils import command_utils

class TypeCommand(command_utils.Command):
    info = {
        "title": "Get Input Type",
        "repository": "https://github.com/SKaplanOfficial/Aria",
        'id': "aria_core_identity_type",
        "version": "1.0.0",
        "description": """
            Gets the semantic type of the input.
        """,
        "requirements": {
            "aria_core_context": "1.0.0",
        },
        "extensions": {},
        "purposes": [
            "Get semantic type."
        ],
        "targets": [],
        "keywords": [
            "aria", "core", "command", "input", "type", "semantics", "context",
        ],
        "example_usage": [
            ("type Helvetica", "Gets the semantic type of 'Helvetica', which is a font family."),
        ],
        "contact_details": {
            "author": "Stephen Kaplan",
            "email": "stephen.kaplan@maine.edu",
            "website": "http://skaplan.io",
        },
        "info_version": "0.9.0",
    }

    def __init__(self):
        super().__init__()

    def execute(self, query, origin) -> None:
        if query.content.startswith("type summary "):
            content = query.content[13:]
            self.show_content_summary(content)
        elif query.content.startswith("type "):
            content = query.content[5:]
            print(self.get_content_type(content))

    def invocation(self, query):
        if not isinstance(query.content, str):
            return False
        return query.content.startswith("type ") or query.content.startswith("type summary")

    def get_content_type(self, content: str) -> str:
        """Gets the semantic type of the string content. The first matching type is used.

        :param content: The content to analyze
        :type content: str
        :return: _description_
        :rtype: A string indicating the semantic type of the content

        .. versionadded:: 1.0.0
        """
        method_order = {
            self.is_url: "URL",
            self.is_phone_number: "Phone Number",
            self.is_expression: "Expression",
            self.is_date: "Date",
            self.is_time: "Time",
            self.is_shortcut_name: "Shortcut",
            self.is_note_folder_name: "Note Folder",
            self.is_shortcut_folder_name: "Shortcut Folder",
            self.is_reminder_list_name: "Reminder List",
            self.is_photo_album_name: "Photo Album",
            self.is_photo_folder_name: "Photo Folder",
            self.is_font_family: "Font Family",
            self.is_typeface: "Typeface",
            
            self.is_chat_name: "Chat",
            self.is_chat_participant_name: "Chat Participant",
            self.is_note_name: "Note",
            self.is_reminder_name: "Reminder",

            self.is_saved_stock: "Saved Stock",
            self.is_sidebar_location_name: "Sidebar Location",

            self.is_photo_name: "Photo",
        }

        for method in method_order:
            if method(content):
                return method_order[method]


    def show_content_summary(self, content: str):
        """Prints a summary of each semantic type and whether the content string is of the type or not.

        :param content: The content to analyze
        :type content: str

        .. versionadded:: 1.0.0
        """
        print("\tURL:\t\t\t", self.is_url(content))
        print("\tPhone Number:\t\t", self.is_phone_number(content))

        print("\tExpression:\t\t", self.is_expression(content))
        print("\tEquation:\t\t", self.is_equation(content))

        print("\tDate:\t\t\t", self.is_date(content))
        print("\tTime:\t\t\t", self.is_time(content))
        # print("\tCoordinates:\t\t", self.is_coordinate(content))

        print("\tNote Folder Name:\t", self.is_note_folder_name(content))
        print("\tNote Name:\t\t", self.is_note_name(content))

        # print("\tMusic Playlist Name:\t", self.is_music_playlist(content))
        # print("\tMusic Track Name:\t", self.is_music_track(content))

        # print("\tTV Playlist Name:\t", self.is_tv_playlist(content))
        # print("\tTV Track Name:\t", self.is_tv_track(content))

        print("\tShortcut Folder Name:\t", self.is_shortcut_folder_name(content))
        print("\tShortcut Name:\t\t", self.is_shortcut_name(content))

        # print("\tContact Group Name:\t", self.is_contact_group(content))
        # print("\tContact Name:\t\t", self.is_contact(content))

        print("\tChat Name:\t\t", self.is_chat_name(content))
        print("\tChat Participant Name:\t", self.is_chat_participant_name(content))

        print("\tSidebar Location Name:\t", self.is_sidebar_location_name(content))

        print("\tReminder List Name:\t", self.is_reminder_list_name(content))
        print("\tReminder Name:\t\t", self.is_reminder_name(content))

        print("\tSaved Stock Name:\t", self.is_saved_stock(content))

        # print("\tFont Collection Name:\t", self.is_font_collection(content))
        print("\tFony Family Name:\t", self.is_font_family(content))
        print("\tTypeface Name:\t\t", self.is_typeface(content))

        print("\tPhoto Album Name:\t", self.is_photo_album_name(content))
        print("\tPhoto Folder Name:\t", self.is_photo_folder_name(content))
        print("\tPhoto Name:\t\t", self.is_photo_name(content))

    def is_url(self, content: str) -> bool:
        """Checks whether the content string is a URL.

        :param content: The content string to analyze
        :type content: str
        :return: True if the string is a URL
        :rtype: bool

        .. versionadded:: 1.0.0
        """
        predicate = re.compile(r'((http|https):\/\/)([A-Za-z0-9]+\.)+([A-Za-z0-9]+)(\/[A-Za-z0-9]+(\.[A-Za-z0-9]+)?)*(\?[A-Za-z0-9]+=[A-Za-z0-9]+(&[A-Za-z0-9]+=[A-Za-z0-9]+)*)?')
        return predicate.match(content) is not None

    def is_phone_number(self, content: str) -> bool:
        """Checks whether the content string is a phone number.

        :param content: The content string to analyze
        :type content: str
        :return: True if the string is a phone number
        :rtype: bool

        .. versionadded:: 1.0.0
        """
        predicate = re.compile(r'^(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$')
        return predicate.match(content) is not None

    def is_date(self, content: str) -> bool:
        """Checks whether the content string represents a date.

        :param content: The content string to analyze
        :type content: str
        :return: True if the string is a date
        :rtype: bool

        .. versionadded:: 1.0.0
        """
        predicate = re.compile(r'^(.* [0-9][0-9]?,? [0-9]{2,4}|[0-9][0-9]? .*,? [0-9]{2,4}|[0-9]{1,2}\/[0-9]{1,2}\/[0-9]{2,4}|[0-9]{2,4}\/[0-9]{1,2}\/[0-9]{1,2})')
        return predicate.match(content) is not None

    def is_time(self, content: str) -> bool:
        """Checks whether the content string represents a time.

        :param content: The content string to analyze
        :type content: str
        :return: True if the string is a time
        :rtype: bool

        .. versionadded:: 1.0.0
        """
        predicate = re.compile(r'^([0-9]{0,2}:[0-9]{2}) ?(A.?M.?|P.?M.?|a.?m.?|p.?m.?)?')
        return predicate.match(content) is not None

    def is_coordinate(self, content: str) -> bool:
        """Checks whether the content string is a coordinate.

        :param content: The content string to analyze
        :type content: str
        :return: True if the string is a coordinate
        :rtype: bool

        .. versionadded:: 1.0.0
        """
        predicate = re.compile(r'^[\(]?([0-9]+\.?[0-9]*|[0-9]*\.[0-9]+), ?([0-9]+\.?[0-9]*|[0-9]*\.[0-9]+)[\)]?')
        return predicate.match(content) is not None

    def is_expression(self, content: str) -> bool:
        """Checks whether the content string represents a mathematical expression.

        :param content: The content string to analyze
        :type content: str
        :return: True if the string is a mathematical expression
        :rtype: bool

        .. versionadded:: 1.0.0
        """
        predicate = re.compile(r'^\(? ?([0-9]+\.?[0-9]*|[0-9]*\.[0-9]+) ?\)? ?[\+\-\*\/\%x\^\!\&\|]+ ?\(? ?([0-9]+\.?[0-9]*|[0-9]*\.[0-9]+) ?\)?')
        return predicate.match(content) is not None

    def is_equation(self, content: str) -> bool:
        """Checks whether the content string represents a mathematical equation.

        :param content: The content string to analyze
        :type content: str
        :return: True if the string is a mathematical equation
        :rtype: bool

        .. versionadded:: 1.0.0
        """
        predicate = re.compile(r'^\(? ?([0-9]+\.?[0-9]*|[0-9]*\.[0-9]+) ?\)? ?[\+\-\*\/\%x\^\!\&\|]* ?\(? ?([0-9]+\.?[0-9]*|[0-9]*\.[0-9]+)? ?\)? ?= ?\(? ?([0-9]+\.?[0-9]*|[0-9]*\.[0-9]+) ?\)? ?[\+\-\*\/\%x\^\!\&\|]* ?\(? ?([0-9]+\.?[0-9]*|[0-9]*\.[0-9]+)? ?\)?')
        return predicate.match(content) is not None

    # Notes
    def is_note_folder_name(self, content: str) -> bool:
        """Checks whether the content string is the name of a folder in Notes.app.

        :param content: The content string to analyze
        :type content: str
        :return: True if the string is the name of a notes folder
        :rtype: bool

        .. versionadded:: 1.0.0
        """
        note_folders = command_utils.plugins["aria_core_context"].data(["note_folders"])
        if note_folders is not None:
            return content in note_folders.name()
        return False

    def is_note_name(self, content: str) -> bool:
        """Checks whether the content string is the name of a note in Notes.app.

        :param content: The content string to analyze
        :type content: str
        :return: True if the string is the name of a note
        :rtype: bool

        .. versionadded:: 1.0.0
        """
        notes = command_utils.plugins["aria_core_context"].data(["notes"])
        if notes is not None:
            return content in notes.name()
        return False

    def is_note_text(self, content: str) -> bool:
        """Checks whether the content string is the text of a note in Notes.app.

        :param content: The content string to analyze
        :type content: str
        :return: True if the string is the text of a note
        :rtype: bool

        .. versionadded:: 1.0.0
        """
        notes = command_utils.plugins["aria_core_context"].data(["notes"])
        if notes is not None:
            return content in notes.plaintext()
        return False

    # Shortcuts
    def is_shortcut_folder_name(self, content: str) -> bool:
        """Checks whether the content string is the name of a folder in Shortcuts.app.

        :param content: The content string to analyze
        :type content: str
        :return: True if the string is the name of a shortcuts folder
        :rtype: bool

        .. versionadded:: 1.0.0
        """
        shortcut_folders = command_utils.plugins["aria_core_context"].data(["shortcut_folders"])
        if shortcut_folders is not None:
            return content in shortcut_folders.name()
        return False

    def is_shortcut_name(self, content: str) -> bool:
        """Checks whether the content string is the name of a shortcut in Shortcuts.app.

        :param content: The content string to analyze
        :type content: str
        :return: True if the string is the name of a shortcut
        :rtype: bool

        .. versionadded:: 1.0.0
        """
        shortcuts = command_utils.plugins["aria_core_context"].data(["shortcuts"])
        if shortcuts is not None:
            return content in shortcuts.name()
        return False

    # Music
    def is_music_playlist(self, content: str) -> bool:
        """Checks whether the content string is the name of a playlist in Music.app.

        :param content: The content string to analyze
        :type content: str
        :return: True if the string is the name of a music playlist
        :rtype: bool

        .. versionadded:: 1.0.0
        """
        music_playlists = command_utils.plugins["aria_core_context"].data(["music_playlists"])
        if music_playlists is not None:
            return content in music_playlists.name()
        return False

    def is_music_track(self, content: str) -> bool:
        """Checks whether the content string is the name of a track in Music.app.

        :param content: The content string to analyze
        :type content: str
        :return: True if the string is the name of a music track
        :rtype: bool

        .. versionadded:: 1.0.0
        """
        music_tracks = command_utils.plugins["aria_core_context"].data(["music_tracks"])
        if music_tracks is not None:
            return content in music_tracks.name()
        return False

    # TV
    def is_tv_playlist(self, content: str) -> bool:
        """Checks whether the content string is the name of a playlist in TV.app.

        :param content: The content string to analyze
        :type content: str
        :return: True if the string is the name of a TV playlist
        :rtype: bool

        .. versionadded:: 1.0.0
        """
        tv_playlists = command_utils.plugins["aria_core_context"].data(["tv_playlists"])
        if tv_playlists is not None:
            return content in tv_playlists.name()
        return False

    def is_tv_track(self, content: str) -> bool:
        """Checks whether the content string is the name of a track (e.g. movie, TV show) in TV.app.

        :param content: The content string to analyze
        :type content: str
        :return: True if the string is the name of a TV track
        :rtype: bool

        .. versionadded:: 1.0.0
        """
        tv_tracks = command_utils.plugins["aria_core_context"].data(["tv_tracks"])
        if tv_tracks is not None:
            return content in tv_tracks.name()
        return False

    # Contacts
    def is_contact_group(self, content: str) -> bool:
        """Checks whether the content string is the name of a contact group in Contacts.app.

        :param content: The content string to analyze
        :type content: str
        :return: True if the string is the name of a contact group
        :rtype: bool

        .. versionadded:: 1.0.0
        """
        contact_groups = command_utils.plugins["aria_core_context"].data(["contact_groups"])
        if contact_groups is not None:
            return content in contact_groups.name()
        return False

    def is_contact(self, content: str) -> bool:
        """Checks whether the content string is the name of a contact in Contacts.app.

        :param content: The content string to analyze
        :type content: str
        :return: True if the string is the name of a contact
        :rtype: bool

        .. versionadded:: 1.0.0
        """
        contacts = command_utils.plugins["aria_core_context"].data(["contacts"])
        if contacts is not None:
            return content in contacts.name()
        return False

    # Messages
    def is_chat_name(self, content: str) -> bool:
        """Checks whether the content string is the name of a chat in Messages.app.

        :param content: The content string to analyze
        :type content: str
        :return: True if the string is the name of a chat
        :rtype: bool

        .. versionadded:: 1.0.0
        """
        chats = command_utils.plugins["aria_core_context"].data(["chats"])
        if chats is not None:
            return content in chats.name()
        return False

    def is_chat_participant_name(self, content: str) -> bool:
        """Checks whether the content string is the name of a chat participant in Messages.app.

        :param content: The content string to analyze
        :type content: str
        :return: True if the string is the name of a chat participant
        :rtype: bool

        .. versionadded:: 1.0.0
        """
        chat_participants = command_utils.plugins["aria_core_context"].data(["chat_participants"])
        if chat_participants is not None:
            return content in chat_participants.name()
        return False

    # Maps
    def is_sidebar_location_name(self, content: str) -> bool:
        """Checks whether the content string is the name of a saved location in Maps.app.

        :param content: The content string to analyze
        :type content: str
        :return: True if the string is the name of a saved sidebar location
        :rtype: bool

        .. versionadded:: 1.0.0
        """
        sidebar_locations = command_utils.plugins["aria_core_context"].data(["sidebar_locations"])
        if sidebar_locations is not None:
            return content in sidebar_locations.name()
        return False

    # Photos
    def is_photo_album_name(self, content: str) -> bool:
        """Checks whether the content string is the name of an album in Photos.app.

        :param content: The content string to analyze
        :type content: str
        :return: True if the string is the name of a photos album
        :rtype: bool

        .. versionadded:: 1.0.0
        """
        photo_albums = command_utils.plugins["aria_core_context"].data(["photo_albums"])
        if photo_albums is not None:
            return content in photo_albums.name()
        return False

    def is_photo_folder_name(self, content: str) -> bool:
        """Checks whether the content string is the name of a folder in Photos.app

        :param content: The content string to analyze
        :type content: str
        :return: True if the string is the name of a photos folder
        :rtype: bool

        .. versionadded:: 1.0.0
        """
        photo_folders = command_utils.plugins["aria_core_context"].data(["photo_folders"])
        if photo_folders is not None:
            return content in photo_folders.name()
        return False

    def is_photo_name(self, content: str) -> bool:
        """Checks whether the content string is the name of a photo in Photos.app.

        :param content: The content string to analyze
        :type content: str
        :return: True if the string is the name of a photo
        :rtype: bool

        .. versionadded:: 1.0.0
        """
        photos = command_utils.plugins["aria_core_context"].data(["photos"])
        if photos is not None:
            return content in photos.name()
        return False

    # Reminders
    def is_reminder_list_name(self, content: str) -> bool:
        """Checks whether the content string is the name of a list in Reminders.app.

        :param content: The content string to analyze
        :type content: str
        :return: True if the string is the name of a reminder list
        :rtype: bool

        .. versionadded:: 1.0.0
        """
        reminder_lists = command_utils.plugins["aria_core_context"].data(["reminder_lists"])
        if reminder_lists is not None:
            return content in reminder_lists.name()
        return False

    def is_reminder_name(self, content: str) -> bool:
        """Checks whether the content string shares a name with a reminder in Reminders.app.

        :param content: The content string to analyze
        :type content: str
        :return: True if the string is the name of a reminder
        :rtype: bool

        .. versionadded:: 1.0.0
        """
        reminders = command_utils.plugins["aria_core_context"].data(["reminders"])
        if reminders is not None:
            return content in reminders.name()
        return False

    # Font Book
    def is_font_collection(self, content: str) -> bool:
        """Checks whether the content string is the name of a font collection in Font Book.app

        :param content: The content string to analyze
        :type content: str
        :return: True if the string is the name of a font collection
        :rtype: bool

        .. versionadded:: 1.0.0
        """
        font_collections = command_utils.plugins["aria_core_context"].data(["font_collections"])
        if font_collections is not None:
            return content in font_collections.name()
        return False

    def is_font_family(self, content: str) -> bool:
        """Checks whether the content string is the name of a font family stored on the system.

        :param content: The content string to analyze
        :type content: str
        :return: True if the string is the name of font family
        :rtype: bool

        .. versionadded:: 1.0.0
        """
        font_families = command_utils.plugins["aria_core_context"].data(["font_families"])
        if font_families is not None:
            return content in font_families.name()
        return False

    def is_typeface(self, content: str) -> bool:
        """Checks whether the content string is the name of a typeface stored on the system.

        :param content: The content string to analyze
        :type content: str
        :return: True if the string is the name of a typeface
        :rtype: bool

        .. versionadded:: 1.0.0
        """
        typefaces = command_utils.plugins["aria_core_context"].data(["typefaces"])
        if typefaces is not None:
            return content in typefaces.name()
        return False

    # Stocks
    def is_saved_stock(self, content: str) -> bool:
        """Checks whether the content string shares a name with a saved stock in Stocks.app.

        :param content: The content string to analyze
        :type content: str
        :return: True if the string is the name of a saved stock
        :rtype: bool

        .. versionadded:: 1.0.0
        """
        saved_stocks = command_utils.plugins["aria_core_context"].data(["saved_stocks"])
        if saved_stocks is not None:
            return content in saved_stocks.name()
        return False

command_exports = [
    TypeCommand(),
]


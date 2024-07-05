"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia import AttributeProperty
from evennia.objects.objects import DefaultRoom
from evennia.utils.ansi import ANSIString
from evennia.utils.evtable import EvTable
from .objects import ObjectParent
from django.conf import settings


def _get_client_width(looker, session=None):
    """
    Discover the looker's client width by using the session, if provided.

    If no session is provided, will use the most recently attached session on
    the looker.

    If no session is found on the looker, will use the DEFAULT_CLIENT_WIDTH
    from settings
    """
    if session is None and looker is not None and looker.sessions.count():
        session = looker.sessions.all()[-1]
    if session is not None:
        return min(settings.CLIENT_DEFAULT_WIDTH, session.get_client_size()[0])
    else:
        return settings.CLIENT_DEFAULT_WIDTH

class Room(ObjectParent, DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See examples/object.py for a list of
    properties and methods available on all Objects.
    """

    exits_per_row = AttributeProperty(3)

    # Styling for EvTables in the room display output
    styles = {
        "title": {
            "fill_char": ANSIString("|R=|n"),
        },
        # Common Section Styles
        "section_table": {
            "header_line_char": ANSIString("|R-|n"),
            "border": "header",
            "pad_left": 1,
            "pad_right": 1,
        },
        "section_header": {},
        "section_contents": {},
        # Character Section Styles
        "character_section_table": {
            "valign": "b",
        },
        "character_section_header": {},
        "character_section_contents": {
            "pad_top": 1,
        },
        "character_shortdesc_column": {},
        "character_idle_time_column": {
            "align": "r",
        },
        "character_name_column": {},
        # Exit Section Styles
        "exit_section_table": {
            "pad_top": 0,
            "pad_bottom": 0,
        },
        "exit_section_header": {},
        "exit_section_contents": {},
        "footer": {
            "fill_char": ANSIString("|R=|n"),
        },
    }

    def get_display_name(self, looker, **kwargs):
        """
        Displays the name of the object in a viewer-aware manner.
        """
        return super().get_display_name(looker, **kwargs)

    def get_extra_display_name_info(self, looker, **kwargs):
        """
        Adds any extra display information to the object's name. By default this is is the
        object's dbref in parentheses, if the looker has permission to see it.
        """
        return super().get_extra_display_name_info(looker, **kwargs)

    def get_display_tags(self, looker, **kwargs):
        """
        Returns a list of textual tags to add to the rooms title string.
        """
        return (tag for tag in self.display_tag_mapping.keys() if self.tags.has(tag))

    def get_display_desc(self, looker, **kwargs):
        """
        Returns the displayed description of the room
        """
        return self.db.desc or "You see nothing special."

    def get_display_characters(self, looker, **kwargs):
        """
        Returns a list of DefaultCharacters that should be displayed in the room for the given viewer.
        """
        return [
            char
            for char in self.contents
            if char.has_account and char.access(looker, "view")
        ]

    def get_display_exits(self, looker, **kwargs):
        """
        Returns a list of DefaultExits that should be displayed in the room for the given viewer.
        """
        return [exit for exit in self.contents if exit.destination]

    def get_display_footer(self, looker, session=None, **kwargs):
        """
        Get the 'footer' of the room description. Called by `return_appearance`.
        """
        styles = self.styles["footer"]
        width = _get_client_width(looker, session)
        return styles["fill_char"] * width

    def format_header(self, looker, header, **kwargs):
        """
        Applies extra formatting to the rooms display header
        """
        return header

    # These are tags that are displayed next to the name of the room
    #
    # The keys are the names of the tags
    # The values are the text to display when the tag is present on the room
    display_tag_mapping = {"ooc": "OOC Area", "chargen": "CG"}

    def format_title(self, looker, name, extra_name_info, tags, session=None, **kwargs):
        """
        Applies extra formatting to the rooms title string.
        The title includes the name, displayed tags, and extra name info such as dbrefs for builders
        """
        tags = "".join(
            f"|w[{self.display_tag_mapping[tag] or tag}]|n" for tag in tags)
        tags = f"{tags} " if tags else ""
        title = f"|Y[|n {tags}|w{name}|w{extra_name_info} |Y]|n"
        styles = self.styles["title"]
        width = _get_client_width(looker, session)
        return ANSIString(title).center(width, styles["fill_char"])

    def format_desc(self, looker, desc, **kwargs):
        """
        Applies extra formatting to the rooms display description
        """
        return desc

    def format_exit_section(self, looker, exits, session=None, **kwargs):
        """
        Returns how the exits of a room should be displayed when viewed from inside the room.
        """
        if not exits:
            return ""
        width = _get_client_width(looker, session)
        table = EvTable(
            width=width,
            **{
                **self.styles["section_table"],
                **self.styles["exit_section_table"],
            },
        )
        table.add_header(
            " |wExits|n ",
            **{
                **self.styles["section_header"],
                **self.styles["exit_section_header"],
            },
        )
        exits = [
            exit.get_display_name(looker)
            for exit in sorted(exits, key=lambda e: e.name)
        ]
        for i in range(0, len(exits), self.exits_per_row):
            table.add_row(
                *exits[i: i + self.exits_per_row],
                **{
                    **self.styles["section_contents"],
                    **self.styles["exit_section_contents"],
                },
            )
        return ANSIString("\n").join(table.get())

    def format_character_section(self, looker, characters, session=None, **kwargs):
        """
        Returns how the characters inside a room should be displayed when viewed from inside the room.
        """
        if not characters:
            return ""
        width = _get_client_width(looker, session)
        table = EvTable(
            width=width,
            **{
                **self.styles["section_table"],
                **self.styles["character_section_table"],
            },
        )
        table.add_header(
            "|w Characters |n",
            **{
                **self.styles["section_header"],
                **self.styles["character_section_header"],
            },
        )
        for char in characters:
            name = char.get_display_name(looker, **kwargs)
            idle_time = char.format_idle_time(looker, **kwargs)
            shortdesc = char.get_display_shortdesc(looker, **kwargs)

            table.add_row(
                *[shortdesc, name, idle_time],
                **{
                    **self.styles["section_contents"],
                    **self.styles["character_section_contents"],
                },
            )
        table.reformat_column(0, **self.styles["character_shortdesc_column"])
        table.reformat_column(
            1, width=int(width * 0.25), **self.styles["character_name_column"]
        )
        table.reformat_column(
            2, width=int(width * 0.0625), **self.styles["character_idle_time_column"]
        )
        return ANSIString("\n").join(table.get())

    def format_footer(self, looker, footer, **kwargs):
        """
        Applies extra formatting to the rooms display footer
        """
        return footer

    def return_appearance(self, looker, **kwargs):
        """
        This is the hook for returning the appearance of the room.
        """
        header = self.format_header(
            looker, self.get_display_header(looker, **kwargs), **kwargs)

        name = self.get_display_name(looker, **kwargs)

        extra_name_info = self.get_extra_display_name_info(looker, **kwargs)

        tags = self.get_display_tags(looker, **kwargs)

        title = self.format_title(
            looker, name, extra_name_info, tags, **kwargs)

        desc = self.format_desc(
            looker, self.get_display_desc(looker, **kwargs), **kwargs)

        character_section = self.format_character_section(
            looker, self.get_display_characters(looker, **kwargs), **kwargs)

        exit_section = self.format_exit_section(
            looker, self.get_display_exits(looker, **kwargs), **kwargs)

        footer = self.format_footer(
            looker,
            self.get_display_footer(looker, **kwargs),
            **kwargs,
        )

        return ANSIString("\n\n").join(
            s
            for s in [header, title, desc, character_section, exit_section, footer]
            if s
        )

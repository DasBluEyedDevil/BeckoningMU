"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia import AttributeProperty
from evennia.objects.objects import DefaultRoom
from evennia.utils.ansi import ANSIString
from evennia.utils.evtable import EvTable
from .objects import ObjectParent


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

    def get_display_tag_mapping(self, looker):
        """
        These are tags that are displayed next to the name of a room

        The keys are the names of the Evennia Tags that should be displayed.
        The values are the text to display when that tag is present on the room.
        """
        return {"ooc": "OOC Area", "chargen": "CG"}

    def get_display_desc(self, looker, **kwargs):
        """
        Returns the displayed description of the room
        """
        return self.db.desc or "You see nothing special."

    def get_display_characters(self, looker, **kwargs):
        """
        Returns a list of DefaultCharacters that should be displayed in the room for the given viewer.
        """
        characters = [
            char
            for char in self.contents
            if char.has_account and char.access(looker, "view")
        ]
        if not characters:
            return ""
        width = looker.get_min_client_width()
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

    def get_display_exits(self, looker, **kwargs):
        """
        Returns a list of DefaultExits that should be displayed in the room for the given viewer.
        """
        exits = [exit for exit in self.contents if exit.destination]

        if not exits:
            return ""
        width = looker.get_min_client_width()
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

    def get_display_footer(self, looker, **kwargs):
        """
        Get the 'footer' of the room description. Called by `return_appearance`.
        """
        styles = self.styles["footer"]
        width = looker.get_min_client_width()
        return styles["fill_char"] * width

    def return_appearance(self, looker, **kwargs):
        """
        This is the hook for returning the appearance of the room.
        """
        header = self.get_display_header(looker, **kwargs)

        name = self.get_display_name(looker, **kwargs)

        extra_name_info = self.get_extra_display_name_info(looker, **kwargs)

        display_tag_mapping = self.get_display_tag_mapping(looker, **kwargs)

        tags = " ".join(
            f"|w[{display_tag_mapping[tag] or tag}]|n" for tag in display_tag_mapping.keys() if self.tags.has(tag))

        title = f"|Y[|n {tags}|w{name}|w{extra_name_info} |Y]|n"
        title = ANSIString(title).center(
            looker.get_min_client_width(), self.styles["title"]["fill_char"])

        desc = self.get_display_desc(looker, **kwargs)

        character_section = self.get_display_characters(looker, **kwargs)

        exit_section = self.get_display_exits(looker, **kwargs)

        footer = self.get_display_footer(looker, **kwargs)

        return ANSIString("\n\n").join(
            s
            for s in [header, title, desc, character_section, exit_section, footer]
            if s
        )

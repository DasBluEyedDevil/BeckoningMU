"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from evennia.objects.objects import DefaultCharacter, DefaultObject
from evennia.accounts.accounts import DefaultAccount
from .objects import ObjectParent


class Character(ObjectParent, DefaultCharacter):
    """
    The Character defaults to reimplementing some of base Object's hook methods with the
    following functionality:

    at_basetype_setup - always assigns the DefaultCmdSet to this object type
                    (important!)sets locks so character cannot be picked up
                    and its commands only be called by itself, not anyone else.
                    (to change things, use at_object_creation() instead).
    at_post_move(source_location) - Launches the "look" command after every move.
    at_post_unpuppet(account) -  when Account disconnects from the Character, we
                    store the current location in the pre_logout_location Attribute and
                    move it to a None-location so the "unpuppeted" character
                    object does not need to stay on grid. Echoes "Account has disconnected"
                    to the room.
    at_pre_puppet - Just before Account re-connects, retrieves the character's
                    pre_logout_location Attribute and move it back on the grid.
    at_post_puppet - Echoes "AccountName has entered the game" to the room.

    """

    def at_object_creation(self):
        super().at_object_creation()

    def get_display_shortdesc(self, looker=None, **kwargs):
        if self.db.shortdesc:
            return self.db.shortdesc
        else:
            return "Use '+short <description>' to set a description."

    def format_idle_time(self, looker, **kwargs):
        # If the character is the looker, show 0s.
        if self == looker:
            return "|g0s|n"
        time = self.idle_time or self.connection_time
        if time is None:
            return "|g0s|n"
        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        # round seconds
        seconds = int(round(seconds, 0))
        minutes = int(round(minutes, 0))
        hours = int(round(hours, 0))
        days = int(round(days, 0))

        if days > 0:
            time_str = f"|x{days}d|n"
        elif hours > 0:
            time_str = f"|x{hours}h|n"
        elif minutes > 0:
            if minutes > 10 and minutes < 15:
                time_str = f"|G{minutes}m|n"
            elif minutes > 15 and minutes < 20:
                time_str = f"|y{minutes}m|n"
            elif minutes > 20 and minutes < 30:
                time_str = f"|r{minutes}m|n"
            elif minutes > 30 and minutes:
                time_str = f"|r{minutes}m|n"
            else:
                time_str = f"|g{minutes}m|n"
        elif seconds > 0:
            time_str = f"|g{seconds}s|n"
        return time_str.strip()


class OOCAvatar(Character):
    """
    A typeclass for "OOC" Avatar Characters.

    An OOC Avatar as created on account creation and used to interact with OOC environments
    """

    @classmethod
    def create(
        cls,
        key,
        account: "DefaultAccount" = None,
        caller: "DefaultObject" = None,
        method: str = "create",
        **kwargs,
    ):
        """
        Creates a basic Character with default parameters, unless otherwise
        specified or extended.

        Provides a friendlier interface to the utils.create_character() function.

        Args:
            key (str): Name of the new Character.
            account (obj, optional): Account to associate this Character with.
                If unset supplying None-- it will
                change the default lockset and skip creator attribution.

        Keyword Args:
            description (str): Brief description for this object.
            ip (str): IP address of creator (for object auditing).
            All other kwargs will be passed into the create_object call.

        Returns:
            tuple: `(new_character, errors)`. On error, the `new_character` is `None` and
            `errors` is a `list` of error strings (an empty list otherwise).

        """
        char, errors = super(Character, cls).create(key, account, caller, method, **kwargs)

        # Make this character the account's primary OOC avatar if it doesn't already have one
        if account and char and not account.db.ooc_avatar:
            account.db.ooc_avatar = char

        return char, errors

    def at_object_creation(self):
        super().at_object_creation()
        self.tags.add("ooc")


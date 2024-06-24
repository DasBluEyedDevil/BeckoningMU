"""
Command sets

All commands in the game must be grouped in a cmdset.  A given command
can be part of any number of cmdsets and cmdsets can be added/removed
and merged onto entities at runtime.

To create new commands to populate the cmdset, see
`commands/command.py`.

This module wraps the default command sets of Evennia; overloads them
to add/remove commands from the default lineup. You can create your
own cmdsets by inheriting from them or directly from `evennia.CmdSet`.

"""

from evennia import default_cmds
from commands.admin import AdminCmdSet
from commands.character import CustomCharacterCmdSet
from commands.chargen import ChargenCmdSet
from commands.comms import CommsCmdSet
from commands.notes import NotesCmdSet
from commands.roleplaying import RpCmdSet
from commands.v5 import V5CmdSet
from bbs.CmdSet import CmdSet as BBSCmdSet
from jobs.jobCmdSet import JobCmdSet
from evennia.contrib.game_systems.mail import CmdMail
from evennia.contrib.game_systems.multidescer import CmdMultiDesc
from evennia.contrib.utils.git_integration import GitCmdSet


class CharacterCmdSet(default_cmds.CharacterCmdSet):
    """
    The `CharacterCmdSet` contains general in-game commands like `look`,
    `get`, etc available on in-game Character objects. It is merged with
    the `AccountCmdSet` when an Account puppets a Character.
    """

    key = "DefaultCharacter"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        # Custom CmdSets
        self.add(AdminCmdSet())
        self.add(CustomCharacterCmdSet())
        self.add(ChargenCmdSet())
        self.add(CommsCmdSet())
        self.add(NotesCmdSet())
        self.add(RpCmdSet())
        self.add(V5CmdSet())
        # Custom Apps CmdSets
        self.add(BBSCmdSet())
        self.add(JobCmdSet())
        # Evennia contrib CmdSets
        self.add(GitCmdSet())
        # Evennia contrib Commands
        self.add(CmdMail(help_category="Comms"))
        self.add(CmdMultiDesc())


class AccountCmdSet(default_cmds.AccountCmdSet):
    """
    This is the cmdset available to the Account at all times. It is
    combined with the `CharacterCmdSet` when the Account puppets a
    Character. It holds game-account-specific commands, channel
    commands, etc.
    """

    key = "DefaultAccount"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #


class UnloggedinCmdSet(default_cmds.UnloggedinCmdSet):
    """
    Command set available to the Session before being logged in.  This
    holds commands like creating a new account, logging in, etc.
    """

    key = "DefaultUnloggedin"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #


class SessionCmdSet(default_cmds.SessionCmdSet):
    """
    This cmdset is made available on Session level once logged in. It
    is empty by default.
    """

    key = "DefaultSession"

    def at_cmdset_creation(self):
        """
        This is the only method defined in a cmdset, called during
        its creation. It should populate the set with command instances.

        As and example we just add the empty base `Command` object.
        It prints some info.
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #


from evennia.commands.cmdset import CmdSet
import evennia.commands.default as default_cmds
from evennia.contrib.game_systems.multidescer import CmdMultiDesc
from .command import Command

HELP_CATEGORY = "character"


class CharacterCustomizationCmdSet(CmdSet):
    """
    Commands for customizing a character's appearance.
    """
    key = "CharacterCustomization"

    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        # use default IC command and move to "character" help category
        self.add(CmdShortDesc())
        self.add(CmdMoniker())
        # Evennia contrib Commands
        self.add(CmdMultiDesc(key="desc", aliases=["+desc"], help_category=HELP_CATEGORY))
        # Override help category of Evennia default commands
        # self.add(default_cmds.general.CmdSetDesc(help_category=HELP_CATEGORY))

class CmdShortDesc(Command):
    """
    Set your short description.

    Usage:
      +short <description>
    """

    key = "shortdesc"
    help_category = HELP_CATEGORY
    aliases = ["short", "+shortdesc", "+short"]
    locks = "cmd:all()"

    def func(self):
        "Implement the command"
        if not self.args:
            self.caller.msg("Usage: +short <description>")
            return
        self.caller.db.shortdesc = self.args.strip()
        self.caller.msg("Short description set to '%s'." % self.args.strip())


class CmdMoniker(Command):
    """
    Set your moniker.

    Usage:
      +moniker <moniker>
    """

    key = "moniker"
    help_category = HELP_CATEGORY
    aliases = ["+moniker"]
    locks = "cmd:all()"

    def func(self):
        "Implement the command"

        # check to see if caller is builder+
        if not self.caller.locks.check_lockstring(self.caller, "perm(Builder)"):
            self.caller.msg("|wCG>|n Pwemission Denied.")
            return

        if not self.args:
            self.caller.msg("Usage: +moniker <moniker>")
            return
        self.caller.db.moniker = self.args.strip()
        self.caller.msg("Moniker set to '%s'." % self.args.strip())


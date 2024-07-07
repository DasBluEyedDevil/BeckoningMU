from evennia.commands.cmdset import CmdSet
import evennia.commands.default.building as default_cmds

HELP_CATEGORY = "building"


class BuildingCmdSet(CmdSet):
    """
    Commands for builders.

    We mostly use the built-in Evennia building commands. This CmdSet mostly
    just customizes the names/aliases a bit.
    """
    key = "Building"

    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        self.add(CmdSetDesc)


class CmdSetDesc(default_cmds.CmdDesc):
    """
    describe an object or the current room.

    Usage:
      setdesc [<obj> =] <description>

    Switches:
      edit - Open up a line editor for more advanced editing.

    Sets the "desc" attribute on an object. If an object is not given,
    describe the current room.
    """
    key = "setdesc"
    aliases = ["@desc", "@setdesc"]
    switch_options = ("edit",)
    locks = "cmd:perm(setdesc) or perm(Builder)"
    help_category = HELP_CATEGORY

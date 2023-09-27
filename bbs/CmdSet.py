# import default CmdSet
from evennia.commands.cmdset import CmdSet
from .commands import CmdBBS, classCmdBbRead


class CmdSet(CmdSet):
    """
    This is the base cmdset for all bb commands.
    """

    def at_cmdset_creation(self):
        self.add(CmdBBS())
        self.add(classCmdBbRead())

import evennia
from evennia.commands.cmdset import CmdSet


class CustomCharacterCmdSet(CmdSet):
    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        self.add(CmdLook())


class CmdLook(evennia.commands.default.general.CmdLook):
    # """
    # look at location or object
    #
    # Usage:
    #   look
    #   look <obj>
    #   look *<account>
    #
    # Observes your location or objects in your vicinity.
    # """

    # key = "look"
    # aliases = ["l", "ls"]
    # locks = "cmd:all()"
    # arg_regex = r"\s|$"

    # Code copied from the default CmdLook with some modifications:
    # 1. pass the session into at_look so that objects can use client screen width
    def func(self):
        """
        Handle the looking.
        """
        caller = self.caller
        if not self.args:
            target = caller.location
            if not target:
                caller.msg("You have no location to look at!")
                return
        else:
            target = caller.search(self.args)
            if not target:
                return
        desc = caller.at_look(target, session=self.session)
        # add the type=look to the outputfunc to make it
        # easy to separate this output in client.
        self.msg(text=(desc, {"type": "look"}), options=None)

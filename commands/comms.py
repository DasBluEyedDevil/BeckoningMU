from evennia.commands.cmdset import CmdSet
from evennia.commands.default.muxcommand import MuxCommand
from evennia.utils.ansi import ANSIString


class CommsCmdSet(CmdSet):
    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        self.add(CmdOOC())


class CmdOOC(MuxCommand):
    """
    Send an OOC message.

    Usage:
      ooc <message>
      ooc/style <OOC style>

    Switches:
        /style - sets your OOC style to the one specified.

    """

    key = "ooc"
    help_category = "General"
    locks = "cmd:all()"

    def func(self):
        "Implement function"

        caller = self.caller

        if "style" in self.switches:
            if not self.args:
                caller.msg("OOC style removed.")
                self.caller.db.ooc_style = ""
                return

            self.caller.db.ooc_style = self.args.strip()
            caller.msg("OOC style set to '%s'." %
                       ANSIString(self.args.strip()))
            return

        speech = self.args.strip()

        # Check for empty message
        if speech in ["", ";", ":"]:
            caller.msg("OOC what?")
            return

        # Calling the at_pre_say hook on the character
        speech = caller.at_pre_say(speech)

        # Format message based on prefix
        if speech.startswith(":"):
            speech = " " + speech[1:].lstrip()
        elif speech.startswith(";"):
            speech = speech[1:].lstrip()
        else:
            speech = f' says, "{speech}"'

        for looker in caller.location.contents:
            # Add display name
            ooc = self.caller.get_display_name(looker) + speech

            # Add OOC style
            if self.caller.db.ooc_style:
                ooc = caller.db.ooc_style + " " + ooc
            else:
                ooc = "|w<|rOOC|n|w>|n " + ooc

            # Send to all in current location.
            looker.msg(ooc)

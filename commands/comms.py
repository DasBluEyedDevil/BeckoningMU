from evennia.commands.cmdset import CmdSet
from evennia.utils.ansi import ANSIString
from .command import Command


class CommsCmdSet(CmdSet):
    key = "Comms"

    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        self.add(CmdOOCSay())


class CmdOOCSay(Command):
    """
    Say something to the room while Out-of-Character (OOC).

    Usage:
      osay <message>
      osay/style <OOC style>

    Switches:
        /style - sets your OOC style to the one specified.

    """

    key = "osay"
    # This should probably go into Comms category, but "say" is currently in General
    help_category = "General"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller

        if "style" in self.switches:
            if not self.args:
                caller.msg("OOC style removed.")
                self.caller.db.osay_style = ""
                return

            self.caller.db.osay_style = self.args.strip()
            caller.msg("OOC style set to '%s'." %
                       ANSIString(self.args.strip()))
            return

        speech = self.args.strip()

        # Check for empty message
        if speech in ["", ";", ":"]:
            caller.msg("Say what?")
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
                ooc = caller.db.osay_style + " " + ooc
            else:
                ooc = "|w<|rOOC|n|w>|n " + ooc

            # Send to all in current location.
            looker.msg(ooc)

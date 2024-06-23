from evennia.commands.cmdset import CmdSet
from evennia.commands.default.muxcommand import MuxCommand


class AdminCmdSet(CmdSet):
    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        self.add(CmdEmit())


class CmdEmit(MuxCommand):
    """
    admin command for emitting message to multiple objects

    Usage:
      emit[/switches] [<obj>, <obj>, ... =] <message>
      remit           [<obj>, <obj>, ... =] <message>
      pemit           [<obj>, <obj>, ... =] <message>

    Switches:
      room     -  limit emits to rooms only (default)
      accounts -  limit emits to accounts only
      contents -  send to the contents of matched objects too

    Emits a message to the selected objects or to
    your immediate surroundings. If the object is a room,
    send to its contents. remit and pemit are just
    limited forms of emit, for sending to rooms and
    to accounts respectively.
    """

    key = "emit"
    aliases = ["pemit", "remit"]
    switch_options = ("room", "accounts", "contents")
    locks = "cmd:perm(emit) or perm(Builder)"
    help_category = "Admin"

    def func(self):
        """Implement the command"""

        caller = self.caller
        args = self.args

        if not args:
            string = "Usage: "
            string += "\nemit[/switches] [<obj>, <obj>, ... =] <message>"
            string += "\nremit           [<obj>, <obj>, ... =] <message>"
            string += "\npemit           [<obj>, <obj>, ... =] <message>"
            caller.msg(string)
            return

        rooms_only = "rooms" in self.switches
        accounts_only = "accounts" in self.switches
        send_to_contents = "contents" in self.switches

        # we check which command was used to force the switches
        if self.cmdstring == "remit":
            rooms_only = True
            send_to_contents = True
        elif self.cmdstring == "pemit":
            accounts_only = True
        else:
            rooms_only = True
            send_to_contents = True

        if not self.rhs:
            message = self.args
            objnames = [caller.location.key]
        else:
            message = self.rhs
            objnames = self.lhslist

        # send to all objects
        for objname in objnames:
            obj = caller.search(objname, global_search=True)
            if not obj:
                return
            if rooms_only and obj.location is not None:
                caller.msg(ANSIString(f"{objname} is not a room. Ignored."))
                continue
            if accounts_only and not obj.has_account:
                caller.msg(f"{objname} has no active account. Ignored.")
                continue
            if obj.access(caller, "tell"):
                obj.msg(ANSIString(message))
                if send_to_contents and hasattr(obj, "msg_contents"):
                    obj.msg_contents(ANSIString(message))
            else:
                caller.msg(f"You are not allowed to emit to {objname}.")

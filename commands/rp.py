from evennia.commands.cmdset import CmdSet
from evennia.commands.default.muxcommand import MuxCommand


class RpCmdSet(CmdSet):
    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        self.add(CmdShortDesc())
        self.add(CmdMoniker())
        self.add(CmdPose())


class CmdShortDesc(MuxCommand):
    """
    Set your short description.

    Usage:
      +short <description>
    """

    key = "+short"
    help_category = "Character Generation"
    aliases = ["shortdesc", "+shortdesc", "short"]
    locks = "cmd:all()"
    help_category = "Character"

    def func(self):
        "Implement the command"
        if not self.args:
            self.caller.msg("Usage: +short <description>")
            return
        self.caller.db.shortdesc = self.args.strip()
        self.caller.msg("Short description set to '%s'." % self.args.strip())


class CmdMoniker(MuxCommand):
    """
    Set your moniker.

    Usage:
      +moniker <moniker>
    """

    key = "+moniker"
    help_category = "Character Generation"
    aliases = ["moniker", "+moniker"]
    locks = "cmd:all()"
    help_category = "Character"

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


class CmdPose(MuxCommand):
    """
    strike a pose

    Usage:
      pose <pose text>
      pose's <pose text>

    Example:
      pose is standing by the wall, smiling.
       -> others will see:
      Tom is standing by the wall, smiling.

    Describe an action being taken. The pose text will
    automatically begin with your name.
    """

    key = "pose"
    aliases = [":", "emote", ";"]
    locks = "cmd:all()"
    arg_regex = ""

    # we want to be able to pose without whitespace between
    # the command/alias and the pose (e.g. :pose)
    arg_regex = None

    def parse(self):
        """
        Custom parse the cases where the emote
        starts with some special letter, such
        as 's, at which we don't want to separate
        the caller's name and the emote with a
        space.
        """
        args = self.args
        if args and not args[0] in ["'", ",", ":"]:
            args = " %s" % args.strip()
        elif args and args[0] == ";":
            args = "%s" % args.strip()

        self.args = args

    def func(self):
        """Hook function"""
        if not self.args:
            msg = "What do you want to do?"
            self.caller.msg(msg)
        else:
            # send an indivtual message to every listening object in the location.
            # We need to use self.caller.get_display_name(looker) to get the name but we
            # need the looker object first.

            # get all of the objects in the location
            lookers = self.caller.location.contents
            # loop through the list of objects
            for looker in lookers:
                # send the message to the object
                looker.msg(
                    f"{self.caller.get_display_name(looker)}{self.args}")

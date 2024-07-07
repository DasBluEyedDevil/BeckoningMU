from evennia.commands.cmdset import CmdSet
import evennia.commands.default as default_cmds
from .command import Command

HELP_CATEGORY = "roleplaying"


class RPCmdSet(CmdSet):
    """ 
    Commands for In-Character communication and roleplaying
    """
    key = "RP"

    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        self.add(CmdPose())
        # override Evennia default commands to put them under the Roleplaying help category
        self.add(default_cmds.general.CmdSay(help_category=HELP_CATEGORY))
        self.add(default_cmds.general.CmdWhisper(help_category=HELP_CATEGORY))


class CmdPose(Command):
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

    help_category = HELP_CATEGORY

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



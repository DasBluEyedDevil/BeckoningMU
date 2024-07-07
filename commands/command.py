"""
Commands

Commands describe the input the account can do to the game.

"""

from evennia.commands.command import InterruptCommand
from evennia.commands.default.muxcommand import MuxCommand


class Command(MuxCommand):
    """
    Base command class used by all commands by default, including built-in Evennia commands.

    Note: you may see this in-game if a child command had no help text defined

    Each Command class implements the following methods, called in this order
    (only func() is actually required):

        - at_pre_cmd(): If this returns anything truthy, execution is aborted.
        - parse(): Should perform any extra parsing needed on self.args
            and store the result on self.
        - func(): Performs the actual work.
        - at_post_cmd(): Extra actions, often things done after
            every command, like prompts.

    """

    def parse(self):
        """
        This method is called by the cmdhandler once the command name
        has been identified. It creates a new set of member variables
        that can be later accessed from self.func() (see below)

        The following variables are available for our use when entering this
        method (from the command definition, and assigned on the fly by the
        cmdhandler):
           self.key - the name of this command ('look')
           self.aliases - the aliases of this cmd ('l')
           self.permissions - permission string for this command
           self.help_category - overall category of command

           self.caller - the object calling this command
           self.cmdstring - the actual command name used to call this
                            (this allows you to know which alias was used,
                             for example)
           self.args - the raw input; everything following self.cmdstring.
           self.cmdset - the cmdset from which this command was picked. Not
                         often used (useful for commands like 'help' or to
                         list all available commands etc)
           self.obj - the object on which this command was defined. It is often
                         the same as self.caller.
        Notes:

            For full documentation of the command syntax, see MuxCommand.parse

            We override the MuxCommand parser here to add the following:
                * /help switch on all commands to show help text
        """
        # MuxCommand uses switch_options to determine which switches
        # are allowed. Add "help" as a valid switch before parsing.
        if not hasattr(self, "switch_options") or not self.switch_options:
            self.switch_options = ("help",)
        elif "help" not in self.switch_options:
            # Some commands use list others use tuple. Annoying
            if isinstance(self.switch_options, list):
                self.switch_options.append("help")
            elif isinstance(self.switch_options, tuple):
                self.switch_options += ("help",)

        # call MuxCommand parser
        super().parse()

        # if /help switch found, show help and exit command early
        if "help" in self.switches:
            self.msg(self.get_help(self.caller, self.cmdset))
            raise InterruptCommand

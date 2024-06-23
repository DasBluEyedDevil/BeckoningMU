"""
Commands for Vampire: the Masquerade 5th edition characters.

"""

from evennia.commands.default.muxcommand import MuxCommand
from evennia.commands.cmdset import CmdSet
import random


class V5CmdSet(CmdSet):
    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        self.add(CmdRouse())
        self.add(CmdSlake())


class CmdRouse(MuxCommand):
    """
    Usage: +rouse

    This command rolls a rouse check.  It takes the hunger mechanic into account.
    """

    key = "+rouse"
    aliases = ["rouse", "ro"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        if self.caller.db.stats["bio"]["splat"] == "vampire":
            roll = random.randint(1, 10)

            try:
                if self.caller.db.stats["pools"]["hunger"] + 1 > 5:
                    self.caller.msg("You are at hunger 5. You must slake.")
                    return
            except KeyError:
                self.caller.db.stats["pools"]["hunger"] = 0

            if roll > 6:
                self.caller.location.msg_contents(
                    "|hGame>|n %s rouses their hunger." % self.caller.name,
                    exclude=self.caller,
                )
                self.caller.msg("|hGame>|n You rouse your hunger|n")
            else:
                self.caller.location.msg_contents(
                    "|hGame>|n %s rouses their blood, and gains |r+1 hunger|n."
                    % self.caller.name,
                    exclude=self.caller,
                )
                self.caller.msg(
                    "|hGame>|n |rYou fail your rouse check, and generate +1 hunger.|n"
                )
                try:
                    self.caller.db.stats["pools"]["hunger"] += 1
                except KeyError:
                    self.caller.db.stats["pools"]["hunger"] = 1

                self.caller.msg(
                    "|hGame>|n Curent hunger: |r%s|n"
                    % self.caller.db.stats["pools"]["hunger"]
                )
        else:
            self.caller.msg("You are not a vampire.")
            return


class CmdSlake(MuxCommand):
    """
    Usage: +slake <number>

    This command slakes your hunger by the number you specify.
    """

    key = "+slake"
    aliases = ["slake", "sl"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        try:
            number = int(self.args)
        except ValueError:
            self.caller.msg("You must specify a number to slake by.")
            return

        try:
            if self.caller.db.stats["pools"]["hunger"] == 0:
                self.caller.msg("You have no hunger to slake.")
                return
        except KeyError:
            self.caller.db.stats["pools"]["hunger"] = 0
            self.caller.msg("You have no hunger to slake.")
            return

        if self.caller.db.stats["bio"]["splat"] == "vampire":
            if self.caller.db.stats["pools"]["hunger"] - number < 0:
                self.caller.msg("You cannot slake more hunger than you have.")
                return
            else:
                self.caller.db.stats["pools"]["hunger"] -= number
                self.caller.msg("You slake %s hunger." % number)
                self.caller.msg(
                    "Current hunger: |r%s|n" % self.caller.db.stats["pools"]["hunger"]
                )

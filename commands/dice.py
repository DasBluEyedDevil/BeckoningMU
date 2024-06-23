from evennia.commands.default.muxcommand import MuxCommand
from evennia.commands.cmdset import CmdSet
from world.data import get_trait_list
import random
from evennia.utils.ansi import ANSIString
from jobs.commands.commands import CmdJob


class DiceCmdSet(CmdSet):
    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        self.add(CmdDice())


class CmdDice(MuxCommand):
    """
    This is the dice roller command. It takes a dice pool and rolls that many dice.

    Usage:
        +roll <dice pool>
        +roll/perm <dice pool>

        The first form of this command rolls a dice pool, which is a combination of
        sheet traits plus numbers.  It takes temp scores into account.  The seccond
        form of this command only works with your permentant values in your traits.

    Example:
        +roll str + brawl  + 2
        +roll 5
        +roll/perm dex + melee
        +roll dex + 2 - 1

        This command also akes the hunger mechanic itto account.

        Aww Also: +stats +sheet
    """

    key = "roll"
    aliases = ["dice", "+roll", "+dice"]
    locks = "cmd:all()"
    help_category = "General"

    def results(self, dice):
        output = []
        res = {}
        count = 0
        tens = 0
        ones = 0
        crits = 0

        for _ in range(0, int(dice)):
            roll = random.randint(1, 10)
            if roll == 10:
                tens += 1
                count += 1
                output.append("|g%s|n " % roll)
            elif roll >= 6:
                output.append("|g%s|n " % roll)
                count += 1
            elif roll == 1:
                output.append("|r%s|n " % roll)
                ones += 1
            else:
                output.append("|y%s|n " % roll)

        if (tens / 2) >= 1:
            crits = int((tens / 2) * 2)

        output.sort(key=lambda x: int(ANSIString((x))))
        s_list = "".join(output)

        res["output"] = output
        res["s_list"] = s_list
        res["count"] = count
        res["crits"] = crits
        res["tens"] = tens
        res["ones"] = ones

        return res

    def func(self):
        if not self.caller.db.stats:
            self.caller.msg("You don't have any stats yet.")
            return

        try:
            hunger = self.caller.db.stats["pools"]["hunger"]
        except KeyError:
            hunger = 0

        ones = 0
        crits = 0
        if not self.args:
            self.caller.msg("Usage: +roll <dice pool>")
            return

        if "job" in self.switches:
            try:
                job, roll = self.args.split(" ", 1)
            except ValueError:
                self.caller.msg("Usage: +roll/job <id> <dice pool>")
                return
        else:
            roll = self.args

        # Anywhere in the string, when there's a plus sign with a space on each side, replace it with a plus
        # This is to allow for people to type in "+1 +2 +3" or "+1+2+3" and have it work the same way.
        args = (
            roll.replace("+", " +")
            .replace(" + ", " +")
            .replace("-", " -")
            .replace(" - ", " -")
            .replace("  ", " ")
            .split(" ")
        )
        dice = []
        dice_pool = 0

        for arg in args:
            if arg[0] == "+" or arg[0] == "-":
                if arg[1:].isdigit():
                    if arg[0] == "+":
                        dice_pool += int(arg[1:])
                    else:
                        dice_pool -= int(arg[1:])
                    dice.append(arg)

                # everything after the first character is a trait
                temp_arg = arg[1:]
                res = get_trait_list(temp_arg)
                if res:
                    # Try to add their dice in the trait to the dice pool
                    try:
                        value = self.caller.db.stats[res.get("category")][
                            res.get("trait")
                        ]

                        # if there's a temp value, add it to the dice pool
                        try:
                            temp = self.caller.db.stats["temp"][res.get(
                                "trait")]
                        except KeyError:
                            temp = 0
                        if "perm" in self.switches:
                            dice_pool += value
                        else:
                            dice_pool += max(value, temp)
                        # Append the dice list with the actual name of the trait.
                        dice.append(arg[0] + res.get("trait"))
                    except KeyError:
                        # if tehre's no dice behind it, still add the trait to the output.
                        dice.append(arg[0] + res.get("trait"))

                else:
                    pass
            else:
                if arg.isdigit():
                    dice_pool += int(arg)
                    dice.append(arg)
                else:
                    res = get_trait_list(arg)
                    if res:
                        # Try to add their dice in the trait to the dice pool
                        try:
                            value = self.caller.db.stats[res.get("category")][
                                res.get("trait")
                            ]

                            # if there's a temp value, add it to the dice pool
                            temp = 0
                            try:
                                temp = (
                                    self.caller.db.stats["temp"].get(
                                        res.get("trait"))
                                    or 0
                                )
                            except KeyError:
                                temp = 0

                            if "perm" in self.switches:
                                dice_pool += value
                            else:
                                try:
                                    dice_pool += max(value, temp)
                                except TypeError:
                                    dice_pool += value

                            # Append the dice list with the actual name of the trait.
                            dice.append(res.get("trait"))
                        except KeyError:
                            # if tehre's no dice behind it, still add the trait to the output.
                            dice.append(res.get("trait"))

        mod_dice_pool = dice_pool - hunger
        if mod_dice_pool <= 0:
            hunger = hunger + mod_dice_pool

        regular_dice = self.results(mod_dice_pool)
        hunger_dice = self.results(hunger)
        # calculate overall crits from regular and tens.
        crits = regular_dice.get("tens") + hunger_dice.get("tens")
        crits = int(crits / 2) * 2

        succs = regular_dice.get("count") + hunger_dice.get("count") + crits
        if succs == 0 and hunger_dice.get("ones") > 0:
            successes = "|rBestial Failure!|n"

        elif succs == 0 and not hunger_dice.get("ones"):
            successes = "|yFailure!|n"

        elif succs > 0 and hunger_dice.get("ones") > 0:
            successes = "|g" + str(succs) + "|n" + " successes"

        elif crits and hunger_dice.get("tens"):
            successes = "|g" + str(succs) + "|n" + " |rMessy Critical!|n"
        else:
            successes = "|g" + str(succs) + "|n" + " successes"
        dice = " ".join(dice).replace(" +", " + ").replace(" -", " - ")

        if "job" in self.switches:
            if hunger:
                msg = f"|wROLL>|n |c{self.caller.get_display_name()}|n rolls |w{dice}|n -> {successes} ({regular_dice.get('s_list').strip()}) |w<|n{hunger_dice.get('s_list').strip()}|w>|n"
            else:
                msg = f"|wROLL>|n |c{self.caller.get_display_name()}|n rolls |w{dice}|n -> {successes} ({regular_dice.get('s_list').strip()})"
            CmdJob.job_comment(self, job, msg, public=True)

        else:
            for looker in self.caller.location.contents:
                if hunger:
                    msg = f"|wROLL>|n |c{self.caller.get_display_name(looker)}|n rolls |w{dice}|n -> {successes} ({regular_dice.get('s_list').strip()}) |w<|n{hunger_dice.get('s_list').strip()}|w>|n"
                else:
                    msg = f"|wROLL>|n |c{self.caller.get_display_name(looker)}|n rolls |w{dice}|n -> {successes} ({regular_dice.get('s_list').strip()})"
                looker.msg(msg)

import random
from evennia.commands.cmdset import CmdSet
from evennia.utils.ansi import ANSIString
from jobs.commands.commands import CmdJob
from .command import Command
from world.data import (
    BIO,
    get_trait_list,
    PHYSICAL,
    MENTAL,
    SOCIAL,
    SKILLS,
)


class RpCmdSet(CmdSet):
    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        self.add(CmdShortDesc())
        self.add(CmdMoniker())
        self.add(CmdPose())
        self.add(CmdSheet())
        self.add(CmdDice())


class CmdShortDesc(Command):
    """
    Set your short description.

    Usage:
      +short <description>
    """

    key = "+short"
    help_category = "Character"
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


class CmdMoniker(Command):
    """
    Set your moniker.

    Usage:
      +moniker <moniker>
    """

    key = "+moniker"
    help_category = "Character"
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

    help_category = "Roleplaying"

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


class CmdSheet(Command):
    """
    This command is used to view a character's sheet. Staff can view any character's
    sheet, but players can only view their own.

    Usage:
        +sheet [<target>]

    See also: +stats, +splat
    """

    key = "+sheet"
    aliases = ["sheet"]
    locks = "cmd:all()"
    help_category = "Roleplaying"

    def show_bio(self, target):
        """
        This method shows the bio of a character.
        """
        # first print the header.
        output = ANSIString(
            "|Y[|n |wCharacter Sheet|n for: |c{}|n |Y]|n".format(
                target.get_display_name(self.caller)
            )
        ).center(78, ANSIString("|R=|n"))
        bio = []

        for item in BIO:
            traits = get_trait_list(item)

            if traits["check"] and not traits["check"](target.db.stats):
                continue

            # if the bio field passes the check, we add it to the list.
            try:
                val = target.db.stats[traits.get("category")][item].split(" ")
                val = " ".join([x.capitalize() for x in val])
                bio.append(
                    ANSIString(
                        format(key=item.capitalize(), val=val,
                               width=38, just="ljust")
                    )
                )
            except KeyError:
                bio.append(ANSIString(
                    format(item, "", width=38, just="ljust")))
            except AttributeError:
                val = target.db.stats[traits.get("category")][item]
                bio.append(ANSIString(
                    format(item, val, width=38, just="ljust")))

        # Noq peint the bio in two columns.
        count = 0
        for i in range(0, len(bio)):
            if count % 2 == 0:
                output += "\n "
            else:
                output += " "

            count += 1
            output += bio[i]

        self.caller.msg(output)

    def show_attributes(self, target):
        """
        This method shows the attributes of a character.
        """
        self.caller.msg(ANSIString("|w Attributes |n").center(
            78, ANSIString("|R=|n")))
        # first we need to build our three lists.
        mental = []
        physical = []
        social = []

        # Do they have a tempstat?
        try:
            if not target.db.stats["temp"]:
                target.db.stats["temp"] = {}
        except KeyError:
            target.db.stats["temp"] = {}

        # now we need to sort the attributes into their lists.
        # check if they have a temp value.  if so, record it.

        try:
            strength = target.db.stats["attributes"]["strength"]
            temp_strength = 0
            if target.db.stats["temp"].get("strength"):
                temp_strength = target.db.stats["temp"]["strength"] or 0
        except KeyError:
            strength = 0
            temp_strength = 0

        try:
            dexterity = target.db.stats["attributes"]["dexterity"]
            temp_dexterity = 0
            if target.db.stats["temp"].get("dexterity"):
                temp_dexterity = target.db.stats["temp"]["dexterity"] or 0
        except KeyError:
            dexterity = 0
            temp_dexterity = 0

        try:
            stamina = target.db.stats["attributes"]["stamina"]
            temp_stamina = 0
            if target.db.stats["temp"].get("stamina"):
                temp_stamina = target.db.stats["temp"]["stamina"] or 0
        except KeyError:
            stamina = 0
            temp_stamina = 0

        try:
            charisma = target.db.stats["attributes"]["charisma"]
            temp_charisma = 0
            if target.db.stats["temp"].get("charisma"):
                temp_charisma = target.db.stats["temp"]["charisma"] or 0
        except KeyError:
            charisma = 0
            temp_charisma = 0

        try:
            manipulation = target.db.stats["attributes"]["manipulation"]
            temp_manipulation = 0
            if target.db.stats["temp"].get("manipulation"):
                temp_manipulation = target.db.stats["temp"]["manipulation"] or 0
        except KeyError:
            manipulation = 0
            temp_manipulation = 0

        try:
            composure = target.db.stats["attributes"]["composure"]
            temp_composure = 0
            if target.db.stats["temp"].get("composure"):
                temp_composure = target.db.stats["temp"]["comppsure"] or 0
        except KeyError:
            composure = 0
            temp_composure = 0

        try:
            resolve = target.db.stats["attributes"]["resolve"]
            temp_resolve = 0
            if target.db.stats["temp"].get("resolve"):
                temp_resolve = target.db.stats["temp"]["resolve"] or 0
        except KeyError:
            resolve = 0
            temp_resolve = 0

        try:
            intelligence = target.db.stats["attributes"]["intelligence"]
            temp_intelliegence = 0
            if target.db.stats["temp"].get("intelliegence"):
                temp_intelliegence = target.db.stats["temp"]["intelliegence"] or 0
        except KeyError:
            intelligence = 0
            temp_intelliegence = 0

        try:
            wits = target.db.stats["attributes"]["wits"]
            temp_wits = 0
            if target.db.stats["temp"].get("wits"):
                temp_wits = target.db.stats["temp"]["wits"] or 0
        except KeyError:
            wits = 0
            temp_wits = 0

        # Now we need to format the output.
        mental.append(format("Intelligence", intelligence,
                      temp=temp_intelliegence))
        mental.append(format("Wits", wits, temp=temp_wits))
        mental.append(format("Resolve", resolve, temp=temp_resolve))

        physical.append(format("Strength", strength, temp=temp_strength))
        physical.append(format("Dexterity", dexterity, temp=temp_dexterity))
        physical.append(format("Stamina", stamina, temp=temp_stamina))

        social.append(format("Charisma", charisma, temp=temp_charisma))
        social.append(
            format("Manipulation", manipulation, temp=temp_manipulation))
        social.append(format("Composure", composure, temp=temp_composure))

        # Now we need to print the output.
        output = (
            "Physical".center(26) + "Mental".center(26) +
            "Social".center(26) + "\n"
        )
        for i in range(0, 3):
            output += " "
            output += physical[i]
            output += "  "
            output += mental[i]
            output += "  "
            output += social[i]
            output += "\n"

        self.caller.msg(output.rstrip())

    def show_skills(self, target):
        """
        This method shows the skills of a character.
        """
        self.caller.msg(ANSIString("|w Skills |n").center(
            78, ANSIString("|R=|n")))
        # first we need to build our three lists.
        mental = []
        physical = []
        social = []

        # now we need to sort the Skills into their lists.
        # We need to list all of the skills on the sheet.
        # We fill in the missing values on in the db with a zero.
        for key in SKILLS:
            try:
                value = target.db.stats["skills"][key]
            except KeyError:
                value = 0

            # If the key has any character specialties, we need to send them to the format fuction with special idnication
            # That it's a specialty.
            specialties = target.db.stats["specialties"].get(key)

            keys = [(PHYSICAL, physical), (MENTAL, mental), (SOCIAL, social)]
            for i in keys:
                if key in i[0]:
                    temp = target.db.stats["temp"].get(key) or 0

                    i[1].append(format(key, value, temp=temp))
                    if specialties:
                        for specialty in specialties:
                            i[1].append(
                                format(
                                    specialty,
                                    specialties.get(specialty),
                                    type="specialty",
                                )
                            )

        # now we need to print the three lists. if one list is shorter than the others, we need to pad it.
        # if the list is shorter than the others, we need to pad it.
        mental_length = len(mental)
        physical_length = len(physical)
        social_length = len(social)

        # now we need to determine which list is the longest.
        longest = max(mental_length, physical_length, social_length)

        # now we need to pad the lists.
        if mental_length < longest:
            for i in range(longest - mental_length):
                mental.append(" " * 24)
        if physical_length < longest:
            for i in range(longest - physical_length):
                physical.append(" " * 24)
        if social_length < longest:
            for i in range(longest - social_length):
                social.append(" " * 24)
        # now we need to print the lists.
        for i in range(longest):
            output = " " + physical[i]
            output += "  " + mental[i]
            output += "  " + social[i]

            self.caller.msg(output)

    def show_disciplines(self, target):
        """
        This method shows the disciplines of a character.
        """
        output = ANSIString("|w Disciplines |n").center(
            78, ANSIString("|R=|n"))

        # first we build our two list

        disciplines = []
        columns = []
        for key, value in target.db.stats["disciplines"].items():
            disciplines.append(format(key, value, width=24))
            specialties = target.db.stats["specialties"].get(key)

            if specialties:
                for specialty in specialties:
                    disciplines.append(
                        format(
                            specialty,
                            specialties.get(specialty),
                            type="specialty",
                            width=24,
                        )
                    )
            columns.append(disciplines)
            disciplines = []

        # for each column, get the longest entry and pad the rest of the entries to match.
        for column in columns:
            try:
                max_length = max(len(columns[0]), len(
                    columns[1]), len(columns[2]))
            except IndexError:
                try:
                    max_length = max(len(columns[0]), len(columns[1]))
                except IndexError:
                    max_length = len(columns[0])

            if len(column) < max_length:
                for i in range(max_length - len(column)):
                    column.append(" " * 24)

        # now we need to print the lists by row.  Two columns per row. if we have more than 2 columns, we need to print
        # the first two columns, then the next two columns, etc.
        # if we have an odd number of columns, we need to print the last column by itself.
        # if we have an even number of columns, we need to print the last two columns together.
        # if we have more than 4 columns, we need to print the first two columns, then the next two columns, etc.
        for i in range(0, len(columns), 3):
            for j in range(max_length):
                output += "\n "
                output += columns[i][j]
                if i + 1 < len(columns):
                    output += "  " + columns[i + 1][j]
                if i + 2 < len(columns):
                    output += "  " + columns[i + 2][j]

            if i + 3 < len(columns):
                output += "\n"

        if len(columns) > 0:
            self.caller.msg(output.strip())

    def show_advantages(self, target):
        """
        This method shows the advantages of a character.
        """
        output = ANSIString("|w Advantages |n").center(39, ANSIString("|R=|n"))
        output += ANSIString("|w Flaws |n").center(39, ANSIString("|R=|n"))

        # first we build our two lists.
        raw_advantages = target.db.stats["advantages"]
        raw_flaws = target.db.stats["flaws"]
        advantages = []
        flaws = []

        # fill in format entry for advanaages and flaws
        for key, value in raw_advantages.items():
            advantages.append(format(key, value, width=37))
        for key, value in raw_flaws.items():
            flaws.append(format(key, value, width=37))

        # get the max length and pad the end of the list with spaces
        max_length = max(len(raw_advantages), len(flaws))
        if len(raw_advantages) < max_length:
            for i in range(max_length - len(raw_advantages)):
                advantages.append(" " * 37)
        if len(raw_flaws) < max_length:
            for i in range(max_length - len(raw_flaws)):
                flaws.append(" " * 37)

        # now we need to print the lists.
        for i in range(max_length):
            output += "\n " + advantages[i] + "  " + flaws[i]
        if max_length > 0:
            self.caller.msg(output)

    def func(self):
        # check to see if caller
        tar = self.caller
        if self.lhs.lower() == "me" or not self.lhs:
            tar = self.caller
        else:
            tar = self.caller.search(self.args, global_search=True)

        try:
            # player has to ahve a splat set first!
            if not tar.db.stats["bio"].get("splat"):
                if self.caller == tar:
                    self.caller.msg(
                        "|wSTATS>|n |yYou must select a splat before you can view your sheet.|n"
                    )
                else:
                    self.caller.msg(
                        "|wSTATS>|n |yThey must select a splat before you can view their sheet.|n"
                    )
                return
        except TypeError:
            self.caller.msg("|wSTATS>|n Pwemission Denied.")
            return
        except AttributeError:
            self.caller.msg("|wSTATS>|n I can't find that player.")
            return

        # check if the target is the caller, or if the caller is admin.
        if self.caller != tar and not self.caller.locks.check_lockstring(
            self.caller, "perm(Admin)"
        ):
            self.caller.msg("|wCG>|n You can only view your own sheet.")
            return

        # show the sheet
        self.caller.msg(self.show_bio(tar))
        self.caller.msg(self.show_attributes(tar))
        self.caller.msg(self.show_skills(tar))
        self.caller.msg(self.show_advantages(tar))
        if tar.db.stats["bio"].get("splat") == "vampire":
            self.caller.msg(self.show_disciplines(tar))

        self.caller.msg(ANSIString(ANSIString("|R=|n") * 78))


class CmdDice(Command):
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
    help_category = "Roleplaying"

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

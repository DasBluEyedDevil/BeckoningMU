"""
This module contains the commands for character generation.

"""

from evennia.commands.default.muxcommand import MuxCommand
from world.data import BIO, get_trait_list, SPLATS, PHYSICAL, MENTAL, SOCIAL, SKILLS, STATS, DISCIPLINES, ADVANTAGES, FLAWS, POOLS
from evennia.utils.ansi import ANSIString
from .utils import target, format
from jobs.commands.commands import CmdJob


class cmdSplat(MuxCommand):
    """
    This is the command to set a sphere on a character. This must be
    done before any other chargen commands can be used.

    Usage:
        +splats to see a list of valid splats.
        +splat [<target>=]<splat> - Sets the splat of the character.

    see also: +sheet +stats

    """

    key = "+splat"
    aliases = ["splat", "+splats", "splats"]
    locks = "cmd:all()"
    help_category = "Character Generation"

    def func(self):
        if not self.caller.locks.check_lockstring(
            self.caller, "perm(Admin)"
        ) and not self.caller.location.tags.has("chargen"):
            self.caller.msg(
                "This command can only be used in Character Generation areas."
            )
            return

        target = self.caller
        splat = self.args.lower()

        # check for a target
        if self.rhs:
            target = self.caller.search(
                self.lhs, global_search=True)
            if not target:
                self.caller.msg("|wSPLAT>|n Could not find target.")
                return

            splat = self.rhs
            target.db.stats.splat = splat

        # if there are no args, list the splats available.
        if not self.args:
            self.caller.msg(
                "|wSPLAT>|n Valid splats are: |w{}|n".format(
                    ", ".join(map(lambda x: ANSIString(f"|w{x.capitalize()}|n"), SPLATS)))
            )
            return

        # Check if a player is already approved.
        if target.db.approved == True:
            self.caller.msg("|wSPLAT>|n You are already approved.")
            return

        # check for a valid splat
        if splat not in SPLATS:
            self.caller.msg("|wSPLAT>|n That is not a valid splat.")
            self.caller.msg("|wSPLAT>|n Valid splats are: |w{}|n".format(
                ", ".join(map(lambda x: ANSIString(f"|w{x.capitalize()}|n"), SPLATS)))
            )
            return

        # set the splat
        target.db.stats["splat"] = splat.lower()
        target.db.stats["bio"] = {"splat": splat.lower()}

        self.caller.msg(
            "|wSPLAT>|n |c{}'s|n splat has set to |w{}|n.".format(target.get_display_name(self.caller), target.db.stats["splat"].upper()))


class cmdCg(MuxCommand):
    """
    This command is used to create a character. it is the main 
    method of setting tour character's chargen settings.

    WARNING!!  Before you can use this command, you must set your 
    splat with +splat!

    Usage:
        +stat[/temp] [<target>/]<trait>=[<value>][/<specialty>]


        examples:
            +stat strength=3
            +stat  athletics=2/Running
            +stat/temp str=3

            +stat Diablerie/strength=3
            +stat Diablerie/athletics=2/Running

            To reset a stat, leave the value blank.  When you resete 
            a stat, you must also reset the specialties.

                +stat strength=

            To reset a specialty, leave the specialty blank.

                +stat athletics=/Running

        To reset your whole +sheet use |r+stats/wipe|n.

    See also:  +splat +sheet

    """

    key = "+stats"
    aliases = ["stat"]
    locks = "cmd:all()"
    help_category = "character Generation"

    def func(self):
        if not self.caller.locks.check_lockstring(self.caller, "perm(Admin)"):
            if not self.caller.location.tags.has("chargen"):
                self.caller.msg(
                    "This command can only be used in Character Generation areas."
                )
                return
            # Unapproved characters can use this command.
            if self.caller.db.stats["approved"] == True:
                self.caller.msg("You are already approved.")
                return
        try:
            # if the command was +stats/wipe me=confirm, then wipe the stats.
            if self.switches[0] == "wipe" and self.rhs == "confirm":
                self.caller.db.stats = STATS
                self.caller.msg("|wSTATS>|n Your stats have been wiped.")
                return

            # if the command was +stats/wipe. then comfirm they need to use +stats/wipe me=confirm
            if self.switches[0] == "wipe":
                self.caller.msg(
                    "|wSTATS>|n You are about to wipe your stats.  This cannot be undone.")
                self.caller.msg(
                    "|wSTATS>|n To confirm, use: |r+stats/wipe me=confirm|n")
                return
        except IndexError:
            pass

        if not self.args:
            self.caller.msg("|wSTATS>|n Usage: +stat <trait>=<value>")
            return

        if not self.rhs and "+" in self.lhs or "-" in self.lhs:
            # this is an add or subtract shortcut.  first we need to prep the + or -.
            args = self.lhs.replace(" + ", " +").replace(" - ", " -")
            self.lhs, self.rhs = args.split(" ", 1)
        ret = target(self)
        # check for a target
        tar = ret.get("target")
        key = ret.get("key")
        instance = ret.get("instance")
        value = ret.get("value")
        specialty = ret.get("specialty")

        # check if caller is target.  Only admins can set other people's stats.
        if self.caller != tar and not self.caller.locks.check_lockstring(self.caller, "perm(Admin)"):
            self.caller.msg("|wSTATS>|n You can only set your own stats.")
            return

        # check for a valid target
        if not tar.db.stats["splat"]:
            if tar == self.caller:
                self.caller.msg(
                    "|wSTATS>|n You must set your splat first.")
            else:
                self.caller.msg(
                    "|wSTATS>|n You must set |c%s's|n splat first." % tar.get_display_name(self.caller))
            return

        # check for a valid key
        traits = get_trait_list(key)
        try:
            key = traits.get("trait")
        except AttributeError:
            self.caller.msg("|wSTATS>|n That is not a valid trait.")
            return

        # check for good values
        try:
            if value and value[0] == "+" or value[0] == "-":
                try:
                    self.rhs = int(tar.db.stats[traits.get(
                        "category")][traits.get("trait")]) + int(value)
                    self.caller.msg(value)
                except ValueError:
                    self.caller.msg(
                        "|wSTATS>|n You must specify a number to add or subtract.")
                    return

            else:
                try:
                    self.rhs = int(self.rhs)
                except ValueError:
                    pass
                except TypeError:
                    pass
        except IndexError:
            pass

        # check to see if we pass the check
        if traits["check"]:

            if not traits["check"](tar.db.stats):
                self.caller.msg("|wSTATS>|n> " + traits["check_message"])
                return

        # check for instance
        if instance and traits.get("instanced"):
            key = "%s(%s)" % (key.capitalize(),
                              instance.capitalize().split("=")[0])

        elif instance and not traits.get("instanced"):
            self.caller.msg("|wSTATS>|n That trait does not have instances.")
            return

        elif not instance and traits.get("instanced"):
            self.caller.msg(
                "|wSTATS>|n You must specify an (instance) for |w%s()|n." % traits.get("trait").upper())
            return

        # if there are instances given and insance isn't oneo of them, then error.
        if traits.get("instances"):
            if instance and instance not in traits.get("instances"):
                self.caller.msg(
                    "|wSTATS>|n |w%s|n is not a valid instance for |w%s()|n." % (instance, traits.get("trait").upper()))
                self.caller.msg(
                    "|wSTATS>|n Valid instances are: |w%s|n." % ", ".join(traits.get("instances")))
                return

        # check for spwcialties [<value>][/<specialty>]
        # to set a specialty, you must set a value and have a value in the key trait first.
        if traits.get("has_specialties") and value and specialty:

            # check for a valid specialty or if no specialties exist, set the value
            if not len(traits["specialties"]):
                print(traits.get("category"))
                # set the  character's trait  if the trait exists
                if tar.db.stats[traits.get("category")].get(key):

                    # update the specialties dictionary entry for the specialty under the key.
                    try:
                        tar.db.stats["specialties"][key][specialty] = value
                    except KeyError:
                        tar.db.stats["specialties"][key] = {specialty: value}

                    self.caller.msg(
                        "|wSTATS>|n Specialty |w%s|n set on |c%s's|n |w%s|n." % (specialty, tar.name, key.upper()))

                    return

            # Else there are specalties defined.  Check for a valid specialty and value
            # check for a valid specialty
            if specialty not in traits["specialties"]:
                self.caller.msg(
                    "|wSTATS>|n That is not a valid specialty for |w%s|n." % key.upper())
                self.caller.msg("|wSTATS>|n Valid specialties are: |w%s|n" % ", ".join(
                    map(lambda x: ANSIString(f"|w{x}|n"), traits["specialties"].keys())))
                return

            try:
                value = int(value)
            except ValueError:
                pass

            # check for a valid value
            try:
                if value.lower() not in traits["specialties"][specialty]["values"]:
                    self.caller.msg(
                        "|wSTATS>|n That is not a valid value for |w%s|n." % (specialty.upper() or key.upper()))
                    self.caller.msg("|wSTATS>|n Valid values are: |w%s|n" % ", ".join(
                        map(lambda x: ANSIString(f"|w{x}|n"), traits["specialties"][specialty]["values"])))

                    return
                else:
                    print(tar.db.stats[traits.get("category")].get(key))
                    # set the  character's trait  if the trait exists
                    if tar.db.stats[traits.get("category")].get(key):
                        # update the specialties dictionary entry for the specialty under the key.
                        try:
                            tar.db.stats["specialties"][key][specialty] = value
                        except KeyError:
                            tar.db.stats["specialties"][key] = {
                                specialty: value}
                        except AttributeError:
                            tar.db.stats["specialties"] = {
                                key: {specialty: value}}

                        self.caller.msg(
                            "|wSTATS>|n Specialty |w%s|n set on |c%s's|n |w%s|n." % (specialty, tar.name, key.upper()))

                        return
            except AttributeError:
                if value not in traits["specialties"][specialty]["values"]:
                    self.caller.msg(
                        "|wSTATS>|n That is not a valid value for |w%s|n." % (specialty.upper() or key.upper()))
                    self.caller.msg("|wSTATS>|n Valid values are: |w%s|n" % ", ".join(
                        map(lambda x: ANSIString(f"|w{x}|n"), traits["specialties"][specialty]["values"])))

                    return
                else:
                    print(tar.db.stats[traits.get("category")].get(key))
                    # set the  character's trait  if the trait exists
                    if tar.db.stats[traits.get("category")].get(key):
                        # update the specialties dictionary entry for the specialty under the key.
                        try:
                            tar.db.stats["specialties"][key][specialty] = value
                        except KeyError:
                            tar.db.stats["specialties"][key] = {
                                specialty: value}
                        except AttributeError:
                            tar.db.stats["specialties"] = {
                                key: {specialty: value}}

                        self.caller.msg(
                            "|wSTATS>|n Specialty |w%s|n set on |c%s's|n |w%s|n." % (specialty, tar.name, key.upper()))

                        return
        # end specialties

        # check for a valid value
        # if no value is given then the trait should be rmeoved from the character
        # along with any specialties

        # if no value is given and a matching specialty for the key is found (case insenstiive)
        # then remove the specialty from the character.
        try:
            if not value and tar.db.stats["specialties"].get(key).get(specialty):
                del tar.db.stats["specialties"][key][specialty]
                self.caller.msg(
                    "|wSTATS>|n Specialty |w%s|n removed from |c%s's|n |w%s|n." % (specialty, tar.name, key.upper()))
                return
        except AttributeError:
            pass
        # if no value is given and no specialty is given, then remove the trait from the character.
        # if the trait has specialties, remove them as well.
        # if the trait is an attribute, then just reset it to 1.
        if not value and not specialty:

            if "temp" in self.switches:
                if tar.db.stats["temp"].get(key):
                    del tar.db.stats["temp"][key]
                self.caller.msg(
                    "|wSTATS>|n (temp) |w%s|n removed from |c%s's|n sheet." % (key.upper(), tar.name))
                return
            else:
                if tar.db.stats["specialties"].get(key):
                    del tar.db.stats["specialties"][key]
                if tar.db.stats[traits.get("category")].get(key):
                    if traits.get("category") == "attributes":
                        tar.db.stats[traits.get("category")][key] = 1
                    else:
                        del tar.db.stats[traits.get("category")][key]
                    # if there's a temp value remove it as well
                    if tar.db.stats["temp"].get(key):
                        del tar.db.stats["temp"][key]

                self.caller.msg(
                    "|wSTATS>|n |w%s|n removed from |c%s's|n sheet." % (key.upper(), tar.name))
                return

        try:
            self.lhs = int(self.lhs)
        except ValueError:
            self.lhs = self.lhs.lower()

        try:
            display_key = key.upper()
        except AttributeError:
            display_key = key

        # check for valid values
        if traits["values"] and self.rhs not in traits["values"]:
            self.caller.msg(
                "|wSTATS>|n That is not a valid value for |w%s|n." % display_key)
            self.caller.msg("|wSTATS>|n Valid values are: |w%s|n" % ", ".join(
                map(lambda x: ANSIString(f"|w{x}|n").capitalize(), traits["values"])))
            return

        # set the value
        if "temp" in self.switches:
            try:
                tar.db.stats["temp"][key] = int(self.rhs)
            except KeyError:
                tar.db.stats["temp"] = {}
                tar.db.stats["temp"][key] = int(self.rhs)

            except ValueError:
                tar.db.stats["temp"][key] = self.rhs

            self.caller.msg("|wSTATS>|n |c%s's|n (temp) |w%s|n set to|w %s|n." % (
                tar.name, display_key, self.rhs))
            return
        else:
            try:
                tar.db.stats[traits.get("category")][key] = self.rhs.lower()
                display = self.rhs.upper()
            except AttributeError:
                tar.db.stats[traits.get("category")][key] = self.rhs
                display = self.rhs

            self.caller.msg("|wSTATS>|n |c%s's|n  |w%s|n set to|w %s|n." %
                            (tar.get_display_name(self.caller), display_key, display))


class cmdSheet(MuxCommand):
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
    help_category = "Character Generation"

    def show_bio(self, target):
        """
        This method shows the bio of a character.
        """
        # first print the header.
        output = ANSIString(
            "|Y[|n |wCharacter Sheet|n for: |c{}|n |Y]|n".format(target.get_display_name(self.caller))).center(78, ANSIString("|R=|n"))
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
                    ANSIString(format(key=item.capitalize(), val=val, width=38, just="ljust")))
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
        output = "Physical".center(
            26) + "Mental".center(26) + "Social".center(26) + "\n"
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
                                format(specialty, specialties.get(specialty), type="specialty"))

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
                        format(specialty, specialties.get(specialty), type="specialty", width=24))
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

            if (i + 3 < len(columns)):
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
                        "|wSTATS>|n |yYou must select a splat before you can view your sheet.|n")
                else:
                    self.caller.msg(
                        "|wSTATS>|n |yThey must select a splat before you can view their sheet.|n")
                return
        except TypeError:
            self.caller.msg(
                "|wSTATS>|n Pwemission Denied.")
            return
        except AttributeError:
            self.caller.msg(
                "|wSTATS>|n I can't find that player.")
            return

        # check if the target is the caller, or if the caller is admin.
        if self.caller != tar and not self.caller.locks.check_lockstring(self.caller, "perm(Admin)"):
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


class cmdSubmit(MuxCommand):
    """
    Submit a charaxter applixation!

    Usage:
      submit
    """

    key = "submit"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        """Submit the application"""
        caller = self.caller
        if not caller.location.tags.has("chargen"):
            caller.msg("This command can only be used in Character Generation areas.")
            return
        args = self.args

        if caller.db.submitted:
            caller.msg("|wSTATS>|n You have already submitted an application.")
            return

        if caller.db.stats["approved"]:
            caller.msg("|wSTATS>|n You have already been approved.")
            return

        description = "%s has submitted an application." % caller.name

        CmdJob.create_job(self, bucket_title="CGEN", title="Character Generation",
                          description=description, created_by=caller)
        self.caller.msg("|wSTATS>|n Application submitted.")
        caller.db.submitted = True


class CmdApprove(MuxCommand):
    """
    Approve a character application!

    Usage:
      approve <character>
    """

    key = "approve"
    locks = "cmd:perm(Builder)"
    help_category = "General"

    def func(self):
        """Submit the application"""
        caller = self.caller
        args = self.args

        if not args:
            caller.msg("|wAPPROVE>|n You must specify a character to approve.")
            return

        char = caller.search(args)

        if not char:
            caller.msg("|wAPPROVE>|n Character not found.")
            return

        if char.db.stats["approved"]:
            caller.msg("|wAPPROVE>|n Character already approved.")
            return

        char.db.stats["approved"] = True
        char.db.stats["approved_by"] = caller.name

        caller.msg("|wAPPROVE>|n Character approved.")

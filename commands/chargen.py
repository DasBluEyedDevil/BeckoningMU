"""
This module contains the commands for character generation.

"""

from evennia.commands.cmdset import CmdSet
from world.data import (
    get_trait_list,
    SPLATS,
    STATS,
)
from evennia.utils.ansi import ANSIString
from .utils import target
from jobs.commands.commands import CmdJob
from .command import Command


class ChargenCmdSet(CmdSet):
    key = "Chargen"

    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        self.add(CmdSplat())
        self.add(CmdStat())
        self.add(CmdSubmit())
        self.add(CmdApprove())


class CmdSplat(Command):
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
    help_category = "character"

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
            target = self.caller.search(self.lhs, global_search=True)
            if not target:
                self.caller.msg("|wSPLAT>|n Could not find target.")
                return

            splat = self.rhs
            target.db.stats.splat = splat

        # if there are no args, list the splats available.
        if not self.args:
            self.caller.msg(
                "|wSPLAT>|n Valid splats are: |w{}|n".format(
                    ", ".join(
                        map(lambda x: ANSIString(
                            f"|w{x.capitalize()}|n"), SPLATS)
                    )
                )
            )
            return

        # Check if a player is already approved.
        if target.db.approved == True:
            self.caller.msg("|wSPLAT>|n You are already approved.")
            return

        # check for a valid splat
        if splat not in SPLATS:
            self.caller.msg("|wSPLAT>|n That is not a valid splat.")
            self.caller.msg(
                "|wSPLAT>|n Valid splats are: |w{}|n".format(
                    ", ".join(
                        map(lambda x: ANSIString(
                            f"|w{x.capitalize()}|n"), SPLATS)
                    )
                )
            )
            return

        # set the splat
        target.db.stats["splat"] = splat.lower()
        target.db.stats["bio"] = {"splat": splat.lower()}

        self.caller.msg(
            "|wSPLAT>|n |c{}'s|n splat has set to |w{}|n.".format(
                target.get_display_name(
                    self.caller), target.db.stats["splat"].upper()
            )
        )


class CmdStat(Command):
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
    help_category = "character"

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
                    "|wSTATS>|n You are about to wipe your stats.  This cannot be undone."
                )
                self.caller.msg(
                    "|wSTATS>|n To confirm, use: |r+stats/wipe me=confirm|n"
                )
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
        if self.caller != tar and not self.caller.locks.check_lockstring(
            self.caller, "perm(Admin)"
        ):
            self.caller.msg("|wSTATS>|n You can only set your own stats.")
            return

        # check for a valid target
        if not tar.db.stats["splat"]:
            if tar == self.caller:
                self.caller.msg("|wSTATS>|n You must set your splat first.")
            else:
                self.caller.msg(
                    "|wSTATS>|n You must set |c%s's|n splat first."
                    % tar.get_display_name(self.caller)
                )
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
                    self.rhs = int(
                        tar.db.stats[traits.get(
                            "category")][traits.get("trait")]
                    ) + int(value)
                    self.caller.msg(value)
                except ValueError:
                    self.caller.msg(
                        "|wSTATS>|n You must specify a number to add or subtract."
                    )
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
                "|wSTATS>|n You must specify an (instance) for |w%s()|n."
                % traits.get("trait").upper()
            )
            return

        # if there are instances given and insance isn't oneo of them, then error.
        if traits.get("instances"):
            if instance and instance not in traits.get("instances"):
                self.caller.msg(
                    "|wSTATS>|n |w%s|n is not a valid instance for |w%s()|n."
                    % (instance, traits.get("trait").upper())
                )
                self.caller.msg(
                    "|wSTATS>|n Valid instances are: |w%s|n."
                    % ", ".join(traits.get("instances"))
                )
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
                        "|wSTATS>|n Specialty |w%s|n set on |c%s's|n |w%s|n."
                        % (specialty, tar.name, key.upper())
                    )

                    return

            # Else there are specalties defined.  Check for a valid specialty and value
            # check for a valid specialty
            if specialty not in traits["specialties"]:
                self.caller.msg(
                    "|wSTATS>|n That is not a valid specialty for |w%s|n." % key.upper()
                )
                self.caller.msg(
                    "|wSTATS>|n Valid specialties are: |w%s|n"
                    % ", ".join(
                        map(
                            lambda x: ANSIString(f"|w{x}|n"),
                            traits["specialties"].keys(),
                        )
                    )
                )
                return

            try:
                value = int(value)
            except ValueError:
                pass

            # check for a valid value
            try:
                if value.lower() not in traits["specialties"][specialty]["values"]:
                    self.caller.msg(
                        "|wSTATS>|n That is not a valid value for |w%s|n."
                        % (specialty.upper() or key.upper())
                    )
                    self.caller.msg(
                        "|wSTATS>|n Valid values are: |w%s|n"
                        % ", ".join(
                            map(
                                lambda x: ANSIString(f"|w{x}|n"),
                                traits["specialties"][specialty]["values"],
                            )
                        )
                    )

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
                            "|wSTATS>|n Specialty |w%s|n set on |c%s's|n |w%s|n."
                            % (specialty, tar.name, key.upper())
                        )

                        return
            except AttributeError:
                if value not in traits["specialties"][specialty]["values"]:
                    self.caller.msg(
                        "|wSTATS>|n That is not a valid value for |w%s|n."
                        % (specialty.upper() or key.upper())
                    )
                    self.caller.msg(
                        "|wSTATS>|n Valid values are: |w%s|n"
                        % ", ".join(
                            map(
                                lambda x: ANSIString(f"|w{x}|n"),
                                traits["specialties"][specialty]["values"],
                            )
                        )
                    )

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
                            "|wSTATS>|n Specialty |w%s|n set on |c%s's|n |w%s|n."
                            % (specialty, tar.name, key.upper())
                        )

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
                    "|wSTATS>|n Specialty |w%s|n removed from |c%s's|n |w%s|n."
                    % (specialty, tar.name, key.upper())
                )
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
                    "|wSTATS>|n (temp) |w%s|n removed from |c%s's|n sheet."
                    % (key.upper(), tar.name)
                )
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
                    "|wSTATS>|n |w%s|n removed from |c%s's|n sheet."
                    % (key.upper(), tar.name)
                )
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
                "|wSTATS>|n That is not a valid value for |w%s|n." % display_key
            )
            self.caller.msg(
                "|wSTATS>|n Valid values are: |w%s|n"
                % ", ".join(
                    map(lambda x: ANSIString(
                        f"|w{x}|n").capitalize(), traits["values"])
                )
            )
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

            self.caller.msg(
                "|wSTATS>|n |c%s's|n (temp) |w%s|n set to|w %s|n."
                % (tar.name, display_key, self.rhs)
            )
            return
        else:
            try:
                tar.db.stats[traits.get("category")][key] = self.rhs.lower()
                display = self.rhs.upper()
            except AttributeError:
                tar.db.stats[traits.get("category")][key] = self.rhs
                display = self.rhs

            self.caller.msg(
                "|wSTATS>|n |c%s's|n  |w%s|n set to|w %s|n."
                % (tar.get_display_name(self.caller), display_key, display)
            )


class CmdSubmit(Command):
    """
    Submit a character application!

    Usage:
      submit
    """

    key = "submit"
    locks = "cmd:all()"
    help_category = "character"

    def func(self):
        """Submit the application"""
        caller = self.caller
        if not caller.locks.check_lockstring(
            caller, "perm(Admin)"
        ) and not caller.location.tags.has("chargen"):
            caller.msg(
                "This command can only be used in Character Generation areas.")
            return
        args = self.args

        if caller.db.submitted:
            caller.msg("|wSTATS>|n You have already submitted an application.")
            return

        if caller.db.stats["approved"]:
            caller.msg("|wSTATS>|n You have already been approved.")
            return

        description = "%s has submitted an application." % caller.name

        CmdJob.create_job(
            self,
            bucket_title="CGEN",
            title="Character Generation",
            description=description,
            created_by=caller,
        )
        self.caller.msg("|wSTATS>|n Application submitted.")
        caller.db.submitted = True


class CmdSubmit(Command):
    """
    Submit a character application!

    Usage:
      submit
    """

    key = "submit"
    locks = "cmd:all()"
    help_category = "character"

    def func(self):
        """Submit the application"""
        caller = self.caller
        if not caller.location.tags.has("chargen"):
            caller.msg(
                "This command can only be used in Character Generation areas.")
            return

        if caller.db.submitted:
            caller.msg("|wSTATS>|n You have already submitted an application.")
            return

        if caller.db.stats["approved"]:
            caller.msg("|wSTATS>|n You have already been approved.")
            return

        description = "%s has submitted an application." % caller.name

        CmdJob.create_job(
            self,
            bucket_title="CGEN",
            title="Character Generation",
            description=description,
            created_by=caller,
        )
        self.caller.msg("|wSTATS>|n Application submitted.")
        caller.db.submitted = True


class CmdApprove(Command):
    """
    Approve a character application!

    Usage:
      approve <character>
    """

    key = "approve"
    locks = "cmd:perm(Builder)"
    help_category = "character"

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

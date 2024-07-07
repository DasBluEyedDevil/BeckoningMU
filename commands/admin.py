from evennia.commands.cmdset import CmdSet
import evennia.commands.default as default_cmds
from evennia.utils import logger
from evennia.utils.ansi import ANSIString
from evennia.utils.search import object_search
from .command import Command

HELP_CATEGORY = "admin"

class AdminCmdSet(CmdSet):
    """
    Commands for game administrators.

    This CmdSet is for Character-level commands, for Account-level commands
    use AdminAccountCmdSet
    """
    key = "Admin"

    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        self.add(CmdEmit())

class AdminAccountCmdSet(CmdSet):
    """
    Commands for game administrators.

    This CmdSet is for Account-level commands, for Character-level commands
    use AccountCmdSet
    """
    key = "AdminAccount"

    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        self.add(CmdPuppet())
        self.add(CmdUnpuppet())

class CmdEmit(Command):
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
    help_category = HELP_CATEGORY

    def func(self):

        if not self.args:
            string = "Usage: "
            string += "\nemit[/switches] [<obj>, <obj>, ... =] <message>"
            string += "\nremit           [<obj>, <obj>, ... =] <message>"
            string += "\npemit           [<obj>, <obj>, ... =] <message>"
            self.msg(string)
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
            if not self.character:
                self.msg("No objects specified.")
                return
            message = self.args
            objnames = [self.character.location.key]
        else:
            message = self.rhs
            objnames = self.lhslist

        # send to all objects
        for objname in objnames:
            obj = self.caller.search(objname, global_search=True)
            if not obj:
                return
            if rooms_only and obj.location is not None:
                self.msg(ANSIString(f"{objname} is not a room. Ignored."))
                continue
            if accounts_only and not obj.has_account:
                self.msg(f"{objname} has no active account. Ignored.")
                continue
            if obj.access(self.caller, "tell"):
                obj.msg(ANSIString(message))
                if send_to_contents and hasattr(obj, "msg_contents"):
                    obj.msg_contents(ANSIString(message))
            else:
                self.msg(f"You are not allowed to emit to {objname}.")


class CmdPuppet(Command):
    """
    control an object you have permission to puppet

    Usage:
      puppet <character>

    Go in-character (IC) as a given Character.

    This will attempt to "become" a different object assuming you have
    the right to do so. Note that it's the ACCOUNT character that puppets
    characters/objects and which needs to have the correct permission!

    You cannot become an object that is already controlled by another
    account. In principle <character> can be any in-game object as long
    as you the account have access right to puppet it.
    """
    key = "puppet"
    help_category = HELP_CATEGORY
    # lock must be all() for different puppeted objects to access it.
    locks = "cmd:perm(puppet) or cmd:pperm(Builder)"
    # this is used by the account
    account_caller = True

    def func(self):
        account = self.account
        session = self.session

        new_character = None
        character_candidates = []

        if not self.args:
            character_candidates = [account.db._last_puppet] if account.db._last_puppet else []
            if not character_candidates:
                self.msg("Usage: puppet <character>")
                return
        else:
            if session.puppet:
                # start by local search - this helps to avoid the user
                # getting locked into their playable characters should one
                # happen to be named the same as another. We replace the suggestion
                # from playable_characters here - this allows builders to puppet objects
                # with the same name as their playable chars should it be necessary
                # (by going to the same location).
                character_candidates = [
                    char
                    for char in session.puppet.search(self.args, quiet=True)
                    if char.access(account, "puppet")
                ]
            if not character_candidates:
                # fall back to global search only if Builder+ has no
                # playable_characters in list and is not standing in a room
                # with a matching char.
                character_candidates.extend(
                    [
                        char
                        for char in object_search(self.args)
                        if char.access(account, "puppet")
                    ]
                )

        # handle possible candidates
        if not character_candidates:
            self.msg("That is not a valid character choice.")
            return
        if len(character_candidates) > 1:
            self.msg(
                "Multiple targets with the same name:\n %s"
                % ", ".join("%s(#%s)" % (obj.key, obj.id) for obj in character_candidates)
            )
            return
        else:
            new_character = character_candidates[0]

        # do the puppet puppet
        try:
            account.puppet_object(session, new_character)
            account.db._last_puppet = new_character
            logger.log_sec(
                f"Puppet Success: (Caller: {account}, Target: {new_character}, IP:"
                f" {self.session.address})."
            )
        except RuntimeError as exc:
            self.msg(f"|rYou cannot become |C{new_character.name}|n: {exc}")
            logger.log_sec(
                f"Puppet Failed: %s (Caller: {account}, Target: {new_character}, IP:"
                f" {self.session.address})."
            )

# Unpuppet has the same logic as Evennia default "ooc" command
class CmdUnpuppet(default_cmds.account.CmdOOC):
    """
    Stop puppeting an object

    Usage:
      unpuppet

    This will leave your current character/object and put you in a incorporeal OOC state.
    """
    key = "unpuppet"
    aliases = []
    help_category = HELP_CATEGORY
    locks = "cmd:perm(puppet) or cmd:pperm(Builder)"
    # this is used by the account
    account_caller = True

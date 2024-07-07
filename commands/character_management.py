import random
from evennia.commands.cmdset import CmdSet
from evennia import utils
from evennia.utils import logger
from evennia.utils.ansi import ANSIString
from .command import Command
from jobs.commands.commands import CmdJob


class CharacterManagementCmdSet(CmdSet):
    key = "CharacterManagement"

    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        # use default IC command and move to "character" help category
        self.add(CmdIC())
        self.add(CmdOOC())


class CmdIC(Command):
    """
    Go in-character (IC) as a given character.

    Usage:
      ic <character>

    Use the "character list" (or "characters") command to see a list of
    your playable characters.
    """
    key = "ic"
    help_category = "character"
    # lock must be all() for different puppeted objects to access it.
    locks = "cmd:all()"
    # this is used by the parent
    account_caller = True

    def func(self):
        account = self.account
        session = self.session

        new_character = None
        character_candidates = []

        if not self.args:
            character_candidates = [account.db._last_ic] if account.db._last_ic else []
            if not character_candidates:
                self.msg("Usage: ic <character>")
                return
        else:
            # argument given

            if playables := filter(lambda char: not char.tags.has("ooc"), account.characters):
                # look at the playable_characters list first
                character_candidates.extend(
                    utils.make_iter(
                        account.search(
                            self.args,
                            candidates=playables,
                            search_object=True,
                            quiet=True,
                        )
                    )
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
            account.db._last_ic = new_character
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


class CmdOOC(Command):
    """
    Go out-of-character (OOC) and return to your OOC avatar

    Usage:
      ooc

    This will leave your current character and return you to your avatar in the OOC hub world
    """

    key = "ooc"
    locks = "cmd:pperm(Player)"
    help_category = "character"

    # this is used by the parent
    account_caller = True

    def func(self):

        account = self.account
        session = self.session

        if not account.db.ooc_avatar:
            self.msg(
                "Your account does not have an OOC Avatar for some reason. Contact an admin for help.")
            return

        old_char = account.get_puppet(session)
        if not old_char or old_char.tags.has("ooc"):
            self.msg("You are already OOC.")
            return
        new_char = account.db.ooc_avatar

        # puppet avatar
        try:
            account.puppet_object(session, new_char)
            account.db._last_puppet = new_char
            logger.log_sec(
                f"Puppet Success: (Caller: {account}, Target: {new_char}, IP:"
                f" {self.session.address})."
            )
        except RuntimeError as exc:
            self.msg(f"|rYou cannot become |C{new_char}|n: {exc}")
            logger.log_sec(
                f"Puppet Failed: %s (Caller: {account}, Target: {new_char}, IP:"
                f" {self.session.address})."
            )


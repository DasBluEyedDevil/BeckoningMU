from evennia.commands.cmdset import CmdSet
from evennia import utils
from evennia.utils import logger
from .command import Command
from django.conf import settings

HELP_CATEGORY = "character"


class CharacterManagementCmdSet(CmdSet):
    """
    Commands for management and creation of Player Characters.

    These are Account-level commands because they are intended to be
    useable regardless of whether the player is puppeting a Character or not.
    This is helpful, for example, if a player somehow gets stuck outside
    of a Character for some reason.

    """
    key = "CharacterManagement"

    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        # use default IC command and move to "character" help category
        self.add(CmdIC())
        self.add(CmdOOC())
        self.add(CmdCharacterList())
        self.add(CmdCharacterCreate())
        self.add(CmdCharacterDelete())


class CmdIC(Command):
    """
    Go in-character (IC) as a given character.

    Usage:
      ic
      ic <character>

    Use the "character list" (or "characters") command to see a list of
    your playable characters.

    If no character name is given, you will take control of the last
    character you played as.
    """
    key = "ic"
    help_category = HELP_CATEGORY
    # lock must be all() for different puppeted objects to access it.
    locks = "cmd:all()"

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
    locks = "cmd:all()"
    help_category = HELP_CATEGORY

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


class CmdCharacterList(Command):
    """
    """

    key = "character list"
    aliases = ("character", "characters", "char", "chars", "char list", "charlist")
    locks = "cmd:all()"
    help_category = HELP_CATEGORY

    def func(self):

        # multiple targets - this is a list of characters
        characters = [char for char in self.account.characters if not char.tags.has("ooc")] 

        num_chars = len(characters)

        if not characters:
            self.msg("You don't have a character yet. Use |w|lc help character create|lt character create|le|n.")
            return

        max_chars = (
            "unlimited"
            if settings.MAX_NR_CHARACTERS is None
            else settings.MAX_NR_CHARACTERS
        )

        sessions = self.account.sessions.all()

        char_strings = []
        for char in characters:
            char_sessions = char.sessions.all()
            if char_sessions:
                for sess in char_sessions:
                    # character is already puppeted
                    if sess in sessions:
                        ip_addr = sess.address[0] if isinstance(sess.address, tuple) else sess.address
                        addr = f"{sess.protocol_key} ({ip_addr})"
                        char_strings.append(
                            f" - |G{char.name}|n - " 
                            f"played by you in session {sess.id} ({addr})"
                        )
                    else:
                        char_strings.append(
                            f" - |R{char.name}|n"
                            "(played by someone else)"
                        )
            else:
                # character is "free to puppet"
                char_strings.append(f" - {char.name}")

        self.msg(
            f"Available character(s) ({num_chars}/{max_chars}, |lc help ic |lt |wic <name>|n|le to play):|n\n"
            + "\n".join(char_strings)
        )


class CmdCharacterCreate(Command):
    """
    """

    key = "character create"
    aliases = ("char create", "charcreate")
    locks = "cmd:pperm(Player)"
    help_category = HELP_CATEGORY

    character_typeclass = "typeclasses.characters.Character"

    def func(self):
        if not self.args:
            self.msg("Usage: charcter create <charname> [= description]")
            return
        key = self.lhs
        description = self.rhs or "Use |lc help desc |lt |wdesc|n |le to set a description." 

        new_character, errors = self.account.create_character(
            key=key,
            description=description,
            ip=self.session.address,
            typeclass=self.character_typeclass,
        )

        if errors:
            self.msg("\n".join(errors))
        if not new_character:
            return

        self.msg(
            f"Created new character {new_character.key}.\nUse |lc ic {new_character.key}|lt |wic {new_character.key}|n |le to play"
            " as this character."
        )


class CmdCharacterDelete(Command):
    """
    delete a character - this cannot be undone!

    Usage:
        character delete <charname>

    Permanently deletes one of your characters.
    """

    key = "character delete"
    aliases = ("character del", "char delete", "char del", "chardelete", "chardel")
    locks = "cmd:pperm(Player)"
    help_category = HELP_CATEGORY

    def func(self):
        if not self.args:
            self.msg("Usage: charcter delete <charname>")
            return

        account = self.account

        # use the playable_characters list to search
        match = [
            char
            for char in utils.make_iter(account.characters)
            if char.key.lower() == self.args.lower() and not char.tags.has("ooc")
        ]
        if not match:
            self.msg("You have no such character to delete.")
            return
        elif len(match) > 1:
            self.msg(
                "Aborting - there are two characters with the same name. Ask an admin to delete the"
                " right one."
            )
            return
        else:  # one match
            from evennia.utils.evmenu import get_input

            def _callback(caller, callback_prompt, result):
                if result.lower() == "yes":
                    # only take action
                    delobj = caller.ndb._char_to_delete
                    key = delobj.key
                    caller.characters.remove(delobj)
                    delobj.delete()
                    self.msg(f"Character '{key}' was permanently deleted.")
                    logger.log_sec(
                        f"Character Deleted: {key} (Caller: {account}, IP: {self.session.address})."
                    )
                else:
                    self.msg("Deletion was aborted.")
                del caller.ndb._char_to_delete

            match = match[0]
            account.ndb._char_to_delete = match

            # Return if caller has no permission to delete this
            if not match.access(account, "delete"):
                self.msg("You do not have permission to delete this character.")
                return

            prompt = f"|rThis will permanently destroy '{match.key}'. This cannot be undone.|n Continue yes/[no]?"
            get_input(account, prompt, _callback)

from evennia.commands.cmdset import CmdSet
from datetime import datetime
from evennia.utils.ansi import ANSIString
from .command import Command

class NotesCmdSet(CmdSet):
    key = "Notes"

    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        self.add(CmdNotes())
        self.add(CmdNoteProve())
        self.add(CmdNoteApprove())

class CmdNotes(Command):
    """
 READ NOTES
   +notes                      - see all your notes
   +note <note name or number> - see your note
   +note/<category>            - see all your notes in a category

   +note <target>/*            - see all visible notes on someone else
   +note <target>/<note>       - see a note on someone else
   +note/<category> <target>/* - see all notes on someone else in a category

 MAKE NOTES
   +note <name>=<text>            - make a note called <name>
   +note/<category> <name>=<text> - make a note in a specific category

 EDIT NOTES
   +note <note>=<new text>     - change the text on a note, removes approval
   +notemove <note>=<category> - move a note to a new category, keeps approval
   +note/<category> <note>=<new text> - change the text of a note into
                                        a new category, removes approval
   +notestatus <note>=PRIVATE|PUBLIC  - make a note in-/visible to others

 SHOW NOTES
   +noteprove <note>=<target(s)> - show any note to a list of targets
                                 - (names or dbrefs separated by commas)
  """

    key = "+notes"
    aliases = ["+notes", "notes", "+note", "note", "+n", "n"]
    locks = "cmd:all()"
    help_category = "notes"

    def get_target(self, target):
        """
        Gets the target object from the name.
        """
        tar = self.caller.search(target, global_search=True)

        # if no target is found check for me and here.
        if not tar:
            if target.lower() == "me":
                tar = self.caller
            elif target.lower() == "here":
                tar = self.caller.location
            else:
                return None
        else:
            return tar

    def func(self):

        # make sure the caller has a notes attribute.
        try:
            self.caller.db.notes
        except AttributeError:
            self.caller.db.notes = {}

        # if there's an = in the name, it's editing a note somehow.
        if "=" in self.args:
            self.edit_note()
            return
        else:
            # if there's no equala, it's a read command.
            self.read_note()
            return

    def edit_note(self):
        try:
            category = self.switches[0]
        except IndexError:
            category = "general"

        name = self.lhs.lower()
        note = self.rhs

        # if there is no note, then it's clearing the note from the system.
        if not note:
            self.caller.db.notes = filter(lambda x: x["title"] != name, self.caller.db.notes)
            self.caller.msg("|wNOTES>|n Note |w%s|n cleared." % name.upper())
            return
        
        # does the note already exist?  If so, edit it.
        for n in self.caller.db.notes:
            if n["title"] == name:
                n["text"] = note
                n["approved"] = False
                n["approved_by"] = None
                self.caller.msg("|wNOTES>|n Note |w%s|n edited." % name.upper())
                return    
        
        # if the note doesn't exist, create it.
        self.caller.db.notes.append({
            "title": name,
            "category": category,
            "text": note,
            "date": datetime.now(),
            "private": True,
            "approved": False,
            "approved_by": None
        })

        self.caller.msg("|wNOTES>|n Note |w%s|n saved." % name.upper())
        return

    def read_note(self):
        """
        Reads a note or list of notes.

        notes[/category] [target/][<title> or *]
        """    
        # Check for a category switch.
        if self.switches and self.switches[0] in self.caller.db.notes:
            category = self.switches[0]
        else:
            category = "general"

        # Check for a target.
        try:
            tar, title  = self.args.split("/")
        except ValueError:
            title = self.args
            tar = self.caller
        tar = self.get_target(tar)

        # If there's no title, then it's a list of notes.
        if not title:
            self.list_notes(category, tar)
            return
        
        # if there's a title, then it's a single note.
        self.single_note(title, tar)

    def list_notes(self, category, tar):
        """
        Lists all the notes in a category.
        """

        # Note list example
        #  #0   This is the title of the note
        #       This is the text of the note if it's too long then...
        #
        #  #1   This is the title of the note
        #       This is the text of the note if it's too long then...

        if category == "general":
            # show all notes.
            try:
                notes = tar.db.notes
            except AttributeError:
                self.caller.msg("|wNOTES>|n No notes found.")
                return
        else:
            # show notes in a category.
            notes = filter(lambda x: x["category"] == category, self.caller.db.notes)
        
        # if there are no notes, say so.
        if not notes:
            self.caller.msg("|wNOTES>|n No notes found.")
            return   

        # get all of the categories
        categories = sorted(set([x["category"] for x in tar.db.notes]))       

        # if there are notes, show them.
        output = ANSIString("|Y[|n Notes for %s |Y]|n" % tar.get_display_name(self.caller)).center(78, ANSIString("|R=|n")) + "\n"
        for category in categories:
            output += ANSIString(" %s " % category.upper()).center(78, ANSIString("|R-|n")) + "\n"
            # filter notes by category
            filter_notes = filter(lambda x: x["category"] == category, tar.db.notes)
            # filter out private notes if looker isn't the target or an admin.
            if tar != self.caller and not self.caller.check_permstring("Immortals"):
                filter_notes = filter(lambda x: x["private"] == False, filter_notes)

            for note in filter_notes:
                if note["category"] == category:
                    output += ANSIString(" %s #%-3s |c%-60s|n" % ( "*" if note["approved"] == True else " ",  notes.index(note), note["title"])) + "\n"
                    # If it's over 72 charaters, end with ...
                    if len(note["text"]) > 65:
                        output += ANSIString("        %s..." % note["text"][:65]) + "\n"
                    else:
                        output += ANSIString("        %s" % note["text"]) + "\n"
        output += ANSIString("|R==|Y[|n * - Approved Note |Y]|n").ljust(78, ANSIString("|R=|n")) + "\n"
        self.caller.msg(output)
        return    
    def single_note(self, title, tar):
        """
        Shows a single note.
        """
        # get the note.  If the title is a #<number> or number, then it's the index of the note.
        # else it's the title.
        try:
            note = tar.db.notes[int(title)]
        except (ValueError, IndexError):
            try:
                notes = filter(lambda x: x["title"] == title, tar.db.notes)
                note = next(notes)
            except (IndexError, TypeError, StopIteration):
                self.caller.msg("|wNOTES>|n No note found.")
                return
        except AttributeError:
            self.caller.msg("|wNOTES>|n No note found.")
            return
        
        # if the note is private and the caller isn't the target or an admin, say so.
        if note["private"] == True and tar != self.caller and not self.caller.check_permstring("Immortals"):
            self.caller.msg("|wNOTES>|n No note found.")
            return

        # if the note is private and the caller is the target or an admin or the note isn't private continue
        if note["private"] == True and (tar == self.caller or self.caller.check_permstring("Immortals")) or note["private"] == False:
            output = ANSIString("|Y[|n Note #%s |Y]|n" % tar.db.notes.index(note)).center(78, ANSIString("|R=|n")) + "\n"
            output += ANSIString(" Note Title:  |c%s|n" % note["title"]) + "\n"
            output += ANSIString(" Private:     |w%s|n" % ("Yes" if note["private"] == True else "No")) + "\n"
            output += ANSIString(" Category:    |w%s|n" % note["category"]) + "\n"
            output += ANSIString(" Approved by: |w%s|n - %s" % (note["approved_by"].get_display_name(self.caller) if note["approved_by"] else "None", note["date"])) + "\n"
            output += ANSIString("|R-|n" * 78) + "\n"
            output += ANSIString(note["text"]) + "\n"
            output += ANSIString("|R=|n" * 78) + "\n"
            self.caller.msg(output)
            return

class CmdNoteApprove(Command):
    """
    Approves a note.

    Usage:
        note/approve [<target>/]note

    Approves a note.  If no target is specified, then it's assumed that the target is the caller.
    """
    key = "note/approve"
    locks = "cmd:perm(Immortals)"
    help_category = "Notes"

    def func(self):
        """
        Approves a note.
        """
        try:
            tar, note = self.args.split("/")
            tar = self.caller.search(tar, global_search=True)
        except ValueError:
            tar = self.caller
            note = self.args

        try:
            note = tar.db.notes[int(note)]
        except (ValueError, IndexError):
            try:
                notes = filter(lambda x: x["title"] == note, tar.db.notes)
                note = next(notes)
            except IndexError:
                self.caller.msg("|wNOTES>|n No note found.")
                return

        note["approved"] = True
        note["date"] = datetime.now().strftime("%m/%d/%Y")
        note["approved_by"] = self.caller
        self.caller.msg("|wNOTES>|n Note approved.")
        return

class CmdNoteProve(Command):
    """
    Proves a note.

    Usage:
        note/prove [<target>/]note

    Proves a note.  If no target is specified, then it's assumed that the target is the room.
    """
    key = "note/prove"
    locks = "cmd:all()"
    help_category = "Notes"

    def func(self):
        """
        Proves a note.
        """
        try:
            tar, note = self.args.split("/")
        except ValueError:
            tar = self.caller
            note = self.args

        tar = self.caller.search(tar, global_search=True)
        try:
            note = self.caller.db.notes[int(note)]
        except (ValueError, IndexError):
            try:
                notes = filter(lambda x: x["title"] == note, tar.db.notes)
                note = next(notes)
            except (IndexError, TypeError, StopIteration):
                self.caller.msg("|wNOTES>|n No note found.")
                return
            
        # Show the note
        output = ANSIString("|Y[|n Note #%s on %s |Y]|n" % (self.caller.db.notes.index(note), self.caller.get_display_name(tar))).center(78, ANSIString("|R=|n")) + "\n"
        output += ANSIString(" Note Title:  |c%s|n" % note["title"]) + "\n"
        output += ANSIString(" Private:     |w%s|n" % ("Yes" if note["private"] == True else "No")) + "\n"
        output += ANSIString(" Category:    |w%s|n" % note["category"]) + "\n"
        #if approved, show the date.
        if note["approved"] == True:
            output += ANSIString(" Approved by: |w%s|n - %s" % (note["approved_by"].get_display_name(self.caller) if note["approved_by"] else "None", note["date"])) + "\n"
        else:
            output += ANSIString(" Approved by: |w%s|n" % (note["approved_by"].get_display_name(self.caller) if note["approved_by"] else "None")) + "\n"
        output += ANSIString("|R-|n" * 78) + "\n"
        output += ANSIString(note["text"]) + "\n"
        output += ANSIString("|R=|n" * 78) + "\n"

        tar.msg(output)

        self.caller.msg("|wNOTES>|n Note |w#%s|n proven to %s." % (self.caller.db.notes.index(note),tar.get_display_name(self.caller)))

        return

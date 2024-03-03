from evennia import Command
from evennia import default_cmds

class CmdSetStatus(Command):
    key = "@setstatus"
    locks = "cmd:perm(Builder)"

    def parse(self):
        self.target, self.value = self.args.split("=")
        try:
            self.value = int(self.value)
        except ValueError:
            self.caller.msg("Please provide a valid integer value for status.")
            return

    def func(self):
        if not hasattr(self, 'value'):
            return
        target_character = self.caller.search(self.target)
        if not target_character:
            return
        if 0 <= self.value <= 5:
            target_character.db.camarilla_status = self.value
            self.caller.msg(f"You've set the status of {target_character} to {self.value}.")
            target_character.msg(f"Your Camarilla status has been set to {self.value}.")
        else:
            self.caller.msg("Status should be between 0 and 5.")

class CmdCheckStatus(Command):
    key = "status"

    def parse(self):
        self.target = self.args.strip() or None

    def func(self):
        target_character = self.caller if not self.target else self.caller.search(self.target)
        if not target_character:
            return
        status_value = target_character.db.camarilla_status or 0
        self.caller.msg(f"{target_character}'s Camarilla status is: {status_value}.")

class CmdSetAge(Command):
    key = "@setage"
    locks = "cmd:perm(Builder)"
    
    def parse(self):
        self.target, self.age = self.args.split("=")

    def func(self):
        char = self.caller.search(self.target)
        if not char:
            return
        if self.age not in ['Fledgling', 'Neonate', 'Ancilla', 'Elder']:
            self.caller.msg("Invalid age. Choose from: Fledgling, Neonate, Ancilla, Elder.")
            return
        char.db.age = self.age
        self.caller.msg(f"{char}'s age set to {self.age}.")


class CmdSetTitle(Command):
    key = "@settitle"
    locks = "cmd:perm(Builder)"
    
    def parse(self):
        self.target, self.title = self.args.split("=")

    def func(self):
        char = self.caller.search(self.target)
        if not char:
            return
        char.db.title = self.title
        self.caller.msg(f"{char}'s title set to {self.title}.")

class CmdGrantStatusPoints(Command):
    key = "@grantstatus"
    locks = "cmd:perm(Builder)"
    
    def parse(self):
        self.target, self.points = self.args.split("=")
        try:
            self.points = int(self.points)
        except ValueError:
            self.caller.msg("Status points must be an integer.")
            return

    def func(self):
        if not hasattr(self, 'points'):
            return
        char = self.caller.search(self.target)
        if not char:
            return
        char.db.status_points = (char.db.status_points or 0) + self.points
        self.caller.msg(f"Granted {self.points} status points to {char}. They now have {char.db.status_points} points.")


class CmdAdjustStatus(Command):
    key = "adjuststatus"
    
    def parse(self):
        parts = self.args.split("=")
        self.target, self.points, self.reason = parts[0], parts[1], parts[2]
        try:
            self.points = int(self.points)
        except ValueError:
            self.caller.msg("Status points must be an integer.")
            return

    def func(self):
        if not hasattr(self, 'points'):
            return
        char = self.caller.search(self.target)
        if not char:
            return
        if abs(self.points) > self.caller.db.status_points:
            self.caller.msg(f"You don't have enough status points to adjust by {self.points}.")
            return
        char.db.status_points = (char.db.status_points or 0) + self.points
        self.caller.db.status_points -= abs(self.points)
        char.msg(f"Your status was adjusted by {self.points} points by {self.caller} for reason: {self.reason}.")
        self.caller.msg(f"You adjusted {char}'s status by {self.points} points. You have {self.caller.db.status_points} status points left.")


class CmdStatusBoard(Command):
    key = "statusboard"
    
    def func(self):
        table = self.styled_table("Name", "Age", "Title", "Status Points", width=80)
        for char in self.caller.search_tag('vampire'):  # Assuming all vampires have a 'vampire' tag.
            table.add_row(char.name, char.db.age or '', char.db.title or '', char.db.status_points or 0)
        self.caller.msg(str(table))

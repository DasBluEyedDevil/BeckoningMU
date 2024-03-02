from jobs.models import Bucket, Job, Comment
from evennia.objects.models import ObjectDB
from evennia.commands.default.muxcommand import MuxCommand
from evennia.accounts.models import AccountDB
from evennia.utils.ansi import ANSIString
from evennia.contrib.game_systems.mail import CmdMail
from jobs.models import Job, Comment
from evennia.utils.utils import lazy_property

class CmdBucket(MuxCommand):
    """
    Manage job buckets.

    Usage:
        bucket [<bucket>]
        bucket/create <name>=<description>
        bucket/view <name>
        bucket/delete <name>
        bucket/list
    """
    pass
    key = "+bucket"
    locks = "cmd:perm(bucket) or perm(Builder)"
    aliases = ["buckets", "bucket"]
    help_category = "Jobs"

    def func(self):
        if not self.args and not self.switches:
            self.list_buckets()
            return

        if not self.switches:
            self.view_bucket()
            return

        if "create" in self.switches:
            try:
                name, description = self.args.split("=")
            except ValueError:
                self.caller.msg("Usage: bucket/create <name>=<description>")
                return
            account = AccountDB.objects.get(id=self.account.id)
            bucket = Bucket.objects.create(
                name=name.strip().lower(),
                description=description.strip(),
                created_by=account,
            )
            self.caller.msg(
                f"|wJOBS>|n Created bucket {bucket.id}: {bucket.name}")

        elif "view" in self.switches:
            self.view_bucket()

        elif "delete" in self.switches:
            name = self.args.strip()
            try:
                bucket = Bucket.objects.get(name=name)
                bucket.delete()
                self.caller.msg(f"|wJOBS>|n Deleted bucket {name}.")
            except Bucket.DoesNotExist:
                self.caller.msg(f"|wJOBS>|n No bucket named {name} exists.")

        elif "list" in self.switches:
            self.list_buckets()
            return

    def view_bucket(self):
        """
        View a bucket.
        """
        name = self.args.strip()
        try:
            bucket = Bucket.objects.get(name=name)

            output = ANSIString(f" {bucket.name.upper()} ").center(
                78, ANSIString("|R=|n")) + "\n"
            output += f" Created by: {bucket.created_by.get_display_name(self.caller)}\n"
            output += f" Created at: {bucket.created_at}\n"
            output += f" Description: {bucket.description}\n"
            output += f" Jobs: {bucket.jobs.count()}\n"
            output += f" Archived: {bucket.is_archived}\n"
            output += ANSIString("|R=|n" * 78) + "\n"

            self.caller.msg(output)

        except Bucket.DoesNotExist:
            self.caller.msg(f"|wJOBS>|n No bucket named {name} exists.")

    def list_buckets(self):
        """
        List all buckets.
        """
        buckets = Bucket.objects.all()
        if not buckets:
            self.caller.msg("|wJOBS>|n No buckets exist.")
            return
       # -------------------------------------------------------------------------------
       #  ID    Name                DESCRIPTION                                    Jobs
        output = ANSIString(" Buckets ").center(78, ANSIString("|R=|n")) + "\n"
        output += ANSIString(
            " |CID    Name                DESCRIPTION                                   Jobs|n ") + "\n"
        output += ANSIString("|R-|n" * 78) + "\n"

        for bucket in buckets:
            output += ANSIString(
                f" #{bucket.id:<5}{bucket.name.upper():<17}   {bucket.description:<41}     {bucket.jobs.count():>4}") + "\n"

        output += ANSIString("|R-|n" * 78) + "\n"
        output += "Type +bucket/view <name> to view a bucket.\n"
        self.caller.msg(output)


class CmdJob(MuxCommand):
    """
    Manage jobs

    Usage:
        job <id>
        job/create <bucket>/<title>=<description>
        job/add <id>=<comment>
        job/public <id>=<comment>
        job/addplayer <id>=<account>
        job/removeplayer <id>=<account>
        job/view <id>
        job/update <id>=<new description>
        job/add <id>=<comment>
        job/delete <id>
        job/claim <id>
        job/complete <id>
        job/reopen <id>
        job/assign <id>=<account>
    """

    key = "jobs"
    locks = "cmd:perm(job) or perm(Builder)"
    aliases = ["job"]
    help_category = "Jobs"

    def func(self):
        if not self.args and not self.switches:
            self.list_jobs()
            return

        if not self.switches:
            self.view_job()
            return

        if "create" in self.switches:
            self.create_job()

        elif "addplayer" in self.switches:
            self.job_addplayer()

        elif "removeplayer" in self.switches:
            self.job_removeplayer()

        elif "add" in self.switches:
            self.job_comment()

        elif "public" in self.switches:
            self.job_comment()

        elif "view" in self.switches:
            self.view_job()

        elif "update" in self.switches:
            try:
                id, new_description = self.args.split("=")
                id = id.strip()
                new_description = new_description.strip()
            except ValueError:
                self.caller.msg(
                    "|wJOBS>|n Usage: job/update <id>=<new description>")
                return

            try:
                job = Job.objects.get(id=id)
                job.description = new_description
                job.save()
                self.caller.msg(
                    f"|wJOBS>|n Updated job {job.id}: {job.title} - {job.description}")
            except Job.DoesNotExist:
                self.caller.msg(f"|wJOBS>|n No job with ID {id} exists.")

        elif "delete" in self.switches:
            id = self.args.strip()
            try:
                job = Job.objects.get(id=id)
                job.delete()
                self.caller.msg(f"|wJOBS>|n Deleted job with ID {id}.")
            except Job.DoesNotExist:
                self.caller.msg(f"|wJOBS>|n No job with ID {id} exists.")

        elif "assign" in self.switches:
            try:
                id, assignee_name = self.args.split("=")
                id = id.strip()
                assignee_name = assignee_name.strip()
            except ValueError:
                self.caller.msg(
                    "|wJOBS>|n Usage: job/assign <id>=<assignee>")
                return

            try:
                job = Job.objects.get(id=id)
                assignee = AccountDB.objects.get(username=assignee_name)
                job.assigned_to = assignee
                job.save()
                self.caller.msg(
                    f"|wJOBS>|n Assigned job {job.id}: {job.title} to {assignee.username}")
            except Job.DoesNotExist:
                self.caller.msg(f"|wJOBS>|n No job with ID {id} exists.")
            except AccountDB.DoesNotExist:
                self.caller.msg(
                    f"|wJOBS>|n No player with username {assignee_name} exists.")

        elif "claim" in self.switches:
            id = self.args.strip()
            try:
                job = Job.objects.get(id=id)
                if job.assigned_to:
                    self.caller.msg(
                        f"|wJOBS>|n Job {id} is already claimed by {job.assigned_to.username}.")
                else:
                    job.assigned_to = self.caller
                    job.save()
                    self.caller.msg(
                        f"|wJOBS>|n You have claimed job {job.id}: {job.title}")
            except Job.DoesNotExist:
                self.caller.msg(f"|wJOBS>|n No job with ID {id} exists.")

        elif "complete" in self.switches:
            id = self.args.strip()
            try:
                job = Job.objects.get(id=id)
                if job.status == 'CLOSED':
                    self.caller.msg(
                        f"|wJOBS>|n Job {id} is already completed.")
                else:
                    job.status = 'CLOSED'
                    job.save()
                    self.caller.msg(
                        f"|wJOBS>|n You have completed job {job.id}: {job.title}")
            except Job.DoesNotExist:
                self.caller.msg(f"|wJOBS>|n No job with ID {id} exists.")

        elif "reopen" in self.switches:
            id = self.args.strip()
            try:
                job = Job.objects.get(id=id)
                if job.status != 'CLOSED':
                    self.caller.msg(
                        f"|wJOBS>|n Job {id} is not completed yet.")
                else:
                    job.status = 'OPEN'
                    job.save()
                    self.caller.msg(
                        f"|wJOBS>|n You have reopened job {job.id}: {job.title}")
            except Job.DoesNotExist:
                self.caller.msg(f"|wJOBS>|n No job with ID {id} exists.")

        elif "assign" in self.switches:
            try:
                id, account_name = self.args.split("=")
                id = id.strip()
                account_name = account_name.strip()
            except ValueError:
                self.caller.msg("|wJOBS>|n Usage: job/assign <id>=<account>")
                return

            try:
                job = Job.objects.get(id=id)
                account = AccountDB.objects.get(username=account_name)
                job.assigned_to = account
                job.save()
                self.caller.msg(
                    f"|wJOBS>|n You have assigned job {job.id}: {job.title} to {account.username}")
            except Job.DoesNotExist:
                self.caller.msg(f"|wJOBS>|n No job with ID {id} exists.")
            except AccountDB.DoesNotExist:
                self.caller.msg(
                    f"|wJOBS>|n No account with username {account_name} exists.")

        # if there's no flags, and no args, just list all jobs
        elif not self.switches and not self.args:
            self.list_jobs()
            return

    def view_job(self):
        """
        View a specific job.
        """
        id = self.args.strip()
        try:
            job = Job.objects.get(id=id)
            # -------------------------------------------------------------------------------
            # Job title: <title>                    ID: <id>
            # Bucket: <bucket>                      Status: <status>
            # Assigned to: <assigned_to>            Created by: <created_by>
            # Additional Players: <additional_players>
            # -------------------------------------------------------------------------------
            output = ANSIString(f" |wJOB #{job.id}|n ").center(
                78, ANSIString("|R=|n")) + "\n"
            output += ANSIString(f"|CJob title:|n {job.title}").ljust(38) + " " \
                + ANSIString(f"|CDate Started:|n {job.created_at.strftime( '%m/%d/%Y' )}").ljust(38) + "\n"
            output += ANSIString(f"|CBucket:|n {job.bucket.name}").ljust(38) + " " \
                + ANSIString(f"|CStatus:|n {job.status}").ljust(38) + "\n"
            output += ANSIString(f"|CAssigned to:|n {job.assigned_to.username if job.assigned_to else 'None'}").ljust(38) + " " \
                + ANSIString(f"|CCreated by:|n {job.created_by.name}").ljust(38) + "\n"
            output += ANSIString(
                f"|CAdditional Players:|n {', '.join([player.username for player in job.players.all()])}").ljust(78) + "\n"
            output += ANSIString("||R-|n" * 78) + "\n"
            output += job.description + "\n\n"

            for comment in job.comments.all():
                output += ANSIString(
                    f" {comment.author.get_display_name(self.caller)} |Y[{comment.created_at.strftime('%m/%d/%Y')}]|n: {comment.content}") + "\n\n"
            output += ANSIString("||R=|n" * 78) + "\n"
            self.caller.msg(output)

        except (Job.DoesNotExist):
            self.caller.msg(f"|wJOBS>|n No job with ID {id} exists.")

    def create_job(self, bucket_title="", title="", description="", created_by=None):
        """
        Create a new job.
        """
        try:

            lhsparts = self.lhs.split("/")
            bucket_title = bucket_title or lhsparts[0]
            title = title or lhsparts[1]
            description = description or self.rhs
            created_by = created_by or self.caller
        except ValueError:
            self.caller.msg(
                "|wJOBS>|n Usage: job/create <bucket>/<title>=<description>")
            return

        try:
            bucket = Bucket.objects.get(name=bucket_title.lower())
        except Bucket.DoesNotExist:
            self.caller.msg(
                f"|wJOBS>|n No bucket named |w{bucket_title}|n exists.")
            return

        account = AccountDB.objects.get(id=created_by.id)
        job = Job.objects.create(
            bucket=bucket,
            title=title,
            description=description,
            created_by=account,
            creator=account
        )
        for acct in AccountDB.objects.all():
            if self.caller.check_permstring("builders"):
                acct.msg(
                    f"|wJOBS>|n New job |w#{job.id}|n created by {account.name}: {job.title}")
                acct.msg(
                    f"|wJOBS>|n Use |wjob/view {job.id}|n to view the job.")

    def list_jobs(self):
        """
        List all jobs.
        """
        # -------------------------------------------------------------------------------
        #  ID    title                       Bucket      Assigned to              Status
        # -------------------------------------------------------------------------------
        jobs = Job.objects.all()

        if not jobs:
            self.caller.msg("|wJOBS>|n There are no jobs.")
            return

        output = ANSIString(" |wJOBS|n ").center(
            78, ANSIString("|R=|n")) + "\n"
        output += ANSIString(
            "|C ID    title                       Bucket      Assigned to              Status|n") + "\n"
        output += ANSIString("||R-|n" * 78) + "\n"

        for job in jobs:
            try:
                assigned_to = job.assigned_to.get_display_name(self.caller)
            except AttributeError:
                assigned_to = "None"

            output += f" #{job.id:<4} {job.title:<25}   {job.bucket.name.upper():<10}  {assigned_to:<20} {job.status:>10}\n"

        output += ANSIString("||R=|n" * 78) + "\n"
        output += "Type |wjob/view <id>|n to view a job."
        self.caller.msg(output)

    def job_addplayer(self):
        """
        Add a player to a job.
        """
        pass

    def job_removeplayer(self):
        """
        Remove a player from a job.
        """
        pass

    def job_comment(self, id=None, note=None, public=False, caller=None):
        """
        Add a comment to a job.
        """
        try:
            id = id or self.lhs
            note = note or self.rhs.strip()
        except ValueError:
            if "public" in self.switches:
                self.caller.msg("|wJOBS>|n Usage: job/public <id>=<comment>")
            else:
                self.caller.msg("|wJOBS>|n Usage: job/add <id>=<comment>")
            return

        try:
            caller = caller or self.caller
        except ValueError:
            caller = self.caller

        if "public" in self.switches:
            public = True

        try:
            job = Job.objects.get(id=id)
            acct = AccountDB.objects.get(id=caller.id)
            allaccts = []
            comm = Comment.objects.create(
                job=job, public=public, author=acct, content=note)
            for player in job.players.all():
                allaccts.append(player)
                player.msg(
                    f"|wJOBS>|n {acct.username} has added a comment to job |w#{job.id}|n")
            for player in filter(lambda x: self.caller.locks.check_lockstring(x, "perm(Admin)"), AccountDB.objects.all()):
                allaccts.append(player)
                player.msg(
                    f"|wJOBS>|n {acct.username} has added a comment to job |w#{job.id}|n")
                note = f"JOB |w#{job.id}>|n {acct.get_display_name(player)} |y[{comm.created_at.strftime('%m/%d/%Y-%I:%M:%S%p')}]|n: {note}"
            if public:
                CmdMail.send_mail(self, recipients=allaccts, caller=self.caller,
                                  subject=f"New Comment on Job #{job.id}.", message=note)

        except Job.DoesNotExist:
            self.caller.msg(f"|wJOBS>|n No job with ID |w{id}|n exists.")


class CmdMyJobs(MuxCommand):
    """
    Interact with your jobs.

    Usage:
      myjobs
      myjobs/create <title>=<description>
      myjobs/view <id>
      myjobs/list

    Allows players to manage their job submissions.
    """
    key = "myjobs"
    aliases = "myjob"
    locks = "cmd:all()"
    help_category = "Jobs"

    @lazy_property
    def jobs(self):
        account = self.caller.account
        return Job.objects.filter(created_by=account)


    def func(self):
        if not self.args and not self.switches:
            self.list_my_jobs()
            return

        if "create" in self.switches:
            self.create_my_job()
        elif "view" in self.switches:
            self.view_my_job()
        elif "list" in self.switches:
            self.list_my_jobs()
        else:
            self.caller.msg("Invalid switch.")

    def create_my_job(self):
        try:
            bucket_name, title_description = self.args.split(maxsplit=1)
            title, description = title_description.split("=", 1)
            bucket = Bucket.objects.get(name=bucket_name)
        except ValueError:
            self.caller.msg(ANSIString(f"|wJob {job.id} created in bucket '{bucket.name}': {title}|n"))
            return
        except Bucket.DoesNotExist:
            self.caller.msg(f"Bucket named '{bucket_name}' not found.")
            return
    
        # Ensuring we're using the account associated with the caller for the 'created_by' field
        account = self.caller.account if hasattr(self.caller, 'account') else None
    
        # Check if the caller's account is valid before proceeding
        if not account:
            self.caller.msg("This command can only be used by a character with a valid account.")
            return
    
        job = Job.objects.create(
            title=title.strip(),
            description=description.strip(),
            created_by=account,  # Assigning the account to 'created_by'
            creator=account,  # Also assigning the account to 'creator' if needed
            bucket=bucket
        )
        self.caller.msg(f"Job {job.id} created in bucket '{bucket.name}': {title}")


    def view_my_job(self):
        try:
            job_id = self.args.strip()
            # Ensure we are querying within the jobs accessible by this account
            account = self.caller.account if hasattr(self.caller, 'account') else None
            if not account:
                self.caller.msg("This command can only be used by a character with a valid account.")
                return
    
            job = self.jobs.get(id=job_id)
        except Job.DoesNotExist:
            self.caller.msg("Job not found.")
            return
    
        output = ANSIString("|R=|n" * 39) + "\n"
        output += ANSIString(f"|wJob {job.id}|n: {job.title}\nDescription: {job.description}\nStatus: |w{job.status}|n").center(78) + "\n"
        output += ANSIString("|R=|n" * 39) + "\n"
    
        self.caller.msg(output)



    def list_my_jobs(self):
        if not isinstance(self.caller, ObjectDB):
            self.caller.msg("This command can only be used by authenticated accounts.")
            return
    
        jobs = self.jobs.all()
        if jobs:
            # Start of frame
            output = ANSIString("|R=|n" * 39) + "\n"
            output += ANSIString("|wYour Jobs|n").center(78, ANSIString("|R=|n")) + "\n"
            output += ANSIString("|R-|n" * 78) + "\n"
            
            for job in jobs:
                output += ANSIString(
                    f"|w#{job.id}|n: {job.title} - Status: |w{job.status}|n\n")
            
            # End of frame
            output += ANSIString("|R=|n" * 78) + "\n"
        else:
            output = "You have no jobs submitted."
        
        self.caller.msg(output)



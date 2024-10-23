from jobs.models import Bucket, Job, Comment
from evennia.objects.models import ObjectDB
from evennia.accounts.models import AccountDB
from evennia.utils import class_from_module
from evennia.utils.ansi import ANSIString
from evennia.utils.utils import lazy_property
from django.conf import settings

HELP_CATEGORY = "jobs"

COMMAND_DEFAULT_CLASS = class_from_module(settings.COMMAND_DEFAULT_CLASS)


class CmdBucket(COMMAND_DEFAULT_CLASS):
    """
    Manage job buckets.

    Usage:
        bucket [<bucket>]
        bucket/create <name>=<description>
        bucket/view <name>
        bucket/delete <name>
        bucket/list
    """
    key = "bucket"
    locks = "cmd:perm(bucket) or perm(Builder)"
    aliases = ["+bucket", "buckets", "+buckets"]
    help_category = HELP_CATEGORY

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
        """View a bucket."""
        name = self.args.strip()
        try:
            bucket = Bucket.objects.get(name=name)

            output = ANSIString(
                f" {bucket.name.upper()} ").center(78,
                                                    ANSIString("|R=|n")) + "\n"
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
        """List all buckets with dynamic column width adjustments."""
        buckets = Bucket.objects.all()
        if not buckets:
            self.caller.msg("|wJOBS>|n No buckets exist.")
            return

        # Calculate max lengths for dynamic column widths.
        max_id_len = max(len(str(bucket.id)) for bucket in buckets)
        max_name_len = max(len(bucket.name) for bucket in buckets)
        max_description_len = max(len(bucket.description)
                                  for bucket in buckets)
        max_jobs_count_len = max(len(str(bucket.jobs.count()))
                                 for bucket in buckets)

        # Minimum lengths.
        min_id_len = 5
        min_name_len = 15
        min_description_len = 30
        min_jobs_count_len = 4

        # Determine column widths.
        id_len = max(min_id_len, max_id_len)
        name_len = max(min_name_len, max_name_len)
        description_len = max(min_description_len, max_description_len)
        jobs_count_len = max(min_jobs_count_len, max_jobs_count_len)

        # Output headers.
        output = ANSIString(" Buckets ").center(
            id_len + name_len + description_len + jobs_count_len + 10,
            ANSIString("|R=|n")) + "\n"
        output += ANSIString(
            f"|CID:<{id_len}} Name:<{name_len}} DESCRIPTION:<{description_len}} Jobs|n"
        ) + "\n"  # Corrected f-string
        output += ANSIString("|R-|n" *
                            (id_len + name_len + description_len +
                             jobs_count_len + 10)) + "\n"

        # Output each bucket.
        for bucket in buckets:
            output += f" #{bucket.id:<{id_len}} {bucket.name.upper():<{name_len}} {bucket.description:<{description_len}} {bucket.jobs.count():>{jobs_count_len}}\n"

        output += ANSIString("|R-|n" *
                            (id_len + name_len + description_len +
                             jobs_count_len + 10)) + "\n"
        output += "Type +bucket/view <name> to view a bucket."
        self.caller.msg(output)

class CmdJob(COMMAND_DEFAULT_CLASS):
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
    key = "job"
    locks = "cmd:perm(job) or perm(Builder)"
    aliases = ["+job", "+jobs"]
    help_category = HELP_CATEGORY

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
            self.job_comment(public=True)

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
                    f"|wJOBS>|n Updated job {job.id}: {job.title} - {job.description}"
                )
            except Job.DoesNotExist:
                self.caller.msg(f"|wJOBS>|n No job with ID {id} exists.")

        elif "delete" in self.switches:
            id = self.args.strip()
            try:
                job = Job.objects.get(id=id)
                job.delete()
                self.caller.msg(f"|wJOBS>|n Deleted job with ID {id}.")
            except Job.DoesNotExist:
                self.caller.msg(
                    f"|wJOBS>|n No job with ID {id} exists.")

        elif "claim" in self.switches:
            self.claim_job()

        elif "unclaim" in self.switches:
            self.unclaim_job()

        elif "complete" in self.switches:
            self.complete_job()

        elif "reopen" in self.switches:
            self.reopen_job()

        elif "assign" in self.switches:
            self.assign_job()

        elif "list" in self.switches:
            self.list_jobs()

    def create_job(self):
        """Create a new job."""
        try:
            bucket_name, title_description = self.args.split("/")
            title, description = title_description.split("=")
        except ValueError:
            self.caller.msg(
                "|wJOBS>|n Usage: job/create <bucket>/<title>=<description>"
            )
            return

        try:
            bucket = Bucket.objects.get(name=bucket_name.strip().lower())
        except Bucket.DoesNotExist:
            self.caller.msg(
                f"|wJOBS>|n No bucket named {bucket_name} exists.")
            return

        account = AccountDB.objects.get(id=self.account.id)
        job = Job.objects.create(
            bucket=bucket,
            title=title.strip(),
            description=description.strip(),
            created_by=account,
        )
        self.caller.msg(f"|wJOBS>|n Created job {job.id}: {job.title}")

    def job_addplayer(self):
        """Add a player to a job."""
        try:
            job_id, account_name = self.args.split("=")
            job_id = job_id.strip()
            account_name = account_name.strip()
        except ValueError:
            self.caller.msg(
                "|wJOBS>|n Usage: job/addplayer <job ID>=<account name>")
            return

        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            self.caller.msg(f"|wJOBS>|n No job with ID {job_id} exists.")
            return

        try:
            account = AccountDB.objects.get(username=account_name)
        except AccountDB.DoesNotExist:
            self.caller.msg(
                f"|wJOBS>|n No account named {account_name} exists.")
            return

        job.assigned_players.add(account)
        self.caller.msg(
            f"|wJOBS>|n Added player {account.username} to job {job.id}: {job.title}"
        )

    def job_removeplayer(self):
        """Remove a player from a job."""
        try:
            job_id, account_name = self.args.split("=")
            job_id = job_id.strip()
            account_name = account_name.strip()
        except ValueError:
            self.caller.msg(
                "|wJOBS>|n Usage: job/removeplayer <job ID>=<account name>")
            return

        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            self.caller.msg(f"|wJOBS>|n No job with ID {job_id} exists.")
            return

        try:
            account = AccountDB.objects.get(username=account_name)
        except AccountDB.DoesNotExist:
            self.caller.msg(
                f"|wJOBS>|n No account named {account_name} exists.")
            return

        job.assigned_players.remove(account)
        self.caller.msg(
            f"|wJOBS>|n Removed player {account.username} from job {job.id}: {job.title}"
        )

    def job_comment(self, public=False):
        """Add a comment to a job."""
        try:
            job_id, comment_text = self.args.split("=", 1)
            job_id = job_id.strip()
        except ValueError:
            self.caller.msg(
                "|wJOBS>|n Usage: job/add <job ID>=<comment text>"
            )
            return

        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            self.caller.msg(f"|wJOBS>|n No job with ID {job_id} exists.")
            return

        account = AccountDB.objects.get(id=self.account.id)
        comment = Comment.objects.create(
            job=job,
            author=account,
            text=comment_text.strip(),
            public=public,
        )

        self.caller.msg(
            f"|wJOBS>|n Added comment to job {job.id}: {job.title}")

    def view_job(self):
        """View a job."""
        if not self.args:
            self.caller.msg("Usage: job <job ID>")
            return

        try:
            job = Job.objects.get(id=self.args)
        except Job.DoesNotExist:
            self.caller.msg(f"|wJOBS>|n No job with ID {self.args} exists.")
            return
        except ValueError:
            self.caller.msg(
                f"|wJOBS>|n '{self.args}' is not a valid job ID.")
            return

        output = ANSIString(f" {job.title.upper()} ").center(78,
                                                            ANSIString("|R=|n"))
        output += f"\n|wBucket:|n {job.bucket.name.upper()}"
        output += f"|wCreated by:|n {job.created_by.get_display_name(self.caller)}"
        output += f"|wCreated at:|n {job.created_at}"
        output += f"|wStatus:|n {job.get_status_display}"

class CmdMyJobs(COMMAND_DEFAULT_CLASS):
    """
    Interact with your jobs.

    Usage:
      myjobs
      myjobs/create <bucket> <title>=<description>
      myjobs/view <id>
      myjobs/list

    Allows players to manage their job submissions.
    """
    key = "myjobs"
    aliases = ["myjob", "+myjobs", "+myjob"]
    locks = "cmd:all()"
    help_category = HELP_CATEGORY

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
            self.caller.msg("Error: You must provide a bucket name, title, and description separated by '='.")
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

        try:
            job = Job.objects.create(
                title=title.strip(),
                description=description.strip(),
                created_by=account,  # Assigning the account to 'created_by'
                creator=account,     # Also assigning the account to 'creator' if needed
                bucket=bucket
            )
            self.caller.msg(f"Job {job.id} created in bucket '{bucket.name}': {title.strip()}")
        except Exception as e:
            self.caller.msg(f"An error occurred while creating the job: {e}")

    def view_my_job(self):
        try:
            job_id = self.args.strip()
            account = self.caller.account if hasattr(self.caller, 'account') else None
            if not account:
                self.caller.msg("This command can only be used by a character with a valid account.")
                return

            job = self.jobs.get(id=job_id)
        except Job.DoesNotExist:
            self.caller.msg("Job not found.")
            return

        # Frame start with dark red framing
        output = "|R" + "=" * 78 + "|n\n"
        output += ("|wJob #" + str(job.id) + "|n").center(78, " ") + "\n"
        output += "|R" + "=" * 78 + "|n\n"

        # Ticket Name and Status with a line of dark red ---'s below them
        output += f"|w{'Ticket Name':<37}|{'Status':>40}|n\n"
        output += "|R" + "-" * 78 + "|n\n"  # Dark red '-' characters for divider

        # Actual values for Ticket Name and Status
        output += f"{job.title:<37}|{job.status:>40}\n"
        output += "|R" + "-" * 78 + "|n\n"  # Dark red '-' characters for another divider before Description

        # Description
        output += "|wDescription:|n\n" + job.description + "\n"
        output += "|R" + "-" * 78 + "|n\n"  # Dark red '-' characters for divider before Comments

        # Comments
        public_comments = job.comments.filter(public=True)
        if public_comments:
            output += "|wComments:|n\n"
            for comment in public_comments:
                output += f"- {comment.author.get_display_name(self.caller)}: {comment.content}\n"
        else:
            output += "|wNo public comments.|n\n"

        # End frame
        output += "|R" + "=" * 78 + "|n\n"

        self.caller.msg(output)

    def list_my_jobs(self):
        if not isinstance(self.caller, ObjectDB):
            self.caller.msg("This command can only be used by authenticated accounts.")
            return

        jobs = self.jobs.all()
        output = ""
        if jobs:
            # Start of frame
            output += ANSIString("|wYour Jobs|n").center(78, ANSIString("|R=|n")) + "\n"
            output += ANSIString("|R-|n" * 78) + "\n"
            
            # Headers
            header = f"|w{'ID':<5} {'Ticket Name':<20} {'              ' + 'Bucket':<15} {'            ' + 'Status':<15}|n"
            output += ANSIString(header) + "\n"
            output += ANSIString("|R-|n" * 78) + "\n"
            
            # Job data
            for job in jobs:
                job_line = f"{job.id:<5} {job.title:<20} {'              ' + job.bucket.name:<15} {'              ' + job.status:<15}"
                output += ANSIString(job_line) + "\n"
            
            # End of frame
            output += ANSIString("|R=|n" * 78) + "\n"
        else:
            output = "You have no jobs submitted."
        
        self.caller.msg(output)




from jobs.models import Bucket, Job, Comment
from evennia.objects.models import ObjectDB
from evennia.accounts.models import AccountDB
from evennia.utils import class_from_module
from evennia.utils.ansi import ANSIString
from evennia.contrib.game_systems.mail import CmdMail
from jobs.models import Job, Comment
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
            self.caller.msg(f"|wJOBS>|n Created bucket {bucket.id}: {bucket.name}")

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
            output = ANSIString(f" {bucket.name.upper()} ").center(78, ANSIString("|R=|n")) + "\n"
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
        List all buckets with dynamic column width adjustments.
        """
        buckets = Bucket.objects.all()
        if not buckets:
            self.caller.msg("|wJOBS>|n No buckets exist.")
            return

        # Calculate max lengths for dynamic column widths.
        max_id_len = max(len(str(bucket.id)) for bucket in buckets)
        max_name_len = max(len(bucket.name) for bucket in buckets)
        max_description_len = max(len(bucket.description) for bucket in buckets)
        max_jobs_count_len = max(len(str(bucket.jobs.count())) for bucket in buckets)

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
            id_len + name_len + description_len + jobs_count_len + 10, ANSIString("|R=|n")) + "\n"
        output += ANSIString(
            f"|CID:<{id_len}} Name:<{name_len}} DESCRIPTION:<{description_len}} Jobs|n") + "\n"
        output += ANSIString("|R-|n" * (id_len + name_len + description_len + jobs_count_len + 10)) + "\n"

        # Output each bucket.
        for bucket in buckets:
            output += f" #{bucket.id:<{id_len}} {bucket.name.upper():<{name_len}} {bucket.description:<{description_len}} {bucket.jobs.count():>{jobs_count_len}}\n"

        output += ANSIString("|R-|n" * (id_len + name_len + description_len + jobs_count_len + 10)) + "\n"
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
    key = "jobs"
    locks = "cmd:perm(job) or perm(Builder)"
    aliases = ["job", "+job", "+jobs"]
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
            self.job_comment()

        elif "view" in self.switches:
            self.view_job()

        elif "update" in self.switches:
            try:
                id, new_description = self.args.split("=")
                id = id.strip()
                new_description = new_description.strip()
            except ValueError:
                self.caller.msg("|wJOBS>|n Usage: job/update <id>=<new description>")
                return

            try:
                job = Job.objects.get(id=id)
                job.description = new_description
                job.save()
                self.caller.msg(f"|wJOBS>|n Updated job {job.id}: {job.title} - {job.description}")
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
                self.caller.msg("|wJOBS>|n Usage: job/assign <id>=<assignee>")
                return

            try:
                job = Job.objects.get(id=id)
                assignee = AccountDB.objects.get(username=assignee_name)
                job.assigned_to = assignee
                job.save()
                self.caller.msg(f"|wJOBS>|n Assigned job {job.id}: {job.title} to {assignee.username}")
            except Job.DoesNotExist:
                self.caller.msg(f"|wJOBS>|n No job with ID {id} exists.")
            except AccountDB.DoesNotExist:
                self.caller.msg(f"|wJOBS>|n No player with username {assignee_name} exists.")

        elif "claim" in self.switches:
            id = self.args.strip()
            try:
                job = Job.objects.get(id=id)
                if job.assigned_to:
                    self.caller.msg(f"|wJOBS>|n Job {id} is already claimed by {job.assigned_to.username}.")
                else:
                    job.assigned_to = self.caller
                    job.save()
                    self.caller.msg(f"|wJOBS>|n You have claimed job {job.id}: {job.title}")
            except Job.DoesNotExist:
                self.caller.msg(f"|wJOBS>|n No job with ID {id} exists.")

        elif "complete" in self.switches:
            id = self.args.strip()
            try:
                job = Job.objects.get(id=id)
                if job.status == 'CLOSED':
                    self.caller.msg(f"|wJOBS>|n Job {id} is already completed.")
                else:
                    job.status = 'CLOSED'
                    job.save()
                    self.caller.msg(f"|wJOBS>|n You have completed job {job.id}: {job.title}")
            except Job.DoesNotExist:
                self.caller.msg(f"|wJOBS>|n No job with ID {id} exists.")

        elif "reopen" in self.switches:
            id = self.args.strip()
            try:
                job = Job.objects.get(id=id)
                if job.status != 'CLOSED':
                    self.caller.msg(f"|wJOBS>|n Job {id} is not completed yet.")
                else:
                    job.status = 'OPEN'
                    job.save()
                    self.caller.msg(f"|wJOBS>|n You have reopened job {job.id}: {job.title}")
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
                self.caller.msg(f"|wJOBS>|n You have assigned job {job.id}: {job.title} to {account.username}")
            except Job.DoesNotExist:
                self.caller.msg(f"|wJOBS>|n No job with ID {id} exists.")
            except AccountDB.DoesNotExist:
                self.caller.msg(f"|wJOBS>|n No account with username {account_name} exists.")

        elif not self.switches and not self.args:
            self.list_jobs()
            return

    def list_jobs(self):
        """
        List all jobs with dynamic column width adjustments.
        """
        jobs = Job.objects.all()

        if not jobs:
            self.caller.msg("|wJOBS>|n There are no jobs.")
            return

        # Calculate max lengths for dynamic column widths.
        max_id_len = max(len(str(job.id)) for job in jobs)
        max_title_len = max(len(job.title) for job in jobs)
        max_bucket_len = max(len(job.bucket.name) for job in jobs)
        max_assigned_to_len = max(len(job.assigned_to.get_display_name(self.caller) if job.assigned_to else "None") for job in jobs)
        max_status_len = max(len(job.status) for job in jobs)

        # Minimum lengths.
        min_id_len = 5
        min_title_len = 15
        min_bucket_len = 10
        min_assigned_to_len = 10
        min_status_len = 10

        # Determine column widths.
        id_len = max(min_id_len, max_id_len)
        title_len = max(min_title_len, max_title_len)
        bucket_len = max(min_bucket_len, max_bucket_len)
        assigned_to_len = max(min_assigned_to_len, max_assigned_to_len)
        status_len = max(min_status_len, max_status_len)

        # Output headers.
        output = ANSIString(" |wJOBS|n ").center(
            id_len + title_len + bucket_len + assigned_to_len + status_len + 10, ANSIString("|R=|n")) + "\n"
        output += ANSIString(
            f"|C{'ID':<{id_len}} {'Title':<{title_len}} {'Bucket':<{bucket_len}} {'Assigned to':<{assigned_to_len}} {'Status':<{status_len}}|n") + "\n"
        output += ANSIString("|R-|n" * (id_len + title_len + bucket_len + assigned_to_len + status_len + 10)) + "\n"

        # Output each job.
        for job in jobs:
            assigned_to = job.assigned_to.get_display_name(self.caller) if job.assigned_to else "None"
            output += f" #{job.id:<{id_len}} {job.title:<{title_len}} {job.bucket.name:<{bucket_len}} {assigned_to:<{assigned_to_len}} {job.status:<{status_len}}\n"

        output += ANSIString("|R-|n" * (id_len + title_len + bucket_len + assigned_to_len + status_len + 10)) + "\n"
        output += "Type |wjob/view <id>|n to view a job."
        self.caller.msg(output)

    def job_addplayer(self):
    """
    Add a player to a job.
    """
    try:
        id, player_name = self.args.split("=")
        id = id.strip()
        player_name = player_name.strip()
    except ValueError:
        self.caller.msg("|wJOBS>|n Usage: job/addplayer <id>=<player>")
        return

    try:
        job = Job.objects.get(id=id)
        player = AccountDB.objects.get(username=player_name)
        job.players.add(player)
        job.save()
        self.caller.msg(f"|wJOBS>|n Added {player.username} to job {job.id}: {job.title}")
    except Job.DoesNotExist:
        self.caller.msg(f"|wJOBS>|n No job with ID {id} exists.")
    except AccountDB.DoesNotExist:
        self.caller.msg(f"|wJOBS>|n No player with username {player_name} exists.")

def job_removeplayer(self):
    """
    Remove a player from a job.
    """
    try:
        id, player_name = self.args.split("=")
        id = id.strip()
        player_name = player_name.strip()
    except ValueError:
        self.caller.msg("|wJOBS>|n Usage: job/removeplayer <id>=<player>")
        return

    try:
        job = Job.objects.get(id=id)
        player = AccountDB.objects.get(username=player_name)
        job.players.remove(player)
        job.save()
        self.caller.msg(f"|wJOBS>|n Removed {player.username} from job {job.id}: {job.title}")
    except Job.DoesNotExist:
        self.caller.msg(f"|wJOBS>|n No job with ID {id} exists.")
    except AccountDB.DoesNotExist:
        self.caller.msg(f"|wJOBS>|n No player with username {player_name} exists.")

def job_comment(self, id=None, note=None, public=False, caller=None):
    """
    Add a comment to a job.
    """
    try:
        id = id or self.lhs
        note = note or self.rhs.strip()
    except ValueError:
        self.caller.msg("|wJOBS>|n Usage: job/public <id>=<comment>" if "public" in self.switches else "|wJOBS>|n Usage: job/add <id>=<comment>")
        return

    caller = caller or self.caller

    # Determine if the comment is public based on the presence of the "public" switch
    public = "public" in self.switches

    try:
        job = Job.objects.get(id=id)
        acct = AccountDB.objects.get(id=caller.id)
        comm = Comment.objects.create(
            job=job, public=public, author=acct, content=note)
        self.caller.msg(f"Your comment has been added to job |w#{job.id}|n.")
        
        # Notify the job's creator if the comment is public and they are not the one adding it
        if public and job.created_by != caller:
            job.created_by.msg(f"|wJOBS>|n {acct.username} has added a public comment to job |w#{job.id}|n: {note}")

        # Send mail to the job's creator if the comment is public
        CmdMail.send_mail(self, recipients=[job.created_by], caller=self.caller,
                          subject=f"New Public Comment on Job #{job.id}", message=note)
    except Job.DoesNotExist:
        self.caller.msg(f"|wJOBS>|n No job with ID |w{id}|n exists.")

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

    def list_my_jobs(self):
        """
        List all jobs created by the caller with dynamic column width adjustments.
        """
        jobs = self.jobs.all()

        if not jobs:
            self.caller.msg("|wMYJOBS>|n You have no jobs.")
            return

        # Calculate max lengths for dynamic column widths.
        max_id_len = max(len(str(job.id)) for job in jobs)
        max_title_len = max(len(job.title) for job in jobs)
        max_bucket_len = max(len(job.bucket.name) for job in jobs)
        max_status_len = max(len(job.status) for job in jobs)

        # Minimum lengths.
        min_id_len = 5
        min_title_len = 15
        min_bucket_len = 10
        min_status_len = 10

        # Determine column widths.
        id_len = max(min_id_len, max_id_len)
        title_len = max(min_title_len, max_title_len)
        bucket_len = max(min_bucket_len, max_bucket_len)
        status_len = max(min_status_len, max_status_len)

        # Output headers.
        output = ANSIString(" |wMY JOBS|n ").center(
            id_len + title_len + bucket_len + status_len + 10, ANSIString("|R=|n")) + "\n"
        output += ANSIString(
            f"|C{'ID':<{id_len}} {'Title':<{title_len}} {'Bucket':<{bucket_len}} {'Status':<{status_len}}|n") + "\n"
        output += ANSIString("|R-|n" * (id_len + title_len + bucket_len + status_len + 10)) + "\n"

        # Output each job.
        for job in jobs:
            output += f" #{job.id:<{id_len}} {job.title:<{title_len}} {job.bucket.name:<{bucket_len}} {job.status:<{status_len}}\n"

        output += ANSIString("|R-|n" * (id_len + title_len + bucket_len + status_len + 10)) + "\n"
        output += "Type |wmyjobs/view <id>|n to view a job."
        self.caller.msg(output)

    def view_my_job(self):
        """
        View a specific job created by the caller.
        """
        id = self.args.strip()
        try:
            job = self.jobs.get(id=id)

            output = ANSIString(f" |wMY JOB #{job.id}|n ").center(78, ANSIString("|R=|n")) + "\n"
            output += f"|wTitle:|n {job.title}\n"
            output += f"|wDescription:|n {job.description}\n"
            output += f"|wBucket:|n {job.bucket.name}\n"
            output += f"|wStatus:|n {job.status}\n"
            output += f"|wCreated at:|n {job.created_at}\n"
            output += f"|wAssigned to:|n {job.assigned_to.get_display_name(self.caller) if job.assigned_to else 'None'}\n"
            output += ANSIString("|R-|n" * 78) + "\n"

            # Output comments.
            for comment in job.comments.all():
                output += ANSIString(f" {comment.author.get_display_name(self.caller)} |Y[{comment.created_at.strftime('%m/%d/%Y')}]|n: {comment.content}") + "\n"
            output += ANSIString("|R-|n" * 78) + "\n"
            self.caller.msg(output)

        except Job.DoesNotExist:
            self.caller.msg(f"|wMYJOBS>|n No job with ID {id} exists.")

def create_my_job(self):
    """
    Create a new job for the caller.
    """
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




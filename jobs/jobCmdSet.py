from evennia import CmdSet
from jobs.commands.commands import CmdBucket, CmdJob
from commands.myjobs import CmdMyJobs


class JobCmdSet(CmdSet):
    """
    This command set includes the commands for managing jobs and buckets.

    """
    key = "job_cmdset"

    def at_cmdset_creation(self):
        self.add(CmdBucket())
        self.add(CmdJob())
        self.add(CmdMyJobs())

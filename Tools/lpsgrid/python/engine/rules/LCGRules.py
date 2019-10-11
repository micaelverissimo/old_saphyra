

__all__ = [""]

from lps_cluster import Rule
from lps_cluster.core.messenger.macros import *


class LCGRule(Rule):

  def __init__(self, db):
    Rule.__init__(self, db)



  # rules( user, task, status = [StatusJob.REGISTED] )
  def __call__(self, user, task, status=None ):


    # LCG rule taken from: https://twiki.cern.ch/twiki/bin/view/PanDA/PandaAthena#Job_priority
    # this must be ordered by creation (date). First must be the older one
    jobs = self.db().getAllJobs( user )

    # The total number of the user's subJobs existing in the whole queue. (existing = job status is one of 
    # defined,assigned,activated,sent,starting,running)
    T = self.db().getTotalUntilRunning()

    # Update all priorities
    for n, job in enumerate( jobs ):
      # This is the LCG rule
      priority = self.db().getPriority(user) - (T+n)/5.
      self.db().setPriority(job, priority)


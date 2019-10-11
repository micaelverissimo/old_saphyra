

__all__ = [""]

from lps_cluster import Logger
from lps_cluster.core.messenger.macros import *


class Rule(Logger):

  def __init__(self, db):

    Logger.__init__(self)
    self._db = db


  def db(self):
    return self.db


  def initialize(self):
    return StatusCode.SUCCESS


  def execute(self):
    return StatusCode.SUCCESS


  def finalize(self):
    return StatusCode.SUCCESS


  # rules( user, task, status = [StatusJob.REGISTED] )
  def __call__(self, user, task, status=None ):

    pass

    # LCG rule taken from: https://twiki.cern.ch/twiki/bin/view/PanDA/PandaAthena#Job_priority
    # this must be ordered by creation (date). First must be the older one
    jobs = self.db().getAllJobs( user )

    # The total number of the user's subJobs existing in the whole queue. (existing = job status is one of 
    # defined,assigned,activated,sent,starting,running)
    T = self.db().getTotalUntilRunning()

    priority = self.db().getPriority(user) - (T


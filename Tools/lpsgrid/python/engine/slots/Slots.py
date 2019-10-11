
__all__ = ["Slots"]


from Gaugi import Logger, NotSet
from Gaugi.messenger.macros import *
from Gaugi import retrieve_kw
from Gaugi import StatusCode
from collections import deque


class Slots( Logger ):

  def __init__(self,name, maxlength ) :
    Logger.__init__(self,name=name)
    self._total = maxlength
    self._slots = [None for _ in range(self._total)]


  def setDatabase( self, db ):
    self.__db = db


  def setOrchestrator( self, orc ):
    self.__orchestrator = orc


  def db(self):
    return self.__db


  def orchestrator(self):
    return self.__orchestrator


  def initialize(self):

    if self.db() is NotSet:
      MSG_FATAL( self, "Database object not passed to slot." )

    if self.orchestrator() is NotSet:
      MSG_FATAL( self, "Orchestrator object not passed to slot.")

    MSG_INFO( self, "Creating cluster stack with %s slots", self.size() )
    return StatusCode.SUCCESS



  def execute(self):
    self.update()
    return StatusCode.SUCCESS


  def finalize(self):
    return StatusCode.SUCCESS


  def update(self):

    to_be_removed = []

    for idx, job in enumerate(self._slots):

      if job.status() is StatusJob.ACTIVATED:
        # TODO: Change the internal state to RUNNING
        # If, we have an error during the message,
        # we will change to BROKEN status
        if job.execute().isFailure():
          # tell to db that we have a broken
          job.job().setStatus( StatusJob.BROKEN )
          to_be_removed.append(idx)
        else: # change to running status
          job.job().setStatus( StatusJob.RUNNING )

      elif job.status() is StatusJob.FAILED:

        # Tell to db that this job was failed
        job.job().setStatus( StatusJob.FAILED )
        # Remove this job into the stack
        to_be_removed.append(idx)

      elif job.status() is StatusJob.RUNNING:
        continue

      elif job.status() is StatusJon.DONE:
        job.job().setStatus( StatusJob.DONE )
        to_be_removed.append(idx)


    # remove all failed/broken/done jobs of the stack
    for r in to_be_removed:
      del self.__slots[r]
      MSG_DEBUG(self, "Removing this %d in the stack. We have $d/%d slots availabel", r, len(self._stack),selt.size())



  #
  # Add an job into the stack
  # Job is an db object
  #
  def push_back( self, job ):
    if self.isAvailable():
      # Create the job object
      obj = Consumer( job )
      # Tell to database that this job will be activated
      obj.setOrchestrator( self.orchestrator() )
      # TODO: the job must set the internal status to ACTIVATED mode
      obj.initialize()
      # Tell to db that this job was activated by the slot
      obj.job().setStatus( StatusJob.ACTIVATED )
      self.__slots.append( obj )
    else:
      MSG_WARNING( self, "You asked to add one job into the stack but there is no available slots yet." )


  def size(self):
    return self._total


  def isAvailable(self):
    return True if self.getRunningJobs() < self.size() else False



  #
  # Get the number of jobs with running status in the GPU slot list
  #
  def getRunningJobs( self ):
    total=0
    for job in self._slots:
      if job.status() is StatusJob.RUNNING:
        total+=1
    return total





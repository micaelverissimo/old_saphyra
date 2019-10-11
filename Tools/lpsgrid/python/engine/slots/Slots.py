
__all__ = ["Slots"]


from Gaugi import Logger, NotSet
from Gaugi.messenger.macros import *
from Gaugi import retrieve_kw
from collections import deque


class Slots( Logger ):

  def __init__(self, maxlenght, nodes) :
    Logger.__init__(self)
    if nodes:
      if not type(nodes) is list:
        MSG_FATAL(self, "Nodes must be a list")
      self._nodes = nodes
      self._total = len(nodes)
    else:
      self._nodes = NotSet
      self._total = maxlength
    self._slots = [None for _ in range(self._total)]


  def setDatabase( self, db ):
    self._db = db


  def setOrchestator( self, orc ):
    self._orchestrator = orc

  
  def db(self):
    return self._db


  def orchestrator(self):
    return self._orchestrator


  def initialize(self):

    if self.db() is NotSet:
      MSG_FATAL( self, "Database object not passed to slot." )

    if self.orchestator() is NotSet:
      MSG_FATAL( self, "Orchestrator object not passed to slot.")

    MSG_INFO( self, "Creating cluster stack with %s slots", self.total() )
    if self._use_gpu:
      if self._available_nodes is NotSet:
        MSG_FATAL(self, "List of available nodes with GPUs not passed to slot.")

      MSG_INFO( self, "This slots will be dedicated for GPUs" )

    return StatusCode.SUCCESS


  def execute(self):
    #self.update()
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
          self.db().setStatus( job.job() , StatusJob.BROKEN )
          to_be_removed.append(idx)
        else: # change to running status
          self.db().setStatus( job.job() , StatusJob.RUNNING )

      elif job.status() is StatusJob.FAILED:

        # Tell to db that this job was failed
        self.db().setStatus( job.job() , StatusJob.FAILED )
        # Remove this job into the stack
        to_be_removed.append(idx)

      elif job.status() is StatusJob.RUNNING:
        continue

      elif job.status() is StatusJon.DONE:
        self.db().setStatus( job.job() , StatusJob.DONE )
        to_be_removed.append(idx)


    # remove all failed/broken/done jobs of the stack
    for r in to_be_removed:
      del self._stack[r]
      MSG_DEBUG(self, "Removing this %d in the stack. We have $d/%d slots availabel", r, len(self._stack),selt.size())



  #
  # Add an job into the stack
  # Job is an db object
  #
  def push_back( self, job ):
    if self.isAvailable():
      # Create the job object
      obj = Job( job )
      # Tell to database that this job will be activated
      obj.setOrchestrator( self.orchestrator() )
      obj.setJobParameters( self.db().getJobParameters( user, task, job ) )
      # TODO: the job must set the internal status to ACTIVATED mode
      obj.initialize()
      # Tell to db that this job was activated by the slot
      self.db().setStatus( job, StatusJob.ACTIVATED )
      self._slots.append( obj )
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





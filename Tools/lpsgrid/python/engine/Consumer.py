
__all__ = ["JobConsumer"]


from Gaugi.messenger import Logger
from Gaugi.messenger.macros import *
from Gaugi import retrieve_kw


class JobConsumer( Logger ):

  #
  # Args: The database manager, the kubernetes API (Kubernetes class) and
  # the database job object), node (use this to choose a specific node for
  # gpu staff
  #
  def __init__(self, db, api, job, node=None ):
    Logger.__init__(self)
    self._db = db
    seff._job = job
    self._api = api
    self._node = node



  def initialize(self):
    return StatusCode.SUCCESS

  def execute(self):
    self.start()
    return StatusCode.SUCCESS

  def finalize(self):
    self.stop()
    return StatusCode.SUCCESS


  def start(self):

    sc = self.db().getStatus(self._job)

    # We need to change the status to starting
    # Some times this can be RUNNING because of shutdown
    # Most part will be REGISTERED
    self._job.setStatus(StatusJob.STARTING)
    jobParams = self.db().getJobParams( self._job )


  def update(self):

    #sc = self.db().getStatus(self._job)
    ## The user send kill to database, we must tell to rancher
    ## to stop this
    #if sc is StatusJob.KILLED:
    #  self.kill()

    #elif sc is StatusJob.STARTING:

    #  # check the status with rancher
    #  rsc = self.rancher().getStatus( self._jobID )
    #  if rsc is StatusJob.RUNNING:
    #    self.db().setStatus( self._job, StatusJob.RUNNING )
    #  elif 
    pass


  def kill(self):
    self.stop()
    self._db.setJobStatus( self.getUsername(), self.getTaksID(), self.getJobID(), StatusJob.KILLED )


  def stop(self):
    # tell to rancher to stop this job in the stack
    return


  def status(self):
    return self._db.getJobStatus( self.getUsername(), self.getTaksID(), self.getJobID() )



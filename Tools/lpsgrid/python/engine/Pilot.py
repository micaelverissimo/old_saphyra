
__all__ = ["Pilot"]


from Gaugi import Logger, NotSet
from Gaugi.messenger.macros import *


class Pilot(Logger):

  def __init__(self):
    Logger.__init__(self)


  def setSchedule( self, sc ):
    self.schedule = sc


  def setDatabase( self, db ):
    self._db = db


  def setCPUSlot( self, slot ):
    self._cpu_slot = slot


  def setGPUSlot( self, slot ):
    self._gpu_slot = slot


  def treat(self):

    if self.db() is NotSet:
      MSG_FATAL( self, "Database is not set." )
    if self.schedule() is NotSet:
      MSG_FATAL( self, "Schedule is not set." )
    if not (self.cpu_slot() and self.gpu_slot()):
      MSG_FATAL( self, "cpu and gpu slots not set. You must set one or bouth" )
    if self.orchestrator() is NotSet:
      MSG_FATAL( self, "Orchestrator is not set" )


  def db(self):
    return self._db


  def sechedule(self):
    return self._schedule


  def orchestrator(self):
    return self._orchestrator


  def getGPUSlots(self):
    return self._gpu_slot


  def getCPUSlots(self):
    return self._cpu_slot


  def initialize(self):

    self.treat()
    # connect to the sql database (service)
    # Setup the kubernetes orchestrator (service)
    # link db to schedule
    self.schedule().setDatabase( self.db() )
    # Update the priority for each N minutes
    self.schedule().setUpdateTime( 5 * MINUTE )

    if self.schedule().initialize().isFailure():
      MSG_FATAL( self, "Not possible to initialize the Schedule tool. abort" )

    # link orchestrator/db to slots
    self.cpu_slots().setDatabase( self.db() )
    self.cpu_slots().setOrchestrator( self.orchestrator() )
    if self.cpu_slots().initialize().isFailure():
      MSG_FATAL( self, "Not possible to initialize the CPU slot tool. abort" )

    # link orchestrator/db to slots
    self.gpu_slots().setDatabase( self.db() )
    self.gpu_slots().setOrchestrator( self.orchestrator() )
    if self.gpu_slots().initialize().isFailure():
      MSG_FATAL( self, "Not possible to initialize the GPU slot tool. abort" )


    return StatusCode.SUCCESS



  def execute(self):

    # Infinite loop
    #while True:

    #  try:
    #    # Calculate all priorities for all REGISTERED jobs for each 5 minutes
    #    self.schedule().execute()

    #    # Prepare jobs for CPU slots only
    #    jobs = self.schedule().getQueue()
    #    while self.cpu_slots().isAvailable():
    #      self.cpu_slots().push_back( jobs.pop() )

    #    # Prepare jobs for GPU slots only
    #    jobs = self.schedule().getQueue(gpu=True)
    #    while self.gpu_slots().isAvailable():
    #      self.gpu_slots().push_back( jobs.pop() )

    #    # Run the pilot for cpu queue
    #    self.cpu_slots().execute()
    #    # Run the pilot for gpu queue
    #    self.gpu_slots().execute()

    #  except:
    #    MSG_ERROR(self, "There is an error in the pilot.")
    #    return StatusCode.FAILURE


    return StatusCode.SUCCESS


  def finalize(self):

    self.db().finalize()
    self.schedule().finalize()
    self.getCPUSlots().finalize()
    self.getGPUSlots().finalize()
    self.orchestator().finalize()
    return StatusCode.SUCCESS








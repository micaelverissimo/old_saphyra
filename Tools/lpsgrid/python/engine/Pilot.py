
__all__ = ["Pilot"]


from Gaugi import Logger, NotSet, StatusCode
from Gaugi.messenger.macros import *


from lpsgrid.engine.slots import *
from lpsgrid.engine.constants import *

class Pilot(Logger):

  def __init__(self, db, schedule, orchestrator):
    Logger.__init__(self)
    self.__cpu_slot = NotSet
    self.__gpu_slot = NotSet
    self.__db = db
    self.__schedule = schedule
    self.__orchestrator = orchestrator




  def setSlots( self, slot ):
    if type(slot) is CPUSlots:
      self.__cpu_slot = slot
    elif type(slot) is GPUSlots:
      self.__gpu_slot = slot
    else:
      MSG_ERROR(self, "slot must be CPUSlots or GPUSlots.")



  def treat(self):
    if not (self.cpuSlots() and self.gpuSlots()):
      MSG_FATAL( self, "cpu and gpu slots not set. You must set one or bouth" )


  def db(self):
    return self.__db


  def schedule(self):
    return self.__schedule


  def orchestrator(self):
    return self.__orchestrator


  def cpuSlots(self):
    return self.__cpu_slot


  def gpuSlots(self):
    return self.__gpu_slot


  def initialize(self):

    self.treat()
    # connect to the sql database (service)
    # Setup the kubernetes orchestrator (service)
    # link db to schedule
    self.schedule().setDatabase( self.db() )
    # Update the priority for each N minutes
    self.schedule().setUpdateTime( 5 )

    if self.schedule().initialize().isFailure():
      MSG_FATAL( self, "Not possible to initialize the Schedule tool. abort" )

    # link orchestrator/db to slots
    self.cpuSlots().setDatabase( self.db() )
    self.cpuSlots().setOrchestrator( self.orchestrator() )
    if self.cpuSlots().initialize().isFailure():
      MSG_FATAL( self, "Not possible to initialize the CPU slot tool. abort" )

    # link orchestrator/db to slots
    self.gpuSlots().setDatabase( self.db() )
    self.gpuSlots().setOrchestrator( self.orchestrator() )
    if self.gpuSlots().initialize().isFailure():
      MSG_FATAL( self, "Not possible to initialize the GPU slot tool. abort" )


    return StatusCode.SUCCESS



  def execute(self):

    # Infinite loop
    while True:

      # Calculate all priorities for all REGISTERED jobs for each 5 minutes
      self.schedule().execute()

      ## Prepare jobs for CPU slots only
      #jobs = self.schedule().getQueue()
      #while self.cpu_slots().isAvailable():
      #  self.cpu_slots().push_back( jobs.pop() )

      ## Prepare jobs for GPU slots only
      #jobs = self.schedule().getQueue(gpu=True)
      #while self.gpu_slots().isAvailable():
      #  self.gpu_slots().push_back( jobs.pop() )

      ## Run the pilot for cpu queue
      #self.cpu_slots().execute()
      ## Run the pilot for gpu queue
      #self.gpu_slots().execute()



    return StatusCode.SUCCESS


  def finalize(self):

    self.db().finalize()
    self.schedule().finalize()
    self.cpuSlots().finalize()
    self.gpuSlots().finalize()
    self.orchestator().finalize()
    return StatusCode.SUCCESS








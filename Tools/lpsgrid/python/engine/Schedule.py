
__all__ = ["Schedule"]


from Gaugi import Logger, NotSet
from Gaugi.messenger.macros import *
from Gaugi import StatusCode
import time
from sqlalchemy import and_, or_
from lpsgrid.engine.enumerations import *
from lpsgrid.engine.constants import *
from ringerdb.models import *

MAX_TEST_JOBS=2
MAX_FAILED_JOBS=1


class Schedule(Logger):

  def __init__(self, name, rules):

    Logger.__init__(self, name=name)
    self.__rules = rules
    self.__then = NotSet
    self.__maxUpdateTime = MAX_UPDATE_TIME

  def initialize(self):
    return StatusCode.SUCCESS


  def tictac( self ):
    if self.__then is NotSet:
      self.__then = time.time()
      return False
    else:
      now = time.time()
      if (now-self.__then) > self.__maxUpdateTime:
        # reset the time
        self.__then = NotSet
        return True
    return False


  def setDatabase(self, db):
    self._db = db


  def db(self):
    return self._db


  def calculate(self):


    for user in self.db().getAllUsers():

      MSG_INFO(self,"Caluclating for %s", user )
      # Get the initial priority of the user
      maxPriority = user.getMaxPriority()
      MSG_INFO( self, "%s with max priority: %d", user.getUserName, user.getMaxPriority())
      # Get the number of tasks
      tasks = user.getAllTasks()

      for task in tasks:

        MSG_INFO(self,"Task status is %s",task.getStatus())
        # Get the task status (REGISTED, TESTING, RUNNING, BROKEN, DONE)
        if task.getStatus() == Status.REGISTERED:
          MSG_INFO(self, "Task with status: registered")
          # We need to check if this is a good task to proceed.
          # To test, we will launch 10 first jobs and if 80%
          # of jobs is DONE, we will change the task status to
          # RUNNING. Until than, all not choosed jobs will have
          # priority equal zero and the 10 ones will be equal
          # USER max priority (1000,2000,..., N)
          self.setJobsToBeTested( user, task )
          # change the task status to: REGISTED to TESTING.
          task.setStatus( Status.TESTING )
          self.db().commit()
        # Check if this is a test
        elif task.getStatus() == Status.TESTING:
          # Check if we can change the task status to RUNNING or BROKEN.
          # If not, this will still TESTING until we decide each signal
          # will be assigned to this task
          MSG_INFO(self, "Task with status: testing")
          self.checkTask( task )

        elif task.getStatus() == Status.RUNNING:
          # If this task was assigned as RUNNING, we must recalculate
          # the priority of all jobs inside of this task.
          MSG_INFO(self, "Task with status: running")


        else: # DONE, BROKEN or FAILED Status
          MSG_INFO(self, "continue...")
          continue

      self.calculatePriorities( user )

    return StatusCode.SUCCESS





  def execute(self):
    # Calculate the priority for every N minute
    if self.tictac():
      MSG_INFO(self, "Calculate...")
      self.calculate()


  def finalize(self):
    self.getContext().finalize()


  def setJobsToBeTested( self, user, task ):

    # Set the first MAX_TEST_JOBS to high user priority
    # This will allow the schedule to consume this jobs faster
    # and check if the current task is good to proceed
    priority = user.getMaxPriority( )
    jobs = task.getAllJobs()
    jobCount = 0
    while (jobCount < MAX_TEST_JOBS):
      try:
        MSG_INFO(self, "add job to the test stack...")
        jobs[jobCount].setPriority(priority)
        jobs[jobCount].setStatus(Status.TESTING)
        jobCount+=1
        self.db().commit()
      except Exception as e:
        MSG_ERROR(self, e)
        break


  def checkTask( self, task ):

    MSG_INFO(self, "Check Tasks assigned...")
    # Maybe we need to checge these rules
    if len(self.db().session().query(Job).filter( and_( or_( Job.status==Status.FAILED,  Job.status==Status.BROKEN), Job.taskId==task.id )).all()) > MAX_FAILED_JOBS:
      task.setStatus( Status.BROKEN )
      MSG_INFO(self, "broken...")
      # kill all jobs into the task assigned as broken status
      self.closeAllJobs( task )
    elif len(self.db().session().query(Job).filter( and_( Job.status==Status.DONE, Job.taskId==task.id )).all()) > MAX_FAILED_JOBS:
      MSG_INFO(self,"assigned all jobs!")
      task.setStatus( Status.RUNNING )
      self.db().commit()
      self.assignedAllJobs(task)
    else:
      MSG_INFO( self, "still stesting....")
      #task.setStatus( Status.TESTING )



  def calculatePriorities( self, user):
    # The rules will be an external class with Rule as inheritance.
    # These rules can be changed depends on the demand.
    return self.__rules( self.db(), user)



  def setUpdateTime( self, t ):
    self.__maxUpdateTime = t



  def closeAllJobs(self, task):
    for job in task.getAllJobs():
      job.setStatus( Status.BROKEN )
      job.setPriority( -1 )


  def assignedAllJobs( self, task ):
    for job in task.getAllJobs():
      if job.getStatus() == Status.REGISTERED:
        job.setStatus( Status.ASSIGNED )
        self.db().commit()












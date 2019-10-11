
__all__ = ["Schedule"]


from Gaugi import Logger, NotSet
from Gaugi.messenger.macros import *
import time


class Schedule(Logger):

  def __init__(self):

    Logger.__init__(self, db, rules)
    self._rules = rules
    self._db
    self._then = NotSet

  def db(self):
    return self._db

  def initialize(self):
    return StatusCode.SUCCESS


  def tictac( self ):
    if self._then is NotSet:
      self._then = time.time()
      return False
    else:
      now = time.time()
      if (now-self._then) > MAX_UPDATE_SECONDS:
        # reset the time
        self._then = NotSet
        return True
    return False



  def calculate(self):


    for user in self.db().getAllUsers():

      # Get the initial priority of the user
      maxPriority = user.getMaxPriority()

      # Get the number of tasks
      tasks = user.getAllTask()


      for task in tasks:

        # Get the task status (REGISTED, TESTING, RUNNING, BROKEN, DONE)
        if task.getStatus() is StatusTask.REGISTED:
          # We need to check if this is a good task to proceed.
          # To test, we will launch 10 first jobs and if 80%
          # of jobs is DONE, we will change the task status to
          # RUNNING. Until than, all not choosed jobs will have
          # priority equal zero and the 10 ones will be equal
          # USER max priority (1000,2000,..., N)
          self.setJobsToBeTested( username, task )
          # change the task status to: REGISTED to TESTING.
          task.setStatus( StatusTask.TESTING )
        # Check if this is a test
        elif task.getStatus() is StatusTask.TESTING:
          # Check if we can change the task status to RUNNING or BROKEN.
          # If not, this will still TESTING until we decide each signal
          # will be assigned to this task
          self.checkTask( task )

        elif task.getStatus() is StatusTask.RUNNING:
          # If this task was assigned as RUNNING, we must recalculate
          # the priority of all jobs inside of this task.
          self.calculatePriorities( task )

        else: # BROKEN Status
          continue


    return StatusCode.SUCCESS





  def execute(self):
    # Calculate the priority for every N minute
    if self.tictac():
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
    while (jobCount < MAX_TEST_JOBS)
      if len(jobs)>0:
        testJob = jobs.pop()
      else: # Stopping the loop since we have less than MAX_TEST_JOBS in the list
        break
      testJob.setPriority( priority )
      jobCount+=1
    self.db().commit()


  def checkTask( self, task ):

    # Maybe we need to checge these rules
    if len(self.db().session().query(Job).filter( and_( or_( Job.status=StatusJob.FAILED,  
      Job.status=StatusJob.BROKEN), Job.taskId==task.id )).all()) > MAX_FAILED_JOBS:
      task.setStatus( StatusTask.BROKEN )
    elif len(self.db().session().query(Job).filter( and_( Job.status=StatusJob.DONE, 
      Job.taskId==task.id )).all()) > MAX_FAILED_JOBS:
      self.db().setStatus( task, StatusTask.RUNNING )
    else:
      self.db().setStatus( task, StatusTask.TESTING )



  def calculatePriorities( self, user, task ):
    # The rules will be an external class with Rule as inheritance.
    # These rules can be changed depends on the demand.
    return self.rules( self.db(), user, task, status = [StatusJob.REGISTED] )








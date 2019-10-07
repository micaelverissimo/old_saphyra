
__all__=['User','Task','Job','Model','DB']

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()


class Status(object):
  RUNNING = "running"
  HOLDING = "holding"
  FAILED  = "failed"
  STARTING= "stating"
  DONE    = "done"


#
#   Users Table
#
class User (Base):
    __tablename__ = 'user'

    # Local
    id = Column(Integer, primary_key = True)
    username = Column(String, unique = True)

    # Foreign
    tasks = relationship("Task", order_by="Task.id", back_populates="user")

    def __repr__ (self):
        return "<User {}>".format(self.username)
 
    # Method that adds tasks into user
    def addTask (self, task):
        self.tasks.append(task)

    # Method that gets all tasks from user
    def getTasks (self):
        return self.tasks


    # Method that gets single task from user
    def getTask (self, taskName):
      for task in self.getTasks():
        if taskName == task.getTaskName():
          return task
      return None



#
#   Tasks Table
#
class Task (Base):
    __tablename__ = 'task'

    # Local
    id = Column(Integer, primary_key = True)
    taskName = Column(String, unique=True)
    inputFilePath = Column(String)
    outputFilePath = Column(String)
    configFilesPath = Column(String)
    status = Column(String)
    etBinIdx  = Column( Integer )
    etaBinIdx = Column( Integer )
 
    # Foreign
    jobs = relationship("Job", order_by="Job.id", back_populates="task")
    userId = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", back_populates="tasks")


    def __repr__ (self):
        return "<Task (taskName='{}', etBinIdx={}, etaBinIdx={}, jobs='{}')>".format(self.taskName, self.etBinIdx, self.etaBinIdx, self.jobs)

    # Method that adds jobs into task
    def addJob (self, job):
        if (isinstance(job, Job)):
            self.jobs.append(job)
            return True
        else:
            return False

    # Method that gets all jobs from task
    def getJobs (self):
        return self.jobs

    # Method that gets single task from user
    def getJob (self, index):
        try:
            return self.jobs[index]
        except:
            return None

    def getStatus(self):
        return self.status

    def setStatus(self):
        self.status = status

    def getTaskName(self):
      self.taskName

#
#   Jobs Table
#
class Job (Base):
    __tablename__ = 'job'

    # Local
    id = Column(Integer, primary_key = True)
    priority = Column(Integer)
    configFilePath = Column(String)
    #execArgs = Column(String)
    status = Column(String)

    # Foreign
    taskId = Column(Integer, ForeignKey('task.id'))
    task = relationship("Task", back_populates="jobs")
    models = relationship("Model", order_by='Model.id',back_populates="job")


    def __repr__ (self):
        return "<Job (configFilePath='{}', priority='{}', status='{}')>".format(
            self.configFilePath, self.priority, self.status
        )

    def getStatus(self):
        return self.status

    def setStatus(self, status):
        self.status = status


    def getParams (self):
        return self.configFilePath


    def addModel( self, model ):
      self.models.append( model )


class Model( Base ):
  __tablename__ = "model"
  id        = Column( Integer, primary_key = True )

  job = relationship( "Job", order_by='Job.id', back_populates='models')
  jobID     = Column( Integer, ForeignKey('job.id' )) 
  modelID   = Column( Integer )
  sort      = Column( Integer )
  init      = Column( Integer )

  # Summary keys
  mse = Column( Float )
  mse_val = Column( Float )
  mse_op = Column( Float )
  auc = Column( Float )
  auc_val = Column( Float )
  auc_op = Column( Float )
  max_sp = Column( Float )
  max_sp_pd = Column( Float )
  max_sp_fa = Column( Float )
  max_sp_val = Column( Float )
  max_sp_pd_val = Column( Float )
  max_sp_fa_val = Column( Float )
  max_sp_op = Column( Float )
  max_sp_pd_op = Column( Float )
  max_sp_fa_op = Column( Float )

  # This keys are defined in: https://github.com/jodafons/saphyra/blob/master/Core/saphyra/python/posproc/Summary.py
  summary_keys = ['mse','mse_val','mse_op',
                  'auc','auc_val','auc_op',
                  'max_sp','max_sp_pd','max_sp_fa',
                  'max_sp_val','max_sp_pd_val','max_sp_fa_val',
                  'max_sp_op', 'max_sp_pd_op', 'max_sp_fa_op']



  # PileupFit variables defined in: https://github.com/jodafons/saphyra/blob/master/Core/saphyra/python/posproc/PileupFit.py
  fitting_commom_keys = ['sp_ref','pd_ref','fa_ref', 'reference','slope','slope_op','offset','offset_op']
  fitting_keys = ['sp','pd','fa', 'sp_val','pd_val','fa_val','sp_op','pd_op','fa_op']
  sp_ref = Column( Float )
  pd_ref = Column( Float )
  fa_ref = Column( Float )
  reference = Column( String )

  slope = Column( Float )
  offset = Column( Float )
  fit_sp = Column( Float )
  fit_pd = Column( Float )
  fit_fa = Column( Float )
  fit_sp_val = Column( Float )
  fit_pd_val = Column( Float )
  fit_fa_val = Column( Float )

  slope_op = Column( Float )
  offset_op = Column( Float )
  fit_sp_op = Column( Float )
  fit_pd_op = Column( Float )
  fit_fa_op = Column( Float )


  def setSort( self, sort ):
    self.sort = sort

  def getSort(self):
    return self.sort

  def setInit( self, init ):
    self.init = init

  def getInit( self ):
    return self.init


  def setFitting( self, d ):
    for key in self.fitting_commom_keys:
      getattr(self, key) = d[key]
    for key in self.fitting_keys:
      getattr(self, 'fit_'+key) = d[key]

  def getFitting( self, d ):
    d={}
    for key in self.fitting_commom_keys:
      d[key] = getattr(self, key) = d[key]
    for key in self.fitting_keys:
      d[key] = getattr(self, 'fit_'+key) = d[key]
    return d



  def setSummary( self, d ):
    for key in self.summary_keys:
      getattr(self, key) = d[key]


  def getSummary( self ):
    d = {}
    for key in self.summary_keys:
      d[key] = getattr(self, key)
    return d







__all__ = ["RingerDB", "aws_url"]

from Gaugi import Logger, NotSet
from Gaugi.messenger.macros import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ringerdb.models import*

aws_url = 'postgres://ringer:6sJ09066sV1990;6@postgres-ringer-db.cahhufxxnnnr.us-east-2.rds.amazonaws.com/ringer'

class RingerDB(Logger):

  def __init__( self, username, url ):

    Logger.__init__(self)
    self.url = url

    self.__username = username
    self.__user = None
    self.__task = None
    self.__job = None


    try: # Get the connection and create an session
      MSG_INFO( self, "Connect to %s.", url )
      self.__engine = create_engine(url)
      Session= sessionmaker(bind=self.__engine)
      self.__session = Session()
    except Exception as e:
      MSG_FATAL( self, e )


    try: # Get the user
      user = self.session().query(Worker).filter(Worker.username==username).first()
      if user:
        self.__user = user
        MSG_INFO(self, '%s', user)
      else:
        MSG_FATAL(self, 'User not found in the current db.')
    except:
      MSG_FATAL(self, "failed to execute the query(Worker.username==username)" )


  def createTask( self , taskName, configFilePath, inputFilePath, outputFilePath, cluster,
                  templateExecArgs="{}", 
                  secondaryDataPath="{}", 
                  etBinIdx=None, 
                  etaBinIdx=None,
                  isGPU=False):

    try:
      # Create the task and append into the user area
      task = Task(taskName=taskName, 
                  inputFilePath=inputFilePath,
                  outputFilePath=outputFilePath,
                  configFilePath=configFilePath,
                  # The task always start as registered status
                  status='registered',
                  cluster=cluster,
                  # Extra args
                  templateExecArgs=templateExecArgs,
                  secondaryDataPath=secondaryDataPath,
                  etBinIdx=etBinIdx,
                  etaBinIdx=etaBinIdx,
                  isGPU=isGPU
                  )
      self.user().addTask(task)
      self.commit()
      return task
    except Exception as e:
      MSG_ERROR(self, e)
      return None


  def createJob( self, task, configFilePath, configId, priority=1000, execArgs="{}", isGPU=False ):

    try:

      job = Job( configFilePath=configFilePath,
                 configId=configId,
                 execArgs=execArgs,
                 cluster=task.getCluster(),
                 retry=0,
                 status="registered",
                 priority=priority,
                 isGPU=isGPU
                 )
      task.addJob(job)
      self.commit()
      return Job
    except Exception as e:
      MSG_ERROR( self, e)
      return None


  def getUser( self, username ):
    try:
      return self.session().query(Worker).filter(Worker.username==username).first()
    except Exception as e:
      MSG_ERROR(self, e)
      return None

  def user(self):
    return self.__user


  def getTask( self, taskName ):
    try: # Get the task object using the task name as filter
      return self.session().query(Task).filter(Task.taskName==taskName).first()
    except Exception as e:
      MSG_ERROR(self, e)
      return None


  def session(self):
    return self.__session


  def commit(self):
    self.session().commit()


  def close(self):
    self.session().close()



  def getCurrentUser(self):
    return self.__user

  def setCurrentJob( self, job ):
    self.__job = job

  def getCurrentJob(self):
    return self.__job

  def setCurrentTask( self , task):
    self.__task = task

  def getCurrentTask(self):
    return self.__task


  def attach_ctx( self,  context ):


    # NOTE: this should be append into the database for future
    taskId = self.getCurrentTask().id

    init = context.getHandler("init")
    sort = context.getHandler("sort")
    imodel = context.getHandler("imodel")
    history = context.getHandler("history")
    time =context.getHandler("time")
    etBinIdx = self.getCurrentJob().getTask().etBinIdx
    etaBinIdx = self.getCurrentJob().getTask().etaBinIdx
    # Create the model database context
    if 'fitting' in history.keys():
      # Setting Summary and PileupFit values
      for key, obj in history['fitting'].items():
        # Create the model context
        model = Model(time=time, taskId=taskId)
        model.setInit(init)
        model.setSort(sort)
        model.setModelId(imodel)
        model.setEtBinIdx(etBinIdx)
        model.setEtaBinIdx(etaBinIdx)
        model.setSummary( history['summary'] )
        model.setFitting( obj )
        self.getCurrentJob().addModel(model)
    else:
      # Setting only Summary values
      model = Model(time=time, taskId=taskId)
      model.setInit(init)
      model.setSort(sort)
      model.setModelId(imodel)
      model.setEtBinIdx(etBinIdx)
      model.setEtaBinIdx(etaBinIdx)
      model.setSummary( history['summary'] )
      self.getCurrentJob().addModel(model)
 
    self.commit()





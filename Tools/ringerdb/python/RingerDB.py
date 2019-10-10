
__all__ = ["DBContext", "aws_url"]

from Gaugi import Logger, NotSet
from Gaugi.messenger.macros import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from saphyra.db.models import*

aws_url = 'postgres://ringer:6sJ09066sV1990;6@postgres-ringer-db.cahhufxxnnnr.us-east-2.rds.amazonaws.com/ringer'

class DBContext(Logger):

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


  def createTask( self, taskName ):

    try:
      # Create the task and append into the user area
      task = Task(taskName=taskName 
                  inputFilePath=inputFilePath,
                  outputFilePath=outputFilePath,
                  configFilePath=configFilePath,
                  # The task always start as registered status
                  status='registered',
                  etBinIdx=etBinIdx,
                  etaBinIdx=etaBinIdx))
      self.user().addTask(task)
      self.commit()
      return task
    except Exception as e:
      MSG_ERROR(self, e)
      return None


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


  def createJob(self, task, configFilePath, configId)
  
    try:
      job = Job(configFilePath=configFilePath, status="registered", configId=configId)
      task.addJob(job)
      self.commit()
      return job
    except Exception as e:
      MSG_ERROR(self, e)
      return None



  def setCurrentJob( self, job ):
    self.__job = job

  def getCurrentJob(self):
    return self.__job



  def attach_ctx( self,  context ):

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
      for key, obj in history['history']['fitting'].items():
        # Create the model context
        model = Model(time=time)
        model.setInit(init)
        model.setSort(sort)
        model.setModelID(imodel)
        model.setEtBinIdx(etBinIdx)
        model.setEtaBinIdx(etaBinIdx)
        model.setSummary( history['summary'] )
        model.setPileupFit( obj )
        self.getCurrentJob().setModel(model)
    else:
      # Setting only Summary values
      model = Model(time=time)
      model.setInit(init)
      model.setSort(sort)
      model.setModelID(imodel)
      model.setEtBinIdx(etBinIdx)
      model.setEtaBinIdx(etaBinIdx)
      model.setSummary( history['summary'] )
      self.getCurrentJob().setModel(model)
 
    self.commit()





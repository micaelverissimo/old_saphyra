
__all__ = ["DataBase", "aws_url"]

from Gaugi import Logger, NotSet
from Gaugi.messenger.macros import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


aws_url = 'postgres://ringer:6sJ09066sV1990;6@postgres-ringer-db.cahhufxxnnnr.us-east-2.rds.amazonaws.com/ringer'


class DataBase( Logger ):


  def __init__( self, url ):
    Logger.__init__(self)
    self.url = url
    self._job = NotSet
    try:
      MSG_INFO( self, "Connect to %s.", url )
      self.__engine = create_engine(url)
      #Base.metadata.create_all(self.__engine)
      Session= sessionmaker(bind=self.__engine)
      self.__session = Session()
    except Exception as e:
      MSG_FATAL( self, e )

  def url(self):
    return self.__url

  def session(self):
    return self.__session

  def commit(self):
    self.session().commit()

  def close(self):
    self.session().close()


  def setCurrentJob( self, job ):
    self._job = job

  def getCurrentJob(self):
    return self._job



  def attach_ctx( self,  context ):

    init = context.getHandler("init")
    sort = context.getHandler("sort")
    history = context.getHandler("history")
    model = Model()
    model.setInit(init)
    model.setSort(sort)
    model.setSummary( history['summary'] )






__all__ = ["DataBase", "aws_url"]

from Gaugi import Logger
from Gaugi.core.messenger.macros import *

aws_url = 'postgres://ringer:6sJ09066sV1990;6@postgres-ringer-db.cahhufxxnnnr.us-east-2.rds.amazonaws.com/ringer'


class DataBase Logger ):


  def __init__( self, url ):
    self.url = url
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    try:
      self.__engine = create_engine(url)
      #Base.metadata.create_all(self.__engine)
      Session= sessionmaker(bind=self.__engine)
      self.__session = Session()
      MSG_INFO("Connected.")
      self.__connected = True
    except:
      self.__connected = True


  def session(self):
    return self.__session

  def commit(self):
    self.session().commit()

  def connected(self):
    return self.__connected






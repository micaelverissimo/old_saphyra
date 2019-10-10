
__all__ = ["Job"]

from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from saphyra.db.models import Base


#
#   Jobs Table
#
class Job (Base):
    __tablename__ = 'job'

    # Local
    id = Column(Integer, primary_key = True)
    configFilePath = Column(String)
    configId = Column(Integer)
    #execArgs = Column(String)
    status = Column(String)

    # Foreign
    taskId = Column(Integer, ForeignKey('task.id'))
    task = relationship("Task", back_populates="jobs")
    models = relationship("Model", order_by='Model.id',back_populates="job")

    cluster  = Column( String )
    priority = Column(Integer)


    def __repr__ (self):
        return "<Job (configFilePath='{}', status='{}')>".format(
            self.configFilePath, self.status
        )

    def getStatus(self):
        return self.status


    def setStatus(self, status):
        self.status = status


    def getParams (self):
        return self.configFilePath


    def addModel( self, model ):
      self.models.append( model )


    def getTask(self):
      return self.task


    def setPriority(self, priority):
      self.priority = priority


    def getPriority(sefl):
      return self.priority


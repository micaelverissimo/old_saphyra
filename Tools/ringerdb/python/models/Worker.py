__all__=['Worker']



from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from ringerdb.models import Base


#
#   Users Table
#
class Worker (Base):

  __tablename__ = 'worker'

  # Local
  id = Column(Integer, primary_key = True)
  username = Column(String, unique = True)
  maxPriority = Column( Integer )

  # Foreign
  tasks = relationship("Task", order_by="Task.id", back_populates="user")


  def __repr__ (self):
    return "<User {}, priority {}>".format(self.username, self.maxPriority)

  # Method that adds tasks into user
  def addTask (self, task):
    self.tasks.append(task)

  # Method that gets all tasks from user
  def getTasks (self):
    return self.tasks


  def getTask (self, taskName):
    for task in self.getTasks():
      if taskName == task.getTaskName():
        return task
    return None


  def getUserName(self):
    return self.username

  def setUserName(self, name ):
    self.username = name


  def getMaxPriority(self):
    return self.maxPriority

  def setMaxPriority(self, value):
    self.maxPriority = value

  

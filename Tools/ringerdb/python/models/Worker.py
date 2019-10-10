__all__=['Worker']



from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from saphyra.db.models import Base


#
#   Users Table
#
class Worker (Base):

  __tablename__ = 'worker'

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


  def name(self):
    return self.username

  def setUserName(self, name ):
    self.username = name


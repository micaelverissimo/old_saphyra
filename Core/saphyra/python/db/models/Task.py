__all__=['Task']


from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from saphyra.db.models import Base



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





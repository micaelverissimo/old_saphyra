__all__ = ["ReadSafeThread"]

from Gaugi import Logger, NotSet, SafeThread, StatusThread
from Gaugi.messenger.macros import *


class ReadDataPool( Logger ):

  def __init__(self, fList):
    
    Logger.__init__(self)
    from Gaugi import csvStr2List
    from Gaugi import expandFolders
    fList = csvStr2List ( fList )
    self._fList = expandFolders( fList )
    self.process_pipe = []


  def __call__( self, reader, ringerOperation, **kw ):
    
    while len(self._fList) > 0:
      
      if len(self.process_pipe) < int(maxJobs):
        job_id = len(self._fList)
        f = self.fList.pop()
        proc = SafeThread( reader )
        self.process_pipe.append( (job_id, proc( f, ringerOperation, **kw)) )
      
      for proc in self.process_pipe:
        if proc[1].status() is StatusThread.STOP:
          MSG_INFO( self,  ('pop process id (%d) from the stack')%(proc[0]) )
          self.process_pipe.remove(proc)
    
    # Check pipe process
    # Protection for the last jobs
    while len(self.process_pipe)>0:
      for proc in self.process_pipe:
        if proc[1].status() is StatusThread.STOP:
          MSG_INFO( self,  ('pop process id (%d) from the stack')%(proc[0]) )
          self.process_pipe.remove(proc)









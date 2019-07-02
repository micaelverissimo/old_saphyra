
__all__ = ["CreatePandaJobs"]

from Gaugi import retrieve_kw, mkdir_p
from Gaugi.messenger import Logger
from Gaugi.messenger.macros import *
from Gaugi.LoopingBounds import *


class CreatePandaJobs( Logger ):



  def __init__( self, **kw):

    Logger.__init__(self, **kw)



  @classmethod
  def _retrieveJobLoopingBoundsCol( cls, varBounds, varWindow ):
    """
      Create window bounded variables from larger range.
    """
    varIncr = varBounds.incr()
    jobWindowList = LoopingBoundsCollection()
    for jobTuple in varBounds.window( varWindow ):
      if len(jobTuple) == 1:
        jobWindowList += MatlabLoopingBounds(jobTuple[0], jobTuple[0])
      elif len(jobTuple) == 0:
        self._fatal("Retrieved empty window.")
      else:
        jobWindowList += MatlabLoopingBounds(jobTuple[0], 
                                             varIncr, 
                                             jobTuple[-1])
    return jobWindowList


  def time_stamp(self):
    from datetime import datetime
    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("%d-%b-%Y-%H.%M.%S")
    return timestampStr


  def __call__( self, **kw): 

    from sklearn.model_selection import *
    from saphyra import Norm1
    
    # Cross validation configuration
    outputFolder        = retrieve_kw( kw, 'outputFolder' ,       'jobConfig'           )
    sortBounds          = retrieve_kw( kw, 'sortBounds'   ,   PythonLoopingBounds(5)    )
    nInits              = retrieve_kw( kw, 'nInits'       ,                10           )
    nSortsPerJob        = retrieve_kw( kw, 'nSortsPerJob' ,           1                 )
    nInitsPerJob        = retrieve_kw( kw, 'nInitsPerJob' ,          10                 ) 
    models              = retrieve_kw( kw, 'models'       ,            None             )
    crossval            = retrieve_kw( kw, 'crossval'     ,         KFold(10,shuffle=True, random_state=0)  )
    ppChain             = retrieve_kw( kw, 'ppChain'      ,         [Norm1()]           )


    time_stamp = self.time_stamp()
    
    # creating the job mechanism file first

    mkdir_p(outputFolder)
    mkdir_p(outputFolder+ '/job_container')
    
    sortJobsWindowList = CreatePandaJobs._retrieveJobLoopingBoundsCol( sortBounds, nSortsPerJob )
    initJobsWindowList = CreatePandaJobs._retrieveJobLoopingBoundsCol( PythonLoopingBounds( nInits ), nInitsPerJob )


    for sortWindowBounds in sortJobsWindowList():

      for initWindowBounds in initJobsWindowList():
        
        MSG_INFO( self, 'Creating job config with sort (%d to %d) and %d inits', 
            sortWindowBounds[0], sortWindowBounds[-1], len(initWindowBounds))

        from saphyra.readers.versions import Job_v1
        job = Job_v1()
        job.set_sorts(list(sortWindowBounds))
        job.set_inits(list(initWindowBounds))
        job.save( outputFolder+'/job_container/' + ('job_config_%s_%s.%s') %
            (sortWindowBounds.formattedString('s'), initWindowBounds.formattedString('i'), time_stamp) )


    from saphyra.readers.versions import CrossVal_v1
    cv = CrossVal_v1()
    cv.set_object(crossval)
    cv.save( outputFolder+'/' +('crossvalFile_%s')%(time_stamp) )
    

    from saphyra.readers.versions import Model_v1
    m = Model_v1()
    m.set_models( models )
    m.save( outputFolder+'/'+ ('modelFile_%s')%(time_stamp) )


    from saphyra.readers.versions import PreProcChain_v1
    pp = PreProcChain_v1(ppChain)
    pp.save( outputFolder+'/'+ ('preprocFile_%s')%(time_stamp) )
    






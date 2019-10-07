
__all__ = ["CreatePandaJobs"]

from Gaugi import retrieve_kw, mkdir_p
from Gaugi.messenger import Logger
from Gaugi.messenger.macros import *
from Gaugi.LoopingBounds import *

# default model (ringer vanilla)
# Remove the keras dependence and get keras from tensorflow 2.0
import tensorflow as tf
default_model = tf.keras.Sequential()
default_model.add(tf.keras.layers.Dense(5, input_shape=(100,), activation='tanh', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
default_model.add(tf.keras.layers.Dense(1, activation='linear', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
default_model.add(tf.keras.layers.Activation('tanh'))
 


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
        MSG_FATAL(self, "Retrieved empty window.")
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

    from sklearn.model_selection import KFold
    from saphyra import Norm1
    
    # Cross validation configuration
    outputFolder        = retrieve_kw( kw, 'outputFolder' ,       'jobConfig'           )
    sortBounds          = retrieve_kw( kw, 'sortBounds'   ,   PythonLoopingBounds(5)    )
    nInits              = retrieve_kw( kw, 'nInits'       ,                10           )
    nSortsPerJob        = retrieve_kw( kw, 'nSortsPerJob' ,           1                 )
    nInitsPerJob        = retrieve_kw( kw, 'nInitsPerJob' ,          10                 ) 
    nModelsPerJob       = retrieve_kw( kw, 'nModelsPerJob',          1                  ) 
    models              = retrieve_kw( kw, 'models'       ,   [default_model]           )
    model_tags          = retrieve_kw( kw, 'model_tags'   ,   ['mlp_100_5_1']           )
    crossval            = retrieve_kw( kw, 'crossval'     , KFold(10,shuffle=True, random_state=512)  )
    ppChain             = retrieve_kw( kw, 'ppChain'      ,         [Norm1()]           )


    time_stamp = self.time_stamp()
    
    # creating the job mechanism file first

    mkdir_p(outputFolder)
    mkdir_p(outputFolder+ '/job_container')
    
    if type(models) is not list:
      models = [models]
    
    modelJobsWindowList = CreatePandaJobs._retrieveJobLoopingBoundsCol( PythonLoopingBounds( len(models) ), nModelsPerJob )
    sortJobsWindowList  = CreatePandaJobs._retrieveJobLoopingBoundsCol( sortBounds                        , nSortsPerJob  )
    initJobsWindowList  = CreatePandaJobs._retrieveJobLoopingBoundsCol( PythonLoopingBounds( nInits )     , nInitsPerJob  )


    nJobs = 0 
    for modelWindowBounds in modelJobsWindowList():

      for sortWindowBounds in sortJobsWindowList():

        for initWindowBounds in initJobsWindowList():

          #print list(sortWindowBounds)
          MSG_INFO( self, 'Creating job config with sort (%d to %d) and %d inits and model Index (%d to %d)', 
              sortWindowBounds[0], sortWindowBounds[-1], len(initWindowBounds), modelWindowBounds[0],modelWindowBounds[-1])
          
          from saphyra.readers.versions import Job_v1
          job = Job_v1()
          job.set_sorts(list(sortWindowBounds))
          job.set_inits(list(initWindowBounds))
          job.set_models([models[i] for i in list(modelWindowBounds)],  list(modelWindowBounds) )
         
          job.save( outputFolder+'/job_container/' + ('job_config_%s_%s_%s.%s') %
              ( 
                modelWindowBounds.formattedString('m'),
                sortWindowBounds.formattedString('s'), 
                initWindowBounds.formattedString('i'), time_stamp) )
          nJobs+=1

    MSG_INFO( self, "A total of %d jobs...", nJobs)
    from saphyra.readers.versions import CrossVal_v1
    cv = CrossVal_v1()
    cv.set_object(crossval)
    cv.save( outputFolder+'/' +('crossvalFile_%s')%(time_stamp) )
    

    from saphyra.readers.versions import Model_v1
    m = Model_v1()
    m.set_models( models , range(len(models)))
    m.save( outputFolder+'/'+ ('modelFile_%s')%(time_stamp) )


    from saphyra.readers.versions import PreProcChain_v1
    pp = PreProcChain_v1(ppChain)
    pp.save( outputFolder+'/'+ ('preprocFile_%s')%(time_stamp) )
    






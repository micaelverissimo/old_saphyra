

__all__ = ['PandasJob']

from Gaugi.messenger import Logger, LoggingLevel
from Gaugi.messenger.macros import *
from Gaugi import StatusCode,  checkForUnusedVars, retrieve_kw
from Gaugi.gtypes import NotSet
from tensorflow.keras.models import clone_model
from tensorflow.keras import backend as K
from copy import deepcopy
from sklearn.utils.class_weight import compute_class_weight
import numpy as np

from saphyra.posproc import Summary

from tensorflow.keras.models import clone_model
from datetime import datetime
import time

class PandasJob( Logger ):

  def __init__(self , dbcontext, pattern_generator, **kw ):

    Logger.__init__(self,   **kw)

    self._pattern_generator = pattern_generator
    self._dbcontext = dbcontext

    self._optimizer     = retrieve_kw( kw, 'optimizer'  , 'adam'                )
    self._loss          = retrieve_kw( kw, 'loss'       , 'binary_crossentropy' )
    self._epochs        = retrieve_kw( kw, 'epochs'     , 1000                  )
    self._batch_size    = retrieve_kw( kw, 'batch_size' , 1024                  )
    self.callbacks      = retrieve_kw( kw, 'callbacks'  , []                    )
    self.posproc        = retrieve_kw( kw, 'posproc'    , []                    )
    self.metrics        = retrieve_kw( kw, 'metrics'    , []                    )
    self._sorts         = retrieve_kw( kw, 'sorts'      , []                    )
    self._inits         = retrieve_kw( kw, 'inits'      , []                    )
    self.crossval       = retrieve_kw( kw, 'crossval'   , NotSet                )
    self._verbose       = retrieve_kw( kw, 'verbose'    , True                  )
    self._class_weight  = retrieve_kw( kw, 'class_weight' , False               )
    self._save_history  = retrieve_kw( kw, 'save_history' , True                )
    from saphyra  import PreProcChain_v1, NoPreProc
    self.ppChain        = retrieve_kw( kw, 'ppChain'    , PreProcChain_v1([NoPreProc()]))

    # DB parameter
    self._taskName  = retrieve_kw( kw, 'taskName', None )


    # Get configurations and model from job config
    job_auto_config = retrieve_kw( kw, 'job'        , NotSet                )
    # read the job configuration from file
    if job_auto_config:
      if type(job_auto_config) is str:
        MSG_INFO( self, 'Reading job configuration from: %s', job_auto_config )
        from saphyra.readers import JobReader
        job = JobReader().load( job_auto_config )
      else:
        job = job_auto_config
      # retrive sort/init lists from file
      self._sorts = job.getSorts()
      self._inits = job.getInits()
      self._models, self._id_models = job.getModels()
      self._jobId = job.id()

    # get model and tag from model file or lists
    models = retrieve_kw( kw, 'models', NotSet )
    if not models is NotSet:
      if type(models) is str:
        from saphyra.readers import ModelReader
        self._models, self._id_models = ModelReader().load( s ).get_models()
      else:
        self._models = models
        self._id_modes = range(len(models))


    # get all parameters to used in the output step
    from saphyra.readers.versions import TunedData_v1
    self._tunedData = retrieve_kw( kw, 'tunedData'  , TunedData_v1()        )
    self._outputfile= retrieve_kw( kw, 'outputfile' , 'tunedDisc'           )

    self._db = None
    checkForUnusedVars(kw)

    if type(self._inits) is int:
      self._inits = range(self._inits)

    self._context = NotSet
    self._index_from_cv = NotSet


  def setDatabase( self, db ):
    self._db = db

  def db(self):
    return self._db


  def getContext(self):
    return self._context


  def setContext(self, ctx):
    self._context = ctx



  @property
  def crossval(self):
    return self._crossval

  @crossval.setter
  def crossval(self, s):
    if type(s) is str:
      from saphyra.readers import CrossValReader
      self._crossval = CrossValReader().load(s)
    else:
      self._crossval = s


  @property
  def sorts(self):
    return self._sorts

  @sorts.setter
  def sorts( self, s):
    self._sorts = s

  @property
  def inits(self):
    return self._inits

  @inits.setter
  def inits( self, s):
    if type(s) is int:
      self._inits = range(s)
    else:
      self._inits = s


  @property
  def ppChain(self):
    return self._ppChain

  @ppChain.setter
  def ppChain( self, s):
    if type(s) is str:
      from saphyra.readers import PreProcReader
      self._ppChain = PreProcReader().load(s)
    else:
      self._ppChain = s


  def initialize( self ):


    from saphyra import JobContext
    # Create the job context
    self.setContext( JobContext() )


    # Initialize the list of pos processor algorithms
    for proc in self.posproc:
      # Set the context into algorithm
      proc.setContext(self.getContext())
      #proc.setStoreGateSvc( self._storegate )
      # Set the logger output level
      proc.level = self.level

      if proc.initialize().isFailure():
        MSG_ERROR(self, "Iniitalizing pos processor tool: %s", proc.name())
        return StatusCode.FAILURE


      # This is not be critical since we can retrieve all data into the output file
      if self.db():
        if self.db().initialize().isFailure():
          MSG_ERROR( self, "Data base connection failed...")
          self._db = None


    return StatusCode.SUCCESS






  def execute( self ):


    for isort, sort in enumerate( self._sorts ):

      # get the current kfold and train, val sets
      x_train, x_val, y_train, y_val, self._index_from_cv = self.pattern_g( self._pattern_generator, self._crossval, sort )


      # Pre processing step
      if self._ppChain.takesParamsFromData:
        MSG_DEBUG( self, "Take parameters from train set..." )
        self._ppChain.takeParams( x_train )

      MSG_INFO( self, "Pre processing train set with %s", self._ppChain )
      x_train = self._ppChain( x_train )

      MSG_INFO( self, "Pre processing validation set with %s", self._ppChain )
      x_val = self._ppChain( x_val )



      for imodel, model in enumerate( self._models ):

        for init in self._inits:

          # force the context is empty for each training
          self.getContext().clear()

          self.getContext().setHandler( "taskName", self._taskName      )
          self.getContext().setHandler( "jobId", self._jobId            )


          self.getContext().setHandler( "crossval", self._crossval      )
          self.getContext().setHandler( "index"   , self._index_from_cv )
          self.getContext().setHandler( "valData" , (x_val, y_val)      )
          self.getContext().setHandler( "trnData" , (x_train, y_train)  )


          # copy the model to a new pointer and make
          # the compilation on loop time
          model_for_this_init = clone_model(model)
          try:
            model_for_this_init.compile( self._optimizer,
                      loss = self._loss,
                      # protection for functions or classes with internal variables
                      # this copy avoid the current training effect the next one.
                      metrics = deepcopy(self.metrics),
                      )
            model_for_this_init.summary()
          except RuntimeError as e:
            MSG_FATAL( self, "Compilation model error: %s" , e)


          MSG_INFO( self, "Training model id (%d) using sort (%d) and init (%d)", self._id_models[imodel], sort, init )
          MSG_INFO( self, "Train Samples      :  (%d, %d)", len(y_train[y_train==1]), len(y_train[y_train==0]))
          MSG_INFO( self, "Validation Samples :  (%d, %d)", len(y_val[y_val==1]),len(y_val[y_val==0]))

          self.getContext().setHandler( "model"   , model_for_this_init )
          self.getContext().setHandler( "sort"    , sort                )
          self.getContext().setHandler( "init"    , init                )
          self.getContext().setHandler( "imodel"  , self._id_models[imodel])

          callbacks = deepcopy(self.callbacks)
          for c in callbacks:
            if hasattr(c, 'set_validation_data'):
              c.set_validation_data( (x_val,y_val) )


          start = datetime.now()

          # Training
          history = model_for_this_init.fit(x_train, y_train,
                              epochs          = self._epochs,
                              batch_size      = self._batch_size,
                              verbose         = True,
                              validation_data = (x_val,y_val),
                              # copy protection to avoid the interruption or interference
                              # in the next training (e.g: early stop)
                              callbacks       = callbacks,
                              class_weight    = compute_class_weight('balanced',np.unique(y_train),y_train) if self._class_weight else None,
                              shuffle         = True).history

          end = datetime.now()
          self.getContext().setHandler("time" , end-start)


          if not self._save_history:
            # NOTE: overwrite to slim version. This is used to reduce the output size
            history = {}

          self.getContext().setHandler( "history", history )


          # prometheus like...
          for proc in self.posproc:
            MSG_INFO( self, "Executing the pos processor %s", proc.name() )
            if proc.execute( self.getContext() ).isFailure():
              MSG_ERROR(self, "There is an erro in %s", proc.name())

          # add the tuned parameters to the output file
          self._tunedData.attach_ctx( self.getContext() )


          if self.db():
            self.db().execute( self.getContext() )


          # Clear everything for the next init
          K.clear_session()


      # You must clean everythin before reopen the dataset
      self.getContext().clear()
      # Clear the keras once again just to be sure
      K.clear_session()



    return StatusCode.SUCCESS



  def finalize( self ):

    for proc in self.posproc:
      if proc.finalize().isFailure():
        MSG_ERROR(self, "There is a problem to finalize the pos processor: %s", proc.name() )
    try:
      # prepare to save the tuned data
      self._tunedData.setDBContext( self._dbcontext )
      self._tunedData.save( self._outputfile )
    except Exception as e:
      MSG_FATAL( self, "Its not possible to save the tuned data: %s" , e )
    # Save all root objects in the store gate service
    #self._storegate.write()
    return StatusCode.SUCCESS





  def pattern_g( self, generator, crossval, sort ):
    # If the index is not set, you muat run the cross validation Kfold to get the index
    # this generator must be implemented by the user
    return generator(crossval, sort)




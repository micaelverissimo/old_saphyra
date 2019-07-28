

__all__ = ['PandasJob']

from Gaugi.messenger import Logger, LoggingLevel
from Gaugi.messenger.macros import *
from Gaugi import StatusCode,  checkForUnusedVars, retrieve_kw
from Gaugi.gtypes import NotSet
from keras.models import clone_model
from copy import deepcopy
from sklearn.utils.class_weight import compute_class_weight
import numpy as np

from saphyra.posproc import Summary

class PandasJob( Logger ):

  def __init__(self , inputfile=None, **kw ):

    Logger.__init__(self,  **kw)
   
    self._optimizer = retrieve_kw( kw, 'optimizer'  , 'adam'                )
    self._loss      = retrieve_kw( kw, 'loss'       , 'binary_crossentropy' )
    self._epochs    = retrieve_kw( kw, 'epochs'     , 1000                  )
    self._batch_size= retrieve_kw( kw, 'batch_size' , 1024                  )
    self.callbacks  = retrieve_kw( kw, 'callbacks'  , []                    )
    self.posproc    = retrieve_kw( kw, 'posproc'    , []                    )
    self.metrics    = retrieve_kw( kw, 'metrics'    , []                    )
    self.models     = retrieve_kw( kw, 'models'     , []                    )
    self._sorts     = retrieve_kw( kw, 'sorts'      , []                    )
    self._inits     = retrieve_kw( kw, 'inits'      , []                    )
    self.crossval   = retrieve_kw( kw, 'crossval'   , NotSet                )
    self.data       = retrieve_kw( kw, 'data'       , NotSet                )
    self.target     = retrieve_kw( kw, 'target'     , NotSet                )
    self._verbose   = retrieve_kw( kw, 'verbose'    , True                  )
    self._class_weight = retrieve_kw( kw, 'class_weight' , False            )

    from saphyra  import PreProcChain_v1, NoPreProc
    self.ppChain    = retrieve_kw( kw, 'ppChain'    , PreProcChain_v1([NoPreProc()]))

    
    job_auto_config = retrieve_kw( kw, 'job'        , NotSet                )
    # read the job configuration from file
    if job_auto_config:
      MSG_INFO( self, 'Reading job configuration from: %s', job_auto_config )
      from saphyra.readers import JobReader
      job = JobReader().load( job_auto_config )
      # retrive sort/init lists from file
      self._sorts = job.get_sorts()
      self._inits = job.get_inits()

    # get all parameters to used in the output step
    from saphyra.readers.versions import TunedData_v1
    self._tunedData = retrieve_kw( kw, 'tunedData'  , TunedData_v1()        )
    self._outputfile= retrieve_kw( kw, 'outputfile' , 'tunedDisc'           )

   
    checkForUnusedVars(kw)

    if type(self._inits) is int:
      self._inits = range(self._inits)

    self._context = NotSet


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
  def models(self):
    return self._models

  @models.setter
  def models( self, s ):
    if type(s) is str:
      from saphyra.readers import ModelReader
      self._models = ModelReader().load( s )
    else:
      self._models = s

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

    # Create the storegate for root objects
    from Gaugi.storage import StoreGate
    MSG_INFO( self, "Creating StoreGate...")
    self._storegate = StoreGate( self._outputfile , level = self.level)
    # Attach into the context
    



    # Initialize the list of pos processor algorithms
    for proc in self.posproc:
      # Set the context into algorithm
      proc.setContext(self.getContext())
      proc.setStoreGateSvc( self._storegate )
      # Set the logger output level
      proc.level = self.level

      if proc.initialize().isFailure():
        MSG_ERROR(self, "Iniitalizing pos processor tool: %s", proc.name())
        return StatusCode.FAILURE



    return StatusCode.SUCCESS






  def execute( self ):

    # get all indexs that will be used in the cross validation data split.
    index = [(train_index, val_index) for train_index, val_index in self._crossval.split(self.data,self.target)]


    for imodel, model in enumerate( self._models ):

      for isort, sort in enumerate( self._sorts ):

        # get the current kfold
        x_train = self.data[index[sort][0]]
        y_train = self.target[index[sort][0]]
        x_val   = self.data[index[sort][1]]
        y_val   = self.target[index[sort][1]]
        
        # Pre processing step
        if self._ppChain.takesParamsFromData:
          MSG_DEBUG( self, "Take parameters from train set..." )
          self._ppChain.takeParams( x_train )

        MSG_INFO( self, "Pre processing train set with %s", self._ppChain )
        x_train = self._ppChain( x_train )

        MSG_INFO( self, "Pre processing validation set with %s", self._ppChain )
        x_val = self._ppChain( x_val )



        
        for init in self._inits:  

          # force the context is empty for each training
          self.getContext().clear()

          self.getContext().setHandler( "crossval", self._crossval )
          self.getContext().setHandler( "index", index)
          self.getContext().setHandler( "valData", (x_val, y_val) )
          self.getContext().setHandler( "trnData", (x_train, y_train) )
          
          
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

         
          MSG_INFO( self, "Training model (%d) using sort (%d) and init (%d)", imodel, isort, init )
          MSG_INFO( self, "Train Samples      :  (%d, %d)", len(y_train[y_train==1]), len(y_train[y_train==0]))
          MSG_INFO( self, "Validation Samples :  (%d, %d)", len(y_val[y_val==1]),len(y_val[y_val==0]))


          self.getContext().setHandler( "model"   , model_for_this_init )
          self.getContext().setHandler( "sort"    , sort                )
          self.getContext().setHandler( "init"    , init                )
          self.getContext().setHandler( "imodel"  , imodel              )

          k = compute_class_weight('balanced',np.unique(y_train),y_train) if self._class_weight else None

          # Training
          history = model_for_this_init.fit(x_train, y_train, 
                              epochs          = self._epochs, 
                              batch_size      = self._batch_size, 
                              verbose         = self._verbose, 
                              validation_data = (x_val,y_val), 
                              # copy protection to avoid the interruption or interference 
                              # in the next training (e.g: early stop)
                              callbacks       = deepcopy(self.callbacks),
                              class_weight    = compute_class_weight('balanced',np.unique(y_train),y_train) if self._class_weight else None,
                              shuffle         = True).history


          self.getContext().setHandler( "history", history )

          
          # prometheus like...
          for proc in self.posproc:
            MSG_INFO( self, "Executing the pos processor %s", proc.name() )
            if proc.execute( self.getContext() ).isFailure():
              MSG_ERROR(self, "There is an erro in %s", proc.name())

          # add the tuned parameters to the output file
          self._tunedData.attach_ctx( self.getContext() )



    return StatusCode.SUCCESS



  def finalize( self ):


    for proc in self.posproc:
      if proc.finalize().isFailure():
        MSG_ERROR(self, "There is a problem to finalize the pos processor: %s", proc.name() )

    try:
      # prepare to save the tuned data
      self._tunedData.save( self._outputfile )
    except e:
      MSG_FATAL( self, "Its not possible to save the tuned data: %s" , e )

    # Save all root objects in the store gate service
    self._storegate.write()

    return StatusCode.SUCCESS



  # TODO: for generator purpose
  def execute_g(self):

    return StatusCode.SUCCESS


  def getContext(self):
    return self._context


  def setContext(self, ctx):
    self._context = ctx





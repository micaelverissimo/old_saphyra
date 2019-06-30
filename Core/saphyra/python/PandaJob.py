

__all__ = ['PandaJob']

from Gaugi.messenger import Logger, LoggingLevel
from Gaugi.messenger.macros import *
from Gaugi import StatusCode,  checkForUnusedVars, retrieve_kw
from Gaugi.gtypes import NotSet



class PandaJob( Logger ):

  def __init__(self , inputfile=None, **kw ):

    Logger.__init__(self,  **kw)
   
    self._optimizer = retrieve_kw( kw, 'optimizer'  , 'adam'                )
    self._loss      = retrieve_kw( kw, 'loss'       , 'binary_crossentropy' )
    self._epochs    = retrieve_kw( kw, 'epochs'     , 1000                  )
    self._batch_size= retrieve_kw( kw, 'batch_size' , 1024                  )
    self.callbacks  = retrieve_kw( kw, 'callbacks'  , []                    )
    self.metrics    = retrieve_kw( kw, 'metrics'    , []                    )
    self._models    = retrieve_kw( kw, 'models'     , []                    )
    self._sorts     = retrieve_kw( kw, 'sorts'      , []                    )
    self._inits     = retrieve_kw( kw, 'inits'      , []                    )
    self._crossval  = retrieve_kw( kw, 'crossval'   , NotSet                )
    self._verbose   = retrieve_kw( kw, 'verbose'    , True                  )
    
    from saphyra.preproc import PreProcChain_v1, NoPreProc
    self._ppChain   = retreive_kw( kw, 'ppChain'    , PreProcChain_v1([NoPreProc()]))

    # get all parameters to used in the output step
    from saphyra.readers.versions import TunedData_v1
    self._tunedData = retrieve_kw( kw, 'tunedData'  , TunedData_v1()        )
    self._outputfile= retrieve_kw( kw, 'outputfile', 'tunedDisc'            )

    inputfile = retrieve_kw( kw, 'inputfile' , NotSet)
    checkForUnusedVars(kw)

    if inputfile:
      MSG_INFO( self, 'Reading job configuration from: %s', inputfile )
      from saphyra.readers import JobReader
      job = JobReader.load( s )
      # retrive sort/init lists from file
      self._sorts = job.get_sorts()
      self._inits = job.get_inits()

    # hold the training
    self.data = NotSet
    self.target = NotSet

    if type(self._inits) is int:
      self._inits = range(self._inits)


  @property
  def model(self):
    return self._models

  @model.setter
  def model( self, s ):
    if type(s) is str:
      from saphyra.readers import ModelReader
      self._models = ModelReader.load( s )
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

  @ppChain.setter
  def ppChain( self, s):
    if type(s) is str:
      from saphyra.readers import PreProcReader
      self._ppChain = PreProcReader.load(s)
    else:
      self._ppChain = s


  def initialize( self ):


    # Compile all keras structs
    for imodel, model in enumerate(self._models):
      MSG_INFO( self, "Compiling model with index (%d).", imodel)
      try:
        model.compile( self._optimizer, 
                     loss = self._loss,
                     metrics = self.metrics,
                     )
        model.summary()
      except RuntimeError, e:
        MSG_FATAL( self, "Compilation model error: %s" , e)

    # check the cross val method
    if not self._crossval:
      MSG_WARNING( self, "The cross validation method is not set. Set this before execute this job." )
    


    return StatusCode.SUCCESS






  def execute( self ):


    # get all indexs that will be used in the cross validation data split.
    indexs = [(train_index, val_index) for train_index, val_index in self._crossval.split(self.data,self.target)]

    for imodel, model in enumerate( self._models ):

      for isort, sort in enumerate( self._sorts ):

        # get the current kfold
        x_train = self.data[indexs[sort][0]]
        y_train = self.target[indexs[sort][0]]
        x_val   = self.data[indexs[sort][1]]
        y_val   = self.target[indexs[sort][1]]

        # Pre processing step
        if self._ppChain.takesParamsFromData:
          MSG_DEBUG( self, "Take parameters from train set..." )
          self._ppChain.takeParams( x_train )

        MSG_INFO( self, "Pre processing train set with %s", self._ppChain )
        x_train = self._ppChain( x_train )

        MSG_INFO( self, "Pre processing validation set with %s", self._ppChain )
        x_val = self._ppChain( x_val )

        for init in self._inits:

          MSG_INFO( self, "Training model (%d) using sort (%d) and init (%d)", imodel, isort, init )
          # Training
          history = model.fit(x_train, y_train, 
                              epochs          = self._epochs, 
                              batch_size      = self._batch_size, 
                              verbose         = self._verbose, 
                              validation_data = (x_val,y_val), 
                              callbacks       = self.callbacks, 
                              shuffle         = True)

          # add the tuned parameters to the output file
          self._tunedData.attach( imodel, sort, init, model, history )



    return StatusCode.SUCCESS



  def finalize( self ):

    try:
      # prepare to save the tuned data
      self._tunedData.save( self._outputfile )
    except e:
      MSG_FATAL( self, "Its not possible to save the tuned data: %s" , e )

    return StatusCode.SUCCESS








__all__ = ['KerasWrapper']

import numpy as np
from Gaugi import ( Logger, LoggingLevel, NotSet, checkForUnusedVars, retrieve_kw,  expandFolders )
from Gaugi.messenger.macros import *
from TuningTools.coreDef import coreConf, npCurrent, TuningToolCores
from libsaphyra import genRoc as c_genRoc

def _checkSecondaryPP( data, pp=None ):
  if not (pp is NotSet or pp is None):
    if type(pp) is list:
      return [ _pp(data) for _pp in pp ]
    else:
      return pp(data)
  else:
    return data




class KerasWrapper( Logger ):

  def __init__(self, **kw ):    
    Logger.__init__( self, **kw )
    self._model         = retrieve_kw( kw, 'model'                , NotSet                          )
    self._secondaryPP   = retrieve_kw( kw, 'secondaryPP'          , NotSet                          )
    from keras.optimizers import RMSprop, SGD, Adam
    adam = Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-08, decay=0.0)
    self._optmin_alg    = retrieve_kw( kw, 'optmin_alg'           , Adam                             )
    self._costFunction  = retrieve_kw( kw, 'costFunction'         , 'mean_squared_error'            ) # 'binary_crossentropy'
    self._metrics       = retrieve_kw( kw, 'metrics'              , ['accuracy', ]                  )
    self._shuffle       = retrieve_kw( kw, 'shuffle'              , True                            )
    self._multiStop     = retrieve_kw( kw, 'doMultiStop'          , False                           )
    self._epochs        = retrieve_kw( kw, 'epochs'               , 1000                            )
    self._nFails        = retrieve_kw( kw, 'nFails'               , 25                              )
    showEvo             = retrieve_kw( kw, 'showEvo'              , 10                              )
    self._minibatch_generator = retrieve_kw( kw, 'use_minibatch_generator', NotSet                  )

    from keras.callbacks import TensorBoard
    from time import time
    tensorboard = TensorBoard(log_dir="logs_{}".format(time()))

    from TuningTools.keras_core.callbacks import BinaryClassificationEarlyStopping as sp_stop
    self._callbacks = [
                              # this is default for my binary problem
                              sp_stop( max_patience   = self._nFails,
                                       save_the_best  = True,
                                       level          = self.level,
                                       showEvo        = showEvo,
                                       #val_minibatch_generator = self._minibath_generator
                                      ),
                              # google/tensorflow monitoring
                              tensorboard,
                              ]



    self._history = NotSet
    self._batchSize = 1024                        
    self._verbose = True if self.level is LoggingLevel.VERBOSE else False
    checkForUnusedVars(kw, self._debug )
    del kw
 
  @property
  def batchSize(self):
    return self._batchSize

  @batchSize.setter
  def batchSize(self, v):
    self._batchSize = v

  @property
  def model(self):
    return self._model

  @model.setter
  def model(self, v):
    self._model = v

  def compile(self, model):
    self._model = model
    MSG_DEBUG( self, "Compiling keras model...")
    # force stop reset in the sp_stop callback
    self._callbacks[0].reset()
    self._model.compile(  loss = self._costFunction,
                          optimizer = self._optmin_alg,
                          metrics = self._metrics )
    self._model.summary()


  def fit(self, trnData, trnTarget, valData, valTarget):
    
    if type(valData) is list:
      for idx, ds in enumerate(valData):
        MSG_INFO(self, "Dataset %d with [%d, %d]", idx,ds.shape[0],ds.shape[1])
    else:
      MSG_INFO(self, "Dataset 0 with [%d, %d]", valData.shape[0],valData.shape[1])

    from TuningTools.keras_core.utilities import to_categorical
    MSG_INFO(self, "Batch fitting size is: %d",self._batchSize)
    self._history = self._model.fit( _checkSecondaryPP(trnData, self._secondaryPP)
                                    , to_categorical(trnTarget,num_classes=2) if self._costFunction is 'binary_crossentropy' else trnTarget
                                    , validation_data = ( _checkSecondaryPP(valData,self._secondaryPP) , \
                                      to_categorical(valTarget,num_classes=2) if self._costFunction is 'binary_crossentropy' else valTarget )
                                    , epochs          = self._epochs
                                    , batch_size      = self._batchSize
                                    , callbacks       = self._callbacks
                                    , verbose         = True
                                    , shuffle         = self._shuffle
                                    )
    MSG_INFO(self, "Finished the fit.")
    return self._history




  def evaluate(self, trnData, trnTarget, valData, valTarget, tstData=npCurrent.fp_array([]), 
                                                             tstTarget=npCurrent.fp_array([]), 
                                                             use_test = False,
                                                             batch_size = 5000):
    # Map the neural network output to [-1,1] range
    def _checkOutput( output ):
      return (output[:,1]-0.5)*2 if output.shape[1]>1 else output

    trnOutput = _checkOutput( self._model.predict(_checkSecondaryPP(trnData,self._secondaryPP),batch_size=batch_size) )
    valOutput = _checkOutput( self._model.predict(_checkSecondaryPP(valData,self._secondaryPP),batch_size=batch_size) )

    from TuningTools.Neural import Roc as RocObject
    if tstData.size:
      tstOutput = _checkOutput( self._model.predict(_checkSecondaryPP(tstData,self._secondaryPP),batch_size=batch_size) )
      output = np.concatenate([trnOutput,valOutput,tstOutput] )
      target = np.concatenate([trnTarget,valTarget,tstTarget] )
      signal = tstOutput[np.where(tstTarget==1)]; noise = tstOutput[np.where(tstTarget==-1)]
      tst_roc = RocObject( c_genRoc(signal, noise, 1, -1, 0.01) )
    else:
      output = np.concatenate([trnOutput,valOutput] )
      target = np.concatenate([trnTarget,valTarget] )
      signal = valOutput[np.where(valTarget==1)]; noise = valOutput[np.where(valTarget==-1)]
      tst_roc = RocObject( c_genRoc(signal, noise, 1, -1, 0.01) )

    signal = output[np.where(target==1)]; noise = output[np.where(target==-1)]
    op_roc = RocObject( c_genRoc(signal, noise, 1, -1, 0.01) )
    return op_roc, tst_roc

  


 


__all__ = ['BinaryClassificationEarlyStopping']

from keras.callbacks import Callback
from Gaugi import Logger, LoggingLevel, NotSet, checkForUnusedVars, retrieve_kw
from Gaugi.messenger.macros import *
from libsaphyra import genRoc as c_genRoc
import numpy as np



class BinaryClassificationEarlyStopping(Callback,Logger):

  def __init__(self, **kw):
    
    # initialize all base objects
    super(Callback, self).__init__()
    Logger.__init__(self,kw)
    self.__showEvo              = retrieve_kw( kw, 'showEvo'            , None    )
    self.__save_the_best        = retrieve_kw( kw, 'save_the_best'      , True    )
    self.__minimal_local_batch  = retrieve_kw( kw, 'minimal_local_batch', 1024    )
    self.__max_patience         = retrieve_kw( kw, 'max_patience'       , 25      )
    self.__val_generator        = retrieve_kw( kw, 'val_generator'      , NotSet  )
    checkForUnusedVars( kw, self._warning )

    self.__verbose = True if self._level is LoggingLevel.VERBOSE else False
    self.__patience_count = 0
    self.__current_score = 0.0
    self.__best_weights = NotSet


  def reset(self):
    self.__patience_count = 0
    self.__current_score = 0.0
    self.__best_weights = NotSet
 

  def on_epoch_end(self, epoch, logs={}):
    
    # get the number of datasets is in the validation and where is the target position in the
    # keras tensor.
    n_datasets, target_index = self.__how_many_datasets()
    target = self.validation_data[target_index]

    # check if the model uses two outputs (cross entropy method)
    if target.shape[1] > 1:
      from TuningTools.keras_core.utilities import inverse_to_categorical
      target = inverse_to_categorical(target)

    s_idx = np.where(target== 1)[0] # get the target positive index
    b_idx = np.where(target==-1)[0] # get the target negative index
   
    # get all the positive (target) samples for each dataset
    local_data = [ self.validation_data[di][s_idx] for di in range(n_datasets) ]
    # generate the neural output for all positive cases
    local_batch = self.__minimal_local_batch if local_data[0].shape[0] > self.__minimal_local_batch else local_data[0].shape[0]         
    y_pred_s = self.model.predict(local_data if n_datasets>1 else local_data[0],  batch_size=local_batch, verbose=self.__verbose)
    
    # get all the negative (target) samples for each dataset
    local_data = [ self.validation_data[di][b_idx] for di in range(n_datasets) ]
    # generate the neural output for all negative cases
    local_batch = self.__minimal_local_batch if local_data[0].shape[0] > self.__minimal_local_batch else local_data[0].shape[0]         
    y_pred_b = self.model.predict(local_data if n_datasets>1 else local_data[0], batch_size=local_batch, verbose=self.__verbose)
   
    # check if the model uses two outputs (cross entropy method)
    if y_pred_s.shape[1]>1:
      # remap the output to [-1,1] range
      y_pred_s = (y_pred_s[:,1]-0.5)*2
      y_pred_b = (y_pred_b[:,1]-0.5)*2

    # generate the roc curve (c++ embeded)
    sp, det, fa, thresholds = c_genRoc( y_pred_s, y_pred_b, 1, -1, 0.01 )
    
    # get the max sp value (knee of the curve)
    knee = np.argmax( sp )
    sp_max = sp[knee]

    # check ig the current sp score is maximal
    if sp_max > self.__current_score:
      MSG_DEBUG( self, 'Best SP reached is: %1.4f (DET=%1.4f, FA=%1.4f)', sp_max*100,det[knee]*100, fa[knee]*100 )
      self.__current_score=sp_max
      self.__patience_count=0
      if self.__save_the_best:
      	self.__best_weights = self.model.get_weights()
    else:
      self.__patience_count+=1

    # display the current training values
    if self.__showEvo and not(epoch % self.__showEvo):
      MSG_INFO(self, 'Epoch %d/%d: loss = %1.4f, acc = %1.4f, val_loss = %1.4f, val_acc = %1.4f and [Patience = %d/%d] with SP = %1.4f',
                      epoch+1, self.params['epochs'], logs['loss'], logs['acc'], logs['val_loss'], logs['val_acc'],
                      self.__patience_count, self.__max_patience, self.__current_score)

    # Stop the fitting
    if self.__patience_count > self.__max_patience:
      MSG_INFO(self, 'Stopping the Training by SP...')
      self.model.stop_training = True


  def on_train_end(self, logs={}):
    # Loading the best model
    if self.__save_the_best:
      MSG_INFO(self, 'Reload the best configuration into the current model...')
      self.model.set_weights( self.__best_weights )
    MSG_INFO(self, "Finished tuning")

    
  def __how_many_datasets(self):
    # Protection for batch and event number for signal and merge case
    # Keras validation format: [data_1, ... , data_i, target, dummy(?), float(?)]
    # minimal case is i=1 and size 4. If size > 4 than we have more than one input (Merge case)
    if len(self.validation_data) > 4:
      n_datasets = len(self.validation_data)-3
      target_index = n_datasets+1
    else:
      n_datasets=1; target_index=1
    return n_datasets, target_index

  



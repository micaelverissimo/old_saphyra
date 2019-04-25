
__all__ = ['EarlyStopping']

from keras.callbacks import Callback

from Gaugi import Logger, LoggingLevel, NotSet, checkForUnusedVars
from libTuningTools import genRoc
import numpy as np

class EarlyStopping(Callback,Logger):

  def __init__(self, display=1, doMultiStop=False, patience = 25, save_the_best=True,  val_generator=None , **kw):
    
    # initialize all base objects
    super(Callback, self).__init__()
    Logger.__init__(self,**kw)
    # number of max fails
    self._patience = {'max':patience,'score':0, 'loss':0}
    self._display = display
    self._save_the_best = save_the_best
    # used to hold the best configs
    self._best_weights = None
    # used to hold the SP value
    self._current_score = 0.0
    self._val_generator=val_generator



  def on_epoch_end(self, epoch, logs={}):
   
    # Protection for batch and event number for signal and merge case
    # NOTE: Keras validation format: [data_1, ... , data_i, target, dummy(?), float(?)]
    # minimal case is i=1 and size 4. If size > 4 than we have more than one input (Merge case)
    if self._val_generator:
      
      y_pred_s=[];  y_pred_b=[]
      for mini_batch in range(len(self._val_generator)):
        data, target = self._val_generator[mini_batch]
        s_idx = np.where(target==1)[0]
        b_idx = np.where(target==-1)[0]
        y_pred_s_mini_batch = self.model.predict(data[s_idx],
                                  batch_size=len(s_idx), verbose=True if self._level is LoggingLevel.VERBOSE else False).reshape(-1)
        y_pred_b_mini_batch = self.model.predict(data[b_idx],
                                  batch_size=len(b_idx), verbose=True if self._level is LoggingLevel.VERBOSE else False).reshape(-1)
        
        y_pred_s.extend( y_pred_s_mini_batch.tolist())
        y_pred_b.extend( y_pred_b_mini_batch.tolist())
      y_pred_s=np.array(y_pred_s)
      y_pred_b=np.array(y_pred_b)
    else: 
      if len(self.validation_data[0]) > 4:
        
        s_idx = np.where(self.validation_data[len(self.validation_data)-2-1]==1)[0]
        b_idx = np.where(self.validation_data[len(self.validation_data)-2-1]==-1)[0]
 
        local_data = [ self.validation_data[di][s_idx] for di in range(len(self.validation_data)-3) ]
        local_batch = 1024*10 if local_data[0].shape[0] > 1024*10 else local_data[0].shape[0] 
        y_pred_s = self.model.predict(local_data, batch_size=local_batch, verbose=True if self._level is LoggingLevel.VERBOSE else False)
      
        local_data = [ self.validation_data[di][b_idx] for di in range(len(self.validation_data)-3) ]
        local_batch = 1024*10 if local_data[0].shape[0] > 1024*10 else local_data[0].shape[0]
        y_pred_b = self.model.predict(local_data, batch_size=local_batch, verbose=True if self._level is LoggingLevel.VERBOSE else False)
 
      else:
        s_idx = np.where(self.validation_data[1]==1)[0]
        b_idx = np.where(self.validation_data[1]==-1)[0]
        local_batch = 1024*10 if self.validation_data[0][s_idx].shape[0] > 1024*10 else self.validation_data[0][s_idx].shape[0]
        y_pred_s = self.model.predict(self.validation_data[0][s_idx],
                                    batch_size=local_batch, verbose=True if self._level is LoggingLevel.VERBOSE else False)
        local_batch = 1024*10 if self.validation_data[0][b_idx].shape[0] > 1024*10 else self.validation_data[0][b_idx].shape[0]
        y_pred_b = self.model.predict(self.validation_data[0][b_idx],
                                    batch_size=1024, verbose=True if self._level is LoggingLevel.VERBOSE else False)
   
    
    y_true = np.concatenate( ( np.ones(len(y_pred_s)),np.ones(len(y_pred_b) )*-1) )
    y_pred = np.concatenate( ( y_pred_s,y_pred_b ) ) 
    #y_pred = self.model.predict(self._directValAccess[0],batch_size=1024*200, verbose=True if self._level is LoggingLevel.VERBOSE else False)
    
    sp, det, fa, thresholds = self.roc( y_pred, y_true )
    # get the max sp value
    knee = np.argmax( sp ); sp_max = sp[knee]
    
    # check ig the current sp score is maximal
    if sp_max > self._current_score:
      self._logger.debug( ('Best SP reached is: %1.4f (DET=%1.4f, FA=%1.4f)')%(sp_max*100,det[knee]*100, fa[knee]*100) )
      self._current_score=sp_max
      self._patience['score']=0
      if self._save_the_best:
      	self._best_weights = self.model.get_weights()
    else:
      self._patience['score']+=1

    if self._display and not(epoch % self._display):
      self._logger.info('Epoch %d/%d: loss = %1.4f, acc = %1.4f, val_loss = %1.4f, val_acc = %1.4f and [Patience = %d/%d]',
          epoch+1, self.params['epochs'], logs['loss'], logs['acc'], logs['val_loss'], logs['val_acc'],
          self._patience['score'], self._patience['max'])

    # Stop the fitting
    if self._patience['score'] > self._patience['max']:
      self._logger.info('Stopping the Training by SP...')
      self.model.stop_training = True


  def on_train_end(self, logs={}):
    # Loading the best model
    if self._save_the_best:
      self._logger.info('Reload the best configuration into the current model...')
      self.model.set_weights( self._best_weights )
    self._logger.info("Finished tuning")
 

  @classmethod
  def roc(cls, pred, target, resolution=0.01):
    signal = pred[np.where(target==1)]; noise = pred[np.where(target==-1)]
    return genRoc( signal, noise, 1, -1, resolution)
      



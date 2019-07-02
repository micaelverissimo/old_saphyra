
__all__ = ["sp"]

from keras.callbacks import Callback
from Gaugi.messenger.macros import *
from Gaugi.messenger import Logger
from Gaugi.gtypes import NotSet
from sklearn.metrics import roc_curve
import numpy as np


class sp(Callback, Logger):
  
  def __init__(self, verbose=False,save_the_best=False, patience=False, **kw):
    super(Callback, self).__init__()
    Logger.__init__(self,**kw)
    self.__verbose = verbose
    self.__patience = patience
    self.__ipatience = 0
    self.__best_sp = 0.0
    self.__save_the_best = save_the_best
    self.__best_weights = NotSet
    self.__best_epoch = 0
  



  def on_epoch_end(self, epoch, logs={}):


    y_true = self.validation_data[1]
    y_pred = self.model.predict(self.validation_data[0],batch_size=1024).ravel()
    fa, pd, thresholds = roc_curve(y_true, y_pred)

    sp = np.sqrt(  np.sqrt(pd*(1-fa)) * (0.5*(pd+(1-fa)))  )
    
    
    
    
    knee = np.argmax(sp)
    logs['max_sp_val'] = sp[knee]
    logs['max_sp_false_alarm_val'] = fa[knee]
    logs['max_sp_prob_detection_val'] = pd[knee]
    if self.__verbose: 
      print( (' - val_sp: %1.4f (fa:%1.4f,pd:%1.4f)') % (sp[knee],fa[knee],pd[knee]) )


    if sp[knee] > self.__best_sp:
      self.__best_sp = sp[knee]
      if self.__save_the_best:
        MSG_INFO(self, 'save the best configuration here...' )
        self.__best_weights =  self.model.get_weights()
        logs['max_sp_best_epoch_val'] = epoch
      self.__ipatience = 0
    else:
      self.__ipatience += 1

    if self.__ipatience > self.__patience:
      MSG_INFO( self, 'Stopping the Training by SP...')
      self.model.stop_training = True



  def on_train_end(self, logs={}):
    # Loading the best model
    if self.__save_the_best:
      MSG_INFO( self, 'Reload the best configuration into the current model...')
      try:
        self.model.set_weights( self.__best_weights )
      except:
        MSG_ERROR(self, "Its not possible to set the weights. Maybe there is some" +
            "problem with the train split (check the quantity and kfold method.)")


    MSG_INFO( self, "Finished tuning")





__all__ = ["sp"]

from tensorflow.keras.callbacks import Callback
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
    self._validation_data = NotSet

  def set_validation_data( self, v ):
    self._validation_data = v

  # This computes dSP/dFA (partial derivative of SP respect to FA)
  def __get_partial_derivative_fa (self, fa, pd):
    c = 0.353553
    up = -(pd * (pd - fa + 1))/(2 * np.sqrt(pd*(1-fa))) - np.sqrt(pd*(1-fa))
    down = np.sqrt( np.sqrt(pd * (1-fa)) * (pd - fa + 1) )
    return c * up / down

  # This computes dSP/dPD (partial derivative of SP respect to PD)
  def __get_partial_derivative_pd (self, fa, pd):
    c = 0.353553
    up = ((1-fa)*(pd-fa+1))/(2*np.sqrt(pd*(1-fa))) + np.sqrt(pd*(1-fa))
    down = np.sqrt( np.sqrt(pd*(1-fa)) * (pd-fa+1) )    
    return c * up / down

  def on_epoch_end(self, epoch, logs={}):

    if self._validation_data: # Tensorflow 2.0
      y_true = self._validation_data[1]
      y_pred = self.model.predict(self._validation_data[0],batch_size=1024).ravel()
    else:
      y_true = self.validation_data[1]
      y_pred = self.model.predict(self.validation_data[0],batch_size=1024).ravel()

    # Computes SP
    fa, pd, thresholds = roc_curve(y_true, y_pred)
    sp = np.sqrt(  np.sqrt(pd*(1-fa)) * (0.5*(pd+(1-fa)))  )

    knee = np.argmax(sp)

    # Computes partial derivatives
    partial_pd = self.__get_partial_derivative_pd(fa[knee], pd[knee])
    partial_fa = self.__get_partial_derivative_fa(fa[knee], pd[knee])

    logs['max_sp_val'] = sp[knee]
    logs['max_sp_fa_val'] = fa[knee]
    logs['max_sp_pd_val'] = pd[knee]
    logs['max_sp_partial_derivative_fa_val'] = partial_fa
    logs['max_sp_partial_derivative_pd_val'] = partial_pd

    if self.__verbose:
      print (" - val_sp: {:.4f} (fa:{:.4f},pd:{:.4f}), patience: {}, dSP/dFA: {:.4f}, dSP/dPD: {:.4f}".format(sp[knee],fa[knee],pd[knee], self.__ipatience, partial_fa, partial_pd))


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




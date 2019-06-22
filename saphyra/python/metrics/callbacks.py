
__all__ = ["sp"]

from keras.callbacks import Callback

class sp(Callback):
  def __init__(self, verbose=False):
    super(Callback, self).__init__()
    self.__verbose = verbose
  

  def on_epoch_end(self, epoch, logs={}):
    from sklearn.metrics import roc_curve
    y_true = self.validation_data[1]
    y_pred = self.model.predict(self.validation_data[0],batch_size=1024).ravel()
    fa, pd, thresholds = roc_curve(y_true, y_pred)
    import numpy as np
    sp = max(np.sqrt(  np.sqrt(pd*(1-fa)) * (0.5*(pd+(1-fa)))  ))
    logs['val_sp'] = sp
    if self.__verbose: 
      print( (' - val_sp: %1.4f') % (sp) )



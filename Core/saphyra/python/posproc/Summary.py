

__all__ = ["Summary"]

from Gaugi.messenger import Logger
from Gaugi.messenger.macros import *
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from sklearn.metrics import roc_auc_score
from sklearn.metrics import mean_squared_error
from sklearn.metrics import roc_curve
import numpy as np

class Summary( Logger ):

  def __init__( self, x_train, y_train, x_val, y_val, **kw ):

    Logger.__init__(self, **kw)
    self._x_train = x_train
    self._x_val = x_val
    self._y_train = y_train
    self._y_val = y_val


  def __call__( self, model ):

    
    d = {}

    MSG_INFO( self, "Starting the train summary..." )

    y_pred = model.predict( self._x_train )
    y_pred_val = model.predict( self._x_val )

    d['auc'] = roc_auc_score(self._y_train, y_pred)
    d['auc_val'] = roc_auc_score(self._y_val, y_pred_val)

    d['mse'] = mean_squared_error(self._y_train, y_pred)
    d['mse_val'] = mean_squared_error(self._y_val, y_pred_val)

    fa, pd, thresholds = roc_curve(self._y_train, y_pred)
    sp = np.sqrt(  np.sqrt(pd*(1-fa)) * (0.5*(pd+(1-fa)))  )
    knee = np.argmax(sp)


    MSG_INFO( self, "Train samples     : Prob. det (%1.4f), False Alarm (%1.4f), SP (%1.4f), AUC (%1.4f) and MSE (%1.4f)",
        pd[knee], fa[knee], sp[knee], d['auc'], d['mse'])
    

    d['max_sp_prob_detection'] = pd[knee]
    d['max_sp_false_alarm'] = fa[knee]
    d['max_sp'] = sp[knee]
    d['roc_prob_detection'] = pd
    d['roc_false_alarm'] = fa


    fa, pd, thresholds = roc_curve(self._y_val, y_pred_val)
    sp = np.sqrt(  np.sqrt(pd*(1-fa)) * (0.5*(pd+(1-fa)))  )
    knee = np.argmax(sp)

    MSG_INFO( self, "Validation Samples: Prob. det (%1.4f), False Alarm (%1.4f), SP (%1.4f), AUC (%1.4f) and MSE (%1.4f)",
        pd[knee], fa[knee], sp[knee], d['auc_val'], d['mse_val'])


    d['max_sp_prob_detection_val'] = pd[knee]
    d['max_sp_false_alarm_val'] = fa[knee]
    d['max_sp_val'] = sp[knee]
    d['roc_prob_detection_val'] = pd
    d['roc_false_alarm_val'] = fa

    return d







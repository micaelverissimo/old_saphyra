

__all__ = ["Summary"]

from Gaugi.messenger import Logger
from Gaugi.messenger.macros import *
from Gaugi import StatusCode
from saphyra import Algorithm
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from sklearn.metrics import roc_auc_score
from sklearn.metrics import mean_squared_error
from sklearn.metrics import roc_curve
import numpy as np

class Summary( Algorithm ):

  def __init__( self, **kw ):
    Algorithm.__init__(self, "Summary", **kw)




  def execute( self, context ):

    
    d = {}
      
    x_train, y_train = context.getHandler("trnData" )
    x_val, y_val     = context.getHandler("valData" )
    model            = context.getHandler("model"    )
    history          = context.getHandler("history")


    MSG_INFO( self, "Starting the train summary..." )

    y_pred = model.predict( x_train )
    y_pred_val = model.predict( x_val )

    # get vectors for operation mode (train+val)
    y_pred_operation = np.concatenate( (y_pred, y_pred_val), axis=0)
    y_operation = np.concatenate((y_train,y_val), axis=0)

    d['auc'] = roc_auc_score(y_train, y_pred)
    d['auc_val'] = roc_auc_score(y_val, y_pred_val)
    d['auc_op'] = roc_auc_score(y_operation, y_pred_operation)


    d['mse'] = mean_squared_error(y_train, y_pred)
    d['mse_val'] = mean_squared_error(y_val, y_pred_val)
    d['mse_op'] = mean_squared_error(y_operation, y_pred_operation)

    # Training
    fa, pd, thresholds = roc_curve(y_train, y_pred)
    sp = np.sqrt(  np.sqrt(pd*(1-fa)) * (0.5*(pd+(1-fa)))  )
    knee = np.argmax(sp)


    MSG_INFO( self, "Train samples     : Prob. det (%1.4f), False Alarm (%1.4f), SP (%1.4f), AUC (%1.4f) and MSE (%1.4f)",
        pd[knee], fa[knee], sp[knee], d['auc'], d['mse'])
    

    d['max_sp_pd'] = pd[knee]
    d['max_sp_fa'] = fa[knee]
    d['max_sp'] = sp[knee]
    d['roc_pd'] = pd
    d['roc_fa'] = fa

    # Validation
    fa, pd, thresholds = roc_curve(y_val, y_pred_val)
    sp = np.sqrt(  np.sqrt(pd*(1-fa)) * (0.5*(pd+(1-fa)))  )
    knee = np.argmax(sp)

    MSG_INFO( self, "Validation Samples: Prob. det (%1.4f), False Alarm (%1.4f), SP (%1.4f), AUC (%1.4f) and MSE (%1.4f)",
        pd[knee], fa[knee], sp[knee], d['auc_val'], d['mse_val'])


    d['max_sp_pd_val'] = pd[knee]
    d['max_sp_fa_val'] = fa[knee]
    d['max_sp_val'] = sp[knee]
    d['roc_pd_val'] = pd
    d['roc_fa_val'] = fa



    # Operation 
    fa, pd, thresholds = roc_curve(y_operation, y_pred_operation)
    sp = np.sqrt(  np.sqrt(pd*(1-fa)) * (0.5*(pd+(1-fa)))  )
    knee = np.argmax(sp)

    MSG_INFO( self, "Operation Samples : Prob. det (%1.4f), False Alarm (%1.4f), SP (%1.4f), AUC (%1.4f) and MSE (%1.4f)",
        pd[knee], fa[knee], sp[knee], d['auc_val'], d['mse_val'])


    d['max_sp_pd_op'] = pd[knee]
    d['max_sp_fa_op'] = fa[knee]
    d['max_sp_op'] = sp[knee]
    d['roc_pd_op'] = pd
    d['roc_fa_op'] = fa

    history['summary'] = d
    
    return StatusCode.SUCCESS






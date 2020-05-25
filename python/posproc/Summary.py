

__all__ = ["Summary"]

from Gaugi.messenger import Logger
from Gaugi.messenger.macros import *
from Gaugi import StatusCode
from saphyra import Algorithm
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from sklearn.metrics import recall_score
from sklearn.metrics import precision_score
from sklearn.metrics import roc_auc_score
from sklearn.metrics import mean_squared_error
from sklearn.metrics import roc_curve
import numpy as np

class Summary( Algorithm ):

  def __init__( self,**kw ):
    Algorithm.__init__(self, "Summary", **kw)


  def execute( self, context ):

    
    d = {}
      
    x_train, y_train = context.getHandler("trnData" )
    x_val, y_val     = context.getHandler("valData" )
    model            = context.getHandler("model"    )
    history          = context.getHandler("history")


    # Get the number of events for each set (train/val). Can be used to approx the number of
    # passed events in pd/fa analysis. Use this to integrate values (approx)
    sgn_total = len( y_train[y_train==1] )
    bkg_total = len( y_train[y_train==0] )
    sgn_total_val = len( y_val[y_val==1] )
    bkg_total_val = len( y_val[y_val==0] )



    MSG_INFO( self, "Starting the train summary..." )

    y_pred = model.predict( x_train )
    y_pred_val = model.predict( x_val )

    # get vectors for operation mode (train+val)
    y_pred_operation = np.concatenate( (y_pred, y_pred_val), axis=0)
    y_operation = np.concatenate((y_train,y_val), axis=0)




    # No threshold is needed
    d['auc'] = roc_auc_score(y_train, y_pred)
    d['auc_val'] = roc_auc_score(y_val, y_pred_val)
    d['auc_op'] = roc_auc_score(y_operation, y_pred_operation)


    # No threshold is needed
    d['mse'] = mean_squared_error(y_train, y_pred)
    d['mse_val'] = mean_squared_error(y_val, y_pred_val)
    d['mse_op'] = mean_squared_error(y_operation, y_pred_operation)


    


    # Here, the threshold is variable and the best values will
    # be setted by the max sp value found in hte roc curve
    # Training
    fa, pd, thresholds = roc_curve(y_train, y_pred)
    sp = np.sqrt(  np.sqrt(pd*(1-fa)) * (0.5*(pd+(1-fa)))  )
    knee = np.argmax(sp)
    threshold = thresholds[knee]

    MSG_INFO( self, "Train samples     : Prob. det (%1.4f), False Alarm (%1.4f), SP (%1.4f), AUC (%1.4f) and MSE (%1.4f)",
        pd[knee], fa[knee], sp[knee], d['auc'], d['mse'])
    

    d['max_sp_pd'] = ( pd[knee], int(pd[knee]*sgn_total), sgn_total)
    d['max_sp_fa'] = ( fa[knee], int(fa[knee]*bkg_total), bkg_total)
    d['max_sp']    = sp[knee]
    d['acc']              = accuracy_score(y_train,y_pred>threshold)
    d['precision_score']  = precision_score(y_train, y_pred>threshold)
    d['recall_score']     = recall_score(y_train, y_pred>threshold)
    d['f1_score']         = f1_score(y_train, y_pred>threshold)



    # Validation
    fa, pd, thresholds = roc_curve(y_val, y_pred_val)
    sp = np.sqrt(  np.sqrt(pd*(1-fa)) * (0.5*(pd+(1-fa)))  )
    knee = np.argmax(sp)
    threshold = thresholds[knee]

    MSG_INFO( self, "Validation Samples: Prob. det (%1.4f), False Alarm (%1.4f), SP (%1.4f), AUC (%1.4f) and MSE (%1.4f)",
        pd[knee], fa[knee], sp[knee], d['auc_val'], d['mse_val'])


    d['max_sp_pd_val'] = (pd[knee], int(pd[knee]*sgn_total_val), sgn_total_val)
    d['max_sp_fa_val'] = (fa[knee], int(fa[knee]*bkg_total_val), bkg_total_val)
    d['max_sp_val'] = sp[knee]
    d['acc_val']              = accuracy_score(y_val,y_pred_val>threshold)
    d['precision_score_val']  = precision_score(y_val, y_pred_val>threshold)
    d['recall_score_val']     = recall_score(y_val, y_pred_val>threshold)
    d['f1_score_val']         = f1_score(y_val, y_pred_val>threshold)


    # Operation 
    fa, pd, thresholds = roc_curve(y_operation, y_pred_operation)
    sp = np.sqrt(  np.sqrt(pd*(1-fa)) * (0.5*(pd+(1-fa)))  )
    knee = np.argmax(sp)
    threshold = thresholds[knee]

    MSG_INFO( self, "Operation Samples : Prob. det (%1.4f), False Alarm (%1.4f), SP (%1.4f), AUC (%1.4f) and MSE (%1.4f)",
        pd[knee], fa[knee], sp[knee], d['auc_val'], d['mse_val'])

    d['threshold_op'] = threshold
    d['max_sp_pd_op'] = ( pd[knee], int( pd[knee]*(sgn_total+sgn_total_val)), (sgn_total+sgn_total_val))
    d['max_sp_fa_op'] = ( fa[knee], int( fa[knee]*(bkg_total+bkg_total_val)), (bkg_total+bkg_total_val))
    d['max_sp_op'] = sp[knee]
    d['acc_op']              = accuracy_score(y_operation,y_pred_operation>threshold)
    d['precision_score_op']  = precision_score(y_operation, y_pred_operation>threshold)
    d['recall_score_op']     = recall_score(y_operation, y_pred_operation>threshold)
    d['f1_score_op']         = f1_score(y_operation, y_pred_operation>threshold)

    history['summary'] = d
    
    return StatusCode.SUCCESS






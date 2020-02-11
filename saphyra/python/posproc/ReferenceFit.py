

__all__ = ["ReferenceFit"]

try:
  xrange
except NameError:
  xrange = range

from saphyra import isTensorFlowTwo
from saphyra import Algorithm
from Gaugi.messenger.macros import *
from Gaugi import StatusCode, progressbar
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from sklearn.metrics import roc_auc_score
from sklearn.metrics import mean_squared_error
from sklearn.metrics import roc_curve
if isTensorFlowTwo():
  from tensorflow.keras import Model
else:
  from keras import Model
import numpy as np
import time
import math

def sp_func(pd, fa):
  return np.sqrt(  np.sqrt(pd*(1-fa)) * (0.5*(pd+(1-fa)))  )


class ReferenceFit( Algorithm ):


  def __init__( self, name, **kw ):
    Algorithm.__init__(self, name, **kw)
    import collections
    self._reference = collections.OrderedDict()


  def add( self, key, reference, pd, fa ):
    pd = (pd[0]/float(pd[1]), pd[0],pd[1])
    fa = (fa[0]/float(fa[1]), fa[0],fa[1])
    MSG_INFO( self, '%s | %s(pd=%1.2f, fa=%1.2f, sp=%1.2f)', key, reference, pd[0]*100, fa[0]*100, sp_func(pd[0],fa[0])*100 )
    self._reference[key] = {'pd':pd, 'fa':fa, 'sp':sp_func(pd[0],fa[0]), 'reference' : reference}



  def execute( self, context ):

    model  = context.getHandler("model")
    # remove the last activation and recreate the mode
    model  = Model(model.inputs, model.layers[-2].output)
    imodel = context.getHandler("imodel")
    index  = context.getHandler("index")
    sort   = context.getHandler("sort" )
    init   = context.getHandler("init" )

    history          = context.getHandler("history" )
    x_train, y_train = context.getHandler("trnData")
    x_val , y_val    = context.getHandler("valData")

    # Get all outputs before the last activation function
    y_pred = model.predict( x_train, batch_size = 1024, verbose=1 )
    y_pred_val = model.predict( x_val, batch_size = 1024, verbose=1 )

    # get vectors for operation mode (train+val)
    y_pred_operation = np.concatenate( (y_pred, y_pred_val), axis=0)
    y_operation = np.concatenate((y_train,y_val), axis=0)


    train_total = len(y_train)
    val_total = len(y_val)

    # Here, the threshold is variable and the best values will
    # be setted by the max sp value found in hte roc curve
    # Training
    fa, pd, thresholds = roc_curve(y_train, y_pred)
    sp = np.sqrt(  np.sqrt(pd*(1-fa)) * (0.5*(pd+(1-fa)))  )

    # Validation
    fa_val, pd_val, thresholds_val = roc_curve(y_val, y_pred_val)
    sp_val = np.sqrt(  np.sqrt(pd_val*(1-fa_val)) * (0.5*(pd_val+(1-fa_val)))  )

    # Operation
    fa_op, pd_op, thresholds_op = roc_curve(y_operation, y_pred_operation)
    sp_op = np.sqrt(  np.sqrt(pd_op*(1-fa_op)) * (0.5*(pd_op+(1-fa_op)))  )

 

    history['reference'] = {}

    for key, ref in self._reference.items():

      d = self.calculate( train_total, val_total , ref, pd,fa,sp,thresholds, pd_val,fa_val,sp_val,thresholds_val, pd_op,fa_op,sp_op,thresholds_op )
      MSG_INFO(self, "          : %s", key )
      MSG_INFO(self, "Reference : [Pd: %1.4f] , Fa: %1.4f and SP: %1.4f ", ref['pd'][0]*100, ref['fa'][0]*100, ref['sp']*100 )
      MSG_INFO(self, "Train     : [Pd: %1.4f] , Fa: %1.4f and SP: %1.4f ", d['pd'][0]*100, d['fa'][0]*100, d['sp']*100 )
      MSG_INFO(self, "Validation: [Pd: %1.4f] , Fa: %1.4f and SP: %1.4f ", d['pd_val'][0]*100, d['fa_val'][0]*100, d['sp_val']*100 )
      MSG_INFO(self, "Operation : [Pd: %1.4f] , Fa: %1.4f and SP: %1.4f ", d['pd_op'][0]*100, d['fa_op'][0]*100, d['sp_op']*100 )
      history['reference'][key] = d

    return StatusCode.SUCCESS



  def closest( self, values , ref ):
    index = np.abs(values-ref)
    index = index.argmin()
    return values[index], index




  def calculate( self, train_total, val_total , ref, pd,fa,sp,thresholds, pd_val,fa_val,sp_val,thresholds_val, pd_op,fa_op,sp_op,thresholds_op ):

    d = {}
    d['pd_ref'] = ref['pd']
    d['fa_ref'] = ref['fa']
    d['sp_ref'] = ref['sp']
    d['reference'] = ref['reference']


    # Get the efficiencies for train dataset
    _, index = self.closest( pd, ref['pd'][0] )
    d['pd'] = ( pd[index],  train_total*float(pd[index]),train_total)
    d['fa'] = ( fa[index],  train_total*float(fa[index]),train_total)
    d['sp'] = sp_func(d['pd'][0], d['fa'][0])
    d['threshold'] = thresholds[index]


    _, index = self.closest( pd_val, ref['pd'][0] )
    d['pd_val'] = ( pd_val[index],  val_total*float(pd_val[index]),val_total)
    d['fa_val'] = ( fa_val[index],  val_total*float(fa_val[index]),val_total)
    d['sp_val'] = sp_func(d['pd_val'][0], d['fa_val'][0])
    d['threshold_val'] = thresholds_val[index]

    op_total = train_total+val_total

    _, index = self.closest( pd_op, ref['pd'][0] )
    d['pd_op'] = ( pd_op[index],  op_total*float(pd_op[index]),op_total)
    d['fa_op'] = ( fa_op[index],  op_total*float(fa_op[index]),op_total)
    d['sp_op'] = sp_func(d['pd_op'][0], d['fa_op'][0])
    d['threshold_op'] = thresholds_op[index]

    return d



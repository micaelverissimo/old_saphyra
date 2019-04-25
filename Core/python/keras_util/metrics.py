__all__ = ['Efficiencies']

#import keras.backend.T as T
import theano.tensor as T
from theano import gof, config
import numpy as np

from TuningTools.TuningJob import ReferenceBenchmark
from TuningTools.coreDef import npCurrent
from Gaugi import keyboard


try:
  from sklearn.metrics import roc_curve
except ImportError:
  raise ImportError("sklearn is not available, please install it.")

class Roc( gof.Op ):
  """
  Based on https://github.com/lisa-lab/pylearn2/blob/master/pylearn2/train_extensions/roc_auc.py
  """
  # TODO This can be shared for all references and computed only once.

  def __init__(self, reference, name=None, use_c_code=config.cxx):
      super(Roc, self).__init__(use_c_code)
      self.name = reference.name + '_roc'
      self.refVal = reference.refVal
      self.reference = reference.reference

  def make_node(self, y_true, y_score):
    """
    Calculate ROC performance indexes
    Parameters
    ----------
    y_true : tensor_like
        Target class labels.
    y_score : tensor_like
        Predicted class labels or probabilities for positive class.
    TODO Write output help
    """
    output = [T.vector(name=self.name, dtype=npCurrent.fp_dtype)]
    return gof.Apply(self, [y_true, y_score], output)


  def perform(self, node, inputs, output_storage):
    """
    Calculate ROC scores.
    Parameters
    ----------
    node : Apply instance
        Symbolic inputs and outputs.
    inputs : list
        Sequence of inputs.
    output_storage : list
        List of mutable 1-element lists.
    ----------
    """
    y_true, y_score = inputs
    fpr, tpr, thresholds = roc_curve(y_true, y_score, pos_label=1, drop_intermediate=True)
    jpr = 1. - fpr
    sp = np.sqrt( (tpr  + jpr)*.5 * np.sqrt(jpr*tpr) )
    if self.reference is ReferenceBenchmark.SP:
      idx = np.argmax( sp )
    else:
      # Get reference for operation:
      if self.reference is ReferenceBenchmark.Pd:
        ref = tpr
      elif self.reference is ReferenceBenchmark.Pf:
        ref = fpr
      delta = ref - self.refVal
      idx   = np.argmin( np.abs( delta ) )
    spVal     = sp[ idx ]
    pdVal     = tpr[ idx ]
    pfVal     = fpr[ idx ]
    threshold = thresholds[ idx ]
    #print spVal, pdVal, pfVal, threshold
    output_storage[0][0] = np.array( [spVal, pdVal, pfVal, threshold], dtype=npCurrent.fp_dtype )

class Efficiencies( object ): 

  def __init__( self, reference ):
    self.roc = Roc( reference )

  def false_alarm_probability(self, y_true, y_pred): 
    return self.roc(y_true, y_pred)[2]

  def detection_probability(self, y_true, y_pred): 
    return self.roc(y_true, y_pred)[1]

  def sp_index(self, y_true, y_pred): 
    return self.roc(y_true, y_pred)[0]

  def threshold(self, y_true, y_pred): 
    return self.roc(y_true, y_pred)[3]


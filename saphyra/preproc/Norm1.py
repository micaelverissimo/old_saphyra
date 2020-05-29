
__all__ = ['Norm1']

from saphyra.preproc import PrepObj
from Gaugi import checkForUnusedVars
import numpy as np


class Norm1(PrepObj):
  """
    Applies norm-1 to data
  """
  takesParamsFromData = False

  def __init__(self, d = {}, **kw):
    d.update( kw ); del kw
    PrepObj.__init__( self, d )
    checkForUnusedVars(d, self._warning )
    del d


  def _retrieveNorm(self, data):
    """
      Calculate pre-processing parameters.
    """
    norms = np.abs( data.sum(axis=1) )
    norms[norms==0] = 1
    return norms

  def __str__(self):
    """
      String representation of the object.
    """
    return "Norm1"

  def shortName(self):
    """
      Short string representation of the object.
    """
    return "N1"

  def _apply(self, data):
    norms = self._retrieveNorm(data)
    ret = data/norms[:,None]
    return ret




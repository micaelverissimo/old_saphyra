
__all__ = ["ReshapeToConv1D"]

from Gaugi import ( Logger, 
                    LoggerStreamable, 
                    checkForUnusedVars, 
                    EnumStringification, 
                    save, 
                    load, 
                    LimitedTypeList, 
                    LoggingLevel, 
                    LoggerRawDictStreamer, 
                    LimitedTypeStreamableList, 
                    RawDictStreamer, 
                    RawDictCnv )

from saphyra.preproc import PrepObj
import numpy as np


class ReshapeToConv1D( PrepObj ):
  """
    Specific normalization for track parameters in mc14, 13TeV.
    Six variables, normalized through simple multiplications.
  """
  _streamerObj = LoggerRawDictStreamer(toPublicAttrs = {})
  _cnvObj = RawDictCnv(toProtectedAttrs = {})
  takesParamsFromData = False
  def __init__(self, d = {}, **kw):
    d.update( kw ); del kw
    PrepObj.__init__(self, d)
    checkForUnusedVars(d, self._warning)
    del d

  def __str__(self):
    """
      String representation of the object.
    """
    return "Conv1D data reshape."

  def shortName(self):
    """
      Short string representation of the object.
    """
    return "ReshapeToConv1D"

  def _apply(self, data):
    data=  np.array([data])
    data = np.transpose(data, [1,2,0])
    return data


  def takeParams(self, trnData):
    return self._apply(trnData)




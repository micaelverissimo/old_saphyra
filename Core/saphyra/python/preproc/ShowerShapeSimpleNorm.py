
__all__ = ["ShowerShapesSimpleNorm"]

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








class ShowerShapesSimpleNorm( PrepObj ):
  """
    Specific normalization for shower shape parameters in mc16, 13TeV.
    Seven variables, normalized through simple multiplications.
  """
  _streamerObj = LoggerRawDictStreamer(toPublicAttrs = {'_factors'})
  _cnvObj = RawDictCnv(toProtectedAttrs = {'_factors'})
  takesParamsFromData = False
  def __init__(self, d = {}, **kw):
    d.update( kw ); del kw
    PrepObj.__init__(self, d)
    checkForUnusedVars(d, self._warning)
    self._factors = [1.0,    # eratio
                     1.0,    # reta
                     1.0,    # rphi
                     0.1,    # rhad
                     0.02,   # weta2
                     0.6,    # f1
                     0.04  ] # f3
    del d

  def __str__(self):
    """
      String representation of the object.
    """
    return "Shower shape data simple normalization"

  def shortName(self):
    """
      Short string representation of the object.
    """
    return "ShShS"

  def _apply(self, data):
    # NOTE: is it a problem that I don't deepcopy the data?
    if isinstance(data, (list,tuple)):
      if len(data) == 0: return data
      import numpy as np
      import copy
      ret = []
      for conj in data:
        conj /= np.array(self._factors)
        ret.append(conj)
      return ret
    else:
      self._fatal("Data is not in the right format, must be list or tuple")

  def takeParams(self, trnData):
    return self._apply(trnData)




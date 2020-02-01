
__all__ = ["TrackSimpleNorm"]

from Gaugi import ( Logger, 
                    LoggerStreamable, 
                    checkForUnusedVars, 
                    EnumStringification, 
                    save, 
                    load, 
                    RawDictStreamer, 
                    RawDictCnv,
                    LoggerRawDictStreamer )              

from saphyra.preproc import PrepObj



class TrackSimpleNorm( PrepObj ):
  """
    Specific normalization for track parameters in mc14, 13TeV.
    Six variables, normalized through simple multiplications.
  """
  _streamerObj = LoggerRawDictStreamer(toPublicAttrs = {'_factors'})
  _cnvObj = RawDictCnv(toProtectedAttrs = {'_factors'})
  takesParamsFromData = False
  def __init__(self, d = {}, **kw):
    d.update( kw ); del kw
    PrepObj.__init__(self, d)
    checkForUnusedVars(d, self._warning)
    self._factors = [0.05,  # deltaeta1
                     1.0,   # deltaPoverP
                     0.05,  # deltaPhiReescaled
                     6.0,   # d0significance
                     0.2,   # d0pvunbiased
                     1.0  ] # TRT_PID (from eProbabilityHT)
    del d

  def __str__(self):
    """
      String representation of the object.
    """
    return "Tracking data simple normalization"

  def shortName(self):
    """
      Short string representation of the object.
    """
    return "TrackSimple"

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




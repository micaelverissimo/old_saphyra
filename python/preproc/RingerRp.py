
__all__ = ['RingerRp']

from saphyra.preproc import Norm1
from Gaugi import checkForUnusedVars, LoggerRawDictStreamer, RawDictCnv
import numpy as np




class RingerRp( Norm1 ):
  """
    Apply ringer-rp reprocessing to data.
  """

  _streamerObj = LoggerRawDictStreamer(toPublicAttrs = {'_alpha', '_beta','_rVec'})
  _cnvObj = RawDictCnv(toProtectedAttrs = {'_alpha','_beta','_rVec'})
  takesParamsFromData = False


  def __init__(self, alpha = 1., beta = 1., d = {}, **kw):
    d.update( kw ); del kw
    Norm1.__init__( self, d )
    checkForUnusedVars(d, self._warning )
    del d
    self._alpha = alpha
    self._beta = beta
    #Layers resolution
    PS      = np.arange(1,9)
    EM1     = np.arange(1,65)
    EM2     = np.arange(1,9)
    EM3     = np.arange(1,9)
    HAD1    = np.arange(1,5)
    HAD2    = np.arange(1,5)
    HAD3    = np.arange(1,5)
    rings   = np.concatenate((PS,EM1,EM2,EM3,HAD1,HAD2,HAD3))
    self._rVec = np.power( rings, self._beta )


  def __str__(self):
    """
      String representation of the object.
    """
    return ("RingerRp_a%g_b%g" % (self._alpha, self._beta)).replace('.','dot')


  def shortName(self):
    """
      Short string representation of the object.
    """
    return "Rp"


  def rVec(self):
    """
      Retrieves the ring pseudo-distance vector
    """
    return self._rVec


  def _apply(self, data):
    self._info('(alpha, beta) = (%f,%f)', self._alpha, self._beta)
    mask = np.ones(100, dtype=bool)
    mask[np.cumsum([0,8,64,8,8,4,4])] = False
    if isinstance(data, (tuple, list,)):
      ret = []
      for i, cdata in enumerate(data):
        rpEnergy = np.sign(cdata)*np.power( abs(cdata), self._alpha )
        #rpEnergy = rpEnergy[ npCurrent.access( pidx=mask, oidx=':') ]
        norms = self._retrieveNorm(rpEnergy)
        rpRings = ( ( rpEnergy * self._rVec ) / norms[ npCurrent.access( pidx=':') ] ).astype( npCurrent.fp_dtype )
        ret.append(rpRings)
    else:
      rpEnergy = np.sign(data)*np.power( abs(cdata), self._alpha )
      #rpEnergy = rpEnergy[ npCurrent.access( pidx=mask, oidx=':') ]
      norms = self._retrieveNorm(rpEnergy)
      rpRings = ( ( rpEnergy * self._rVec ) / norms[ npCurrent.access( pidx=':') ] ).astype( npCurrent.fp_dtype )
      ret = rpRings
    return ret




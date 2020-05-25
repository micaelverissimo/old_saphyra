
__all__ = ['Reference_v1']


from sklearn.model_selection import *
from Gaugi import LoggerStreamable, LoggerRawDictStreamer, RawDictCnv, NotSet
from tensorflow.keras.models import model_from_json
import json





class Reference_v1( LoggerStreamable ):


  _streamerObj = LoggerRawDictStreamer(toPublicAttrs = {'_sgnRef', '_bkgRef', '_etBins', '_etaBins', '_etBinIdx', '_etaBinIdx'})
  _cnvObj = RawDictCnv(toProtectedAttrs = {'_sgnRef', '_bkgRef', '_etBins', '_etaBins', '_etBinIdx', '_etaBinIdx'})
  __version =  1


  def __init__( self, **kw ):

    LoggerStreamable.__init__(self, **kw)
    import collections
    self._sgnRef = collections.OrderedDict()
    self._bkgRef = collections.OrderedDict()
    self._etBins = NotSet
    self._etaBins = NotSet
    self._etBinIdx = NotSet
    self._etaBinIdx = NotSet


  def setEtBins(self, etBins ):
    self._etBins = etBins

  def setEtaBins( self, etaBins ):
    self._etaBins = etaBins


  def setEtBinIdx(self, etBinIdx ):
    self._etBinIdx = etBinIdx

  def setEtaBinIdx(self, etaBinIdx ):
    self._etaBinIdx = etaBinIdx


  def getEtBiinIdx(self):
    return self._etBinIdx

  def getEtaBiinIdx(self):
    return self._etaBinIdx


  def addSgn( self, reference, branch, passed, total):
    self._sgnRef[ reference ] = {'passed':passed, 'total':total, 'reference': branch}

  def addBkg( self, reference, branch, passed, total):
    self._bkgRef[ reference ] = {'passed':passed, 'total':total, 'reference': branch}


  def getSgnPassed(self, reference):
    return self._sgnRef[reference]['passed']

  def getSgnTotal(self, reference):
    return self._sgnRef[reference]['total']


  def getBkgPassed(self, reference):
    return self._bkgRef[reference]['passed']

  def getBkgTotal(self, reference):
    return self._bkgRef[reference]['total']



  def save(self, ofile):
    d = self.toRawObj()
    from Gaugi import save
    save( d, ofile, compress=True)








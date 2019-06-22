
__all__ = ['CrossVal_v1']


from sklearn.model_selection import *
from Gaugi import LoggerStreamable, LoggerRawDictStreamer, RawDictCnv, checkForUnusedVars
from saphyra.enumerations import *




class CrossVal_v1( LoggerStreamable ):

  _streamerObj = LoggerRawDictStreamer(toPublicAttrs = {'_shuffle', '_random_state', '_n_splits', '_method'})
  _cnvObj = RawDictCnv(toProtectedAttrs = {'_shuffle', '_random_state', '_n_splits', '_method'})
  __version =  1

  def __init__( self,  **kw ):
    LoggerStreamable.__init__(self, kw)
    self._obj = None


  def set_object(self, obj):
    self._obj = obj
    if type(obj) is KFold:
      self._method = CrossValMethod.KFold
    elif type(obj) is LeaveOneOut:
      self._method = CrossValMethod.LeaveOneOut
    elif type(obj) is StratifiedKFold:
      self._method = CrossValMethod.StratifiedKFold
    else:
      self._logger.fatal("Method (%s )not supported. Check your object.", self._method)
    if not type(obj) is LeaveOneOut:
      self._shuffle = obj.shuffle
      self._n_splits = obj.n_splits
      self._random_state = obj.random_state
    else:
      self._shuffle = False; self._random_state = None; self._n_splits = None


  def get_object(self):
    if self._obj:
      return self._obj
    else:
      if self._method is CrossValMethod.KFold:
        obj= KFold(self._n_splits, random_state=self._random_state,  shuffle=self._shuffle)
      elif self._method is CrossValMethod.LeaveOneOut:
        obj= LeaveOneOut()
      elif self._method is CrossValMethod.StratifiedKFold:
        obj= StratifiedKFold(self._n_splits, random_state=self._random_state,  shuffle=self._shuffle)
      else:
        self._logger.fatal("Method (%s )not supported. Check your object.", self._method)
      self._obj = obj
      return self._obj


  def save(self, fname):
    d = self.toRawObj()
    from Gaugi import save
    save( d, fname, compress=True)











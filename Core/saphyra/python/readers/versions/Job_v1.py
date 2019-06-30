

__all__ = ['Job_v1']


from Gaugi import LoggerStreamable, LoggerRawDictStreamer, RawDictCnv



class Job_v1( LoggerStreamable ):

  _streamerObj = LoggerRawDictStreamer(toPublicAttrs = {'_sorts', '_inits'})
  _cnvObj = RawDictCnv(toProtectedAttrs = {'_sorts', '_inits'})

  __version =  1

  def __init__( self, **kw ):
    LoggerStreamable.__init__(self, kw)
    self._sorts = []
    self._inits = []

  def set_sorts(self, v):
    if type(v) is int:
      self._sorts = [v]

  def set_inits(self, v):
    if type(v) is int:
      self._inits = range(v)

  def get_sorts(self):
    return self._sorts

  def get_inits(self):
    return self._inits

  def save(self, fname):
    d = self.toRawObj()
    from Gaugi import save
    save( d, fname, compress=True)


 



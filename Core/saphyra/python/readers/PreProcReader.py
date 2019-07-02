
__all__ = ['PreProcReader']


from Gaugi import Logger, NotSet


class PreProcReader( Logger ):

  def __init__( self, **kw ):
    Logger.__init__(self, kw)
    self._obj = NotSet

  def load( self, ofile ):

    from Gaugi import load
    raw = load( ofile )
    # get the file version
    version = raw['__version']

    # the current file version
    if version == 1:
      from saphyra import PreProcChain_v1
      print raw
      self._obj = PreProcChain_v1.fromRawObj( raw )
      print self._obj
      print type(self._obj)
    else:
      # error because the file does not exist
      self._logger.fatal( 'File version (%d) not supported in (%s)', version, ofile)

    # return the list of keras models
    return self._obj
    

  def save(self, obj, ofile):
    obj.save(ofile)


  def object(self):
    return self._obj





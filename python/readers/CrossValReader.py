
__all__ = ['CrossValReader']


from Gaugi import Logger, NotSet


class CrossValReader( Logger ):

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
      from saphyra import CrossVal_v1
      self._obj = CrossVal_v1.fromRawObj( raw )
    else:
      # error because the file does not exist
      self._logger.fatal( 'File version (%d) not supported in (%s)', version, ofile)

    # get the cross validation skelern object
    return self._obj.get_object()


  def save(self, obj, ofile):
    obj.save(ofile)


  def object(self):
    return self._obj





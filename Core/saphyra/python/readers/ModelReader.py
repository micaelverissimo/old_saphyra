
__all__ = ['ModelReader']


from Gaugi import Logger, NotSet


class ModelReader( Logger ):

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
      from saphyra import Model_v1
      self._obj = Model_v1.fromRawObj( raw )
    else:
      # error because the file does not exist
      self._logger.fatal( 'File version (%d) not supported in (%s)', version, ofile)

    # print all keras model
    for obj in self._obj.get_models():
      obj.summary()

    # return the list of keras models
    return self._obj.get_models()
    

  def save(self, obj, ofile):
    obj.save(ofile)


  def object(self):
    return self._obj





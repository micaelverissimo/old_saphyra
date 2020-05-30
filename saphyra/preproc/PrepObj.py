
__all__ = ["PrepObj"]

from Gaugi import ( Logger, 
                    LoggerStreamable, 
                    checkForUnusedVars, 
                    EnumStringification, 
                    save, 
                    load,
                    RawDictStreamer, 
                    RawDictCnv,
                    LoggerRawDictStreamer )
                    # LimitedTypeList, 
                    # LoggingLevel, 
                    # LimitedTypeStreamableList, )



class PrepObj( LoggerStreamable ):

  takesParamsFromData = True

  def __init__(self, d = {}, **kw):
    d.update( kw )
    LoggerStreamable.__init__(self, d)


  def __call__(self, data, revert = False):
    """
      The revert should be used to undo the pre-processing.
    """
    if revert:
      try:
        self._logger.debug('Reverting %s...', self.__class__.__name__)
        data = self._undo(data)
      except AttributeError:
        self._logger.fatal("It is impossible to revert PreProc ")#%s" % \
    else:
      self._logger.debug('Applying %s...', self.__class__.__name__)
      data = self._apply(data)
    return data

  def takeParams(self, data):
    """
      Calculate pre-processing parameters.
    """
    self._logger.debug("No need to retrieve any parameters from data.")
    return self._apply(data)

  def release(self):
    """
      Release calculated pre-proessing parameters.
    """
    self._logger.debug(("No parameters were taken from data, therefore none was "
        "also empty."))

  def psprocessing(self, data, extra, pCount = 0):
    """
      Pre-sort processing
    """
    return data, extra

  def __str__(self):
    """
      Overload this method to return the string representation
      of the pre-processing.
    """
    pass

  def shortName(self):
    """
      Overload this method to return the short string representation
      of the pre-processing.
    """
    pass

  def isRevertible(self):
    """
      Check whether the PreProc is revertible
    """
    import inspect
    return any([a[0] == '_undo' for a in inspect.getmembers(self) ])

  def _apply(self, data):
    """
      Overload this method to apply the pre-processing
    """
    return data




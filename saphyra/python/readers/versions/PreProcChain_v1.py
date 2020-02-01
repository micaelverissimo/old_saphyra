
__all__ = ["PreProcChain_v1"]

from Gaugi import ( Logger, 
                    checkForUnusedVars, 
                    EnumStringification, 
                    save, 
                    load, )
                    # LimitedTypeList, 
                    # LoggingLevel, 
                    # LoggerRawDictStreamer, 
                    # LimitedTypeStreamableList, 
                    # )

from Gaugi.messenger.macros import *
from saphyra.preproc import PrepObj

import six

#class PreProcChain_v1 ( six.with_metaclass( LimitedTypeStreamableList,  Logger) ):
class PreProcChain_v1 ( Logger ):
  """
    The PreProcChain is the object to hold the pre-processing chain to be
    applied to data. They will be sequentially applied to the input data.
  """

  __version = 1

  # Use class factory
  #__metaclass__ = LimitedTypeStreamableList
  
  # These are the list (LimitedTypeList) accepted objects:
  #_acceptedTypes = (PrepObj,)

  @property
  def takesParamsFromData( self ):
    #return True
    for pp in self:
      if pp.takesParamsFromData: return True
    return False

  def __init__(self, *args, **kw):
    #from Gaugi.LimitedTypeList import _LimitedTypeList____init__
    #_LimitedTypeList____init__(self, *args)
    Logger.__init__(self, kw)

  def __call__(self, data, revert = False, saveArgsDict = None):
    """
      Apply/revert pre-processing chain.
    """
    if not self:
      MSG_WARNING(self, "No pre-processing available in this chain.")
      return
    for pp in self:
      data = pp(data, revert)
    return data


  def __str__(self):
    """
      String representation of the object.
    """
    string = 'NoPreProc'
    if self:
      string = ''
      for pp in self:
        string += (str(pp) + '->')
      string = string[:-2]
    return string

  def shortName(self):
    string = 'NoPreProc'
    if self:
      string = ''
      for pp in self:
        string += (pp.shortName() + '-')
      string = string[:-1]
    return string


  def isRevertible(self):
    """
      Check whether the PreProc is revertible
    """
    for pp in self:
      if not pp.isRevertible():
        return False
    return True


  def takeParams(self, trnData, saveArgsDict = None):
    """
      Take pre-processing parameters for all objects in chain.
    """
    if not self:
      MSG_WARNING(self, "No pre-processing available in this chain.")
      return
    for pp in self:
      trnData = pp.takeParams(trnData)
    return trnData


  def psprocessing(self, trnData, extraData, pCount = 0):
    """
      Pre-sort processing
    """
    if not self:
      MSG_WARNING(self, "No pre-processing available in this chain.")
      return
    for pp in self:
      trnData, extraData = pp.psprocessing(trnData, extraData, pCount)

    return trnData, extraData


  def setLevel(self, value):
    """
      Override Logger setLevel method so that we can be sure that every
      pre-processing will have same logging level than that was set for the
      PreProcChain instance.
    """
    for pp in self:
      pp.level = LoggingLevel.retrieve( value )
    self._level = LoggingLevel.retrieve( value )
    self._logger.setLevel(self._level)


  def save(self, ofile):
    save( self.toRawObj(), ofile, compress=True)




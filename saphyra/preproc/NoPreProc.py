
__all__ = ['NoPreProc']

from saphyra.preproc import PrepObj
from Gaugi import checkForUnusedVars

class NoPreProc(PrepObj):
  """
    Do not apply any pre-processing to data.
  """
  takesParamsFromData = False

  def __init__( self, **kw ):
    PrepObj.__init__( self, kw )
    checkForUnusedVars(kw, self._warning )
    del kw

  def __str__(self):
    """
      String representation of the object.
    """
    return "NoPreProc"

  def shortName(self):
    """
      Short string representation of the object.
    """
    return "NoPP"

  def _undo(self, data):
    return data




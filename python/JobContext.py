
__all__ = ["JobContext"]

from Gaugi.messenger  import Logger
from Gaugi.messenger.macros import *
from Gaugi.gtypes import NotSet
from Gaugi import StatusCode


class JobContext(Logger):

  def __init__(self):
    Logger.__init__(self) 
    import collections
    self._containers = collections.OrderedDict()
    self._decorations = dict()

  def setHandler(self, key, obj):
    if key in self._containers.keys():
      MSG_ERROR(self, "Key %s exist into the event context. Attach is not possible...",key)
    else:
      self._containers[key]=obj

  def getHandler(self,key):
    return None if not key in self._containers.keys() else self._containers[key]


  def execute(self):
    return StatusCode.SUCCESS

  def initialize(self):
    return StatusCode.SUCCESS

  def finalize(self):
    return StatusCode.SUCCESS

  def setDecor(self, key, v):
    self._decoration[key] = v

  def getDecor(self,key):
    try:
      return self._decoration[key]
    except KeyError:
      MSG_ERROR(self, 'Decoration %s not found',key)

  def clearDecorations(self):
    self._decoration = dict()

  def decorations(self):
    return self._decoration.keys()


  def clear(self):
    import collections
    self._containers = collections.OrderedDict()
    self._decorations = dict()



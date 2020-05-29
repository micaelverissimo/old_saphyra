__all__ = ['PatternGenerator']


from Gaugi import Logger, NotSet
from Gaugi.messenger.macros import *
from Gaugi import load
import numpy as np




class PatternGenerator( Logger ):

  def __init__(self, path, generator , **kw):
    Logger.__init__(self)
    self._path = path
    self._generator = generator
    self._kw = kw


  def __call__(self, cv, sort):
    MSG_INFO(self, "Reading %s...", self._path)
    return self._generator(self._path, cv, sort, **self._kw)












__all__ = ['Algorithm']

from Gaugi.messenger import  Logger
from Gaugi.messenger.macros import *
from Gaugi import EnumStringification, NotSet
from Gaugi import StatusCode


# Base class used for all tools for this framework
class Algorithm( Logger ):

  def __init__(self, name):
    Logger.__init__(self)
    self._name = name
    self._context   = NotSet
    self._storegateSvc = NotSet

  def name(self):
    return self._name

  def setContext( self, context ):
    self._context = context

  def getContext(self):
    return self._context

  def setStoreGateSvc(self,sg):
    self._storegateSvc=sg

  def getStoreGateSvc(self):
    return self._storegateSvc

  @property
  def storeSvc(self):
    if self._storegateSvc is not None:
      return self._storegateSvc
    else:
      MSG_FATAL( self, "Attempted to access storeSvc which wasn't set.")

  @storeSvc.setter
  def storeSvc(self, s):
    from Gaugi.storage import StoreGate
    if not isinstance(s, StoreGate):
      PRH_MSG_FATAL( self, "Attempted to set StoreGate to instance of non StoreGate type")
    self._storegateSvc=s


  def initialize(self):
    return StatusCode.SUCCESS

  def execute(self, context):
    self.setContext(context)
    return StatusCode.SUCCESS

  def finalize(self):
    return StatusCode.SUCCESS

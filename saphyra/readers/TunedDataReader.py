
__all__ = ['TunedDataReader']


from Gaugi import Logger, NotSet
from Gaugi.messenger.macros import *

class TunedDataReader( Logger ):

  def __init__( self, **kw ):
    Logger.__init__(self, kw)
    self._obj = NotSet

  def load( self, fList ):
    from Gaugi import load
    from Gaugi import csvStr2List, expandFolders, progressbar
    fList = csvStr2List(fList)
    fList = expandFolders(fList)
    from saphyra import TunedData_v1
    self._obj = TunedData_v1()

    for inputFile in progressbar(fList, len(fList), prefix="Reading tuned data collection...", logger=self._logger):

      raw = load( inputFile )
      # get the file version
      version = raw['__version']
      # the current file version
      if version == 1:
        obj = TunedData_v1.fromRawObj( raw )
        self._obj.merge( obj )
      else:
        # error because the file does not exist
        self._logger.fatal( 'File version (%d) not supported in (%s)', version, inputFile)

    # return the list of keras models
    return self._obj
    

  def save(self, obj, ofile):
    obj.save(ofile)


  def object(self):
    return self._obj







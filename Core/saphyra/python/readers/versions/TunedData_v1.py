
__all__ = ['TunedData_v1']


from sklearn.model_selection import *
from Gaugi import LoggerStreamable, LoggerRawDictStreamer, RawDictCnv
from keras.models import model_from_json
import json





class TunedData_v1( LoggerStreamable ):


  _streamerObj = LoggerRawDictStreamer(toPublicAttrs = {'_tunedData'})
  _cnvObj = RawDictCnv(toProtectedAttrs = {'_tunedData'})
  __version =  1


  def __init__( self, **kw ):

    LoggerStreamable.__init__(self, kw)
    self._tunedData = []
  


  def attach( self, imodel, sort, init, model, history, metadata={} ):

    self._tunedData.append({'imodel'   : imodel,
                            'sort'     : sort,
                            'init'     : init,
                            'history'  : history,
                            'sequence' : json.loads(model.to_json()),
                            'weights'  : model.get_weights() ,
                            'metadata' : metadata, 
                           })

  def merge( self, obj ):
    self._tunedData.extend( obj.get_data() )


  def get_data(self):
    return self._tunedData


  def save(self, ofile):
    d = self.toRawObj()
    from Gaugi import save
    save( d, ofile, compress=True)








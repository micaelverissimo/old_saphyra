
__all__ = ['Model_v1']


from sklearn.model_selection import *
from Gaugi import LoggerStreamable, LoggerRawDictStreamer, RawDictCnv
from keras.models import model_from_json
import json





class Model_v1( LoggerStreamable ):

  _streamerObj = LoggerRawDictStreamer(toPublicAttrs = {'_models'})
  _cnvObj = RawDictCnv(toProtectedAttrs = {'_models'})

  __version =  1

  def __init__( self, **kw ):

    LoggerStreamable.__init__(self, kw)
    self._models = None
  

  def set_models(self, models):
    self._models = list()
    if type(models) is not list:
      models=[models]
    for model in models:
      self._models.append( {'model':  json.loads(model.to_json()), 'weights': model.get_weights() } )


  def get_models(self):
    # Loop over all keras model
    models = []
    for d in self._models:
      model = model_from_json( json.dumps(d['model'], separators=(',', ':'))  )
      model.set_weights( d['weights'] )
      models.append( model )
    return models
  

  def save(self, fname):
    d = self.toRawObj()
    from Gaugi import save
    save( d, fname, compress=True)








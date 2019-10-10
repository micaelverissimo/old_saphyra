

__all__ = ['Job_v1']


from sklearn.model_selection import *
from Gaugi import LoggerStreamable, LoggerRawDictStreamer, RawDictCnv

# Just to remove the keras dependence
import tensorflow as tf
model_from_json = tf.keras.models.model_from_json

import json




class Job_v1( LoggerStreamable ):

  _streamerObj = LoggerRawDictStreamer(toPublicAttrs = {'_id' , '_sorts', '_inits', '_models'})
  _cnvObj = RawDictCnv(toProtectedAttrs = {'_id', '_sorts', '_inits', '_models'})

  __version =  1

  def __init__( self, **kw ):
    LoggerStreamable.__init__(self, kw)
    self._sorts  = []
    self._inits  = []
    self._models = []
    self._id     = None

  def set_sorts(self, v):
    if type(v) is int:
      self._sorts = [v]
    else:
      self._sorts = v

  def set_inits(self, v):
    if type(v) is int:
      self._inits = range(v)
    else:
      self._inits = v

  def get_sorts(self):
    return self._sorts

  def get_inits(self):
    return self._inits


  def set_models(self, models, id_models):
    self._models = list()
    if type(models) is not list:
      models=[models]
    for idx, model in enumerate(models):
      self._models.append( {'model':  json.loads(model.to_json()), 'weights': model.get_weights() , 'id_model': id_models[idx]} )


  def get_models(self):
    # Loop over all keras model
    models = []; id_models = []
    for d in self._models:
      model = model_from_json( json.dumps(d['model'], separators=(',', ':'))  )
      model.set_weights( d['weights'] )
      models.append( model )
      id_models.append( d['id_model'] )
    return models, id_models


  def set_id( self, id ):
    self._id = id

  def id(self):
    return self._id

  def save(self, fname):
    d = self.toRawObj()
    d['__version'] = self.__version
    from Gaugi import save
    save( d, fname, compress=True)


 





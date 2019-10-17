
__all__ = ['TunedData_v1']


from sklearn.model_selection import *
from Gaugi import LoggerStreamable, LoggerRawDictStreamer, RawDictCnv
from tensorflow.keras.models import model_from_json
import json





class TunedData_v1( LoggerStreamable ):


  _streamerObj = LoggerRawDictStreamer(toPublicAttrs = {'_tunedData', '_jobid', '_taskname', '_username'})
  _cnvObj = RawDictCnv(toProtectedAttrs = {'_tunedData', '_jobid', '_taskname', '_username'})
  __version =  1


  def __init__( self, **kw ):

    LoggerStreamable.__init__(self, **kw)
    self._tunedData = []
    self._username  = None
    self._taskname  = None
    self._jobid     = None


  def setDBContext( self, context ):
    self._username = context.username()
    self._taskname = context.taskname()
    self._jobid = context.jobid()

  def getDBContext( self ):
    try:
      from ringerdb import DBContext
      return DBContext( self._username, self._taskname, self._jobid)
    except Exception as e:
      MSG_WARNING(self,e)
      return None

  def attach( self, id_model, sort, init, tag, model, history, metadata={} ):

    self._tunedData.append({'imodel'   : id_model,
                            'sort'     : sort,
                            'init'     : init,
                            'history'  : history,
                            'sequence' : json.loads(model.to_json()),
                            'weights'  : model.get_weights() ,
                            'metadata' : metadata, 
                           })



  def attach_ctx( self, context ,  metadata={}):
    self._tunedData.append({'imodel'   : context.getHandler("id_model"),
                            'sort'     : context.getHandler("sort"),
                            'init'     : context.getHandler("init"),
                            'history'  : context.getHandler("history"),
                            'sequence' : json.loads(context.getHandler("model").to_json()),
                            'weights'  : context.getHandler("model").get_weights() ,
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








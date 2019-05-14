
__all__ = ['MiniBatchGenerator']


from keras.utils import Sequence
from Gaugi import Logger, LoggingLevel, NotSet, checkForUnusedVars
import numpy as np


# Use this generator if you have large datasets
class MiniBatchGenerator(Sequence, Logger):

  def __init__( self, data, target, batch_size=32, secondaryPP=None, shuffle=True, **kw):
    
    super(Sequence, self).__init__()
    Logger.__init__(self,**kw)
    self._data = data
    self._target = target
    self.batch_size = batch_size
    self._secondaryPP=secondaryPP
    self.shuffle = shuffle
    self.on_epoch_end()

  def __len__( self ):
    return int(np.floor( self._max_batch_size )/ self.batch_size)

  def __getitem__(self, index):
    # Generate indexes of the batch
    lower_bound = int(index*(0.5*self.batch_size))
    upper_bound = int((index+1)*(0.5*self.batch_size))
    #print 'INDX = ',index, ' | ',lower_bound,'->',upper_bound, ' limit is ',len(self._signal_indexes)
    signal_indexes = self._signal_indexes[lower_bound:upper_bound]
    noise_indexes = self._noise_indexes[lower_bound:upper_bound]
    indexes = np.concatenate((signal_indexes,noise_indexes))
    np.random.shuffle(indexes)
    def _checkSecondaryPP( data, pp=None ):
      if not (pp is NotSet or pp is None):
        if type(pp) is list:
          return [ _pp(data) for _pp in pp ]
        else:
          return pp(data)
      else:
        return data
    self._logger.debug('inflate minibatch dataset...')
    return _checkSecondaryPP(self._data[indexes], self._secondaryPP ), self._target[indexes]


  def on_epoch_end(self):
    #Updates indexes after each epoch
    self._signal_indexes = np.where(self._target==1)[0]
    self._noise_indexes = np.where(self._target==-1)[0]
    # get the max number of event to process in the next epoch to ensure a balance training
    self._max_batch_size = min(len(self._signal_indexes),len(self._noise_indexes))
    self._signal_indexes[0:self._max_batch_size-1]
    self._noise_indexes[0:self._max_batch_size-1]
    if self.shuffle:  
      np.random.shuffle(self._signal_indexes)
      np.random.shuffle(self._noise_indexes)





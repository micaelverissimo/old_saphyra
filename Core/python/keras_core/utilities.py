
__all__ = ["to_categorical", "inverse_to_categorical"]

def to_categorical( target , num_classes=2):
  # definitions must be:
  # positive (1) will be map in [0,1]
  # negative (-1) will be map in [1,0]
  from keras.utils import to_categorical
  import numpy as np
  from copy import copy
  _target = copy(target)
  _target[np.where(_target==-1)] = 0
  return to_categorical( _target, num_classes=num_classes )


def inverse_to_categorical( target ):
  import numpy as np
  _target = np.argmax(target,axis=1)
  _target[np.where(_target==0)]=-1
  return _target



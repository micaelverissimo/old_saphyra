
__all__ =['isTensorFlowTwo']

def isTensorFlowTwo():
  import tensorflow as tf
  return True if int(tf.__version__.split('.')[0]) >= 2 else False



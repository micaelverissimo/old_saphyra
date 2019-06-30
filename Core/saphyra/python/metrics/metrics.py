
__all__ = ["auc", "f1_score"]


def auc(y_true, y_pred, num_thresholds=2000):
  import tensorflow as tf
  from keras import backend as K
  auc = tf.metrics.auc(y_true, y_pred,num_thresholds=num_thresholds)[1]
  K.get_session().run(tf.local_variables_initializer())
  return auc


def f1_score(y_true, y_pred):
  import tensorflow as tf
  f1 = tf.contrib.metrics.f1_score(y_true, y_pred)[1]
  from keras import backend as K
  K.get_session().run(tf.local_variables_initializer())
  return f1

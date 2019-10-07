
__all__ = ["auc", "f1_score"]


from tensorflow.keras import backend as K


def auc(y_true, y_pred, num_thresholds=2000):
  import tensorflow as tf
  auc = tf.metrics.auc(y_true, y_pred,num_thresholds=num_thresholds)[1]
  K.get_session().run(tf.local_variables_initializer())
  return auc


def f1_score(y_true, y_pred):
  import tensorflow as tf
  f1 = tf.contrib.metrics.f1_score(y_true, y_pred)[1]
  K.get_session().run(tf.local_variables_initializer())
  return f1

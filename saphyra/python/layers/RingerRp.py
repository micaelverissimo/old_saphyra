
__all__ = ['RingerRp']


from tensorflow.keras.layers import Layer
from tensorflow.keras import backend as K
import numpy as np
import tensorflow as tf


PS      = np.arange(1,9)
EM1     = np.arange(1,65)
EM2     = np.arange(1,9)
EM3     = np.arange(1,9)
HAD1    = np.arange(1,5)
HAD2    = np.arange(1,5)
HAD3    = np.arange(1,5)


class RingerRp(Layer):



  def __init__(self, alpha=None, beta=None, **kwargs):
    super(RingerRp, self).__init__(**kwargs)
    self.output_dim = (100,)

  def build( self, input_shape ):
    self.alpha = self.add_weight( name='alpha',
                               shape=(1,1),
                               initializer=tf.keras.initializers.RandomNormal(mean=2, stddev=0.5),
                               trainable=True)

    self.beta = self.add_weight(name='beta',
                                  shape=(1,1),
                                  initializer=tf.keras.initializers.RandomNormal(mean=4, stddev=0.5),
                                  trainable=True)

    self.rvec = K.constant(np.concatenate((PS,EM1,EM2,EM3,HAD1,HAD2,HAD3)))
    super(RingerRp, self).build(input_shape)






  def call(self, input):

    Ea = K.sign(input)*K.pow( K.abs(input), self.alpha )
    rb =  K.pow(self.rvec, self.beta)
    Ea_sum = tf.reshape( K.sum( Ea, axis=1), (-1,1))
    out = (Ea*rb)/ Ea_sum
    return out



  def get_output_shape_for(self, input_shape):
    return self.output_dim





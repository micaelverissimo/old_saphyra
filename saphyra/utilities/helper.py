
__all__ =['isTensorFlowTwo', 'get_output_from']

def isTensorFlowTwo():
  import tensorflow as tf
  return True if int(tf.__version__.split('.')[0]) >= 2 else False



from tensorflow.keras.models import Model

def get_output_from( model, layer_name, data ):
    return Model(inputs=model.input, outputs=model.get_layer(layer_name).output).predict( data, batch_size=4096, verbose=True )




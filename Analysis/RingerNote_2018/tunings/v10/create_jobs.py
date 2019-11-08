



from saphyra import *


# ppChain
from saphyra import PreProcChain_v1, Norm1, ReshapeToConv1D

pp = PreProcChain_v1( [Norm1()] )





def get_models( ):  
  
  from tensorflow.keras.models import Sequential
  from tensorflow.keras.layers import Dense, Dropout, Activation, Conv1D, Flatten
  filter_conv_1       = [4,8,16,32,64]
  kernel_size_conv_1  = [2,4,6,8]
  filter_conv_2       = [4,8,16,32,64]
  kernel_size_conv_2  = [2,4,6,8]
  neurons_dense_1     = [8,16,32,64,128]

  models = []

  # Build all models with only one conv layer
  for f1 in filter_conv_1:
    for k1 in kernel_size_conv_1:
      for d1 in neurons_dense_1:
        model = Sequential()
        model.add(Conv1D(f1, kernel_size=k1, activation='relu', input_shape=(100,1),name='conv1' )) 
        model.add(Flatten())
        model.add(Dense(d1,  activation='relu',name='dense1'))
        model.add(Dropout(0.5))
        model.add(Dense(1, activation='linear',name='dense2'))
        model.add(Activation('sigmoid',name='output'))
        models.append( model )


  # Build all models with only one conv layer
  for f1 in filter_conv_1:
    print(f1)
    for k1 in kernel_size_conv_1:
      for f2 in filter_conv_2:
        for k2 in kernel_size_conv_2:
          for d1 in neurons_dense_1:
            model = Sequential()
            model.add(Conv1D(f1, kernel_size=k1, activation='relu', input_shape=(100,1),name='conv1' )) 
            model.add(Conv1D(f2, kernel_size=k2, activation='relu',name='conv2' )) 
            model.add(Flatten())
            model.add(Dense(d1,  activation='relu', name='dense1'))
            model.add(Dropout(0.5))
            model.add(Dense(1, activation='linear',name='dense2'))
            model.add(Activation('sigmoid',name='output'))
            models.append( model )

  print("Total number of models: %d" % len(models) )
  return models





from sklearn.model_selection import StratifiedKFold, KFold
kf = StratifiedKFold(n_splits=10, random_state=512, shuffle=True)
#kf = KFold(n_splits=10, random_state=1234, shuffle=True)


models = get_models()
from Gaugi import PythonLoopingBounds
createPandaJobs( models        = models,
        ppChain       = pp,
        crossVal      = kf,
        nInits        = 1,
        nInitsPerJob  = 1,
        sortBounds    = PythonLoopingBounds(10),
        nSortsPerJob  = 10,
        nModelsPerJob = 1,
        outputFolder  = 'job_config.ringer.v10.cnn_grid_search.10sorts.1inits'
        )



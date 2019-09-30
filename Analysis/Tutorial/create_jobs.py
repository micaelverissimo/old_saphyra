



from saphyra import *
pandas=CreatePandaJobs()


# ppChain
from saphyra import PreProcChain_v1, Norm1, ReshapeToConv1D
pp = PreProcChain_v1( [Norm1(), ReshapeToConv1D()] )


from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Conv1D, Flatten


# [Model]
# Build the conv1d CNN model (Ringer ultimate)
def get_model( ): 
  modelCol = []
  model = Sequential()
  model.add(Conv1D(16, kernel_size=3, activation='relu', input_shape=(100,1) )) 
  model.add(Conv1D(32, kernel_size=3, activation='relu' )) 
  model.add(Dropout(0.25))
  model.add(Flatten())
  model.add(Dense(64,  activation='relu', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
  model.add(Dropout(0.25))
  model.add(Dense(1, activation='linear', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
  model.add(Activation('sigmoid'))
  modelCol.append(model)
  return modelCol



from sklearn.model_selection import StratifiedKFold, KFold
kf = StratifiedKFold(n_splits=10, random_state=512, shuffle=True)



from Gaugi import PythonLoopingBounds
pandas( models        = get_model(),
        ppChain       = pp,
        crossVal      = kf,
        nInits        = 1,
        nInitsPerJob  = 1,
        sortBounds    = PythonLoopingBounds(10),
        nSortsPerJob  = 1,
        nModelsPerJob = 1,
        outputFolder  = 'job_config.ringer.cnn.10sorts.10inits'
        )



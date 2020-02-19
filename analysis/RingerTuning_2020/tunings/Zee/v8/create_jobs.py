



from saphyra import *


# ppChain
from saphyra import PreProcChain_v1, Norm1, ReshapeToConv1D

pp = PreProcChain_v1( [Norm1()] )


from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Activation, Conv1D, Flatten



def get_model( ):
  modelCol = []
  for n in range(2,10+1):
    model = Sequential()
    model.add(Dense(n, input_shape=(100,), activation='tanh'))
    model.add(Dense(1, activation='linear'))
    model.add(Activation('tanh'))
    modelCol.append(model)
  return modelCol



from sklearn.model_selection import StratifiedKFold, KFold
kf = StratifiedKFold(n_splits=10, random_state=512, shuffle=True)



createPandaJobs( models        = get_model(),
        ppChain       = pp,
        crossVal      = kf,
        nInits        = 5,
        nInitsPerJob  = 1,
        sortBounds    = 10,
        nSortsPerJob  = 1,
        nModelsPerJob = 5,
        outputFolder  = 'job_config.Zee_v8.n2to10.10sorts.5inits'
        )



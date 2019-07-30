



from saphyra import *
pandas=CreatePandaJobs()


# ppChain
from saphyra import PreProcChain_v1, Norm1
pp = PreProcChain_v1( [Norm1()] )


modelCol = []
#from keras.models import Sequential
#from keras.layers import Dense, Dropout, Activation
from tensorflow.keras.layers import *
from tensorflow.keras.models import *


# Build the standard MLP model (Ringer vanilla)
def get_model( neurons ):
  modelCol = []
  for n in neurons:
    model = Sequential()
    model.add(Dense(n, input_shape=(100,), activation='tanh', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
    model.add(Dense(1, activation='linear', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
    model.add(Activation('tanh'))
    modelCol.append(model)
  return modelCol


from sklearn.model_selection import StratifiedKFold, KFold
kf = StratifiedKFold(n_splits=10, random_state=512, shuffle=True)


from Gaugi import PythonLoopingBounds
pandas( models = get_model( [5,6,7,8,9,10] ),
        ppChain = pp,
        crossVal = kf,
        nInits = 5,
        nInitsPerJob = 5,
        sortBounds =  PythonLoopingBounds(10),
        nSortsPerJob = 10,
        outputFolder = 'job_config.ringer_v8')



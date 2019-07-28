



from saphyra import *
pandas=CreatePandaJobs()


# ppChain
from saphyra import PreProcChain_v1, Norm1
pp = PreProcChain_v1( [Norm1()] )


modelCol = []
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation

# Build the standard MLP model (Ringer vanilla)
def get_model( neurons ): 
  modelCol = []
  for n in neurons:
    model = Sequential()
    #model.add(Conv1D(16, kernel_size=3, activation='relu', input_shape=(100,1) )) 
    #model.add(Conv1D(32, kernel_size=3, activation='relu' )) 
    #model.add(Flatten())
    model.add(Dense(n, input_shape=(100,), activation='tanh', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
    model.add(Dense(1, activation='linear', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
    model.add(Activation('tanh'))
    modelCol.append(model)
  return modelCol


from sklearn.model_selection import StratifiedKFold, KFold
kf = StratifiedKFold(n_splits=10, random_state=512, shuffle=True)
#kf = KFold(n_splits=10, random_state=1234, shuffle=True)



from Gaugi import PythonLoopingBounds
pandas( models = get_model( [5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20] ),
        ppChain = pp,
        crossVal = kf,
        nInits = 10,
        nInitsPerJob = 1,
        sortBounds =  PythonLoopingBounds(10),
        nSortsPerJob = 1,
        outputFolder = 'job_config.ringer_v8')



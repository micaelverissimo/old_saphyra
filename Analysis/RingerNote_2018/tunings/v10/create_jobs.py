



from saphyra import *


# ppChain
from saphyra import PreProcChain_v1, Norm1, ReshapeToConv1D

pp = PreProcChain_v1( [Norm1()] )


from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Activation, Conv1D, Flatten






model0 = Sequential()
model0.add(Conv1D(8, kernel_size=kernel_size, activation='relu', input_shape=(100,1) )) 
model0.add(Dropout(0.25))
model0.add(Flatten())
model0.add(Dense(16,  activation='relu', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
model0.add(Dropout(0.25))
model0.add(Dense(1, activation='linear', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
model0.add(Activation('sigmoid'))



model1 = Sequential()
model1.add(Conv1D(16, kernel_size=kernel_size, activation='relu', input_shape=(100,1) )) 
model1.add(Dropout(0.25))
model1.add(Flatten())
model1.add(Dense(32,  activation='relu', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
model1.add(Dropout(0.25))
model1.add(Dense(1, activation='linear', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
model1.add(Activation('sigmoid'))


model2 = Sequential()
model2.add(Conv1D(32, kernel_size=kernel_size, activation='relu', input_shape=(100,1) )) 
model2.add(Dropout(0.25))
model2.add(Flatten())
model2.add(Dense(64,  activation='relu', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
model2.add(Dropout(0.25))
model2.add(Dense(1, activation='linear', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
model2.add(Activation('sigmoid'))



model3 = Sequential()
model3.add(Conv1D(8, kernel_size=kernel_size, activation='relu', input_shape=(100,1) )) 
model3.add(Conv1D(16, kernel_size=kernel_size, activation='relu' )) 
model3.add(Dropout(0.25))
model3.add(Flatten())
model3.add(Dense(32,  activation='relu', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
model3.add(Dropout(0.25))
model3.add(Dense(1, activation='linear', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
model3.add(Activation('sigmoid'))




model4 = Sequential()
model4.add(Conv1D(16, kernel_size=kernel_size, activation='relu', input_shape=(100,1) )) 
model4.add(Conv1D(32, kernel_size=kernel_size, activation='relu' )) 
model4.add(Dropout(0.25))
model4.add(Flatten())
model4.add(Dense(64,  activation='relu', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
model4.add(Dropout(0.25))
model4.add(Dense(1, activation='linear', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
model4.add(Activation('sigmoid'))






model = Sequential()
model.add(Conv1D(8, kernel_size=kernel_size, activation='relu', input_shape=(100,1) )) 
model.add(Conv1D(16, kernel_size=kernel_size, activation='relu' )) 
model.add(Dropout(0.25))
model.add(Flatten())
model.add(Dense(32,  activation='relu', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
model.add(Dropout(0.25))
model.add(Dense(16,  activation='relu', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
model.add(Dropout(0.25))
model.add(Dense(1, activation='linear', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
model.add(Activation('sigmoid'))














def get_model( ):
  modelCol = []
  for n in range(2,15+1):
    model = Sequential()
    model.add(Dense(n, input_shape=(100,), activation='tanh', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
    model.add(Dense(1, activation='linear', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
    model.add(Activation('tanh'))
    modelCol.append(model)
  return modelCol



from sklearn.model_selection import StratifiedKFold, KFold
kf = StratifiedKFold(n_splits=10, random_state=512, shuffle=True)
#kf = KFold(n_splits=10, random_state=1234, shuffle=True)



from Gaugi import PythonLoopingBounds
createPandaJobs( models        = get_model(),
        ppChain       = pp,
        crossVal      = kf,
        nInits        = 10,
        nInitsPerJob  = 2,
        sortBounds    = PythonLoopingBounds(10),
        nSortsPerJob  = 1,
        nModelsPerJob = 5,
        outputFolder  = 'job_config.ringer.v8.mlp2to15.10sorts.10inits'
        )



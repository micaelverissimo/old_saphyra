



from saphyra import *


# ppChain
from saphyra import PreProcChain_v1, Norm1, ReshapeToConv1D

pp = PreProcChain_v1( [Norm1()] )





def get_models( kernel_size ):  
  
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
  
  
  
  
  
  
  model5 = Sequential()
  model5.add(Conv1D(8, kernel_size=kernel_size, activation='relu', input_shape=(100,1) )) 
  model5.add(Conv1D(16, kernel_size=kernel_size, activation='relu' )) 
  model5.add(Dropout(0.25))
  model5.add(Flatten())
  model5.add(Dense(32,  activation='relu', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
  model5.add(Dropout(0.25))
  model5.add(Dense(16,  activation='relu', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
  model5.add(Dropout(0.25))
  model5.add(Dense(1, activation='linear', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
  model5.add(Activation('sigmoid'))
  
  
  
  
  model6 = Sequential()
  model6.add(Conv1D(16, kernel_size=kernel_size, activation='relu', input_shape=(100,1) )) 
  model6.add(Conv1D(32, kernel_size=kernel_size, activation='relu' )) 
  model6.add(Dropout(0.25))
  model6.add(Flatten())
  model6.add(Dense(64,  activation='relu', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
  model6.add(Dropout(0.25))
  model6.add(Dense(32,  activation='relu', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
  model6.add(Dropout(0.25))
  model6.add(Dense(1, activation='linear', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
  model6.add(Activation('sigmoid'))
  
  
  
  model7 = Sequential()
  model7.add(Conv1D(32, kernel_size=kernel_size, activation='relu', input_shape=(100,1) )) 
  model7.add(Conv1D(64, kernel_size=kernel_size, activation='relu' )) 
  model7.add(Dropout(0.25))
  model7.add(Conv1D(128, kernel_size=kernel_size, activation='relu' )) 
  model7.add(Dropout(0.25))
  model7.add(Flatten())
  model7.add(Dense(64,  activation='relu', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
  model7.add(Dropout(0.25))
  model7.add(Dense(32,  activation='relu', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
  model7.add(Dropout(0.25))
  model7.add(Dense(1, activation='linear', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
  model7.add(Activation('sigmoid'))
  
  
  modelCol = [model0,model1,model2,model3,model4,model5,model6,model7]
  return modelCol








from sklearn.model_selection import StratifiedKFold, KFold
kf = StratifiedKFold(n_splits=10, random_state=512, shuffle=True)
#kf = KFold(n_splits=10, random_state=1234, shuffle=True)



from Gaugi import PythonLoopingBounds
createPandaJobs( models        = get_models(2),
        ppChain       = pp,
        crossVal      = kf,
        nInits        = 5,
        nInitsPerJob  = 2,
        sortBounds    = PythonLoopingBounds(10),
        nSortsPerJob  = 1,
        nModelsPerJob = 2,
        outputFolder  = 'job_config.ringer.v10.cnn.10sorts.5inits'
        )



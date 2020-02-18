




from saphyra import *


# ppChain
from saphyra import PreProcChain_v1, Norm1, ReshapeToConv1D, NoPreProc

pp = PreProcChain_v1( [NoPreProc()] )

# import tensorflow/keras wrapper
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Input, Concatenate, Reshape, Dense, Dropout, Activation, Conv1D, Flatten, MaxPooling1D



model = Sequential()
model.add(Conv1D(16, kernel_size=2, activation='relu', input_shape=(100,1) ))
model.add(Conv1D(32, kernel_size=2, activation='relu' ))
model.add(Flatten())
model.add(Dense(32,  activation='relu'))
model.add(Dense(1, activation='linear'))
model.add(Activation('sigmoid'))



from sklearn.model_selection import StratifiedKFold, KFold
kf = StratifiedKFold(n_splits=10, random_state=512, shuffle=True)


createPandaJobs( models        = [model],
        ppChain       = pp,
        crossVal      = kf,
        nInits        = 5,
        nInitsPerJob  = 1,
        sortBounds    = 10,
        nSortsPerJob  = 1,
        nModelsPerJob = 1,
        outputFolder  = 'job_config.Zee_v10.10sorts.5inits'
        )



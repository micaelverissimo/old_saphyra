



from saphyra import *


# ppChain
from saphyra import PreProcChain_v1, Norm1, ReshapeToConv1D, NoPreProc

pp = PreProcChain_v1( [NoPreProc()] )



# import tensorflow/keras wrapper
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Input, Concatenate, Reshape, Dense, Dropout, Activation, Conv1D, Flatten, MaxPooling1D

input_ps = Input(shape=(8,1))
conv1_ps  = Conv1D( 8, kernel_size=2, activation='relu', name='conv1_ps' )(input_ps)
#conv2_ps  = Conv1D( 8, kernel_size=2, activation='relu', name='conv2_ps' )(conv1_ps)

input_em1 = Input(shape=(64,1))
conv1_em1  = Conv1D( 8, kernel_size=2, activation='relu', name='conv1_em1' )(input_em1)
#conv2_em1  = Conv1D( 8, kernel_size=2, activation='relu', name='conv2_em1' )(conv1_em1)

input_em2 = Input(shape=(8,1))
conv1_em2  = Conv1D( 8, kernel_size=2, activation='relu', name='conv1_em2' )(input_em2)
#conv2_em2  = Conv1D( 8, kernel_size=2, activation='relu', name='conv2_em2' )(conv1_em2)

input_em3 = Input(shape=(8,1))
conv1_em3  = Conv1D( 8, kernel_size=2, activation='relu', name='conv1_em3' )(input_em3)
#conv2_em3  = Conv1D( 8, kernel_size=2, activation='relu', name='conv2_em3' )(conv1_em3)

input_had1 = Input(shape=(4,1))
conv1_had1  = Conv1D( 8, kernel_size=2, activation='relu', name='conv1_had1' )(input_had1)
#conv2_had1  = Conv1D( 8, kernel_size=2, activation='relu', name='conv2_had1' )(conv1_had1)

input_had2 = Input(shape=(4,1))
conv1_had2  = Conv1D( 8, kernel_size=2, activation='relu', name='conv1_had2' )(input_had2)
#conv2_had2  = Conv1D( 8, kernel_size=2, activation='relu', name='conv2_had2' )(conv1_had2)

input_had3 = Input(shape=(4,1))
conv1_had3  = Conv1D( 8, kernel_size=2, activation='relu', name='conv1_had3' )(input_had3)
#conv2_had3  = Conv1D( 8, kernel_size=2, activation='relu', name='conv2_had3' )(conv1_had3)



merge_all = Concatenate(axis=1)([conv1_ps,conv1_em1,conv1_em2,conv1_em3,conv1_had1,conv1_had2,conv1_had3])
#merge_all = Concatenate(axis=1)([conv2_ps,conv2_em1,conv2_em2,conv2_em3,conv2_had1,conv2_had2,conv2_had3])
conv1_all  = Conv1D( 64, kernel_size=3, activation='relu', name='conv1_all' )(merge_all)
#conv2_all  = Conv1D( 64, kernel_size=2, activation='relu', name='conv2_all' )(conv1_all)
#conv3_all  = Conv1D( 64, kernel_size=2, activation='relu', name='conv3_all' )(conv2_all)
flatten   = Flatten(name='flatten')(conv1_all)
dense_1   = Dense(64,  activation='relu',name='dense1')(flatten)
dense_2   = Dense(1,  activation='linear',name='dense2')(dense_1)
output    = Activation('sigmoid',name='output')(dense_2)
model     = Model( [input_ps,input_em1,input_em2,input_em3,input_had1,input_had2,input_had3], output )




from sklearn.model_selection import StratifiedKFold, KFold
kf = StratifiedKFold(n_splits=10, random_state=512, shuffle=True)


from Gaugi import PythonLoopingBounds
createPandaJobs( models        = [model],
        ppChain       = pp,
        crossVal      = kf,
        nInits        = 5,
        nInitsPerJob  = 1,
        sortBounds    = PythonLoopingBounds(10),
        nSortsPerJob  = 1,
        nModelsPerJob = 1,
        outputFolder  = 'job_config.Zee_ringer.v11.RingerNet.10sorts.5inits'
        )



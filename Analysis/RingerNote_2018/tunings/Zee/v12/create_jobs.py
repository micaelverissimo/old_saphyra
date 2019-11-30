



from saphyra import *


# ppChain
from saphyra import PreProcChain_v1, Norm1, ReshapeToConv1D, NoPreProc

pp = PreProcChain_v1( [NoPreProc()] )



# import tensorflow/keras wrapper
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Input, Concatenate, Reshape, Dense, Dropout, Activation, Conv1D, Conv2D, Flatten, MaxPooling1D


#
# Eletromagnetic PS (Pre-Sampler)
#
input_ps = Input(shape=(8,1))
conv1d_1_ps  = Conv1D( 8, kernel_size=2, activation='relu', name='conv1d_1_ps' )(input_ps)
conv1d_2_ps  = Conv1D( 8, kernel_size=2, activation='relu', name='conv2d_2_ps' )(conv1d_1_ps)
ps = Reshape( (6,8,1), name='reshape_1_ps' )(conv1d_2_ps)
#
# Eletromagnetic EM1
#
input_em1 = Input(shape=(64,1))
#input_em1_reshaped = Reshape( (8,8), name='reshape_1_em1' )(input_em1)
#conv1d_1_em1  = Conv1D( 8, kernel_size=2, activation='relu', name='conv1d_1_em1' )(input_em1_reshaped)
conv1d_1_em1  = Conv1D( 8, kernel_size=2, activation='relu', name='conv1d_1_em1' )(input_em1) # 63
maxpol_1_em1  = MaxPooling1D( pool_size=2 )(conv1d_1_em1) # 32
conv1d_2_em1  = Conv1D( 8, kernel_size=2, activation='relu', name='conv1d_2_em1' )(maxpol_1_em1) # 31
maxpol_2_em1  = MaxPooling1D( pool_size=2 )(conv1d_2_em1) # 16
conv1d_3_em1  = Conv1D( 8, kernel_size=2, activation='relu', name='conv1d_3_em1' )(maxpol_2_em1) # 15
maxpol_3_em1  = MaxPooling1D( pool_size=2 )(conv1d_3_em1) # 7
conv1d_4_em1  = Conv1D( 8, kernel_size=2, activation='relu', name='conv1d_4_em1' )(maxpol_3_em1) # 15
em1 = Reshape( (6,8,1), name='reshape_2_em1' )(conv1d_4_em1)

#
# Eletromagnetic EM2
#
input_em2 = Input(shape=(8,1))
conv1d_1_em2  = Conv1D( 8, kernel_size=2, activation='relu', name='conv1d_1_em2' )(input_em2)
conv1d_2_em2  = Conv1D( 8, kernel_size=2, activation='relu', name='conv1d_2_em2' )(conv1d_1_em2)
em2 = Reshape( (6,8,1), name='reshape_1_em2' )(conv1d_2_em2)
#
# Eletromagnetic EM3
#
input_em3 = Input(shape=(8,1))
conv1d_1_em3  = Conv1D( 8, kernel_size=2, activation='relu', name='conv1d_1_em3' )(input_em3)
conv1d_2_em3  = Conv1D( 8, kernel_size=2, activation='relu', name='conv1d_2_em3' )(conv1d_1_em3)
em3 = Reshape( (6,8,1), name='reshape_1_em3' )(conv1d_2_em3)
#
# Hadronica HAD1
#
input_had1 = Input(shape=(4,1))
conv1d_1_had1  = Conv1D( 8, kernel_size=2, activation='relu', name='conv1d_1_had1' )(input_had1)
conv1d_2_had1  = Conv1D( 8, kernel_size=2, activation='relu', name='conv1d_2_had1' )(conv1d_1_had1)
had1 = Reshape( (2,8,1), name='reshape_1_had1' )(conv1d_2_had1)
#
# Hadronica HAD2
#
input_had2 = Input(shape=(4,1))
conv1d_1_had2  = Conv1D( 8, kernel_size=2, activation='relu', name='conv1d_1_had2' )(input_had2)
conv1d_2_had2  = Conv1D( 8, kernel_size=2, activation='relu', name='conv1d_2_had2' )(conv1d_1_had2)
had2 = Reshape( (2,8,1), name='reshape_1_had2' )(conv1d_2_had2)
#
# Hadronica HAD3
#
input_had3 = Input(shape=(4,1))
conv1d_1_had3  = Conv1D( 8, kernel_size=2, activation='relu', name='conv1d_1_had3' )(input_had3)
conv1d_2_had3  = Conv1D( 8, kernel_size=2, activation='relu', name='conv1d_2_had3' )(conv1d_1_had3)
had3 = Reshape( (2,8,1), name='reshape_1_had3' )(conv1d_2_had3)


#
#  Here, the shape is: (N_events, "rings", filter, layer)
#
# Eletronic merge (Longitudinal exploration), output is (None, 6, 8, 3)
merge_em = Concatenate(axis=3, name='concat_em')([ps,em1,em2,em3])
conv2d_1_em_merged = Conv2D( 8, kernel_size=(1,1), activation='relu', name='conv2d_1_em_merged')(merge_em) # output is (None, 6, 8, 16)




#
#  Here, the shape is: (N_events, "rings", filter, layer)
#
# Hadronic merge (Longitudinal exploration), output is (None, 2, 8, 3)
merge_had = Concatenate(axis=3, name='concat_had')([had1,had2,had3])
conv2d_1_had_merged = Conv2D( 8, kernel_size=(1,1), activation='relu', name='conv2d_1_had_merged')(merge_had) # output is (None, 2, 8, 16




# Explore all layers
merge_all          = Concatenate(axis=1,name='concat_all')([conv2d_1_em_merged, conv2d_1_had_merged]) # output is (None, 8, 8 , 16)
conv2d_1_merge_all =  Conv2D( 1, kernel_size=(1,1), name='conv2d_1_merge_all')(merge_all) # output is (None, 8, 8, 1)
r = Reshape( (8, 8) )(conv2d_1_merge_all)
n = Conv1D( 16, kernel_size=2)(r)

#conv2d_2_merge_all =  Conv2D( 16, kernel_size=(2,2), name='conv2d_2_merge_all')(Dropout(0,5)(conv2d_1_merge_all)) # output is (None, 6, 6, 16)
#conv2d_3_merge_all =  Conv2D( 32, kernel_size=(2,2), name='conv2d_3_merge_all')(conv2d_2_merge_all) # output is (None, 5, 5, 32)



# Fully connected (classification layer)
flatten   = Flatten(name='flatten')(n)
dense_1   = Dense(64,  activation='relu',name='dense_1')(flatten)
#dense_2   = Dense(8,  activation='relu' ,name='dense_2')(Dropout(0.5)(dense_1))
dense_3   = Dense(1,  activation='linear',name='dense_3')(dense_1)
output    = Activation('sigmoid',name='output')(dense_3)
model     = Model( [input_ps,input_em1,input_em2,input_em3,input_had1,input_had2,input_had3], output )

model.summary()



from sklearn.model_selection import StratifiedKFold, KFold
kf = StratifiedKFold(n_splits=10, random_state=512, shuffle=True)


from Gaugi import PythonLoopingBounds
createPandaJobs( models        = [model],
        ppChain       = pp,
        crossVal      = kf,
        nInits        = 1,
        nInitsPerJob  = 1,
        sortBounds    = PythonLoopingBounds(10),
        nSortsPerJob  = 1,
        nModelsPerJob = 1,
        outputFolder  = 'job_config.Zee_ringer.v10.RingerNet.10sorts.1inits'
        )







from saphyra import *
pandas=CreatePandaJobs()


# ppChain
from saphyra import PreProcChain_v1, Norm1
pp = PreProcChain_v1( [Norm1()] )



from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation
# creating the keras model first
model = Sequential()
model.add(Dense(100, input_shape=(100,)))
model.add(Activation('relu'))
model.add(Dropout(0.5))
model.add(Dense(5))
model.add(Activation('relu'))
model.add(Dense(1))
model.add(Activation('sigmoid'))
modelCol = [model]




from sklearn.model_selection import StratifiedKFold, KFold
#kf = StratifiedKFold(n_splits=10, random_state=1234, shuffle=True)
kf = KFold(n_splits=10, random_state=1234, shuffle=True)



from Gaugi import PythonLoopingBounds
pandas( models = modelCol,
        ppChain = pp,
        crossVal = kf,
        nInits = 10,
        nIninsPerJob = 10,
        sortBounds =  PythonLoopingBounds(10),
        nSortsPerJob = 5,
        outputFolder = 'job_test')


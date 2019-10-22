



from saphyra import *
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Activation, Conv1D, Flatten

kernel_size = 3
model = Sequential()
model.add(Conv1D(16, kernel_size=kernel_size, activation='relu', input_shape=(100,1) ))
model.add(Conv1D(32, kernel_size=kernel_size, activation='relu' ))
model.add(Dropout(0.25))
model.add(Flatten())
model.add(Dense(64,  activation='relu', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
model.add(Dropout(0.25))
model.add(Dense(1, activation='linear', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
model.add(Activation('sigmoid'))
models = [model]




from sklearn.model_selection import StratifiedKFold, KFold
kf = StratifiedKFold(n_splits=10, random_state=512, shuffle=True)
#kf = KFold(n_splits=10, random_state=1234, shuffle=True)




from saphyra.readers.versions import Job_v1

minibatchs = [256,512,1024,2048,4096,8196]
nJobs  = 0
for idx, minibatch in enumerate(minibatchs):

  job = Job_v1()
  # to be user by the database table
  job.setId( nJobs )
  job.setSorts([0])
  job.setInits([i for i in range(10)])
  job.setModels([model], [0])
  job.setMetadata( {'batch_size': minibatch} )
  # save the job
  job.save( 'job.minibatch.%d' % idx )







from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D, Activation

model = Sequential()
model.add(Conv2D(16, kernel_size=(3, 3), activation='relu', input_shape=(10,10,1)) ) # 8X8
model.add(Conv2D(32, (3, 3), activation='relu')) # 6X6
model.add(Flatten())
model.add(Dropout(0.25))
model.add(Dense(64, activation='relu'))
model.add(Dense(1))
model.add(Activation('tanh'))


from TuningTools.CreateTuningJobFiles import createTuningJobFiles
createTuningJobFiles( outputFolder   = 'config',
                      sortBounds     = 10,
                      nInits         = 1,
                      #neuronBounds   = [1,6],
                      nNeuronsPerJob = 1,
                      models         = model,
                      nInitsPerJob   = 1,
                      nSortsPerJob   = 10,
                      prefix         = 'job',
                      compress       = True )


#from TuningTools import TuningJobConfigArchieve
#with TuningJobConfigArchieve('config/job_slim.hn0001.s0000.i0000.pic.gz') as (n,s,i,m):
#  print m



#from TuningTools.CrossValid import CrossValid, CrossValidArchieve
#crossValid = CrossValid(nSorts = 10,
#                        nBoxes = 10,
#                        nTrain = 9, 
#                        nValid = 1,
#                        )
#place = CrossValidArchieve( 'crossValid', 
#                            crossValid = crossValid,
#                            ).save( True )


#from TuningTools.PreProc import *
#ppCol = PreProcChain( Norm1() ) 


#from TuningTools.TuningJob import fixPPCol
#ppCol = fixPPCol(ppCol)
#place = PreProcArchieve( 'ppFile', ppCol = ppCol ).save()


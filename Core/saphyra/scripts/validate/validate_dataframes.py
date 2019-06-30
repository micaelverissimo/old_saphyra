



from saphyra import CrossVal_v1
from Gaugi import load
from sklearn.model_selection import KFold

obj1 = CrossVal_v1( )
obj1.set_object( KFold(10, random_state=203) )
print obj1.get_object()
obj1.save( 'crossval.file.pic.gz' )


d = load( 'crossval.file.pic.gz' ) 
print d
obj2 = CrossVal_v1.fromRawObj( load( 'crossval.file.pic.gz' ) )
print obj2
print obj2.get_object()






from saphyra import Model_v1
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D

model = Sequential()
model.add(Conv2D(32, (3, 3), padding='same',
                   input_shape=(32, 32, 3)
                   ))
model.add(Activation('relu'))
model.add(Conv2D(32, (3, 3)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Conv2D(64, (3, 3), padding='same'))
model.add(Activation('relu'))
model.add(Conv2D(64, (3, 3)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Flatten())
model.add(Dense(512))
model.add(Activation('relu'))
model.add(Dropout(0.5))
model.add(Dense(10))
model.add(Activation('softmax'))
model.summary()




obj3 = Model_v1()
obj3.set_models( [model, model, model, model] )
obj3.save('model.file.pic.gz')


obj4 = Model_v1.fromRawObj( load('model.file.pic.gz') )
print obj4.get_models()






from saphyra import Job_v1

obj5 = Job_v1()
obj5.set_sorts(5)
obj5.set_inits(100)
obj5.save('job.file.pic.gz')


obj6 = Job_v1.fromRawObj( load('job.file.pic.gz'))
print obj6.get_sorts()
print obj6.get_inits()




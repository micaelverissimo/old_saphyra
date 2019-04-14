

from keras.models import Sequential
from keras.layers import Merge, Dense, Dropout, Flatten, Conv2D, MaxPooling2D, Activation
from keras.models import Model    
from keras.layers import *

model1 = Sequential()
model1.add(Conv2D(2, kernel_size=(2, 2), activation='relu', input_shape=(5,5,1)) )
model1.add(Conv2D(2, (2, 2), activation='relu')) # 6X6
model1.add(Flatten())
model1.add(Dropout(0.25))
model1.add(Dense(2, activation='relu'))

model2 = Sequential()
model2.add(Conv2D(3, kernel_size=(2, 2), activation='relu', input_shape=(3,3,1)) )
model2.add(Flatten())
model2.add(Dropout(0.25))
model2.add(Dense(3, activation='relu'))


conc = Concatenate()([model1.output, model2.output])

out = Dense(100, activation='relu')(conc)
out = Dropout(0.5)(out)
out = Dense(10, activation='softmax')(out)

model3 = Model([model1.input, model2.input], out)


#merged = Merge( [model1, model2], mode='concat' )
#model3 = Sequential()
#model3.add(merged)
#model3.add(Dense(3, activation='relu') )
#model3.add(Dense(1, activation='tanh') )



from keras.models import model_from_json
model4 = model_from_json(model3.to_json())
print model4.layers

model4.set_weights( model3.get_weights() )



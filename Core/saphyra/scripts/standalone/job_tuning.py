

from Gaugi.messenger import LoggingLevel, Logger
import argparse

mainLogger = Logger.getModuleLogger("job")
parser = argparse.ArgumentParser(description = '', add_help = False)
parser = argparse.ArgumentParser()

parser.add_argument('-c','--crossValFile', action='store', 
        dest='crossValFile', required = False, default = None,
            help = "The cross validation file. One per job.")

parser.add_argument('-d','--dataFile', action='store', 
        dest='datatFile', required = False, default = None,
            help = "The data file to be used in the training phase")

parser.add_argument('-o','--outputFile', action='store', 
        dest='outputFile', required = False, default = None,
            help = "The output store name.")

import sys,os
if len(sys.argv)==1:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()




# Loading the training samples
from Gaugi import load
data = load( args.inputFile )


# Get the cross validation index for this job
from saphyra.dataframe import CrossVal_v1 as CrossVal
crossval = CrossVal.load( args.cvfile )
crossval = crossval.get_object()
indexs = [(train_index, val_index) for train_index, val_index in crossval.split(data,target)]


from saphyra.dataframe import Model_v1 as Model
model_col  = Model.load( args.model_file )


from saphyra.dataframe import Job_v1 as Job
job = Job.load( args.job_file )


# create the model
from keras_core import sp, auc
from keras.callbacks import EarlyStopping
val_auc_stop = EarlyStopping(monitor = 'val_auc', min_delta=0.0, patience = 25, verbose=True, mode = 'auto')
val_sp_stop = EarlyStopping(monitor = 'val_sp', min_delta=0.0, patience = 25, verbose=True, mode = 'auto')

from keras.callbacks import ModelCheckpoint
checkpoint = ModelCheckpoint('best_model', monitor='val_sp', verbose=0, save_best_only=True, mode='max')
callbacks_list  =[sp(verbose=False) , checkpoint ,val_sp_stop]



for model in model_col.get_models():

  # compile the model
  model.compile( loss='binary_crossentropy', optimizer='adam', metrics=['accuracy',auc] )
  model.summary()

  for sort in job.get_sorts():

    # Get train/val datasets
    x_train = data[indexs[sort][0]]
    y_train = target[indexs[sort][0]]
    x_val   = data[indexs[sort][1]]
    y_val   = target[indexs[sort][1]]

    for init in job.get_inits():

      # Training
      history = model.fit(x_train, y_train, epochs=1000, batch_size=1024, verbose=1, 
                          validation_data=(x_val,y_val), callbacks = callbacks_list, 
                          shuffle = True)

      job.attach( sort, init, model.get_weights(), history )


job.save()





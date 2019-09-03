#!/usr/bin/env python

from saphyra import PandasJob, sp, PreProcChain_v1, Norm1, Summary, PileupFit, ReshapeToConv1D
from sklearn.model_selection import KFold,StratifiedKFold
from Gaugi.messenger import LoggingLevel, Logger
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Conv1D, Flatten
from Gaugi import load
import argparse
import sys,os
import numpy as np

mainLogger = Logger.getModuleLogger("job")
parser = argparse.ArgumentParser(description = '', add_help = False)
parser = argparse.ArgumentParser()


parser.add_argument('-o','--outputFile', action='store',
        dest='outputFile', required = False, default = None,
            help = "The output tuning name.")

parser.add_argument('-d','--dataFile', action='store',
        dest='dataFile', required = False, default = None,
            help = "The data/target file used to train the model.")

parser.add_argument('--layer', action='store', 
        dest='layer', required = True, default = 0, type=int,
            help = "The calo layer")


def get_model( ninputs ):
  modelCol = []
  from keras.models import Sequential
  from keras.layers import Dense, Dropout, Activation, Conv1D, Flatten
  for n in range(1,20+1):
    model = Sequential()
    model.add(Dense(n, input_shape=(ninputs,), activation='tanh', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
    model.add(Dense(1, activation='linear', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
    model.add(Activation('tanh'))
    modelCol.append(model)
  return modelCol




if len(sys.argv)==1:
  parser.print_help()
  sys.exit(1)

args = parser.parse_args()
is layer == 1:
  _slice = (0,7)
elif layer == 2:
  _slice = (8, 71)
elif layer == 3:
  _slice = (72, 79)
elif layer == 4:
  _slice = (80,87)
elif layer == 5:
  _slice = (88,91)
elif layer == 6:
  _slice = (92,95)
elif layer == 7:
  _slice = (96,99)
else:
  _slice = (0,99)

# Reading data and get all information needed
# by the tuning proceding
raw = load(args.dataFile)
data = raw['data'][:,1:101]
data = data[:,_slice[0]:_slice[1]]
target = raw['target']
pileup = raw['data'][:,0]
del raw




ref_target = [
              ('tight_v8'       , 'T0HLTElectronRingerTight_v8'     ),
              ('medium_v8'      , 'T0HLTElectronRingerMedium_v8'    ),
              ('loose_v8'       , 'T0HLTElectronRingerLoose_v8'     ),
              ('vloose_v8'      , 'T0HLTElectronRingerVeryLoose_v8' ),
              ('tight_v6'       , 'T0HLTElectronRingerTight_v6'     ),
              ('medium_v6'      , 'T0HLTElectronRingerMedium_v6'    ),
              ('loose_v6'       , 'T0HLTElectronRingerLoose_v6'     ),
              ('vloose_v6'      , 'T0HLTElectronRingerVeryLoose_v6' ),
              ('tight_cutbased' , 'T0HLTElectronT2CaloTight'        ),
              ('medium_cutbased', 'T0HLTElectronT2CaloMedium'       ),
              ('loose_cutbased' , 'T0HLTElectronT2CaloLoose'        ),
              ('vloose_cutbased', 'T0HLTElectronT2CaloVLoose'       ),
              ]

posproc = [Summary()]

obj = PileupFit( "PileupFit", pileup )

# Calculate the reference for each operation point
# using the ringer v6 tuning as reference
for ref in ref_target:
  d = raw['data'][:,np.where(raw['features'] == ref[1])[0][0]-1]
  d_s = d[target==1]
  d_b = d[target!=1]
  pd = sum(d_s)/float(len(d_s))
  fa = sum(d_b)/float(len(d_b))
  obj.add( ref[0], ref[1], pd, fa )

posproc.append( obj )

# remove raw data
del raw



# ppChain
from saphyra import PreProcChain_v1, Norm1
pp = PreProcChain_v1( [Norm1()] )


from sklearn.model_selection import StratifiedKFold, KFold
kf = StratifiedKFold(n_splits=10, random_state=512, shuffle=True)



ninputs = _slice[1] - _slice[0] + 1

# Create the job
job = PandasJob(  models    = get_model( ninputs ),
                  sorts     = range(10),
                  inits     = [0],
                  loss      = 'mse',
                  metrics   = ['accuracy'],
                  epochs    = 5000,
                  ppChain   = pp,
                  crossval  = kf,
                  outputfile= args.outputFile,
                  data      = data,
                  target    = target,
                  batch_size= 4096,
                  class_weight = True )


job.posproc   += posproc
# SP stop (regularization)
job.callbacks += [sp(patience=25, verbose=True, save_the_best=True)]
job.initialize()
job.execute()
job.finalize()










#!/usr/bin/env python

import ROOT
import keras
import numpy
import sklearn
import Gaugi
import saphyra



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



parser.add_argument('-c','--configFile', action='store', 
        dest='configFile', required = True,
            help = "The job config file that will be used to configure the job (sort and init).")

parser.add_argument('-o','--outputFile', action='store', 
        dest='outputFile', required = False, default = None,
            help = "The output tuning name.")


parser.add_argument('-d','--dataFile', action='store', 
        dest='dataFile', required = False, default = None,
            help = "The data/target file used to train the model.")


parser.add_argument('-r','--refFile', action='store', 
        dest='refFile', required = False, default = None,
            help = "The reference file.")



if len(sys.argv)==1:
  parser.print_help()
  sys.exit(1)

args = parser.parse_args()


# Reading data and get all information needed
# by the tuning proceding
raw = load(args.dataFile)
data = raw['data'][:,1:101]
target = raw['target']
pileup = raw['data'][:,0]
del raw


ref_target = [
              ('tight_cutbased' , 'T0HLTElectronT2CaloTight'        ),
              ('medium_cutbased', 'T0HLTElectronT2CaloMedium'       ),
              ('loose_cutbased' , 'T0HLTElectronT2CaloLoose'        ),
              ('vloose_cutbased', 'T0HLTElectronT2CaloVLoose'       ),
              ]



from saphyra import ReferenceReader
ref_obj = ReferenceReader().load(args.refFile)

posproc = [Summary()]
obj = PileupFit( "PileupFit", pileup )
# Calculate the reference for each operation point
# using the ringer v6 tuning as reference
for ref in ref_target:
  pd = ref_obj.getSgnPassed(ref[0]) / float(ref_obj.getSgnTotal(ref[0]))
  fa = ref_obj.getBkgPassed(ref[0]) / float(ref_obj.getBkgTotal(ref[0]))
  obj.add( ref[0], ref[1], pd, fa )
posproc.append( obj )




from sklearn.model_selection import StratifiedKFold, KFold
kf = StratifiedKFold(n_splits=10, random_state=512, shuffle=True)

from saphyra import PreProcChain_v1, Norm1
pp = PreProcChain_v1( [Norm1()] )



def get_model( neurons ):
  modelCol = []
  for n in neurons:
    model = Sequential()
    model.add(Dense(n, input_shape=(100,), activation='tanh', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
    model.add(Dense(1, activation='linear', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
    model.add(Activation('tanh'))
    modelCol.append(model)
  return modelCol


# Create the job
job = PandasJob(  job       = args.configFile, 
                  models    = get_model( [1,2,3,4,5,6,7,8,9,10] ),
                  #loss      = 'binary_crossentropy',
                  loss      = 'mse',
                  metrics   = ['accuracy'],
                  epochs    = 5000,
                  ppChain   = pp,
                  crossval  = kf,
                  outputfile= args.outputFile,
                  data      = data,
                  target    = target,
                  class_weight = True )


job.posproc   += posproc
# SP stop (regularization)
job.callbacks += [sp(patience=25, verbose=True, save_the_best=True)]
job.initialize()
job.execute()
job.finalize()








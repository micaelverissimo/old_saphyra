#!/usr/bin/env python


def getPatterns( path ):
  from Gaugi import load
  d = load(path)
  data = d['data'][:,1:101]
  target = d['target']
  return data, target


def getPileup( path ):
  from Gaugi import load
  return load(path)['data'][:,0]



def getModel():
  modelCol = []
  from keras.models import Sequential
  from keras.layers import Dense, Dropout, Activation, Conv1D, Flatten
  for n in range(1,20+1):
    model = Sequential()
    model.add(Dense(n, input_shape=(100,), activation='tanh', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
    model.add(Dense(1, activation='linear', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
    model.add(Activation('tanh'))
    modelCol.append(model)
  return modelCol





from saphyra import PandasJob, PatternGenerator,  sp, PreProcChain_v1, Norm1, Summary, PileupFit, ReshapeToConv1D
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


parser.add_argument('-r','--refFile', action='store', 
        dest='refFile', required = False, default = None,
            help = "The reference file.")



if len(sys.argv)==1:
  parser.print_help()
  sys.exit(1)

args = parser.parse_args()

from saphyra import PreProcChain_v1, Norm1
pp = PreProcChain_v1( [Norm1()] )

from sklearn.model_selection import StratifiedKFold, KFold
kf = StratifiedKFold(n_splits=10, random_state=512, shuffle=True)

from saphyra import ReferenceReader
ref_obj = ReferenceReader().load(args.refFile)


ref_target = [
              ('tight_cutbased' , 'T0HLTElectronT2CaloTight'        ),
              ('medium_cutbased', 'T0HLTElectronT2CaloMedium'       ),
              ('loose_cutbased' , 'T0HLTElectronT2CaloLoose'        ),
              ('vloose_cutbased', 'T0HLTElectronT2CaloVLoose'       ),
              ]


posproc = [Summary()]
correction = PileupFit( "PileupFit", getPileup(args.dataFile) )
# Calculate the reference for each operation point
# using the ringer v6 tuning as reference
for ref in ref_target:
  pd = ref_obj.getSgnPassed(ref[0]) / float(ref_obj.getSgnTotal(ref[0]))
  fa = ref_obj.getBkgPassed(ref[0]) / float(ref_obj.getBkgTotal(ref[0]))
  correction.add( ref[0], ref[1], pd, fa )
posproc = [Summary(), correction]




# Create the job
job = PandasJob(  pattern_generator = PatternGenerator( args.dataFile, getPatterns ), 
                  models    = getModel(),
                  sorts     = range(10),
                  inits     = [0],
                  loss      = 'mse',
                  metrics   = ['accuracy'],
                  epochs    = 5,
                  ppChain   = pp,
                  crossval  = kf,
                  outputfile= args.outputFile,
                  batch_size= 4096,
                  class_weight = True )


job.posproc   += posproc
# SP stop (regularization)
job.callbacks += [sp(patience=25, verbose=True, save_the_best=True)]
job.initialize()
job.execute()
job.finalize()










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



parser.add_argument('-c','--configFile', action='store', 
        dest='configFile', required = True,
            help = "The job config file that will be used to configure the job (sort and init).")

parser.add_argument('-o','--outputFile', action='store', 
        dest='outputFile', required = False, default = None,
            help = "The output tuning name.")

parser.add_argument('-x','--crossValFile', action='store', 
        dest='crossValFile', required = False, default = None,
            help = "The crossval file.")

parser.add_argument('-d','--dataFile', action='store', 
        dest='dataFile', required = False, default = None,
            help = "The data/target file used to train the model.")


parser.add_argument('-p','--ppFile', action='store', 
        dest='ppFile', required = False, default = None,
            help = "The preproc chain file.")

parser.add_argument('-m','--modelFile', action='store', 
        dest='modelFile', required = False, default = None,
            help = "The Keras model collection file.")



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


# Create the job
job = PandasJob(  
                  job       = args.configFile, 
                  models    = args.modelFile,
                  loss      = 'mse',
                  metrics   = ['accuracy'],
                  epochs    = 5,
                  ppChain   = args.ppFile,
                  crossval  = args.crossValFile,
                  outputfile= args.outputFile,
                  data      = data,
                  target    = target,
                  class_weight = True,
                  )


job.posproc   += posproc
# SP stop (regularization)
job.callbacks += [sp(patience=50, verbose=True, save_the_best=True)]
job.initialize()
job.execute()
job.finalize()










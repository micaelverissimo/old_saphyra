#!/usr/bin/env python

import sys,os
import argparse
import numpy as np

from saphyra import (PandasJob,
                     PatternGenerator, 
                     sp, 
                     PreProcChain_v1, 
                     Norm1,
                     ReferenceFit, 
                     Summary, 
                     ReshapeToConv1D,
                     ReferenceReader)

from sklearn.model_selection import KFold,StratifiedKFold
from Gaugi.messenger import LoggingLevel, Logger
from Gaugi import load

try:
  from tensorflow.compat.v1 import ConfigProto
  from tensorflow.compat.v1 import InteractiveSession

  config = ConfigProto()
  config.gpu_options.allow_growth = True
  session = InteractiveSession(config=config)
except Exception as e:
  print(e)
  print("Not possible to set gpu allow growth")


def getPatterns( path, cv, sort):
  from Gaugi import load
  d = load(path)
  data = d['data'][:,1:101]
  target = d['target']

  splits = [(train_index, val_index) for train_index, val_index in cv.split(data,target)]
  
  x_train = data [ splits[sort][0]]
  y_train = target [ splits[sort][0] ]
  x_val = data [ splits[sort][1]]
  y_val = target [ splits[sort][1] ]

  return x_train, x_val, y_train, y_val, splits



def getPileup( path ):
  return load(path)['data'][:,0]


def getJobConfigId( path ):
  return dict(load(path))['id']

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

parser.add_argument('-t', '--task', action='store', 
                    dest='task', required = True, default = None,
                    help = "The task name into the database")

parser.add_argument('-u', '--user', action='store',
                    dest='user', required = True, default = None,
                    help = "The user name into the database")

if len(sys.argv)==1:
  parser.print_help()
  sys.exit(1)

args = parser.parse_args()

job_id = getJobConfigId( args.configFile )
from ringerdb import DBContext
dbcontext = DBContext( args.user, args.task, job_id )

try:
  print('starting...')

  outputFile = args.outputFile
  if '/' in outputFile:
    # This is a path
    outputFile = (outputFile+'/tunedDiscr.jobID_%s'%str(job_id).zfill(4)).replace('//','/')
  else:
    outputFile+='.jobId_%s'%str(job_id).zfill(4)

  ref_target = [
                ('tight_cutbased' , 'T0HLTElectronT2CaloTight'        ),
                ('medium_cutbased', 'T0HLTElectronT2CaloMedium'       ),
                ('loose_cutbased' , 'T0HLTElectronT2CaloLoose'        ),
                ('vloose_cutbased', 'T0HLTElectronT2CaloVLoose'       ),
                ]
  
  
  print('loading references...')
  ref_obj = ReferenceReader().load(args.refFile)
  
  # cross validation
  kf = StratifiedKFold(n_splits=10, random_state=512, shuffle=True)
  
  # ppChain
  pp = PreProcChain_v1( [Norm1()] )
  print(pp)
  
  
  # NOTE: This must be default, always
  posproc = [Summary()]

  # print('laoding pileup from data file....')
  # correction = PileupFit( "PileupFit", getPileup(args.dataFile) )
  # # Calculate the reference for each operation point
  # # using thdocker login https://hub.docker.come ringer v6 tuning as reference
  # for ref in ref_target:
  #   # (passed, total)
  #   pd = (ref_obj.getSgnPassed(ref[0]) , ref_obj.getSgnTotal(ref[0]))
  #   fa = (ref_obj.getBkgPassed(ref[0]) , ref_obj.getBkgTotal(ref[0]))
  #   correction.add( ref[0], ref[1], pd, fa )
  # posproc = [Summary(), correction]

  # Calculate the reference for each operation point
  # using the ringer cutbased as reference
  correction = ReferenceFit( "ReferenceFit" )
  for ref in ref_target:
    # (passed, total)
    pd = (ref_obj.getSgnPassed(ref[0]) , ref_obj.getSgnTotal(ref[0]))
    fa = (ref_obj.getBkgPassed(ref[0]) , ref_obj.getBkgTotal(ref[0]))
    correction.add( ref[0], ref[1], pd, fa )
  posproc = [Summary(), correction]
  
  print('start panda!')
  # Create the panda job 
  job = PandasJob(  dbcontext, pattern_generator = PatternGenerator( args.dataFile, getPatterns ), 
                    job               = args.configFile, 
                    loss              = 'mean_squared_error',
                    #loss              = 'binary_crossentropy',
                    metrics           = ['accuracy'],
                    epochs            = 5000,
                    ppChain           = pp,
                    crossval          = kf,
                    outputfile        = outputFile,
                    class_weight      = True,
                    #save_history      = False,
                    )
  
  job.posproc   += posproc
  job.callbacks += [sp(patience=100, verbose=True, save_the_best=True)]
  job.initialize()
   
  job.execute()
  job.finalize()
  
  sys.exit(0)

except  Exception as e:
  print(e)
  sys.exit(1)

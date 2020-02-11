#!/usr/bin/env python

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
 
  
  def norm1( data ):
      norms = np.abs( data.sum(axis=1) )
      norms[norms==0] = 1
      return data/norms[:,None]
  
  def reshape( data ):
      data = np.array([data])
      return np.transpose(data, [1,2,0])

  # Load data
  d = load(path)
  data = norm1(d['data'][:,1:101])
  target = d['target']

  # This is mandatory
  splits = [(train_index, val_index) for train_index, val_index in cv.split(data,target)]

  x_train = reshape( data [ splits[sort][0] ]  )
  y_train = target [ splits[sort][0] ]
  x_val   = reshape(data [ splits[sort][1] ]),
  y_val   = target [ splits[sort][1] ]

  return x_train, x_val, y_train, y_val, splits




def getPileup( path ):
  from Gaugi import load
  return load(path)['data'][:,0]


def getJobConfigId( path ):
  from Gaugi import load
  return dict(load(path))['id']


from saphyra import PandasJob, PatternGenerator, sp, PreProcChain_v1, Norm1, ReferenceFit,Summary, ReshapeToConv1D
from sklearn.model_selection import KFold,StratifiedKFold
from Gaugi.messenger import LoggingLevel, Logger
from Gaugi import load
import numpy as np
import argparse
import sys,os


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

parser.add_argument('--useDB', action='store',
        dest='useDB', required = False, default = False,
            help = "Use database.")


if len(sys.argv)==1:
  parser.print_help()
  sys.exit(1)

args = parser.parse_args()


# Check if this job will run in DB mode
useDB = args.useDB
job_id = getJobConfigId( args.configFile )


from ringerdb import DBContext
dbcontext = DBContext( args.user, args.task, job_id )

if useDB:


    from ringerdb import RingerDB, DBContext
    from ringerdb.models import *
    url = 'postgres://ringer:6sJ09066sV1990;6@postgres-ringer-db.cahhufxxnnnr.us-east-2.rds.amazonaws.com/ringer'
    try:
      db = RingerDB(url, dbcontext)
      if db.initialize().isFailure():  useDB=False
    except Exception as e:
      print(e)
      useDB=False

try:

  if useDB:
    db.getContext().job().setStatus( "starting" ); db.commit()
  
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
  
  
  from saphyra import ReferenceReader
  ref_obj = ReferenceReader().load(args.refFile)
  
  from sklearn.model_selection import StratifiedKFold, KFold
  kf = StratifiedKFold(n_splits=10, random_state=512, shuffle=True)
  
  # ppChain
  from saphyra import PreProcChain_v1, NoPreProc
  pp = PreProcChain_v1( [NoPreProc()] )
  
  
  # NOTE: This must be default, always
  posproc = [Summary()]
  
  correction = ReferenceFit( "ReferenceFit" )
  # Calculate the reference for each operation point
  # using the ringer v6 tuning as reference
  for ref in ref_target:
    # (passed, total)
    pd = (ref_obj.getSgnPassed(ref[0]) , ref_obj.getSgnTotal(ref[0]))
    fa = (ref_obj.getBkgPassed(ref[0]) , ref_obj.getBkgTotal(ref[0]))
    correction.add( ref[0], ref[1], pd, fa )
  posproc = [Summary(), correction]
  
  
  # Create the panda job
  job = PandasJob(  dbcontext, pattern_generator = PatternGenerator( args.dataFile, getPatterns ),
                    job               = args.configFile,
                    #loss              = 'mean_squared_error',
                    loss              = 'binary_crossentropy',
                    metrics           = ['accuracy'],
                    epochs            = 2,
                    ppChain           = pp,
                    crossval          = kf,
                    outputfile        = outputFile,
                    class_weight      = True,
                    #save_history      = False,
                    )
  
  job.posproc   += posproc
  job.callbacks += [sp(patience=25, verbose=True, save_the_best=True)]
  job.initialize()
  
  if useDB:
    job.setDatabase( db )
    db.getContext().job().setStatus('running')
    db.commit()
  
  job.execute()
  job.finalize()
  
  if useDB:
    db.getContext().job().setStatus('done')
    db.commit()
    db.finalize()
  sys.exit(0)

except  Exception as e:
  print(e)
  if useDB:
    db.getContext().job().setStatus('failed')
    db.commit()
    db.finalize()
  sys.exit(1)

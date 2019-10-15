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


def getJobConfigId( path ):
  from Gaugi import load
  return dict(load(path))['id']

from saphyra import PandasJob, PatternGenerator, sp, PreProcChain_v1, Norm1, Summary, PileupFit, ReshapeToConv1D
from sklearn.model_selection import KFold,StratifiedKFold
from Gaugi.messenger import LoggingLevel, Logger
from Gaugi import load
import numpy as np
import argparse
import sys,os


from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession
import tensorflow as tf
config = ConfigProto()
config.gpu_options.allow_growth = True
tf.keras.backend.set_session(tf.Session(config=config))


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




parser.add_argument('--taskName', action='store', 
        dest='taskName', required = False, default = None,
            help = "The task name into the database")


if len(sys.argv)==1:
  parser.print_help()
  sys.exit(1)

args = parser.parse_args()


# Check if this job will run in DB mode
useDB = True if (args.taskName) else False


if useDB:
    from ringerdb import RingerDB
    from ringerdb.models import *
    url = 'postgres://ringer:6sJ09066sV1990;6@postgres-ringer-db.cahhufxxnnnr.us-east-2.rds.amazonaws.com/ringer'
    try:
      db = RingerDB('jodafons', url)
    except Exception as e:
      print(e)
      raise SystemExit

    task = db.getTask( args.taskName )
    if not task:
      print("there is no this task name (%s) into the database. abort...")
      sys.exit()

    id = getJobConfigId( args.configFile )
    job = task.getJob(id)
    if not job:
      print("there is no job with configId (%s) into the database. abort...")
      raise SystemExit
    #from sqlalchemy import and_
    #job = db.session().query(Job).filter( and_(Job.taskId==task.id ,Job.configId==id) ).first()
    print(job)
    # check if there is model into the job. If yes, we must erase and retry
    models = job.getModels()
    if models:
      for model in models:
        print("Delete: %s"%model)
        db.session().delete(model)
        db.commit()
      job.retry = job.retry+1
      db.commit()
    
    # Fill this execArgs just for good practicy
    db.setCurrentTask( task )
    db.setCurrentJob(job)
   



try:

  if useDB:
    db.getCurrentJob().setStatus( "starting" )
    db.commit()


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
  from saphyra import PreProcChain_v1, Norm1, ReshapeToConv1D
  pp = PreProcChain_v1( [Norm1(), ReshapeToConv1D()] )
  
  
  # NOTE: This must be default, always
  posproc = [Summary()]

  correction = PileupFit( "PileupFit", getPileup(args.dataFile) )
  # Calculate the reference for each operation point
  # using the ringer v6 tuning as reference
  for ref in ref_target:
    # (passed, total)
    pd = (ref_obj.getSgnPassed(ref[0]) , ref_obj.getSgnTotal(ref[0]))
    fa = (ref_obj.getBkgPassed(ref[0]) , ref_obj.getBkgTotal(ref[0]))
    correction.add( ref[0], ref[1], pd, fa )
  posproc = [Summary(), correction]
  
  
  # Create the panda job 
  pjob = PandasJob(  pattern_generator = PatternGenerator( args.dataFile, getPatterns ), 
                    job               = args.configFile, 
                    loss              = 'binary_crossentropy',
                    metrics           = ['accuracy'],
                    epochs            = 2,
                    ppChain           = pp,
                    crossval          = kf,
                    outputfile        = args.outputFile,
                    class_weight      = True,
                    #save_history      = False,
                    )
  
  pjob.posproc   += posproc
  pjob.callbacks += [sp(patience=25, verbose=True, save_the_best=True)]
  pjob.initialize()
  
  if useDB:
    pjob.setDBContext( db )
    db.getCurrentJob().setStatus('running')
    db.commit()
  

  pjob.execute()
  pjob.finalize()
  
  if useDB:
    db.getCurrentJob().setStatus('done')
    db.commit()
  

except  Exception as e:
  print(e)
  if useDB:
    db.getCurrentJob().setStatus('failed')
    db.commit()
  raise SystemExit


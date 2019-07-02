#!/usr/bin/env python

from Gaugi.messenger import LoggingLevel, Logger
import argparse

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



import sys,os
if len(sys.argv)==1:
  parser.print_help()
  sys.exit(1)

args = parser.parse_args()




from Gaugi import load
raw = load(args.dataFile)
data = raw['data'][:,0:100]
target = raw['target']
target=target.astype(int)
del raw


from saphyra import PandaJob, sp, PreProcChain_v1, Norm1
from sklearn.model_selection import KFold,StratifiedKFold

job = PandaJob(   job       = args.configFile, 
                  models    = args.modelFile,
                  loss      = 'binary_crossentropy',
                  metrics   = ['accuracy'],
                  epochs    = 5000,
                  ppChain   = args.ppFile,
                  crossval  = args.crossValFile,
                  #crossval   = StratifiedKFold(2, shuffle=True, random_state=0),
                  #ppChain   = PreProcChain_v1([Norm1(), Norm1()]),
                  outputfile= args.outputFile,
                  class_weight = False,
                  data      = data,
                  target    = target,
                  )


job.callbacks +=   [sp(patience=25, verbose=True, save_the_best=True)]
job.initialize()
job.execute()
job.finalize()










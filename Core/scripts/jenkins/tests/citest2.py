#!/usr/bin/env python
from timeit import default_timer as timer
from RingerCore import Logger, LoggingLevel
from TuningTools import TuningJob
from TuningTools.TuningJob import BatchSizeMethod
from TuningTools.PreProc import *
import logging

start = timer()
DatasetLocationInput = 'data/tuningData_citest1.npz'
tuningJob = TuningJob()
tuningJob( DatasetLocationInput, 
           #neuronBoundsCol = [5, 5], 
           #sortBoundsCol = [0, 1],
           #initBoundsCol = 10, 
           confFileList = 'data/config_citest0.pic.gz',
           crossValidFile = 'data/crossValid_citest0.pic.gz',
           epochs = 6,
           showEvo = 0,
           doMultiStop = True,
           maxFail = 100,
           #batchSize = 10,
           #batchMethod = BatchSizeMethod.OneSample,
           #seed = 0,
           refFilePath='data/tuningData_citest1-eff.npz',
           ppFile = 'data/ppFile_citest0.pic.gz',
           #clusterFile='data/crossValidSubset_citest0.pic.gz',
           #crossValidSeed = 66,
           level = 10
           )

end = timer()

print 'execution time is: ', (end - start)     
import sys,os
sys.exit(os.EX_OK) # code 0, all ok

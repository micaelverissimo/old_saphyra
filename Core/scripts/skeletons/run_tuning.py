#!/usr/bin/env python
from timeit import default_timer as timer
from RingerCore.Logger import Logger, LoggingLevel
from TuningTools.TuningJob import TuningJob
from TuningTools.PreProc import *
import logging

start = timer()
basepath = 'files'
DatasetLocationInput = basepath + '/data.pic.npz'


tuningJob = TuningJob()
tuningJob( DatasetLocationInput, 
           #neuronBoundsCol = [5, 5], 
           #sortBoundsCol = [0, 1],
           #initBoundsCol = 10, 
           confFileList = basepath + '/config.nn5to6_sorts5_5by5_inits5_5by5/job.hnl0005.hnu0006.sl0000.su0004.il0000.iu0004.pic.gz',
           ppFileList = basepath+'/ppMapStd.pic.gz',
           crossValidFile = basepath+'/crossValid_5sorts.pic.gz',
           epochs = 5000,
           showEvo = 0,
           doMultiStop = True,
           maxFail = 100,
           #seed = 0,
           #ppCol = PreProcCollection( PreProcChain( MapStd() ) ),
           #crossValidSeed = 66,
           level = 10
           )


end = timer()

print 'execution time is: ', (end - start)      

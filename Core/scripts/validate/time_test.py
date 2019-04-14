#!/usr/bin/env python

# TODO Improve skeleton documentation

from timeit import default_timer as timer

start = timer()

DatasetLocationInput = '/afs/cern.ch/work/j/jodafons/public/validate_tuningtool/mc14_13TeV.147406.129160.sgn.offLikelihood.bkg.truth.trig.e24_lhmedium_L1EM20VH_etBin_0_etaBin_0.npz'

#try:
from RingerCore import Logger, LoggingLevel
mainLogger = Logger.getModuleLogger(__name__)
mainLogger.info("Entering main job.")

from TuningTools import TuningJob
tuningJob = TuningJob()

from TuningTools.PreProc import *

basepath = '/afs/cern.ch/work/j/jodafons/public'

tuningJob( DatasetLocationInput, 
           neuronBoundsCol = [15, 15], 
           sortBoundsCol = [0, 1],
           initBoundsCol = 5, 
           #confFileList = basepath + '/user.wsfreund.config.nn5to20_sorts50_1by1_inits100_100by100/job.hn0015.s0040.il0000.iu0099.pic.gz',
           #ppFileList = basepath+'/user.wsfreund.Norm1/ppFile_pp_Norm1.pic.gz',
           #crossValidFile = basepath+'/user.wsfreund.CrossValid.50Sorts.seed_0/crossValid.pic.gz',
           epochs = 100,
           showEvo = 0,
           #algorithmName= 'rprop',
           #doMultiStop = True,
           #doPerf = True,
           maxFail = 100,
           #seed = 0,
           ppCol = PreProcCollection( PreProcChain( MapStd() ) ),
           crossValidSeed = 66,
           level = LoggingLevel.DEBUG )

mainLogger.info("Finished.")

end = timer()

print 'execution time is: ', (end - start)      

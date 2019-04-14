#!/usr/bin/env python

# TODO Improve skeleton documentation

from timeit import default_timer as timer

start = timer()

DatasetLocationInput = '/afs/cern.ch/work/j/jodafons/public/validate_tuningtool/mc14_13TeV.147406.129160.sgn.offLikelihood.bkg.truth.trig.e24_lhmedium_nod0_l1etcut20_l2etcut19_efetcut24_binned.pic.npz'

#DatasetLocationInput = '/afs/cern.ch/work/j/jodafons/public/validate_tuningtool/mc14_13TeV.147406.129160.sgn.offLikelihood.bkg.truth.trig.e24_lhmedium_L1EM20VH_etBin_0_etaBin_0.npz'

#try:
from RingerCore.Logger import Logger, LoggingLevel
mainLogger = Logger.getModuleLogger(__name__)
mainLogger.info("Entering main job.")

from TuningTools.TuningJob import TuningJob
tuningJob = TuningJob()

from TuningTools.PreProc import *

basepath = '/afs/cern.ch/work/j/jodafons/public'

tuningJob( DatasetLocationInput, 
           neuronBoundsCol = [15, 15], 
           sortBoundsCol = [0, 1],
           initBoundsCol = 1, 
           epochs = 1000,
           showEvo = 1,
           detGoal = 0.99,
           faGoal = 0.30,
           doMultiStop = True,
           #doPerf = True,
           maxFail = 100,
           #seed = 0,
           ppCol = PreProcCollection( PreProcChain( MapStd() ) ),
           #ppCol = PreProcCollection( PreProcChain( Norm1() ) ),
           crossValidSeed = 66,
           etBins = [1],
           etaBins = [1],
           level = LoggingLevel.DEBUG )

end = timer()
print 'execution time is: ', (end - start)      

mainLogger.info("Finished.")

'''
from TuningTools.TuningJob import TunedDiscrArchieve

obj = TunedDiscrArchieve( "nn.tuned.ppstd.hn0015.s0000.i0000.et0001.eta0001.pic.gz" )
mDict = dict()
with obj as TDArchieve:
  nets = TDArchieve.getData()['tunedDiscriminators'][0]
  mDict['sp']  = nets[0]['trainEvolution']
  mDict['det'] = nets[1]['trainEvolution']
  mDict['fa']  = nets[2]['trainEvolution']

import scipy.io
scipy.io.savemat('validate_stops.mat', mDict)
'''



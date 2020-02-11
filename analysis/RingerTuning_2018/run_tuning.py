#/usr/bin/env python
from timeit import default_timer as timer
from RingerCore.Logger import Logger, LoggingLevel
from TuningTools.TuningJob import TuningJob
from TuningTools.PreProc import *
import logging

start = timer()
#DatasetLocationInput = 'data/files/data17_13TeV.AllPeriods.sgn.probes_EGAM1.bkg.vetoProbes_EGAM7_et4_eta0.npz'
DatasetLocationInput = 'data/files/data17_13TeV.AllPeriods.sgn.probes_EGAM1.bkg.VProbes_EGAM7.GRL_v97_et2_eta0.npz'

ppCol = PreProcChain( RingerEtaMu(pileupThreshold=100, etamin=0.0, etamax=0.8) ) 
#ppCol = PreProcChain( Norm1() ) 
#ppCol = PreProcChain( RingerRp(alpha=0.5,beta=0.5) ) 
from TuningTools.TuningJob import fixPPCol
#ppCol = fixPPCol(ppCol)
from TuningTools.coreDef      import coreConf, TuningToolCores
coreConf.conf = TuningToolCores.FastNet
from TuningTools.TuningJob    import ReferenceBenchmark,   ReferenceBenchmarkCollection, BatchSizeMethod

from RingerCore.Configure import Development
Development.set( True )


tuningJob = TuningJob()
tuningJob( DatasetLocationInput, 
           neuronBoundsCol = [5, 5], 
           sortBoundsCol = [0, 1],
           initBoundsCol =2, 
           epochs = 1000,
           batchSize=20000,
           #batchMethod=BatchSizeMethod.HalfSizeSignalClass,
           showEvo = 10,
           doMultiStop = False,
           maxFail = 100,
           #ppCol = ppCol,
           #level = 10,
           etBins = 2,
           etaBins = 0,
           crossValidFile= 'data/files/crossValid.GRL_v97.pic.gz',
           ppFile='ppFile.pic.gz',
           #confFileList='config.n5to20.jackKnife.inits_100by100/job.hn0009.s0000.il0000.iu0099.pic.gz',
           refFile='data/files/data17_13TeV.allPeriods.tight_effs.GRL_v97.npz',
           )


end = timer()

print 'execution time is: ', (end - start)      

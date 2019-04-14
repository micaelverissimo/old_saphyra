#/usr/bin/env python
from timeit import default_timer as timer
from RingerCore.Logger import Logger, LoggingLevel
from TuningTools.TuningJob import TuningJob
from TuningTools.PreProc import *
import logging

start = timer()
DatasetLocationInput = 'data/files/data17_13TeV.AllPeriods.sgn.probes_EGAM2.bkg.VProbes_EGAM7.GRL_v97_et0_eta0.npz'

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
           initBoundsCol =1, 
           epochs = 1000,
           showEvo = 1,
           doMultiStop = False,
           #ppCol = ppCol,
           #level = 10,
           etBins = 0,
           etaBins = 0,
           crossValidFile= 'data/files/crossValid_10sorts.pic.gz',
           ppFile='data/files/preproc_norm1.pic.gz',
           #confFileList='config.n5to20.jackKnife.inits_100by100/job.hn0009.s0000.il0000.iu0099.pic.gz',
           refFile='data/files/data17_13TeV.AllPeriods.sgn.probes_EGAM2.bkg.VProbes_EGAM7.GRL_v97-eff.npz',
           )


end = timer()

print 'execution time is: ', (end - start)      

#/usr/bin/env python
from timeit import default_timer as timer
from RingerCore.Logger import Logger, LoggingLevel
from TuningTools.TuningJob import TuningJob
from TuningTools.PreProc import *
import logging

start = timer()
DatasetLocationInput = 'data_cern/files/new_mc/mc15_13TeV.361106.423300.sgn.probes_lhmedium.bkg.vetotruth.patterns.npz'

ppCol = PreProcChain( Norm1() ) 


from TuningTools.TuningJob import fixPPCol
ppCol = fixPPCol(ppCol)
from TuningTools.coreDef      import coreConf, TuningToolCores
coreConf.conf = TuningToolCores.FastNet
from TuningTools.TuningJob    import ReferenceBenchmark,   ReferenceBenchmarkCollection, BatchSizeMethod

from RingerCore.Configure import Development
Development.set( True )


tuningJob = TuningJob()
tuningJob( DatasetLocationInput, 
           neuronBoundsCol = [5,5], 
           sortBoundsCol = 10,
           initBoundsCol =2, 
           epochs = 1000,
           showEvo = 1,
           doMultiStop = False,
           #ppCol = ppCol,
           level = 10,
           etBins = 0,
           etaBins = 0,
           crossValidFile= 'data_cern/files/crossValid.v6.pic.gz',
           #ppFile='data/files/preproc_norm1.pic.gz',
           #confFileList='config.n5to20.jackKnife.inits_100by100/job.hn0009.s0000.il0000.iu0099.pic.gz',
           refFile='data_cern/files/mc15_13TeV.361106.423300.sgn.probes.bkg.vetotruth.trig.l2calo.vloose-eff.npz',
           )


end = timer()

print 'execution time is: ', (end - start)      

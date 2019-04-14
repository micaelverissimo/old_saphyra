#/usr/bin/env python
from timeit import default_timer as timer
from RingerCore.Logger import Logger, LoggingLevel
from TuningTools.TuningJob import TuningJob
from TuningTools.PreProc import *
import logging

start = timer()
DatasetLocationInput = '/home/jodafons/Public/ringer/root/TuningTools/scripts/analysis_scripts/Offline_mc16_201802XX_v6/data/files/mc16calostd_lhgrid_v3/mc16a.zee.20M.jf17.20M.offline.binned.calostd.wdatadrivenlh_et2_eta0.npz'

from TuningTools.TuningJob import fixPPCol
from TuningTools.coreDef      import coreConf, TuningToolCores
coreConf.conf = TuningToolCores.FastNet
from TuningTools.TuningJob    import ReferenceBenchmark,   ReferenceBenchmarkCollection, BatchSizeMethod
from RingerCore.Configure import Development
Development.set( True )


tuningJob = TuningJob()
tuningJob( DatasetLocationInput, 
           neuronBoundsCol = [5, 5], 
           sortBoundsCol = [0, 10],
           initBoundsCol =2, 
           epochs = 200,
           showEvo = 1,
           doMultiStop = False,
           level=9,
           maxFail = 100,
           etBins = 2,
           etaBins = 0,
           ppFile = '../data/files/user.jodafons.ppFile.ShowerShapesSimpleNorm.pic.gz/ppFile.ShowerShapesSimpleNorm.pic.gz',
           refFile = '../data/files/mc16calostd_lhgrid_v3/mc16a.zee.20M.jf17.20M.offline.binned.calostd.wdatadrivenlh_eff.2.npz',
           crossValidFile= '../data/files/user.jodafons.crossValid.10sorts.pic.gz/crossValid.10sorts.pic.gz',
           )


end = timer()

print 'execution time is: ', (end - start)      

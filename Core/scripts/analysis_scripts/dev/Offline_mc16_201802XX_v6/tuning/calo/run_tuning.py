#/usr/bin/env python
from timeit import default_timer as timer
from RingerCore.Logger import Logger, LoggingLevel
from TuningTools.TuningJob import TuningJob
from TuningTools.PreProc import *
import logging

start = timer()
#DatasetLocationInput = '/home/jodafons/Public/ringer/root/TuningTools/scripts/analysis_scripts/Offline_mc16_201802XX_v6/data/files/mc16calo_lhgrid_v3/mc16a.zee.20M.jf17.20M.offline.binned.calo.wdatadrivenlh_et2_eta0.npz'
DatasetLocationInput = '/home/jodafons/Public/ringer/root/TuningTools/scripts/analysis_scripts/Offline_mc16_201802XX_v6/data/files/mc16caloseg_lhgrid_v3/mc16a.zee.20M.jf17.20M.offline.binned.caloPS.wdatadrivenlh_et3_eta8.npz'

from TuningTools.TuningJob import fixPPCol
from TuningTools.coreDef      import coreConf, TuningToolCores
coreConf.conf = TuningToolCores.FastNet
from TuningTools.TuningJob    import ReferenceBenchmark,   ReferenceBenchmarkCollection, BatchSizeMethod
from RingerCore.Configure import Development
Development.set( True )


tuningJob = TuningJob()
tuningJob( DatasetLocationInput, 
           neuronBoundsCol = [50, 50], 
           sortBoundsCol = [0, 1],
           initBoundsCol = 1, 
           epochs = 5000,
           showEvo = 100,
           doMultiStop = True,
           level=9,
           maxFail = 100,
           etBins = 3,
           etaBins = 8,
           operationPoint = 'Offline_LH_DataDriven2016_Rel21_Medium',
           #ppFile = '../data/files/user.jodafons.ppFile_TrackSimpleNorm.pic.gz/ppFile.Norm1.pic.gz',
           #ppFile = '../../data/files/ppFile.SegHAD1_Norm1.pic.gz',
           #ppFile = '../../data/files/ppFile.Norm1_SegEM1.pic.gz',
           refFile = '../../data/files/mc16calo_lhgrid_v3/mc16a.zee.20M.jf17.20M.offline.binned.calo.wdatadrivenlh_eff.npz',
           crossValidFile= '../../data/files/user.jodafons.crossValid.10sorts.pic.gz/crossValid.10sorts.pic.gz',
           )


end = timer()

print 'execution time is: ', (end - start)      

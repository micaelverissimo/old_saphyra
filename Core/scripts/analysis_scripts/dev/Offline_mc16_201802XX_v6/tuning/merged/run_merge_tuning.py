#/usr/bin/env python
from timeit import default_timer as timer
from RingerCore.Logger import Logger, LoggingLevel
from TuningTools.TuningJob import TuningJob
from TuningTools.PreProc import *
import logging

basepath = '/home/jodafons/Public/ringer/root/TuningTools/scripts/analysis_scripts/Offline_mc16_201802XX_v6/data'

start = timer()
DatasetLocationInput = [
                  'mc16a.zee.20M.jf17.20M.offline.binned.caloPS.wdatadrivenlh_et2_eta0.npz',
                  'mc16a.zee.20M.jf17.20M.offline.binned.caloEM1.wdatadrivenlh_et2_eta0.npz',
                  'mc16a.zee.20M.jf17.20M.offline.binned.caloEM2.wdatadrivenlh_et2_eta0.npz',
                  'mc16a.zee.20M.jf17.20M.offline.binned.caloEM3.wdatadrivenlh_et2_eta0.npz',
                  'mc16a.zee.20M.jf17.20M.offline.binned.caloHAD1.wdatadrivenlh_et2_eta0.npz',
                  'mc16a.zee.20M.jf17.20M.offline.binned.caloHAD2.wdatadrivenlh_et2_eta0.npz',
                  'mc16a.zee.20M.jf17.20M.offline.binned.caloHAD3.wdatadrivenlh_et2_eta0.npz',
                  ]

expertPaths = [
                'mc16a.zee.20M.jf17.20M.offline.binned.caloPS.wdatadrivenlh.v6.crossValStat/mc16a.zee.20M.jf17.20M.offline.binned.caloPS.wdatadrivenlh.v6.crossValStat_et2_eta0.pic.gz',
                'mc16a.zee.20M.jf17.20M.offline.binned.caloEM1.wdatadrivenlh.v6.crossValStat/mc16a.zee.20M.jf17.20M.offline.binned.caloEM1.wdatadrivenlh.v6.crossValStat_et2_eta0.pic.gz',
                'mc16a.zee.20M.jf17.20M.offline.binned.caloEM2.wdatadrivenlh.v6.crossValStat/mc16a.zee.20M.jf17.20M.offline.binned.caloEM2.wdatadrivenlh.v6.crossValStat_et2_eta0.pic.gz',
                'mc16a.zee.20M.jf17.20M.offline.binned.caloEM3.wdatadrivenlh.v6.crossValStat/mc16a.zee.20M.jf17.20M.offline.binned.caloEM3.wdatadrivenlh.v6.crossValStat_et2_eta0.pic.gz',
                'mc16a.zee.20M.jf17.20M.offline.binned.caloHAD1.wdatadrivenlh.v6.crossValStat/mc16a.zee.20M.jf17.20M.offline.binned.caloHAD1.wdatadrivenlh.v6.crossValStat_et2_eta0.pic.gz',
                'mc16a.zee.20M.jf17.20M.offline.binned.caloHAD2.wdatadrivenlh.v6.crossValStat/mc16a.zee.20M.jf17.20M.offline.binned.caloHAD2.wdatadrivenlh.v6.crossValStat_et2_eta0.pic.gz',
                'mc16a.zee.20M.jf17.20M.offline.binned.caloHAD3.wdatadrivenlh.v6.crossValStat/mc16a.zee.20M.jf17.20M.offline.binned.caloHAD3.wdatadrivenlh.v6.crossValStat_et2_eta0.pic.gz',
                ]

from TuningTools.TuningJob import fixPPCol
from TuningTools.coreDef      import coreConf, TuningToolCores
coreConf.conf = TuningToolCores.FastNet
from TuningTools.TuningJob    import ReferenceBenchmark,   ReferenceBenchmarkCollection, BatchSizeMethod
from RingerCore.Configure import Development
Development.set( True )

from TuningTools.TuningJob import fixPPCol

ppCol = PreProcChain([Norm1()])
ppCol = fixPPCol(ppCol)
place = PreProcArchieve( 'ppFile', ppCol = ppCol ).save()


for i in range(len(DatasetLocationInput)):
  DatasetLocationInput[i] =basepath+'/files/mc16caloseg_lhgrid_v3/'+DatasetLocationInput[i]

for i in range(len(expertPaths)):
  expertPaths[i] = basepath+'/precrossval/'+expertPaths[i]

from pprint import pprint
pprint(expertPaths)
pprint(DatasetLocationInput)

tuningJob = TuningJob()
tuningJob( DatasetLocationInput, 
           expertPaths = expertPaths,
           neuronBoundsCol = [5, 5], 
           sortBoundsCol = [0, 1],
           initBoundsCol =1, 
           level=9,
           epochs = 5000,
           showEvo = 100,
           doMultiStop = False,
           maxFail = 100,
           etBins = 2,
           etaBins = 0,
           ppFile = [place]*7,
           operationPoint = 'Offline_LH_DataDriven2016_Rel21_Medium',
           crossValidFile= '../../data/files/user.jodafons.crossValid.10sorts.pic.gz/crossValid.10sorts.pic.gz',
           #refFile = 'data/files/mc16calo_lhgrid_v3/mc16a.zee.20M.jf17.20M.offline.binned.calo.wdatadrivenlh_eff.npz',
           refFile = '../../data/files/mc16calo_lhgrid_v3/mc16a.zee.20M.jf17.20M.offline.binned.calo.wdatadrivenlh_eff.npz',
           #ppFile= '/home/jodafons/Public/ringer/root/TuningTools/scripts/analysis_scripts/Offline_mc16_201802XX_v6/data/files/user.jodafons.ppFile.ExpertNetworksSimpleNorm.pic.gz/ppFile.ExpertNetworksSimpleNorm.pic.gz',
           #ppFile= '/home/jodafons/Public/ringer/root/TuningTools/scripts/analysis_scripts/Offline_mc16_201802XX_v6/data/files/user.jodafons.ppFile.ExpertNetworksShowerShapeSimpleNorm.pic.gz/ppFile.ExpertNetworksShowerShapeSimpleNorm.pic.gz',
           #ppFile= 'data/files/user.jodafons.ppFile.ExpertNetworksShowerShapeAndTrackSimpleNorm.pic.gz/ppFile.ExpertNetworksShowerShapeAndTrackSimpleNorm.pic.gz',
           )


end = timer()

print 'execution time is: ', (end - start)      

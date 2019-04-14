#!/usr/bin/env python

from RingerCore import LoggingLevel, expandFolders, Logger, mkdir_p
from TuningTools import CrossValidStatAnalysis, RingerOperation
from pprint import pprint
import os
mainLogger = Logger.getModuleLogger( __name__ )


basepath = 'data/crossval'
crossval = [
            # track only 
            [
              'mc16a.zee.20M.jf17.20M.offline.binned.track.wdatadrivenlh.v6.crossValStat_Offline_LH_DataDriven2016_Rel21_Medium_PileupCorrection/',
              'mc16a.zee.20M.jf17.20M.offline.binned.track.wdatadrivenlh.v6.crossValStat_Offline_LH_DataDriven2016_Rel21_VeryLoose_PileupCorrection',
            ],
            # Cutbased
            [ 
              'mc16a.zee.20M.jf17.20M.offline.binned.calo.wdatadrivenlh.v6.crossValStat_Offline_CutBasedMedium_PileupCorrection',
            ],
            # ringer only
            [ 
              'mc16a.zee.20M.jf17.20M.offline.binned.calo.wdatadrivenlh.v6.crossValStat_Offline_LH_DataDriven2016_Rel21_Medium_PileupCorrection/',
              'mc16a.zee.20M.jf17.20M.offline.binned.calo.wdatadrivenlh.v6.crossValStat_Offline_LH_DataDriven2016_Rel21_VeryLoose_PileupCorrection/',
            ],
            # ringer + track
            [
             'mc16a.zee.20M.jf17.20M.offline.binned.caloAndTrack.wdatadrivenlh.v6.crossValStat_Offline_LH_DataDriven2016_Rel21_Tight_PileupCorrection/',
             'mc16a.zee.20M.jf17.20M.offline.binned.caloAndTrack.wdatadrivenlh.v6.crossValStat_Offline_LH_DataDriven2016_Rel21_Medium_PileupCorrection/',
             'mc16a.zee.20M.jf17.20M.offline.binned.caloAndTrack.wdatadrivenlh.v6.crossValStat_Offline_LH_DataDriven2016_Rel21_Loose_PileupCorrection/',
             'mc16a.zee.20M.jf17.20M.offline.binned.caloAndTrack.wdatadrivenlh.v6.crossValStat_Offline_LH_DataDriven2016_Rel21_VeryLoose_PileupCorrection/',
             ],
            # ringer + shower shape + track
            [
              'mc16a.zee.20M.jf17.20M.offline.binned.caloAndShowerAndTrack.wdatadrivenlh.v6.crossValStat_Offline_LH_DataDriven2016_Rel21_Medium_PileupCorrection/',
              'mc16a.zee.20M.jf17.20M.offline.binned.caloAndShowerAndTrack.wdatadrivenlh.v6.crossValStat_Offline_LH_DataDriven2016_Rel21_VeryLoose_PileupCorrection/',
            ],
          ]

ref = 'Pd'

tuningdirs = [
              'mc16a_20180308_tlh_v6',
              'mc16a_20180308_ccutbased_v6',
              'mc16a_20180308_clh_v6',
              'mc16a_20180308_ectlh_v6',
              'mc16a_20180308_ecstlh_v6',
             ]

pidnames   = [
              ['Medium',
                'VeryLoose'
                ],
              ['Medium'],
              ['Medium','VeryLoose'],
              [
                'Tight',
                'Medium',
                'Loose',
                'VeryLoose'
                ],
              ['Medium', 'VeryLoose'],
             ]


####################### Extract Ringer Configuration #########################

for idx, cv in enumerate(crossval):

  tpath = os.getcwd()+'/'+tuningdirs[idx]
  mkdir_p(tpath)

  for jdx, pid in enumerate(pidnames[idx]):

    files = expandFolders(basepath+'/'+cv[jdx])
    crossValGrid=[]
    for path in files:
      if path.endswith('.pic.gz'):
        crossValGrid.append(path)
 
    d = CrossValidStatAnalysis.exportDiscrFilesToOnlineFormat(crossValGrid, refBenchCol=ref,
                                                        discrFilename = '%s/ElectronRinger%sConstants'%(tpath,pid),
                                                        thresFilename = '%s/ElectronRinger%sThresholds'%(tpath,pid),
                                                        version = 4,
                                                        )













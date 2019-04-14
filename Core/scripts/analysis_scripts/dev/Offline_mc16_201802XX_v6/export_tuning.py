#!/usr/bin/env python

from RingerCore import LoggingLevel, expandFolders, Logger, mkdir_p
from TuningTools import CrossValidStatAnalysis, RingerOperation
from pprint import pprint
import os
mainLogger = Logger.getModuleLogger( __name__ )


basepath = 'data/crossval/'
crossval =    [
      [basepath+'mc16a.zee.20M.jf17.20M.offline.binned.caloAndTrack.wdatadrivenlh.v6.crossValStat_Offline_LH_DataDriven2016_Rel21_Tight_PileupCorrection/',     ],
      #[basepath+'mc16a.zee.20M.jf17.20M.offline.binned.caloAndTrack.wdatadrivenlh.v6.crossValStat_Offline_LH_DataDriven2016_Rel21_Medium_PileupCorrection/',    ],
      #[basepath+'mc16a.zee.20M.jf17.20M.offline.binned.caloAndTrack.wdatadrivenlh.v6.crossValStat_Offline_LH_DataDriven2016_Rel21_Loose_PileupCorrection/',     ],
      #[basepath+'mc16a.zee.20M.jf17.20M.offline.binned.caloAndTrack.wdatadrivenlh.v6.crossValStat_Offline_LH_DataDriven2016_Rel21_VeryLoose_PileupCorrection/', ],
             ]

filenameWeights = [
                    'ElectronRingerTightConstants',
                    #'ElectronRingerMediumConstants',
                    #'ElectronRingerLooseConstants',
                    #'ElectronRingerVeryloooseConstants',
                  ]

filenameThres = [
                    'ElectronRingerTightThresholds',
                    #'ElectronRingerMediumThresholds',
                    #'ElectronRingerLooseThresholds',
                    #'ElectronRingerVeryLooseThresholds',
                  ]


ref = 'Pd'



####################### Extract Ringer Configuration #########################

from TuningTools import CreateSelectorFiles

export = CreateSelectorFiles()
export( crossval, filenameWeights, filenameThres, ref )


















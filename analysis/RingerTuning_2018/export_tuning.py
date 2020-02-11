#!/usr/bin/env python

from RingerCore import LoggingLevel, expandFolders, Logger, mkdir_p
from TuningTools import CrossValidStatAnalysis, RingerOperation
from pprint import pprint
import os
mainLogger = Logger.getModuleLogger( __name__ )


basepath = 'data/crossval/'
crossval =    [
      [basepath],
      [basepath],
      [basepath],
      [basepath],
             ]


####################### Data 2017 #########################
# 25 bins

config = 5
ref    = 'SP'



filenameWeights = [
                    'TrigL2CaloRingerElectronTightConstants',
                    'TrigL2CaloRingerElectronMediumConstants',
                    'TrigL2CaloRingerElectronLooseConstants',
                    'TrigL2CaloRingerElectronVeryLooseConstants',
                  ]

filenameThres = [
                    'TrigL2CaloRingerElectronTightThresholds',
                    'TrigL2CaloRingerElectronMediumThresholds',
                    'TrigL2CaloRingerElectronLooseThresholds',
                    'TrigL2CaloRingerElectronVeryLooseThresholds',
                  ]



####################### Extract Ringer Configuration #########################

from TuningTools import CreateSelectorFiles, TrigMultiVarHypo_v2

export = CreateSelectorFiles(  model = TrigMultiVarHypo_v2(toPickle=True) )
export( crossval, filenameWeights, filenameThres, ref, config )


















#!/usr/bin/env python

from RingerCore import LoggingLevel, expandFolders, Logger
from TuningTools import CrossValidStatAnalysis, RingerOperation
from pprint import pprint
mainLogger = Logger.getModuleLogger( __name__ )

basepath = 'data/crossval/'

SP = 'SP'


####################### Data 2017 #########################
# 15 bins

TightConfigList = [[5 for _ in range(5)] for __ in range(3)]
TightRefBenchmarkList     =  [[SP] * 5]*3

MediumConfigList = TightConfigList
LooseConfigList = TightConfigList
VeryLooseConfigList = TightConfigList

MediumRefBenchmarkList = TightRefBenchmarkList
LooseRefBenchmarkList = TightRefBenchmarkList
VeryLooseRefBenchmarkList = TightRefBenchmarkList


####################### Global Configuration #########################
configList =  [
                TightConfigList,
                MediumConfigList,
                LooseConfigList,
                VeryLooseConfigList,
              ]

refBenchmarkList = [
                    TightRefBenchmarkList,
                    MediumRefBenchmarkList,
                    LooseRefBenchmarkList,
                    VeryLooseRefBenchmarkList,
                    ]

tuningNameList = [
                    'ElectronHighEnergyTightConf',
                    'ElectronHighEnergyMediumConf',
                    'ElectronHighEnergyLooseConf',
                    'ElectronHighEnergyVeryLooseConf',
                 ]

# Et Bins
etBins       = [ 3,7,10,15 ]
# Eta bins
etaBins      = [0, 0.8 , 1.37, 1.54, 2.37, 2.5]

####################### Extract Ringer Configuration #########################
import numpy as np
outputDict=dict()

files = expandFolders(basepath)
crossValGrid=[]
for path in files:
  if path.endswith('.pic.gz'):
    crossValGrid.append(path)

pprint(crossValGrid)
pprint(configList[0])
pprint(refBenchmarkList[0])
d = CrossValidStatAnalysis.exportDiscrFiles(crossValGrid,
                                            RingerOperation.L2,
                                            triggerChains=tuningNameList[0],
                                            refBenchCol=refBenchmarkList[0],
                                            nEtBins = len(etBins),
                                            nEtaBins = len(etaBins),
                                            configCol=configList[0])

print d.keys()

from copy import copy
for tuningName in tuningNameList:
  c = { tuningName : copy(d[tuningNameList[0]]) }
  mainLogger.info('%d bins found in this tuning: %s',len(c[tuningName].keys()),tuningName)
  outputDict.update(c)

####################### Write Ringer Configuration #########################



nDict   = {'version':1, 'type': ['Fex' ]  , 'date':0, 'metadata':dict(), 'tuning':dict(), 'name':['v7']}
thrDict = {'version':1, 'type': ['Hypo']  , 'date':0, 'metadata':dict(), 'tuning':dict(), 'name':['v7']}


metadata = {'UseLumiTool': True,
            'UseLumiVar' : False,
            'UseEtaVar'  : False,
            'LumiCut'    : 100,
            'DoPileupCorrection':False,
            'UseNoActivationFunctionInTheLastLayer': False,
            }

# Hold the metadata default configuration
nDict['metadata'] = metadata
thrDict['metadata'] = metadata


from copy import copy
for tkey in outputDict.keys():
 
  discrs = dict()
  thresholds = dict()
  print outputDict[tkey].keys()

  for bkey in sorted(outputDict[tkey].keys()):

    discr = {'discriminator':dict(),'configuration':dict()}
    cut   = {'configuration':dict()}
    discr['discriminator']['nodes']         = outputDict[tkey][bkey]['discriminator']['nodes']
    discr['discriminator']['weights']       = outputDict[tkey][bkey]['discriminator']['weights']
    discr['discriminator']['bias']          = outputDict[tkey][bkey]['discriminator']['bias']
    discr['configuration']['etBin']         = outputDict[tkey][bkey]['configuration']['etBinIdx']
    discr['configuration']['etaBin']        = outputDict[tkey][bkey]['configuration']['etaBinIdx']
    cut['configuration']['etBin']     = outputDict[tkey][bkey]['configuration']['etBinIdx']
    cut['configuration']['etaBin']    = outputDict[tkey][bkey]['configuration']['etaBinIdx']
    thr = outputDict[tkey][bkey]['discriminator']['threshold']
    cut['threshold'] = (0,0,thr)
    discrs[bkey] = discr
    thresholds[bkey] = cut

  nDict['tuning'][tkey]     = discrs
  thrDict['tuning'][tkey]  = thresholds



pyfile = open('TrigL2CaloRingerConstants.py','w')
pyfile.write('def SignaturesMap():\n')
pyfile.write('  s=dict()\n')
for key in nDict.keys():
  pyfile.write('  s["%s"]=%s\n' % (key, nDict[key]))
pyfile.write('  return s\n')

pyfile = open('TrigL2CaloRingerThresholds.py','w')
pyfile.write('def ThresholdsMap():\n')
pyfile.write('  s=dict()\n')
for key in thrDict.keys():
  pyfile.write('  s["%s"]=%s\n' % (key, thrDict[key]))
pyfile.write('  return s\n')










#!/usr/bin/env python

from RingerCore import LoggingLevel, expandFolders, Logger
from TuningTools import CrossValidStatAnalysis, RingerOperation
from pprint import pprint
mainLogger = Logger.getModuleLogger( __name__ )

basepath = '/home/wsfreund/CERN-DATA/Online/nn_stats'

veryLoosePath = 'user.jodafons.nnstat.mc15_13TeV.sgn.361106.probes.newLH.bkg.423300.vetotruth.strig.l2calo.VeryLoose.npz/'
loosePath = 'user.jodafons.nnstat.mc15_13TeV.sgn.361106.probes.newLH.bkg.423300.vetotruth.strig.l2calo.Loose.npz/'
mediumPath = 'user.jodafons.nnstat.mc15_13TeV.sgn.361106.probes.newLH.bkg.423300.vetotruth.strig.l2calo.medium.npz/'
tightPath = 'user.jodafons.nnstat.mc15_13TeV.sgn.361106.probes.newLH.bkg.423300.vetotruth.strig.l2calo.tight.npz/'

SP = 'SP'
Pd = 'Pd'
Pf = 'Pf'
pathList = [tightPath, mediumPath, loosePath, veryLoosePath]


####################### VeryLoose MC15 #########################
# 20 bins
VeryLooseConfigList = [
                # EFCalo, Et 0, Eta 0
                #  Pd, SP, Pf
              [[   5  ],
               [# Et 0, Eta 1
                   5 ],
               [# Et 0, Eta 2
                   12  ],
               [# Et 0, Eta 3
                   6  ]],
                # EFCalo, Et 1, Eta 0
                #  Pd, SP, Pf
              [[   6  ],
               [# Et 1, Eta 1
                   16  ],
               [# Et 1, Eta 2
                   7 ],
               [# Et 1, Eta 3
                   7  ]],
                # EFCalo, Et 2, Eta 0
                #  Pd, SP, Pf
              [[   5  ],
               [# Et 2, Eta 1
                   8 ],
               [# Et 2, Eta 2
                   5  ],
               [# Et 2, Eta 3
                   10 ]],
                # EFCalo, Et 3, Eta 0
                #  Pd, SP, Pf
              [[   5 ],
               [# Et 3, Eta 1
                   7 ],
               [# Et 3, Eta 2
                   5  ],
               [# Et 3, Eta 3
                   7 ]],

                # EFCalo, Et 4, Eta 0
                #  Pd, SP, Pf
              [[   12 ],
               [# Et 4, Eta 1
                   5 ],
               [# Et 4, Eta 2
                   5  ],
               [# Et 4, Eta 3
                   12 ]]

            ]

VeryLooseRefBenchmarkList = [
                # EFCalo, Et 0, Eta 0
                #  Pd, SP, Pf
              [[   Pd  ],
               [# Et 0, Eta 1
                   Pd ],
               [# Et 0, Eta 2
                   SP  ],
               [# Et 0, Eta 3
                   Pd  ]],
                # EFCalo, Et 1, Eta 0
                #  Pd, SP, Pf
              [[   Pd  ],
               [# Et 1, Eta 1
                   Pd  ],
               [# Et 1, Eta 2
                   SP ],
               [# Et 1, Eta 3
                   Pd  ]],
                # EFCalo, Et 2, Eta 0
                #  Pd, SP, Pf
              [[   Pd  ],
               [# Et 2, Eta 1
                   Pd ],
               [# Et 2, Eta 2
                   SP  ],
               [# Et 2, Eta 3
                   Pd ]],
                # EFCalo, Et 3, Eta 0
                #  Pd, SP, Pf
              [[   Pd ],
               [# Et 3, Eta 1
                   Pd ],
               [# Et 3, Eta 2
                   SP  ],
               [# Et 3, Eta 3
                   Pd ]],

                # EFCalo, Et 4, Eta 0
                #  Pd, SP, Pf
              [[   Pd ],
               [# Et 4, Eta 1
                   Pd ],
               [# Et 4, Eta 2
                   SP  ],
               [# Et 4, Eta 3
                   SP ]]

            ]

####################### Loose MC15 #########################
LooseConfigList = [
                # EFCalo, Et 0, Eta 0
                #  Pd, SP, Pf
              [[   5  ],
               [# Et 0, Eta 1
                   5 ],
               [# Et 0, Eta 2
                   7  ],
               [# Et 0, Eta 3
                   6  ]],
                # EFCalo, Et 1, Eta 0
                #  Pd, SP, Pf
              [[   5  ],
               [# Et 1, Eta 1
                   6  ],
               [# Et 1, Eta 2
                   5 ],
               [# Et 1, Eta 3
                   13  ]],
                # EFCalo, Et 2, Eta 0
                #  Pd, SP, Pf
              [[   5  ],
               [# Et 2, Eta 1
                   9 ],
               [# Et 2, Eta 2
                   5  ],
               [# Et 2, Eta 3
                   13 ]],
                # EFCalo, Et 3, Eta 0
                #  Pd, SP, Pf
              [[   5 ],
               [# Et 3, Eta 1
                   5 ],
               [# Et 3, Eta 2
                   5  ],
               [# Et 3, Eta 3
                   10 ]],

                # EFCalo, Et 4, Eta 0
                #  Pd, SP, Pf
              [[   5 ],
               [# Et 4, Eta 1
                   5 ],
               [# Et 4, Eta 2
                   5  ],
               [# Et 4, Eta 3
                   5 ]]

            ]

LooseRefBenchmarkList = [
                # EFCalo, Et 0, Eta 0
                #  Pd, SP, Pf
              [[   Pd  ],
               [# Et 0, Eta 1
                   Pd ],
               [# Et 0, Eta 2
                   SP  ],
               [# Et 0, Eta 3
                   Pd  ]],
                # EFCalo, Et 1, Eta 0
                #  Pd, SP, Pf
              [[   Pd  ],
               [# Et 1, Eta 1
                   Pd  ],
               [# Et 1, Eta 2
                   SP ],
               [# Et 1, Eta 3
                   SP  ]],
                # EFCalo, Et 2, Eta 0
                #  Pd, SP, Pf
              [[   SP  ],
               [# Et 2, Eta 1
                   SP ],
               [# Et 2, Eta 2
                   SP  ],
               [# Et 2, Eta 3
                   SP ]],
                # EFCalo, Et 3, Eta 0
                #  Pd, SP, Pf
              [[   SP ],
               [# Et 3, Eta 1
                   SP ],
               [# Et 3, Eta 2
                   SP  ],
               [# Et 3, Eta 3
                   SP ]],

                # EFCalo, Et 4, Eta 0
                #  Pd, SP, Pf
              [[   SP ],
               [# Et 4, Eta 1
                   SP ],
               [# Et 4, Eta 2
                   SP  ],
               [# Et 4, Eta 3
                   SP ]]

            ]


####################### Medium MC15 #########################
# 20 bins
MediumConfigList = [
                # EFCalo, Et 0, Eta 0
                #  Pd, SP, Pf
              [[   6  ],
               [# Et 0, Eta 1
                   5 ],
               [# Et 0, Eta 2
                   7  ],
               [# Et 0, Eta 3
                   7  ]],
                # EFCalo, Et 1, Eta 0
                #  Pd, SP, Pf
              [[   5  ],
               [# Et 1, Eta 1
                   6  ],
               [# Et 1, Eta 2
                   5 ],
               [# Et 1, Eta 3
                   18  ]],
                # EFCalo, Et 2, Eta 0
                #  Pd, SP, Pf
              [[   5  ],
               [# Et 2, Eta 1
                   5 ],
               [# Et 2, Eta 2
                   5  ],
               [# Et 2, Eta 3
                   5 ]],
                # EFCalo, Et 3, Eta 0
                #  Pd, SP, Pf
              [[   5 ],
               [# Et 3, Eta 1
                   5 ],
               [# Et 3, Eta 2
                   5  ],
               [# Et 3, Eta 3
                   5 ]],

                # EFCalo, Et 4, Eta 0
                #  Pd, SP, Pf
              [[   5 ],
               [# Et 4, Eta 1
                   5 ],
               [# Et 4, Eta 2
                   7  ],
               [# Et 4, Eta 3
                   5 ]]

            ]


MediumRefBenchmarkList    =  [[Pd] * 4]*5


####################### Tight MC15 #########################
# 20 bins
TightConfigList = [
                # EFCalo, Et 0, Eta 0
                #  Pd, SP, Pf
              [[   5  ],
               [# Et 0, Eta 1
                   5 ],
               [# Et 0, Eta 2
                   5  ],
               [# Et 0, Eta 3
                   5  ]],
                # EFCalo, Et 1, Eta 0
                #  Pd, SP, Pf
              [[   5  ],
               [# Et 1, Eta 1
                   5  ],
               [# Et 1, Eta 2
                   5 ],
               [# Et 1, Eta 3
                   15  ]],
                # EFCalo, Et 2, Eta 0
                #  Pd, SP, Pf
              [[   5  ],
               [# Et 2, Eta 1
                   5 ],
               [# Et 2, Eta 2
                   14  ],
               [# Et 2, Eta 3
                   5 ]],
                # EFCalo, Et 3, Eta 0
                #  Pd, SP, Pf
              [[   5 ],
               [# Et 3, Eta 1
                   5 ],
               [# Et 3, Eta 2
                   5  ],
               [# Et 3, Eta 3
                   5 ]],
                # EFCalo, Et 4, Eta 0
                #  Pd, SP, Pf
              [[   5 ],
               [# Et 4, Eta 1
                   5 ],
               [# Et 4, Eta 2
                   5  ],
               [# Et 4, Eta 3
                   5 ]]

            ]


TightRefBenchmarkList     =  [[Pd] * 4]*5





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
etBins       = [15, 20, 30, 40, 50, 500000 ]
# Eta bins
etaBins      = [0, 0.8 , 1.37, 1.54, 2.5]

# [Tight, Medium, Loose and VeryLoose]
thrRelax     = [-0.1,-0.1,0,0]

####################### Extract Ringer Configuration #########################
import numpy as np
outputDict=dict()
for idx, tuningName in enumerate(tuningNameList):
  files = expandFolders(basepath+'/'+pathList[idx])
  crossValGrid=[]
  for path in files:
    if path.endswith('.pic'):
      crossValGrid.append(path)
  
  pprint(crossValGrid)
  pprint(configList[idx])
  pprint(refBenchmarkList[idx])
  c = CrossValidStatAnalysis.exportDiscrFiles(crossValGrid,
                                              RingerOperation.L2,
                                              triggerChains=tuningName,
                                              refBenchCol=refBenchmarkList[idx],
                                              EtBins = etBins,
                                              EtaBins = etaBins,
                                              configCol=configList[idx])

  mainLogger.info('%d bins found in this tuning: %s',len(c[tuningName].keys()),tuningName)
  
  for etIdx in range(len(etBins)-1):
    for etaIdx in range(len(etaBins)-1):
      thr = c[tuningName][('et%d_eta%d')%(etIdx,etaIdx)]['discriminator']['threshold']
      if np.abs(thrRelax[idx])>0:
        if (np.abs(thr+thrRelax[idx])<0.95):
          c[tuningName][('et%d_eta%d')%(etIdx,etaIdx)]['discriminator']['threshold'] += thrRelax[idx]
          mainLogger.warning('Relax threshold %f of (etBin = %d, etaBin = %d) to %f', thr, etIdx, etaIdx, thr+thrRelax[idx])


  outputDict.update(c)

####################### Write Ringer Configuration #########################
output = open('TrigL2CaloRingerConstants.py','w')
output.write('def SignaturesMap():\n')
output.write('  signatures=dict()\n')
for key in tuningNameList:
  output.write('  signatures["%s"]=%s\n' % (key, outputDict[key]))
output.write('  return signatures\n')
###########################################################################

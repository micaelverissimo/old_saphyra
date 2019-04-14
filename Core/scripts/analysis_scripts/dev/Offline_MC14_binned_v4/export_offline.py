#!/usr/bin/env python

from RingerCore import LoggingLevel, expandFolders, Logger
from TuningTools import CrossValidStatAnalysis, RingerOperation
from pprint import pprint
import os.path
mainLogger = Logger.getModuleLogger( __name__ )

basepath = '/home/wsfreund/CERN-DATA/Offline/nn_stats/v4'

#veryLoosePath = 'user.jodafons.nnstat.mc15_13TeV.sgn.361106.probes.newLH.bkg.423300.vetotruth.strig.l2calo.VeryLoose.npz/'
loosePath = 'loose_orig'
mediumPath = 'medium_orig'
tightPath = 'tight_orig'

pathList = [tightPath, mediumPath, loosePath, ]

####################### Loose MC15 #########################
# NOTE: Et 0, eta 3: performance increases up to 20
LooseConfigList = [
                # EFCalo, Et 0, Eta 0
                #  Pd, SP, Pf
              [[  9, 15 , 6  ],
               [# Et 0, Eta 1
                  20, 8, 7 ],
               [# Et 0, Eta 2
                  15, 5 , 11 ],
               [# Et 0, Eta 3
                   20, 20, 20  ]],
                # EFCalo, Et 1, Eta 0
                #  Pd, SP, Pf
              [[   8, 12 , 17 ],
               [# Et 1, Eta 1
                   20, 15, 16  ],
               [# Et 1, Eta 2
                   17, 17, 15 ],
               [# Et 1, Eta 3
                   7, 6, 10  ]],
                # EFCalo, Et 2, Eta 0
                #  Pd, SP, Pf
              [[   11, 9 , 15  ],
               [# Et 2, Eta 1
                   13, 12, 5  ],
               [# Et 2, Eta 2
                   10, 6, 17  ],
               [# Et 2, Eta 3
                   7, 20, 8 ]],
                # EFCalo, Et 3, Eta 0
                #  Pd, SP, Pf
              [[   10, 9, 11],
               [# Et 3, Eta 1
                   14, 9, 13 ],
               [# Et 3, Eta 2
                   7 , 17, 10  ],
               [# Et 3, Eta 3
                   6, 17, 18 ]],
                ]
LooseConfigList = [[[5,5,5]*4]*5]
LooseConfigPd = [[ configEta[0] for configEta in configEt] for configEt in LooseConfigList]
LooseConfigSP = [[ configEta[1] for configEta in configEt] for configEt in LooseConfigList]
LooseConfigPf = [[ configEta[2] for configEta in configEt] for configEt in LooseConfigList]

####################### Medium MC15 #########################
# NOTE: Cannot operate at same pf (et bin 0,)
MediumConfigList = [
                # EFCalo, Et 0, Eta 0
                #  Pd, SP, Pf
              [[   9, 15, 19  ],
               [# Et 0, Eta 1
                   5, 8, 20],
               [# Et 0, Eta 2
                   9, 8, 12  ],
               [# Et 0, Eta 3
                   15, 17, 13  ]],
                # EFCalo, Et 1, Eta 0
                #  Pd, SP, Pf
              [[   10, 18, 15  ],
               [# Et 1, Eta 1
                   19, 20, 20  ],
               [# Et 1, Eta 2
                   14, 13, 13 ],
               [# Et 1, Eta 3
                   7, 9, 8  ]],
                # EFCalo, Et 2, Eta 0
                #  Pd, SP, Pf
              [[   20, 10, 15  ],
               [# Et 2, Eta 1
                   17, 20, 15 ],
               [# Et 2, Eta 2
                   6, 15, 16  ],
               [# Et 2, Eta 3
                   8, 13, 11 ]],
                # EFCalo, Et 3, Eta 0
                #  Pd, SP, Pf
              [[   13, 7, 20 ],
               [# Et 3, Eta 1
                   14, 17, 7 ],
               [# Et 3, Eta 2
                   15, 5, 5  ],
               [# Et 3, Eta 3
                   7, 11, 16 ]],

            ]

MediumConfigList = [[[5,5,5]*4]*5 ]
MediumConfigPd = [[ configEta[0] for configEta in configEt] for configEt in MediumConfigList]
MediumConfigSP = [[ configEta[1] for configEta in configEt] for configEt in MediumConfigList]
MediumConfigPf = [[ configEta[2] for configEta in configEt] for configEt in MediumConfigList]

####################### Tight MC15 #########################
# 20 bins
TightConfigList = [
                # EFCalo, Et 0, Eta 0
                #  Pd, SP, Pf
              [[   14, 6, 5 ],
               [# Et 0, Eta 1
                   18, 11, 5 ],
               [# Et 0, Eta 2
                   13, 9 , 5 ],
               [# Et 0, Eta 3
                   12, 12, 5 ]],
                # EFCalo, Et 1, Eta 0
                #  Pd, SP, Pf
              [[   13, 20, 20 ],
               [# Et 1, Eta 1
                   19, 8, 20  ],
               [# Et 1, Eta 2
                   14, 10, 13 ],
               [# Et 1, Eta 3
                   11, 9, 5  ]],
                # EFCalo, Et 2, Eta 0
                #  Pd, SP, Pf
              [[   10, 17, 15  ],
               [# Et 2, Eta 1
                   7, 8, 14 ],
               [# Et 2, Eta 2
                   5, 14, 14  ],
               [# Et 2, Eta 3
                   12, 10, 20 ]],
                # EFCalo, Et 3, Eta 0
                #  Pd, SP, Pf
              [[   19, 14, 10 ],
               [# Et 3, Eta 1
                   11, 5, 20 ],
               [# Et 3, Eta 2
                   18, 5, 16  ],
               [# Et 3, Eta 3
                   9, 13, 7 ]],
            ]

TightConfigList = [[[5,5,5]*4]*5 ]
TightConfigPd = [[ configEta[0] for configEta in configEt] for configEt in TightConfigList]
TightConfigSP = [[ configEta[1] for configEta in configEt] for configEt in TightConfigList]
TightConfigPf = [[ configEta[2] for configEta in configEt] for configEt in TightConfigList]

####################### Global Configuration #########################
configList =  [
                [TightConfigPd, TightConfigSP, TightConfigPf],
                [MediumConfigPd, MediumConfigSP, MediumConfigPf],
                [LooseConfigPd, LooseConfigSP, LooseConfigPf],
              ]

referenceBenchCol = [['Pd','SP','Pf'],
                     ['Pd','SP','Pf'],
                     ['Pd','SP','Pf']]

# Et Bins
etBins       = [ 20, 30, 40, 50, 500000 ]
# Eta bins
etaBins      = [ 0, 0.8 , 1.37, 1.54, 2.5 ]

# [Tight, Medium, Loose and VeryLoose]
thrRelax     = [0,0,0,0]

####################### Extract Ringer Configuration #########################
import numpy as np
for path, referenceBench, configCol in zip(pathList, referenceBenchCol, configList):
  files = expandFolders( os.path.join( basepath, path ), '*.pic.gz')
  for conf, ref in zip(configCol, referenceBench):
    refBenchmark =  [[ref] * len(conf)]*len(conf[0])
    c = CrossValidStatAnalysis.exportDiscrFiles( sorted(files)
                                               , RingerOperation.Offline
                                               , refBenchCol   = ref
                                               , EtBins        = etBins
                                               , EtaBins       = etaBins
                                               , configCol     = conf
                                               #, level         = LoggingLevel.VERBOSE
                                               )
###########################################################################




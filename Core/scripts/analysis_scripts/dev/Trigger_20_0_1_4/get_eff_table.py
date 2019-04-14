#!/usr/bin/env python


crossValGrid = \
    [['/afs/cern.ch/work/j/jodafons/public/CrossValStat/crossValStat_etaBin_0_etBin_0.pic'
     ,'/afs/cern.ch/work/j/jodafons/public/CrossValStat/crossValStat_etaBin_1_etBin_0.pic'
     ,'/afs/cern.ch/work/j/jodafons/public/CrossValStat/crossValStat_etaBin_2_etBin_0.pic'
     ,'/afs/cern.ch/work/j/jodafons/public/CrossValStat/crossValStat_etaBin_3_etBin_0.pic']
    ,['/afs/cern.ch/work/j/jodafons/public/CrossValStat/crossValStat_etaBin_0_etBin_1.pic'
     ,'/afs/cern.ch/work/j/jodafons/public/CrossValStat/crossValStat_etaBin_1_etBin_1.pic'
     ,'/afs/cern.ch/work/j/jodafons/public/CrossValStat/crossValStat_etaBin_2_etBin_1.pic'
     ,'/afs/cern.ch/work/j/jodafons/public/CrossValStat/crossValStat_etaBin_3_etBin_1.pic']
    ,['/afs/cern.ch/work/j/jodafons/public/CrossValStat/crossValStat_etaBin_0_etBin_2.pic'
     ,'/afs/cern.ch/work/j/jodafons/public/CrossValStat/crossValStat_etaBin_1_etBin_2.pic'
     ,'/afs/cern.ch/work/j/jodafons/public/CrossValStat/crossValStat_etaBin_2_etBin_2.pic'
     ,'/afs/cern.ch/work/j/jodafons/public/CrossValStat/crossValStat_etaBin_3_etBin_2.pic']]

configBaseList = ['L2Calo','EFCalo']

configMap = [[# L2Calo, Et 0, Eta 0
              #  Pd, SP, Pf
            [[   5,  9,  5   ],
             [# Et 0, Eta 1
                11, 11,  5   ],
             [# Et 0, Eta 2
                 9,  5,  5   ],
             [# Et 0, Eta 3
                 9, 12,  5   ]],
              # L2Calo, Et 1, Eta 0
              #  Pd, SP, Pf
            [[   5,  5,  5   ],
             [# Et 1, Eta 1
                 5, 11,  5   ],
             [# Et 1, Eta 2
                 5, 15,  5   ],
             [# Et 1, Eta 3
                 5,  5,  5   ]],
              # L2Calo, Et 2, Eta 0
              #  Pd, SP, Pf
            [[   5,  5,  5   ],
             [# Et 2, Eta 1
                 5,  5,  5   ],
             [# Et 2, Eta 2
                 5,  5,  5   ],
             [# Et 2, Eta 3
                 5,  5,  5   ]]],
              # EFCalo, Et 0, Eta 0
              #  Pd, SP, Pf
           [[[   5,  9, 14   ],
             [# Et 0, Eta 1
                 5, 11, 14   ],
             [# Et 0, Eta 2
                 5,  5,  5   ],
             [# Et 0, Eta 3
                14, 12,  5   ]],
              # EFCalo, Et 1, Eta 0
              #  Pd, SP, Pf
            [[   5,  5,  5   ],
             [# Et 1, Eta 1
                 5, 11,  5   ],
             [# Et 1, Eta 2
                 5, 15,  5   ],
             [# Et 1, Eta 3
                 5,  5,  5   ]],
              # EFCalo, Et 2, Eta 0
              #  Pd, SP, Pf
            [[   5,  5,  5   ],
             [# Et 2, Eta 1
                 5,  5,  5   ],
             [# Et 2, Eta 2
                 5,  5,  5   ],
             [# Et 2, Eta 3
                 5,  5,  5   ]]]]

from pprint import pprint
pprint(configMap)

from TuningTools.CrossValidStat import CrossValidStatAnalysis
CrossValidStatAnalysis.printTables(configBaseList, 
                                   crossValGrid,
                                   configMap)



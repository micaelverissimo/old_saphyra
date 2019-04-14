#!/usr/bin/env python

crossValGrid = \
            [['/afs/cern.ch/user/w/wsfreund/Ringer/xAODRingerOfflinePorting/RingerTPFrameWork/TuningTools/scripts/skeletons/FixET_Norm1_20.7.3.6_7916634.pic'  
            ,'/afs/cern.ch/user/w/wsfreund/Ringer/xAODRingerOfflinePorting/RingerTPFrameWork/TuningTools/scripts/skeletons/FixET_Norm1_20.7.3.6_7916635.pic'  
            ,'/afs/cern.ch/user/w/wsfreund/Ringer/xAODRingerOfflinePorting/RingerTPFrameWork/TuningTools/scripts/skeletons/FixET_Norm1_20.7.3.6_7916636.pic'  
            ,'/afs/cern.ch/user/w/wsfreund/Ringer/xAODRingerOfflinePorting/RingerTPFrameWork/TuningTools/scripts/skeletons/FixET_Norm1_20.7.3.6_7916637.pic']  
            ,['/afs/cern.ch/user/w/wsfreund/Ringer/xAODRingerOfflinePorting/RingerTPFrameWork/TuningTools/scripts/skeletons/FixET_Norm1_20.7.3.6_7916638.pic'  
            ,'/afs/cern.ch/user/w/wsfreund/Ringer/xAODRingerOfflinePorting/RingerTPFrameWork/TuningTools/scripts/skeletons/FixET_Norm1_20.7.3.6_7916639.pic'  
            ,'/afs/cern.ch/user/w/wsfreund/Ringer/xAODRingerOfflinePorting/RingerTPFrameWork/TuningTools/scripts/skeletons/FixET_Norm1_20.7.3.6_7916641.pic'  
            ,'/afs/cern.ch/user/w/wsfreund/Ringer/xAODRingerOfflinePorting/RingerTPFrameWork/TuningTools/scripts/skeletons/FixET_Norm1_20.7.3.6_7916642.pic']  
            ,['/afs/cern.ch/user/w/wsfreund/Ringer/xAODRingerOfflinePorting/RingerTPFrameWork/TuningTools/scripts/skeletons/FixET_Norm1_20.7.3.6_7916643.pic' 
            ,'/afs/cern.ch/user/w/wsfreund/Ringer/xAODRingerOfflinePorting/RingerTPFrameWork/TuningTools/scripts/skeletons/FixET_Norm1_20.7.3.6_7916644.pic' 
            ,'/afs/cern.ch/user/w/wsfreund/Ringer/xAODRingerOfflinePorting/RingerTPFrameWork/TuningTools/scripts/skeletons/FixET_Norm1_20.7.3.6_7916645.pic' 
            ,'/afs/cern.ch/user/w/wsfreund/Ringer/xAODRingerOfflinePorting/RingerTPFrameWork/TuningTools/scripts/skeletons/FixET_Norm1_20.7.3.6_7916647.pic']
            ,['/afs/cern.ch/user/w/wsfreund/Ringer/xAODRingerOfflinePorting/RingerTPFrameWork/TuningTools/scripts/skeletons/FixET_Norm1_20.7.3.6_7916648.pic'
            ,'/afs/cern.ch/user/w/wsfreund/Ringer/xAODRingerOfflinePorting/RingerTPFrameWork/TuningTools/scripts/skeletons/FixET_Norm1_20.7.3.6_7916649.pic'
            ,'/afs/cern.ch/user/w/wsfreund/Ringer/xAODRingerOfflinePorting/RingerTPFrameWork/TuningTools/scripts/skeletons/FixET_Norm1_20.7.3.6_7916650.pic'
            ,'/afs/cern.ch/user/w/wsfreund/Ringer/xAODRingerOfflinePorting/RingerTPFrameWork/TuningTools/scripts/skeletons/FixET_Norm1_20.7.3.6_7916651.pic']]


#crossValGrid = [['/Users/wsfreund/Documents/Doutorado/CERN/xAOD/RingerProject/root/TuningTools/scripts/skeletons/FixET_Norm1_20.7.3.6_7916634.pic.gz']]
#configBaseList = ['EFCalo']
configBaseList = ['Medium']

configMap = [[
              # EFCalo, Et 0, Eta 0
              #  Pd, SP, Pf
           [[   7, 7, 7   ],
             [# Et 0, Eta 1
                16,16,16  ],
             [# Et 0, Eta 2
                 19,07,19   ],
             [# Et 0, Eta 3
                14, 11,  11   ]],
              # EFCalo, Et 1, Eta 0
              #  Pd, SP, Pf
            [[   7,  10, 7   ],
             [# Et 1, Eta 1
                 8, 10, 20   ],
             [# Et 1, Eta 2
                 11, 11, 8   ],
             [# Et 1, Eta 3
                 11,  7, 17   ]],
              # EFCalo, Et 2, Eta 0
              #  Pd, SP, Pf
            [[   14,  20,  14   ],
             [# Et 2, Eta 1
                 13,  11,  11   ],
             [# Et 2, Eta 2
                 9,  9,  19   ],
             [# Et 2, Eta 3
                 20,  20,  15   ]],
              # EFCalo, Et 3, Eta 0
              #  Pd, SP, Pf
            [[   20, 20,  20   ],
             [# Et 3, Eta 1
                 11,  7,  7   ],
             [# Et 3, Eta 2
                 17,  17,  19   ],
             [# Et 3, Eta 3
                 16,  16,  16   ]]
                               ]]

from pprint import pprint
pprint(configMap)

from TuningTools.CrossValidStat import CrossValidStatAnalysis
CrossValidStatAnalysis.printTables(configBaseList, 
                                   crossValGrid,
                                   configMap)




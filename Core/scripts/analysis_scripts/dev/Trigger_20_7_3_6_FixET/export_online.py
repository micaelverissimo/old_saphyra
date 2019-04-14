#!/usr/bin/env python

from RingerCore.Logger import LoggingLevel
from RingerCore.FileIO import expandFolders
from TuningTools.CrossValidStat import CrossValidStatAnalysis
from TuningTools.ReadData import RingerOperation
from pprint import pprint

crossValGrid = expandFolders('$ROOTCOREBIN/../TuningTools/scripts/skeletons/','FixET_Norm1*.pic')

#configMap = [
#              # EFCalo, Et 0, Eta 0
#              #  Pd, SP, Pf
#           [[   7, 7, 7   ],
#             [# Et 0, Eta 1
#                16,16,16  ],
#             [# Et 0, Eta 2
#                 19,07,19   ],
#             [# Et 0, Eta 3
#                14, 11,  11   ]],
#              # EFCalo, Et 1, Eta 0
#              #  Pd, SP, Pf
#            [[   7,  10, 7   ],
#             [# Et 1, Eta 1
#                 8, 10, 20   ],
#             [# Et 1, Eta 2
#                 11, 11, 8   ],
#             [# Et 1, Eta 3
#                 11,  7, 17   ]],
#              # EFCalo, Et 2, Eta 0
#              #  Pd, SP, Pf
#            [[   14,  20,  14   ],
#             [# Et 2, Eta 1
#                 13,  11,  11   ],
#             [# Et 2, Eta 2
#                 9,  9,  19   ],
#             [# Et 2, Eta 3
#                 20,  20,  15   ]],
#              # EFCalo, Et 3, Eta 0
#              #  Pd, SP, Pf
#            [[   20, 20,  20   ],
#             [# Et 3, Eta 1
#                 11,  7,  7   ],
#             [# Et 3, Eta 2
#                 17,  17,  19   ],
#             [# Et 3, Eta 3
#                 16,  16,  16   ]]
#                               ]
#
#
#refBenchmarkList = [["Medium_LH_EFCalo_Pd","Medium_MaxSP","Medium_LH_EFCalo_Pf"]]
#
#chainNames=['e24_lhmedium_L1EM20VH_L2EFCalo_ringer_pd',
#            'e24_lhmedium_L1EM20VH_ringer_sp',
#            'e24_lhmedium_L1EM20VH_L2EFCalo_ringer_pf']

configList = [
              # EFCalo, Et 0, Eta 0
              #  Pd, SP, Pf
           [[   7   ],
             [# Et 0, Eta 1
                16  ],
             [# Et 0, Eta 2
                 7   ],
             [# Et 0, Eta 3
                14   ]],
              # EFCalo, Et 1, Eta 0
              #  Pd, SP, Pf
            [[   7   ],
             [# Et 1, Eta 1
                 20   ],
             [# Et 1, Eta 2
                 11   ],
             [# Et 1, Eta 3
                 17   ]],
              # EFCalo, Et 2, Eta 0
              #  Pd, SP, Pf
            [[   14   ],
             [# Et 2, Eta 1
                 11   ],
             [# Et 2, Eta 2
                 9   ],
             [# Et 2, Eta 3
                 20   ]],
              # EFCalo, Et 3, Eta 0
              #  Pd, SP, Pf
            [[   20   ],
             [# Et 3, Eta 1
                 7   ],
             [# Et 3, Eta 2
                 17   ],
             [# Et 3, Eta 3
                 16   ]]
                               ]


refBenchmarkList = [[ # Et 0, Eta 0
                    ["Medium_LH_EFCalo_Pf"],
                      # Et 0, Eta 1
                    ["Medium_LH_EFCalo_Pf"],
                      # Et 0, Eta 2
                    ["Medium_MaxSP"],
                      # Et 0, Eta 3
                    ["Medium_LH_EFCalo_Pd"]],
                      # Et 1, Eta 0
                    [["Medium_LH_EFCalo_Pf"],
                      # Et 1, Eta 1
                    ["Medium_LH_EFCalo_Pf"],
                      # Et 1, Eta 2
                    ["Medium_LH_EFCalo_Pd"],
                      # Et 1, Eta 3
                    ["Medium_LH_EFCalo_Pf"]],
                      # Et 2, Eta 0
                    [["Medium_LH_EFCalo_Pf"],
                      # Et 2, Eta 1
                    ["Medium_LH_EFCalo_Pf"],
                      # Et 2, Eta 2
                    ["Medium_LH_EFCalo_Pd"],
                      # Et 2, Eta 3
                    ["Medium_LH_EFCalo_Pd"]],
                      # Et 3, Eta 0
                    [["Medium_LH_EFCalo_Pf"],
                      # Et 3, Eta 1
                    ["Medium_LH_EFCalo_Pf"],
                      # Et 3, Eta 2
                    ["Medium_LH_EFCalo_Pd"],
                      # Et 3, Eta 3
                    ["Medium_LH_EFCalo_Pf"]],
                    ]


chainNames=['e24_lhmedium_EFCalo']

CrossValidStatAnalysis.exportDiscrFiles(crossValGrid,
                                        RingerOperation.L2,
                                        refBenchCol=refBenchmarkList,
                                        configCol=configList,
                                        triggerChains=chainNames
                                        )



#!/usr/bin/env python


crossValGrid = [['crossValStat.pic']]

configBaseList =  ['Loose_LH',
                  'Medium_',
                  'Tight_LH']

configMap = [
            [[[   16,  16,  16  ]]],
            [[[   16,  16,  16  ]]],
            [[[   16,  16,  16  ]]],
            [[[   16,  16,  16  ]]],
            [[[   16,  16,  16  ]]],
            ]

from pprint import pprint
pprint(configMap)

from TuningTools.CrossValidStat import CrossValidStatAnalysis
CrossValidStatAnalysis.printTables(configBaseList, 
                                   crossValGrid,
                                   configMap)

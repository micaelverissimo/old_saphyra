#!/usr/bin/env python

from RingerCore.Logger import LoggingLevel
from RingerCore.FileIO import load
from TuningTools.CrossValidStat  import CrossValidStatAnalysis, \
                                        ReferenceBenchmark
from TuningTools.ReadData import RingerOperation


path = \
    '/tmp/jodafons/news/tunedDiscr.mc14.sgn.offLH.bkg.truth.trig.l1cluscut_20.l2etcut_19.e24_medium.eta.et.dep/' + \
    'tuned.mc14.sgn.offLH.bkg.truth.trig.l1cluscut_20.l2etcut_19.e24_medium_etaBin_3_etBin_2_multiFEX/'
    #'tuned.mc14.sgn.offLH.bkg.truth.trig.l1cluscut_20.l2etcut_19.e24_medium_etaBin_3_etBin_1_multiFEX/'
    #'tuned.mc14.sgn.offLH.bkg.truth.trig.l1cluscut_20.l2etcut_19.e24_medium_etaBin_3_etBin_0_multiFEX/'
    #'tuned.mc14.sgn.offLH.bkg.truth.trig.l1cluscut_20.l2etcut_19.e24_medium_etaBin_2_etBin_2/'
    #'tuned.mc14.sgn.offLH.bkg.truth.trig.l1cluscut_20.l2etcut_19.e24_medium_etaBin_2_etBin_1/'
    #'tuned.mc14.sgn.offLH.bkg.truth.trig.l1cluscut_20.l2etcut_19.e24_medium_etaBin_2_etBin_0/'
    #'tuned.mc14.sgn.offLH.bkg.truth.trig.l1cluscut_20.l2etcut_19.e24_medium_etaBin_1_etBin_2/'
    #'tuned.mc14.sgn.offLH.bkg.truth.trig.l1cluscut_20.l2etcut_19.e24_medium_etaBin_1_etBin_1/'
    #'tuned.mc14.sgn.offLH.bkg.truth.trig.l1cluscut_20.l2etcut_19.e24_medium_etaBin_1_etBin_0/'
    #'tuned.mc14.sgn.offLH.bkg.truth.trig.l1cluscut_20.l2etcut_19.e24_medium_etaBin_0_etBin_2/'
    #'tuned.mc14.sgn.offLH.bkg.truth.trig.l1cluscut_20.l2etcut_19.e24_medium_etaBin_0_etBin_1/'
    #'tuned.mc14.sgn.offLH.bkg.truth.trig.l1cluscut_20.l2etcut_19.e24_medium_etaBin_0_etBin_0/'

stat = CrossValidStatAnalysis( path, level = LoggingLevel.DEBUG )

################################## For Trigger ##################################

# Define the reference benchmarks
'''
#Online: e24_lhmedium_L1EM20VH bins: eta = 0, Et = 0
Medium_LH_L2Calo_Pd = ReferenceBenchmark( "Medium_LH_L2Calo_Pd", "Pd", refVal = 0.97068690 )
Medium_LH_EFCalo_Pd = ReferenceBenchmark( "Medium_LH_EFCalo_Pd", "Pd", refVal = 0.76709501 )
Medium_MaxSP        = ReferenceBenchmark( "Medium_MaxSP", "SP"                             )
Medium_LH_L2Calo_Pf = ReferenceBenchmark( "Medium_LH_L2Calo_Pf", "Pf", refVal = 0.08612440 )
Medium_LH_EFCalo_Pf = ReferenceBenchmark( "Medium_LH_EFCalo_Pf", "Pf", refVal = 0.02853092 )
outputName = 'crossValStat_etaBin_0_etBin_0'
'''
'''
#Online: e24_lhmedium_L1EM20VH bins: eta = 0, Et = 1
Medium_LH_L2Calo_Pd = ReferenceBenchmark( "Medium_LH_L2Calo_Pd", "Pd", refVal = 0.99028310 )
Medium_LH_EFCalo_Pd = ReferenceBenchmark( "Medium_LH_EFCalo_Pd", "Pd", refVal = 0.98887632 )
Medium_MaxSP        = ReferenceBenchmark( "Medium_MaxSP", "SP"                             )
Medium_LH_L2Calo_Pf = ReferenceBenchmark( "Medium_LH_L2Calo_Pf", "Pf", refVal = 0.11915313 )
Medium_LH_EFCalo_Pf = ReferenceBenchmark( "Medium_LH_EFCalo_Pf", "Pf", refVal = 0.06597735 )
outputName = 'crossValStat_etaBin_0_etBin_1'
'''
'''
#Online: e24_lhmedium_L1EM20VH bins: eta = 0, Et = 2
Medium_LH_L2Calo_Pd = ReferenceBenchmark( "Medium_LH_L2Calo_Pd", "Pd", refVal = 0.99430093 )
Medium_LH_EFCalo_Pd = ReferenceBenchmark( "Medium_LH_EFCalo_Pd", "Pd", refVal = 0.99344874 )
Medium_MaxSP        = ReferenceBenchmark( "Medium_MaxSP", "SP"                             )
Medium_LH_L2Calo_Pf = ReferenceBenchmark( "Medium_LH_L2Calo_Pf", "Pf", refVal = 0.07354260 )
Medium_LH_EFCalo_Pf = ReferenceBenchmark( "Medium_LH_EFCalo_Pf", "Pf", refVal = 0.03497758 )
outputName = 'crossValStat_etaBin_0_etBin_2'
'''
'''
#Online: e24_lhmedium_L1EM20VH bins: eta = 1, Et = 0
Medium_LH_L2Calo_Pd = ReferenceBenchmark( "Medium_LH_L2Calo_Pd", "Pd", refVal = 0.9692     )
Medium_LH_EFCalo_Pd = ReferenceBenchmark( "Medium_LH_EFCalo_Pd", "Pd", refVal = 0.8326     )
Medium_MaxSP        = ReferenceBenchmark( "Medium_MaxSP", "SP"                             )
Medium_LH_L2Calo_Pf = ReferenceBenchmark( "Medium_LH_L2Calo_Pf", "Pf", refVal = 0.0976     )
Medium_LH_EFCalo_Pf = ReferenceBenchmark( "Medium_LH_EFCalo_Pf", "Pf", refVal = 0.0366     )
outputName = 'crossValStat_etaBin_1_etBin_0'
'''
'''
#Online: e24_lhmedium_L1EM20VH bins: eta = 1, Et = 1
Medium_LH_L2Calo_Pd = ReferenceBenchmark( "Medium_LH_L2Calo_Pd", "Pd", refVal = 0.9915     )
Medium_LH_EFCalo_Pd = ReferenceBenchmark( "Medium_LH_EFCalo_Pd", "Pd", refVal = 0.9894     )
Medium_MaxSP        = ReferenceBenchmark( "Medium_MaxSP", "SP"                             )
Medium_LH_L2Calo_Pf = ReferenceBenchmark( "Medium_LH_L2Calo_Pf", "Pf", refVal = 0.1195     )
Medium_LH_EFCalo_Pf = ReferenceBenchmark( "Medium_LH_EFCalo_Pf", "Pf", refVal = 0.0580     )
outputName = 'crossValStat_etaBin_1_etBin_1'
'''
'''
#Online: e24_lhmedium_L1EM20VH bins: eta = 1, Et = 2
Medium_LH_L2Calo_Pd = ReferenceBenchmark( "Medium_LH_L2Calo_Pd", "Pd", refVal = 0.9969     )
Medium_LH_EFCalo_Pd = ReferenceBenchmark( "Medium_LH_EFCalo_Pd", "Pd", refVal = 0.9960     )
Medium_MaxSP        = ReferenceBenchmark( "Medium_MaxSP", "SP"                             )
Medium_LH_L2Calo_Pf = ReferenceBenchmark( "Medium_LH_L2Calo_Pf", "Pf", refVal = 0.1131     )
Medium_LH_EFCalo_Pf = ReferenceBenchmark( "Medium_LH_EFCalo_Pf", "Pf", refVal = 0.0598     )
outputName = 'crossValStat_etaBin_1_etBin_2'
'''

'''
#Online: e24_lhmedium_L1EM20VH bins: eta = 2, Et = 0 (Crack)
Medium_LH_L2Calo_Pd = ReferenceBenchmark( "Medium_LH_L2Calo_Pd", "Pd", refVal = 0.9069     )
Medium_LH_EFCalo_Pd = ReferenceBenchmark( "Medium_LH_EFCalo_Pd", "Pd", refVal = 0.8491     )
Medium_MaxSP        = ReferenceBenchmark( "Medium_MaxSP", "SP"                             )
Medium_LH_L2Calo_Pf = ReferenceBenchmark( "Medium_LH_L2Calo_Pf", "Pf", refVal = 0.4645     )
Medium_LH_EFCalo_Pf = ReferenceBenchmark( "Medium_LH_EFCalo_Pf", "Pf", refVal = 0.1830     )
outputName = 'crossValStat_etaBin_2_etBin_0'
'''
'''
#Online: e24_lhmedium_L1EM20VH bins: eta = 2, Et = 1 (Crack)
Medium_LH_L2Calo_Pd = ReferenceBenchmark( "Medium_LH_L2Calo_Pd", "Pd", refVal = 0.9586     )
Medium_LH_EFCalo_Pd = ReferenceBenchmark( "Medium_LH_EFCalo_Pd", "Pd", refVal = 0.9527     )
Medium_MaxSP        = ReferenceBenchmark( "Medium_MaxSP", "SP"                             )
Medium_LH_L2Calo_Pf = ReferenceBenchmark( "Medium_LH_L2Calo_Pf", "Pf", refVal = 0.5085     )
Medium_LH_EFCalo_Pf = ReferenceBenchmark( "Medium_LH_EFCalo_Pf", "Pf", refVal = 0.2283     )
outputName = 'crossValStat_etaBin_2_etBin_1'
'''
'''
#Online: e24_lhmedium_L1EM20VH bins: eta = 2, Et = 2 (Crack)
Medium_LH_L2Calo_Pd = ReferenceBenchmark( "Medium_LH_L2Calo_Pd", "Pd", refVal = 0.9674     )
Medium_LH_EFCalo_Pd = ReferenceBenchmark( "Medium_LH_EFCalo_Pd", "Pd", refVal = 0.9662     )
Medium_MaxSP        = ReferenceBenchmark( "Medium_MaxSP", "SP"                             )
Medium_LH_L2Calo_Pf = ReferenceBenchmark( "Medium_LH_L2Calo_Pf", "Pf", refVal = 0.4454     )
Medium_LH_EFCalo_Pf = ReferenceBenchmark( "Medium_LH_EFCalo_Pf", "Pf", refVal = 0.1260     )
outputName = 'crossValStat_etaBin_2_etBin_2'
'''

'''
#Online: e24_lhmedium_L1EM20VH bins: eta = 3, Et = 0 (EndCap)
Medium_LH_L2Calo_Pd = ReferenceBenchmark( "Medium_LH_L2Calo_Pd", "Pd", refVal = 0.9513     )
Medium_LH_EFCalo_Pd = ReferenceBenchmark( "Medium_LH_EFCalo_Pd", "Pd", refVal = 0.8093     )
Medium_MaxSP        = ReferenceBenchmark( "Medium_MaxSP", "SP"                             )
Medium_LH_L2Calo_Pf = ReferenceBenchmark( "Medium_LH_L2Calo_Pf", "Pf", refVal = 0.1761     )
Medium_LH_EFCalo_Pf = ReferenceBenchmark( "Medium_LH_EFCalo_Pf", "Pf", refVal = 0.0681     )
outputName = 'crossValStat_etaBin_3_etBin_0_multiFEX'
'''
'''
#Online: e24_lhmedium_L1EM20VH bins: eta = 3, Et = 1 (EndCap)
Medium_LH_L2Calo_Pd = ReferenceBenchmark( "Medium_LH_L2Calo_Pd", "Pd", refVal = 0.9755     )
Medium_LH_EFCalo_Pd = ReferenceBenchmark( "Medium_LH_EFCalo_Pd", "Pd", refVal = 0.9673     )
Medium_MaxSP        = ReferenceBenchmark( "Medium_MaxSP", "SP"                             )
Medium_LH_L2Calo_Pf = ReferenceBenchmark( "Medium_LH_L2Calo_Pf", "Pf", refVal = 0.2283     )
Medium_LH_EFCalo_Pf = ReferenceBenchmark( "Medium_LH_EFCalo_Pf", "Pf", refVal = 0.1226     )
outputName = 'crossValStat_etaBin_3_etBin_1_multiFEX'

'''
#No MultiFex
#Online: e24_lhmedium_L1EM20VH bins: eta = 3, Et = 2 (EndCap)
Medium_LH_L2Calo_Pd = ReferenceBenchmark( "Medium_LH_L2Calo_Pd", "Pd", refVal = 0.9847     )
Medium_LH_EFCalo_Pd = ReferenceBenchmark( "Medium_LH_EFCalo_Pd", "Pd", refVal = 0.9820     )
Medium_MaxSP        = ReferenceBenchmark( "Medium_MaxSP", "SP"                             )
Medium_LH_L2Calo_Pf = ReferenceBenchmark( "Medium_LH_L2Calo_Pf", "Pf", refVal = 0.1411     )
Medium_LH_EFCalo_Pf = ReferenceBenchmark( "Medium_LH_EFCalo_Pf", "Pf", refVal = 0.0569     )
outputName = 'crossValStat_etaBin_3_etBin_2_multiFEX'

# Add them to a list:
refBenchmarkList = [
                    Medium_LH_L2Calo_Pd, 
                    Medium_LH_EFCalo_Pd, 
                    Medium_MaxSP, 
                    Medium_LH_L2Calo_Pf,
                    Medium_LH_EFCalo_Pf,
                    ]
                  
# Run the cross-validation analysis:
stat( refBenchmarkList, outputName=outputName )

#!/usr/bin/env python

from RingerCore.Logger import LoggingLevel
from RingerCore.FileIO import load
from TuningTools.CrossValidStat  import CrossValidStatAnalysis, \
                                        ReferenceBenchmark
from TuningTools.ReadData import RingerOperation

path='/tmp/jodafons/news/tunedDiscr.mc14.sgn.offLH.bkg.truth.trig.l1cluscut_20.l2etcut_19.e24_medium/' + \
    'user.jodafons.nn.mc14_13TeV.147406.sgn.Off_LH.129160.bkg.truth.l1_20.l2_19.e24_medium_L1EM18VH.indep_eta_et.t0007_tunedDiscrXYZ.tgz/'

stat = CrossValidStatAnalysis( path, level = LoggingLevel.DEBUG )

################################## For Trigger ##################################

# Define the reference benchmarks
#Online: e24_lhmedium_L1EM20VH, all range of eta/et. We will use the global eff
Medium_LH_L2Calo_Pd = ReferenceBenchmark( "Medium_LH_L2Calo_Pd", "Pd", refVal = 0.9809     )
Medium_LH_EFCalo_Pd = ReferenceBenchmark( "Medium_LH_EFCalo_Pd", "Pd", refVal = 0.9506     )
Medium_MaxSP        = ReferenceBenchmark( "Medium_MaxSP", "SP"                             )
Medium_LH_L2Calo_Pf = ReferenceBenchmark( "Medium_LH_L2Calo_Pf", "Pf", refVal = 0.1358     )
Medium_LH_EFCalo_Pf = ReferenceBenchmark( "Medium_LH_EFCalo_Pf", "Pf", refVal = 0.0582     )
outputName = 'crossValStat_indep'

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



#!/usr/bin/env python

from RingerCore.Logger import LoggingLevel
from RingerCore.FileIO import load, save
from TuningTools.CrossValidStat  import CrossValidStatAnalysis, \
                                        ReferenceBenchmark
from TuningTools.ReadData import RingerOperation, BranchEffCollector

basepath ='/tmp/jodafons/Tuning2015'

fileList = [
['user.wsfreund.tuned.mc14.sgn.offLH.bkg.truth.trig.l1cluscut_20.l2etcut_19.e24_medium_etBin_0_etaBin_0.t0001_tunedDiscrXYZ.tgz/',
'user.wsfreund.tuned.mc14.sgn.offLH.bkg.truth.trig.l1cluscut_20.l2etcut_19.e24_medium_etBin_1_etaBin_0.t0001_tunedDiscrXYZ.tgz/',
'user.wsfreund.tuned.mc14.sgn.offLH.bkg.truth.trig.l1cluscut_20.l2etcut_19.e24_medium_etBin_2_etaBin_0.t0001_tunedDiscrXYZ.tgz/'],

['user.jodafons.nn.mc14_13TeV.147406.sgn.Off_LH.129160.bkg.truth.l1_20.l2_19.e24_medium_etBin_0_etaBin_1.t0002_tunedDiscrXYZ.tgz/',
'user.jodafons.nn.mc14_13TeV.147406.sgn.Off_LH.129160.bkg.truth.l1_20.l2_19.e24_medium_etBin_1_etaBin_1.t0002_tunedDiscrXYZ.tgz/',
'user.jodafons.nn.mc14_13TeV.147406.sgn.Off_LH.129160.bkg.truth.l1_20.l2_19.e24_medium_etBin_2_etaBin_1.t0002_tunedDiscrXYZ.tgz/'],

['user.damazio.tuned.mc14.sgn.offLH.bkg.truth.trig.l1cluscut_20.l2etcut_19.e24_medium_etBin_0_etaBin_2.t0002_tunedDiscrXYZ.tgz/',
'user.damazio.tuned.mc14.sgn.offLH.bkg.truth.trig.l1cluscut_20.l2etcut_19.e24_medium_etBin_1_etaBin_2.t0002_tunedDiscrXYZ.tgz/',
'user.damazio.tuned.mc14.sgn.offLH.bkg.truth.trig.l1cluscut_20.l2etcut_19.e24_medium_etBin_2_etaBin_2.t0002_tunedDiscrXYZ.tgz/'],

['user.nbullacr.tuned.mc14.sgn.offLH.bkg.truth.trig.l1cluscut_20.l2etcut_19.e24_medium_etBin_0_etaBin_3.t0001_tunedDiscrXYZ.tgz/',
'user.nbullacr.tuned.mc14.sgn.offLH.bkg.truth.trig.l1cluscut_20.l2etcut_19.e24_medium_etBin_1_etaBin_3.t0001_tunedDiscrXYZ.tgz/',
'user.nbullacr.tuned.mc14.sgn.offLH.bkg.truth.trig.l1cluscut_20.l2etcut_19.e24_medium_etBin_2_etaBin_3.t0001_tunedDiscrXYZ.tgz/'],
]

summaryList = [
'mc14_13TeV.147406.129160.sgn.offCutID.bkg.truth.trig.e24_lhmedium_L1EM20VH_summary.pic.gz',
'mc14_13TeV.147406.129160.sgn.offCutID.bkg.truth.trig.e24_lhtight_L1EM20VH_summary.pic.gz',
]

lhmediumSummary = load(summaryList[0])
lhtightSummary  = load(summaryList[1])



for nEta in [3]:

  for nEt in [0, 1, 2]:


    outputName = ('crossValStat_mc14_13TeV.147406.129160.sgn.offCutID.bkg.truth.trig.e24.etaBin_%d_etBin_%d')%(nEta,nEt)

    stat = CrossValidStatAnalysis( basepath+'/'+fileList[nEta][nEt], level = LoggingLevel.DEBUG )

    Medium_LH_L2Calo_Pd = ReferenceBenchmark( "Medium_LH_L2Calo_Pd", "Pd", refVal = lhmediumSummary['sgn'][nEt][nEta][0].efficiency()/float(100)  )
    Medium_LH_L2Calo_Pf = ReferenceBenchmark( "Medium_LH_L2Calo_Pf", "Pf", refVal = lhmediumSummary['bkg'][nEt][nEta][0].efficiency()/float(100)  )
    Medium_LH_EFCalo_Pd = ReferenceBenchmark( "Medium_LH_EFCalo_Pd", "Pd", refVal = lhmediumSummary['sgn'][nEt][nEta][2].efficiency()/float(100)  )
    Medium_LH_EFCalo_Pf = ReferenceBenchmark( "Medium_LH_EFCalo_Pf", "Pf", refVal = lhmediumSummary['bkg'][nEt][nEta][2].efficiency()/float(100)  )
    
    Tight_LH_L2Calo_Pd  = ReferenceBenchmark( "Tight_LH_L2Calo_Pd" , "Pd", refVal = lhtightSummary['sgn'][nEt][nEta][0].efficiency()/float(100) )
    Tight_LH_L2Calo_Pf  = ReferenceBenchmark( "Tight_LH_L2Calo_Pf" , "Pf", refVal = lhtightSummary['bkg'][nEt][nEta][0].efficiency()/float(100) )
    Tight_LH_EFCalo_Pd  = ReferenceBenchmark( "Tight_LH_EFCalo_Pd" , "Pd", refVal = lhtightSummary['sgn'][nEt][nEta][2].efficiency()/float(100) )
    Tight_LH_EFCalo_Pf  = ReferenceBenchmark( "Tight_LH_EFCalo_Pf" , "Pf", refVal = lhtightSummary['bkg'][nEt][nEta][2].efficiency()/float(100) )

    Medium_LH_MaxSP        = ReferenceBenchmark( "Medium_LH_MaxSP", "SP" )


    # Add them to a list:
    refBenchmarkList = [
                    Medium_LH_L2Calo_Pd, 
                    Medium_LH_EFCalo_Pd, 
                    Medium_LH_L2Calo_Pf,
                    Medium_LH_EFCalo_Pf,
                    Medium_LH_MaxSP,
                    Tight_LH_L2Calo_Pd, 
                    Tight_LH_EFCalo_Pd, 
                    Tight_LH_L2Calo_Pf,
                    Tight_LH_EFCalo_Pf, 
                    ]
                  
    # Run the cross-validation analysis:
    stat( refBenchmarkList, outputName=outputName )



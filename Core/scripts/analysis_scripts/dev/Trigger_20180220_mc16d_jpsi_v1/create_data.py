#!/usr/bin/env python

import numpy as np
from RingerCore.Configure import Development
Development.set( True )



etBins       = [3,7,10,15]
etaBins      = [0, 0.8 , 1.37, 1.54, 2.37, 2.5]
#basePath     = '/home/jodafons/CERN-DATA/data/mc16_13TeV'
basePath     = '/home/jodafons/CERN-DATA/data/data17_13TeV/GRL_v97'

#bkgInputFile = 'user.jodafons.mc16d_13TeV.361237.Pythia8EvtGen_A3NNPDF23LO_minbias_inelastic.r10210.Physval.r6001_GLOBAL/'
#sgnInputFile = 'user.jodafons.mc16d_13TeV.423200.Pythia8B_A14_CTEQ6L1_Jpsie3e3.r10210.Physval.r6003_GLOBAL/'
sgnInputFile = 'EGAM2'
bkgInputFile = 'EGAM7'
#outputFile   = 'mc16d_13TeV.sgn_Jpsie3e3_truth.bkg_minbias_truth.r10210'
outputFile   = 'sample'
treePath     = ["*/HLT/Physval/Egamma/probes",
                "*/HLT/Physval/Egamma/fakes"]

import os.path
from TuningTools import Reference, RingerOperation
from TuningTools import createData
from RingerCore  import LoggingLevel
from TuningTools.dataframe import Dataframe

createData( sgnFileList      = os.path.join( basePath, sgnInputFile ),
            bkgFileList      = os.path.join( basePath, bkgInputFile ),
            ringerOperation  = RingerOperation.Trigger,
            #referenceSgn     = Reference.Truth,
            #referenceBkg     = Reference.Truth, 
            referenceSgn     = Reference.Off_Likelihood, # probes passed by lhmedium
            referenceBkg     = Reference.Off_Likelihood, # electrons/any reproved by very loose
            treePath         = treePath,
            pattern_oFile    = outputFile,
            l2EtCut          = 2,
            offEtCut         = 2,
            #nClusters        = 1000,
            etBins           = etBins,
            etaBins          = etaBins,
            toMatlab         = True,
            plotMeans        = True,
            plotProfiles     = False,
            dataframe        = Dataframe.PhysVal_v2,
            #level     = LoggingLevel.VERBOSE
          )



from RingerCore import traverse
from TuningTools import BenchmarkEfficiencyArchieve
 
refname_list= ['veryloose','loose','medium','tight']
effFile  = outputFile+'-eff.npz'
refFile     = BenchmarkEfficiencyArchieve.load(effFile,False,None,None,True,True)
nEtBins     = refFile.nEtBins
nEtaBins    = refFile.nEtaBins
etBins      = refFile.etBins
etaBins     = refFile.etaBins
sgnEff      = refFile.signalEfficiencies
bkgEff      = refFile.backgroundEfficiencies
sgnCrossEff = refFile.signalCrossEfficiencies
bkgCrossEff = refFile.backgroundCrossEfficiencies
operation   = refFile.operation


for refname in refname_list:
  for etBinIdx in range(nEtBins):
    for etaBinIdx in range(nEtaBins):
      for key in sgnEff.keys():
        sgnEff[key][etBinIdx][etaBinIdx].setEfficiency(0.8)#dummy
        bkgEff[key][etBinIdx][etaBinIdx].setEfficiency(0.1)#dummy
  
  kwin = {'etaBins':                     etaBins
         ,'etBins':                      etBins
         ,'signalEfficiencies':          sgnEff
         ,'backgroundEfficiencies':      bkgEff
         ,'signalCrossEfficiencies':     sgnCrossEff
         ,'backgroundCrossEfficiencies': bkgCrossEff
         ,'operation':                   operation}
  
  ofile = BenchmarkEfficiencyArchieve(kwin).save(outputFile+'.'+refname+'-eff.npz')





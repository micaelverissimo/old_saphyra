#!/usr/bin/env python

import numpy as np
from RingerCore.Configure import Development
Development.set( True )


etBins       = [15, 20, 30, 40, 50, 500000 ]
etaBins      = [0, 0.8 , 1.37, 1.54, 2.37, 2.5]

tight20160701 = np.array(
  # eta 0          0.8         1.37      1.54     2.37
  [[0.849,     0.83898649, 0.7945,  0.8285,     0.82856316] # Et 15
  ,[0.866025,  0.85846486, 0.7975,  0.8568,     0.85683684] # Et 20
  ,[0.892305,  0.88658649, 0.8109,  0.8798,     0.87986105] # Et 30
  ,[0.9014375, 0.89668919, 0.815,   0.8967,     0.89674474] # Et 40
  ,[0.902375,  0.90035135, 0.8235,  0.9009,     0.90092632]])*100. # Et 50
medium20160701 = np.array(
# eta 0          0.8         1.37        1.54    2.37
  [[ 0.906125, 0.8907973,  0.8385,  0.8812,   0.88125263] # Et 15
  ,[ 0.924125, 0.91683784, 0.8438,  0.9121,   0.91210316] # Et 20
  ,[ 0.944885, 0.93741676, 0.84908, 0.9240,   0.92400337] # Et 30
  ,[ 0.948,    0.94378378, 0.85675, 0.9372,   0.93723947] # Et 40
  ,[ 0.947125, 0.94508108, 0.8595,  0.9384,   0.93848421]])*100. # Et 50

loose20160701 = np.array(
# eta 0          0.8         1.37        1.54    2.37
  [[ 0.9425,  0.93227027,  0.876,  0.9196,     0.9196    ] # Et 15
  ,[ 0.95465, 0.94708108, 0.8706,  0.9347,     0.93477684] # Et 20
  ,[ 0.96871, 0.96318919, 0.87894, 0.9518,     0.95187642] # Et 30
  ,[ 0.97425, 0.97103378, 0.884,   0.9657,     0.96574474] # Et 40
  ,[ 0.97525, 0.97298649, 0.887,   0.9670,     0.96703158]])*100. # Et 50
  
veryloose20160701 = np.array(
# eta 0          0.8         1.37        1.54     2.37
  [[ 0.978,   0.96458108, 0.9145,  0.9578,      0.95786316]
  ,[ 0.98615, 0.97850541, 0.9028,  0.9673,      0.96738947]
  ,[ 0.99369, 0.9900427,  0.90956, 0.9778,      0.97782105]
  ,[ 0.995,   0.99293919, 0.917,   0.9862,      0.98623421]
  ,[ 0.99525, 0.99318919, 0.9165,  0.9858,      0.98582632]])*100.

#etaBins      = [0, 0.8]

#for ref in (veryloose20160701, loose20160701, medium20160701, tight20160701):
ref = tight20160701
from RingerCore import traverse
pdrefs = ref
#print pdrefs
pfrefs = np.array( [[0.05]*len(etaBins)]*len(etBins) )*100. # 3 5 7 10
efficiencyValues = np.array([np.array([refs]) for refs in zip(traverse(pdrefs,tree_types=(np.ndarray),simple_ret=True)
                                                 ,traverse(pfrefs,tree_types=(np.ndarray),simple_ret=True))]).reshape(pdrefs.shape + (2,) )


sgnInputFile = '/eos/user/j/jodafons/CERN-DATA/data/data17_13TeV/PhysVal_v2/EGAM1/'
bkgInputFile = '/eos/user/j/jodafons/CERN-DATA/data/data17_13TeV/PhysVal_v2/EGAM7/'
outputFile   = 'sample'
treePath     = ["*/HLT/Physval/Egamma/probes",
                "*/HLT/Physval/Egamma/fakes"]

import os.path
from TuningTools import Reference, RingerOperation
from TuningTools import createData
from Gaugi  import LoggingLevel
from TuningTools.dataframe import Dataframe

createData( sgnFileList      = sgnInputFile,
            bkgFileList      = bkgInputFile,
            ringerOperation  = RingerOperation.Trigger,
            referenceSgn     = Reference.Off_Likelihood, # probes passed by lhmedium
            referenceBkg     = Reference.Off_Likelihood, # electrons/any reproved by very loose
            treePath         = treePath,
            pattern_oFile    = outputFile,
            l2EtCut          = 14,
            offEtCut         = 10,
            nClusters        = 1000,
            etBins           = etBins,
            etaBins          = etaBins,
            toMatlab         = True,
            #efficiencyValues = efficiencyValues,
            plotMeans        = True,
            plotProfiles     = False,
            dataframe        = Dataframe.PhysVal_v2,
            #level     = LoggingLevel.VERBOSE
          )



from RingerCore import traverse
from TuningTools import BenchmarkEfficiencyArchieve
 
refname_list= ['veryloose','loose','medium','tight']
pdrefs_list = [veryloose20160701,loose20160701,medium20160701,tight20160701]
pfrefs_list = [0.07,0.05,0.03,0.01]


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


for refIdx in range(len(pdrefs_list)):
  refname = refname_list[refIdx]
  pdrefs  = pdrefs_list[refIdx]
  pfrefs  = np.array( [[pfrefs_list[refIdx]]*len(etaBins)]*len(etBins) )*100.
  efficiencyValues = np.array([np.array([refs]) for refs in zip(traverse(pdrefs,tree_types=(np.ndarray),simple_ret=True)
                                                   ,traverse(pfrefs,tree_types=(np.ndarray),simple_ret=True))]).reshape(pdrefs.shape + (2,) )
  #print efficiencyValues

  for etBinIdx in range(nEtBins):
    for etaBinIdx in range(nEtaBins):
      
      for key in sgnEff.keys():
        sgnEff[key][etBinIdx][etaBinIdx].setEfficiency(pdrefs[etBinIdx][etaBinIdx])
        bkgEff[key][etBinIdx][etaBinIdx].setEfficiency(pfrefs[etBinIdx][etaBinIdx])
  
  kwin = {'etaBins':                     etaBins
         ,'etBins':                      etBins
         ,'signalEfficiencies':          sgnEff
         ,'backgroundEfficiencies':      bkgEff
         ,'signalCrossEfficiencies':     sgnCrossEff
         ,'backgroundCrossEfficiencies': bkgCrossEff
         ,'operation':                   operation}
  
  ofile = BenchmarkEfficiencyArchieve(kwin).save(outputFile+'.'+refname+'-eff.npz')





#!/usr/bin/env python

import numpy as np


etBins       = [15, 20, 30, 40, 50, 500000 ]
etaBins      = [0, 0.8 , 1.37, 1.54, 2.37, 2.5]


tight20160701 = np.array(
  # eta 0          0.8         1.37      1.54     2.37
  [[0.9739    ,  0.9725    , 0.9282 ,  0.9688,     0.9264] # Et 15
  ,[0.9766    ,  0.9745    , 0.9065 ,  0.9735,     0.9363] # Et 20
  ,[0.9801    ,  0.9811    , 0.9518 ,  0.9775,     0.9441] # Et 30
  ,[0.9834    ,  0.9847    , 0.9606 ,  0.9815,     0.9470] # Et 40
  ,[0.9896    ,  0.9904    , 0.985  ,  0.9859,     0.9620]])*100. # Et 50

medium20160701 = np.array(
  # eta 0          0.8         1.37        1.54    2.37
  [[ 0.9841  , 0.9819    , 0.9371,  0.9796,   0.9542    ] # Et 15
  ,[ 0.9861  , 0.9838    , 0.9407,  0.9833,   0.9639    ] # Et 20
  ,[ 0.9886  , 0.9883    , 0.9612,  0.9864,   0.9611    ] # Et 30
  ,[ 0.9902  , 0.9902    , 0.9744,  0.9876,   0.9499    ] # Et 40
  ,[ 0.9924  , 0.9927    , 0.9761,  0.9907,   0.9768]])*100. # Et 50

loose20160701 = np.array(
  # eta 0          0.8         1.37        1.54    2.37
  [[ 0.9821  , 0.9778   , 0.9391,  0.9729,     0.9360    ] # Et 15
  ,[ 0.9865  , 0.9830   , 0.9390,  0.9814,     0.9504    ] # Et 20
  ,[ 0.9894  , 0.9884   , 0.9653,  0.9864,     0.9578    ] # Et 30
  ,[ 0.9919  , 0.9908   , 0.9737,  0.9891,     0.9620    ] # Et 40
  ,[ 0.9932  , 0.9928   , 0.9753,  0.9918,     0.9801   ]])*100. # Et 50
  
veryloose20160701 = np.array(
# eta 0          0.8         1.37        1.54     2.37
  [[ 0.9861  , 0.9803   , 0.9366,  0.9744,      0.9470    ]
  ,[ 0.9892  , 0.9869   , 0.9431,  0.9834,      0.9633    ]
  ,[ 0.9914  , 0.9904   , 0.9724,  0.9885,      0.9680    ]
  ,[ 0.9930  , 0.9921   , 0.9778,  0.9763,      0.9533    ]
  ,[ 0.9938  , 0.9933   , 0.9794,  0.9925,      0.9826    ]])*100.

#etaBins      = [0, 0.8]

#for ref in (veryloose20160701, loose20160701, medium20160701, tight20160701):
ref = tight20160701
from RingerCore import traverse
pdrefs = ref
#print pdrefs
pfrefs = np.array( [[0.05]*len(etaBins)]*len(etBins) )*100. # 3 5 7 10
efficiencyValues = np.array([np.array([refs]) for refs in zip(traverse(pdrefs,tree_types=(np.ndarray),simple_ret=True)
                                                 ,traverse(pfrefs,tree_types=(np.ndarray),simple_ret=True))]).reshape(pdrefs.shape + (2,) )


basePath     = '/eos/user/j/jodafons/CERN-DATA/data/data17_13TeV/'
sgnInputFile = 'EGAM1'
bkgInputFile = 'EGAM7'
outputFile   = 'sample'
treePath     = ["*/HLT/Physval/Egamma/probes",
                "*/HLT/Physval/Egamma/fakes"]

import os.path
from TuningTools import Reference, RingerOperation, Detector
from TuningTools import createData
from RingerCore  import LoggingLevel
from TuningTools.dataframe import Dataframe
from RingerCore.Configure import Development
Development.set( True )

createData( sgnFileList      = os.path.join( basePath, sgnInputFile ),
            bkgFileList      = os.path.join( basePath, bkgInputFile ),
            ringerOperation  = RingerOperation.L2Calo,
            referenceSgn     = Reference.Off_Likelihood, # probes passed by lhmedium
            referenceBkg     = Reference.Off_Likelihood, # electrons/any reproved by very loose
            treePath         = treePath,
            pattern_oFile    = outputFile,
            l2EtCut          = 14,
            offEtCut         = 10,
            #nClusters        = 1000,
            etBins           = etBins,
            etaBins          = etaBins,
            toMatlab         = True,
            #efficiencyValues = efficiencyValues,
            plotMeans        = True,
            plotProfiles     = False,
            dataframe        = Dataframe.PhysVal_v2,
            #extractDet       = Detector.Tracking,
            extractDet       = Detector.Calorimetry,
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





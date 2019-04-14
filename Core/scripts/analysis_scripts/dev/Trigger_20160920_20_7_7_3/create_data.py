#!/usr/bin/env python

#etBins       = [0, 30, 40, 50, 100000 ]
etBins       = [15, 20, 30, 40, 50, 500000 ]
etaBins      = [0, 0.8 , 1.37, 1.54, 2.5]
#etaBins      = [0, 0.8]

import numpy as np
tight20160701 = np.array(
  # eta 0          0.8         1.37        1.54
  [[0.849,     0.83898649, 0.7945, 0.82856316] # Et 15
  ,[0.866025,  0.85846486, 0.7975, 0.85683684] # Et 20
  ,[0.892305,  0.88658649, 0.8109, 0.87986105] # Et 30
  ,[0.9014375, 0.89668919, 0.815,  0.89674474] # Et 40
  ,[0.902375,  0.90035135, 0.8235, 0.90092632]])*100. # Et 50
medium20160701 = np.array(
# eta 0          0.8         1.37        1.54
  [[ 0.906125, 0.8907973,  0.8385,  0.88125263] # Et 15
  ,[ 0.924125, 0.91683784, 0.8438,  0.91210316] # Et 20
  ,[ 0.944885, 0.93741676, 0.84908, 0.92400337] # Et 30
  ,[ 0.948,    0.94378378, 0.85675, 0.93723947] # Et 40
  ,[ 0.947125, 0.94508108, 0.8595,  0.93848421]])*100. # Et 50

loose20160701 = np.array(
# eta 0          0.8         1.37        1.54
  [[ 0.9425,  0.93227027,  0.876,  0.9196    ] # Et 15
  ,[ 0.95465, 0.94708108, 0.8706,  0.93477684] # Et 20
  ,[ 0.96871, 0.96318919, 0.87894, 0.95187642] # Et 30
  ,[ 0.97425, 0.97103378, 0.884,   0.96574474] # Et 40
  ,[ 0.97525, 0.97298649, 0.887,   0.96703158]])*100. # Et 50
  
veryloose20160701 = np.array(
  [[ 0.978  ,    0.96458108, 0.9145 ,    0.95786316]
  ,[ 0.98615,    0.97850541, 0.9028 ,    0.96738947]
  ,[ 0.99369,    0.9900427 , 0.90956,    0.97782105]
  ,[ 0.995  ,    0.99293919, 0.917  ,    0.98623421]
  ,[ 0.99525,    0.99318919, 0.9165 ,    0.98582632]])*100.

from RingerCore import traverse
pdrefs = medium20160701
pfrefs = np.array( [[0.05]*len(etaBins)]*len(etBins) )*100.
efficiencyValues = np.array([np.array([refs]) for refs in zip(traverse(pdrefs,tree_types=(np.ndarray),simple_ret=True)
                                                 ,traverse(pfrefs,tree_types=(np.ndarray),simple_ret=True))]).reshape(pdrefs.shape + (2,) )
print efficiencyValues
basePath     = '/home/wsfreund/CERN-DATA'
sgnInputFile = 'user.jodafons.mc15_13TeV.361106.PowhegPythia8EvtGen_AZNLOCTEQ6L1_Zee.merge.AOD.e3601_s2876_r7917_r7676.dump.trigPB.p0200_GLOBAL/'
bkgInputFile = 'user.jodafons.mc15_13TeV.423300.Pythia8EvtGen_A14NNPDF23LO_perf_JF17.merge.AOD.e3848_s2876_r7917_r7676.dump.trigEL.p0201_GLOBAL/'
outputFile   = 'mc15_13TeV.361106.423300.sgn.trigegprobes.bkg.vetotruth.trig.l2calo.medium'
treePath     = ["HLT/Egamma/Expert/support/probes",
                "HLT/Egamma/Expert/support/trigger"]
#crossValPath = 'crossValid_5sorts.pic.gz'


#from TuningTools  import CrossValidArchieve
#with CrossValidArchieve( crossValPath ) as CVArchieve:
#  crossVal = CVArchieve
#  del CVArchieve

import os.path
from TuningTools import Reference, RingerOperation
from TuningTools import createData
from RingerCore  import LoggingLevel
createData( sgnFileList      = os.path.join( basePath, sgnInputFile ),
            bkgFileList      = os.path.join( basePath, bkgInputFile ),
            ringerOperation  = RingerOperation.L2Calo,
            referenceSgn     = Reference.AcceptAll,
            referenceBkg     = Reference.Truth,
            treePath         = treePath,
            pattern_oFile    = outputFile,
            #offEtCut        = 15,
            #getRatesOnly    = args.getRatesOnly,
            #nClusters        = 1000,
            etBins           = etBins,
            etaBins          = etaBins,
            toMatlab         = True,
            efficiencyValues = efficiencyValues,
            plotProfiles     = True,
            label            = "mc15c",
            #level            = LoggingLevel.VERBOSE,
            supportTriggers  = True,
          )

#!/usr/bin/env python

etaBins = [0.00,0.60,0.80,1.15,1.37,1.52,1.81,2.01,2.37,2.47]
etBins  = [15,20,30,40,50000]

#etaBins      = [0, 0.8]

import numpy as np

# Thresholds
thres_lh_etavect = [0,0.6,0.8,1.15,1.37,1.52,1.81,2.01,2.37,2.47]
thres_lh_etvect = [4,7,10,15,20,25,30,35,40,45,50]

import numpy as np
tight20160701 = np.array( [[0.484,0.532,0.490,0.466,0.252,0.510,0.494,0.384,0.349], # 4 GeV
                           [0.531,0.599,0.557,0.532,0.381,0.575,0.569,0.454,0.403], # 7 GeV
                           [0.594,0.641,0.589,0.572,0.416,0.587,0.580,0.554,0.472], # 10 GeV
                           [0.700,0.692,0.680,0.675,0.589,0.687,0.690,0.624,0.671], # 15 GeV
                           [0.709,0.686,0.694,0.689,0.646,0.701,0.718,0.677,0.734], # 20 GeV
                           [0.752,0.749,0.736,0.730,0.561,0.747,0.744,0.708,0.745], # 25 GeV
                           [0.776,0.773,0.761,0.760,0.614,0.752,0.769,0.728,0.795], # 30 GeV
                           [0.794,0.791,0.786,0.783,0.629,0.780,0.785,0.766,0.792], # 35 GeV
                           [0.803,0.795,0.782,0.792,0.613,0.783,0.800,0.780,0.820], # 40 GeV
                           [0.808,0.795,0.793,0.812,0.647,0.798,0.814,0.799,0.853]] ) * 100. # 45 GeV

medium20160701 = np.array([[0.667,0.674,0.652,0.617,0.343,0.609,0.592,0.576,0.524], # 4 GeV
                           [0.670,0.737,0.715,0.679,0.527,0.701,0.683,0.587,0.537], # 7 GeV
                           [0.751,0.778,0.746,0.712,0.549,0.721,0.713,0.707,0.649], # 10 GeV
                           [0.815,0.804,0.782,0.781,0.677,0.794,0.764,0.742,0.757], # 15 GeV
                           [0.833,0.810,0.813,0.811,0.735,0.823,0.814,0.802,0.815], # 20 GeV
                           [0.863,0.860,0.848,0.848,0.656,0.842,0.834,0.827,0.817], # 25 GeV
                           [0.886,0.873,0.870,0.864,0.681,0.835,0.861,0.829,0.848], # 30 GeV
                           [0.897,0.894,0.886,0.875,0.714,0.876,0.867,0.842,0.866], # 35 GeV
                           [0.900,0.891,0.887,0.882,0.708,0.883,0.879,0.862,0.896], # 40 GeV
                           [0.894,0.895,0.893,0.886,0.719,0.882,0.888,0.869,0.913]] ) * 100. # 45 GeV

loose20160701 = np.array( [[0.813,0.810,0.807,0.781,0.536,0.758,0.739,0.750,0.709], # 4 GeV
                           [0.819,0.816,0.813,0.787,0.670,0.808,0.789,0.753,0.711], # 7 GeV
                           [0.853,0.850,0.827,0.801,0.692,0.837,0.818,0.816,0.777], # 10 GeV
                           [0.886,0.882,0.869,0.858,0.752,0.854,0.855,0.823,0.802], # 15 GeV
                           [0.897,0.888,0.885,0.884,0.791,0.880,0.871,0.853,0.875], # 20 GeV
                           [0.921,0.913,0.905,0.894,0.708,0.894,0.875,0.858,0.853], # 25 GeV
                           [0.934,0.930,0.922,0.912,0.735,0.908,0.909,0.866,0.869], # 30 GeV
                           [0.942,0.940,0.937,0.930,0.779,0.931,0.931,0.905,0.913], # 35 GeV
                           [0.947,0.945,0.941,0.934,0.762,0.935,0.936,0.922,0.919], # 40 GeV
                           [0.951,0.949,0.948,0.943,0.774,0.940,0.944,0.926,0.945]]) * 100. # 45 GeV

veryloose20160701 = np.array([[0.896,0.893,0.890,0.884,0.719,0.875,0.866,0.859,0.821], # 4 GeV
                              [0.928,0.925,0.922,0.916,0.758,0.906,0.897,0.890,0.854], # 7 GeV
                              [0.928,0.925,0.922,0.915,0.766,0.906,0.897,0.889,0.856], # 10 GeV
                              [0.958,0.950,0.932,0.925,0.829,0.920,0.925,0.909,0.876], # 15 GeV
                              [0.966,0.957,0.955,0.943,0.844,0.943,0.929,0.916,0.904], # 20 GeV
                              [0.979,0.975,0.962,0.961,0.780,0.956,0.942,0.929,0.919], # 25 GeV
                              [0.988,0.985,0.980,0.973,0.803,0.961,0.956,0.923,0.922], # 30 GeV
                              [0.988,0.986,0.984,0.981,0.834,0.976,0.971,0.963,0.960], # 35 GeV
                              [0.990,0.988,0.987,0.983,0.835,0.978,0.974,0.970,0.972], # 40 GeV
                              [0.991,0.989,0.988,0.984,0.833,0.979,0.974,0.966,0.976]]) * 100. # 45 GeV
def standardRef( val ):
  return np.array( val )

def transformToEFCalo( val ):
  return np.array( val ) + (1 - np.array( val ) ) / 2

def mergeEffTable( val ):
  import itertools
  shape = val.shape
  #shorterEtaEffTable = np.zeros( shape=(shape[0], 4) )
  # eta 0.0, 0.6, 0.8, 0.15, 1.37, 1.52, 1.81, 2.01, 2.37
  #for etIdx, etaIdx in itertools.product( range( shape[0] ), range( 4 ) ):
  #  if etaIdx == 0: # merge 0 -> .6 -> .8
  #    shorterEtaEffTable[etIdx,etaIdx] = ( val[etIdx,0]*.6 + val[etIdx,1]*.2 ) / .8
  #  if etaIdx == 1: # merge 1.15 -> 1.37 -> 1.52
  #    shorterEtaEffTable[etIdx,etaIdx] = ( val[etIdx,2]*.22 + val[etIdx,3]*.15 ) / .37
  #  if etaIdx == 2: # 1.37 -> 1.52
  #    shorterEtaEffTable[etIdx,etaIdx] = val[etIdx,4]
  #  if etaIdx == 3: # merge 1.52 -> 1.8 -> 2.47
  #    shorterEtaEffTable[etIdx,etaIdx] = ( val[etIdx,5]*.29 + val[etIdx,6]*.2 + val[etIdx,7]*.46 )/(.95)
  shorterEffTable = np.zeros( shape=(4,9) )
  for etIdx, etaIdx in itertools.product( range(4), range(9) ):
    refIdx = etIdx + 3
    if etIdx == 0: # 15 up to 20
      shorterEffTable[etIdx,etaIdx] = val[refIdx,etaIdx]
    if etIdx == 1: # merge 20, 25
      shorterEffTable[etIdx,etaIdx] = (val[refIdx,etaIdx]*.4 + val[refIdx+1,etaIdx]*.6)
    if etIdx == 2: # merge 30, 35
      shorterEffTable[etIdx,etaIdx] = (val[refIdx+1,etaIdx]*.48 + val[refIdx+2,etaIdx]*.52)
    if etIdx == 3: # merge 40, 45
      shorterEffTable[etIdx,etaIdx] = (val[refIdx+2,etaIdx]*.5 + val[refIdx+3,etaIdx]*.5)
  return shorterEffTable

from RingerCore import traverse
pdrefs = mergeEffTable( medium20160701 )
print pdrefs
pfrefs = np.array( [[0.05]*len(etaBins)]*len(etBins) )*100. # 3 5 7 10
efficiencyValues = np.array([np.array([refs]) for refs in zip(traverse(pdrefs,tree_types=(np.ndarray),simple_ret=True)
                                                 ,traverse(pfrefs,tree_types=(np.ndarray),simple_ret=True))]).reshape(pdrefs.shape + (2,) )
print efficiencyValues
basePath     = '/home/wsfreund/CERN-DATA'
sgnInputFile = 'user.jodafons.mc15_13TeV.361106.PowhegPythia8EvtGen_AZNLOCTEQ6L1_Zee.merge.AOD.e3601_s2876_r7917_r7676.dump.trigPB.p0200_GLOBAL/'
bkgInputFile = 'user.jodafons.mc15_13TeV.423300.Pythia8EvtGen_A14NNPDF23LO_perf_JF17.merge.AOD.e3848_s2876_r7917_r7676.dump.trigEL.p0201_GLOBAL/'
outputFile   = 'mc15_13TeV.361106.423300.sgn.trigegprobes.bkg.vetotruth.trig.l2calo.eg.std.grid.medium'
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
            nClusters        = 1000,
            etBins           = etBins,
            etaBins          = etaBins,
            toMatlab         = True,
            efficiencyValues = efficiencyValues,
            plotProfiles     = True,
            supportTriggers  = True,
            #level     = LoggingLevel.VERBOSE
          )

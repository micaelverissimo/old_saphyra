#!/usr/bin/env python

import numpy as np
from RingerCore import traverse


etBins       = [3.,7.,10.,15.]
etaBins      = [0.0, 0.8 , 1.37, 1.54, 2.37, 2.5]
#basePath     = '/eos/user/j/jodafons/CERN-DATA/data/data17_13TeV/SkimmedNtuple'
basePath     = '/home/jodafons/CERN-DATA/data/data17_13TeV/SkimmedNtuple'
sgnInputFile = 'user.jodafons.data17_13TeV.AllYear.physics_Main.deriv.DAOD_EGAM2.f889_m1902_p3336.SkimmedNtuple.GRL_v97.r1000_GLOBAL'
bkgInputFile = 'user.jodafons.data17_13TeV.AllYear.physics_Main.deriv.DAOD_EGAM7.f889_m1902_p3336.SkimmedNtuple.GRL_v97.r1000_GLOBAL'
outputFile   = 'sample'
treePath     = ["JpsiCandidate",
                "ZeeCandidate"]



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
            l2EtCut          = 1,
            offEtCut         = 1,
            #nClusters        = 1000,
            etBins           = etBins,
            etaBins          = etaBins,
            toMatlab         = True,
            #efficiencyValues = efficiencyValues,
            plotMeans        = True,
            plotProfiles     = False,
            dataframe        = Dataframe.SkimmedNtuple,
            #extractDet       = Detector.Tracking,
            extractDet       = Detector.Calorimetry,
            #level     = LoggingLevel.VERBOSE
          )







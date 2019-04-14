#!/usr/bin/env python

from RingerCore import ArgumentParser, BooleanStr, Logger
import argparse

mainLogger = Logger.getModuleLogger("job")

parser = argparse.ArgumentParser(description = '', add_help = False)
parser = argparse.ArgumentParser()


parser.add_argument('-o','--outputFile', action='store', 
    dest='outputFile', required = False, default = None,
    help = "The output store name.")


import sys,os
if len(sys.argv)==1:
  parser.print_help()
  sys.exit(1)

args = parser.parse_args()



import numpy as np
from RingerCore import traverse


basepath      = '/eos/user/j/jodafons/CERN-DATA/data/mc15_13TeV/'
sgnFileList   = []
bkgFileList   = []
outputFile    = args.outputFile

etBins       = [15, 20, 30, 40, 50, 500000 ]
#etaBins      = [0, 0.8 , 1.37, 1.54, 2.37, 2.5]
etaBins      = [0, 0.8 , 1.37, 1.54, 2.5]

sgnFileList.append( os.path.join( basepath, 'user.jodafons.mc15_13TeV.361106.PowhegPythia8EvtGen_AZNLOCTEQ6L1_Zee.merge.AOD.e3601_s2876_r7917_r7676.PhysVal_v2' ) )
bkgFileList.append( os.path.join( basepath, 'user.jodafons.mc15_13TeV.423300.Pythia8EvtGen_A14NNPDF23LO_perf_JF17.merge.AOD.e3848_s2876_r7917_r7676.PhysVal_v2' ) )
treePath = ['*/HLT/Egamma/Egamma/probes', '*/HLT/Egamma/Egamma/fakes']



import os.path
from TuningTools import Reference, RingerOperation, Detector
from TuningTools import createData
from RingerCore  import LoggingLevel
from TuningTools.dataframe import Dataframe
from RingerCore.Configure import Development

Development.set( True )
createData( sgnFileList      = sgnFileList,
            bkgFileList      = bkgFileList,
            ringerOperation  = RingerOperation.L2Calo,
            referenceSgn     = Reference.Off_Likelihood, # probes passed by lhmedium
            #referenceBkg     = Reference.Off_Likelihood, # electrons/any reproved by very loose
            referenceBkg     = Reference.Off_Likelihood, # electrons/any reproved by very loose
            treePath         = treePath,
            pattern_oFile    = outputFile,
            l2EtCut          = 15,
            offEtCut         = 15,
            #nClusters        = 1000,
            etBins           = etBins,
            etaBins          = etaBins,
            toMatlab         = True,
            plotMeans        = True,
            plotProfiles     = False,
            dataframe        = Dataframe.PhysVal_v2,
            #extractDet       = Detector.Tracking,
            extractDet       = Detector.Calorimetry,
            #level     = LoggingLevel.VERBOSE
          )







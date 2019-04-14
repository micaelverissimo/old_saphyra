#!/usr/bin/env python

from RingerCore import ArgumentParser, BooleanStr, Logger
import argparse

mainLogger = Logger.getModuleLogger("job")

parser = argparse.ArgumentParser(description = '', add_help = False)
parser = argparse.ArgumentParser()


parser.add_argument('-o','--outputFile', action='store', 
    dest='outputFile', required = False, default = None,
    help = "The output store name.")

parser.add_argument('--Zee', action='store_true', 
    dest='doZee', required = False, default=False, 
    help = "Use Zee configuration")

parser.add_argument('--Jpsi', action='store_true', 
    dest='doJpsi', required = False, default = False,
    help = "Use Jpsi configuration")

parser.add_argument('--2017', action='store_true', 
    dest='use2017', required = False, default = False,
    help = "Use 2017 all year samples")

parser.add_argument('--2018', action='store_true', 
    dest='use2018', required = False, default = False, 
    help = "Use 2018 Late June samples")


import sys,os
if len(sys.argv)==1:
  parser.print_help()
  sys.exit(1)

args = parser.parse_args()



import numpy as np
from RingerCore import traverse


basepath      = '/home/jodafons/CERN-DATA/data/data17_13TeV'
treePath      = ["Candidate", "Candidate"]
sgnFileList   = []
bkgFileList   = []
outputFile    = args.outputFile

if args.doJpsi:
  
  etBins       = [3.,7.,10.,15.]
  etaBins      = [0.0, 0.8 , 1.37, 1.54, 2.37, 2.5]

  if args.use2017:
    sgnFileList.append( os.path.join( basepath, 'user.jodafons.data17_13TeV.AllYear.EGAM2.SkimmedNtuple_v2.r0001' ) )
    bkgFileList.append( os.path.join( basepath, 'user.jodafons.data17_13TeV.AllYear.EGAM7.SkimmedNtuple_v2.r0001' ) )
  if args.use2018:
    sgnFileList.append( os.path.join( basepath, 'user.jodafons.data18_13TeV.LateJune.EGAM2.SkimmedNtuple_v2.r0001' ) )
    bkgFileList.append( os.path.join( basepath, 'user.jodafons.data18_13TeV.LateJune.EGAM7.SkimmedNtuple_v2.r0001' ) )
  

elif args.doZee:
  
  etBins       = [15, 20, 30, 40, 50, 500000 ]
  etaBins      = [0, 0.8 , 1.37, 1.54, 2.37, 2.5]
  
  if args.use2017:
    sgnFileList.append( os.path.join( basepath, 'user.jodafons.data17_13TeV.AllYear.EGAM1.SkimmedNtuple_v2.r0001' ) )
    bkgFileList.append( os.path.join( basepath, 'user.jodafons.data17_13TeV.AllYear.EGAM7.SkimmedNtuple_v2.r0001' ) )
  if args.use2018:
    sgnFileList.append( os.path.join( basepath, 'user.jodafons.data17_13TeV.AllYear.EGAM1.SkimmedNtuple_v2.r0001' ) )
    bkgFileList.append( os.path.join( basepath, 'user.jodafons.data17_13TeV.AllYear.EGAM7.SkimmedNtuple_v2.r0001' ) )
 

else:
  print 'You must select one event configuration!'



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
            referenceBkg     = Reference.Off_Likelihood, # electrons/any reproved by very loose
            treePath         = treePath,
            pattern_oFile    = outputFile,
            l2EtCut          = 1,
            offEtCut         = 1,
            #nClusters        = 1000,
            etBins           = etBins,
            etaBins          = etaBins,
            toMatlab         = True,
            plotMeans        = True,
            plotProfiles     = False,
            dataframe        = Dataframe.SkimmedNtuple_v2,
            #extractDet       = Detector.Tracking,
            extractDet       = Detector.Calorimetry,
            #level     = LoggingLevel.VERBOSE
          )







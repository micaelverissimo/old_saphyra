#!/usr/bin/env python

from RingerCore import LoggingLevel, Logger
mainLogger = Logger.getModuleLogger("FileJuicer")

import argparse
parser = argparse.ArgumentParser(description = '', add_help = False)
parser = argparse.ArgumentParser()

parser.add_argument('-i','--inputFile', action='store', 
    dest='inputFile', required = True, help = "File to Juice!")
parser.add_argument('-o','--outputPath', action='store', required = False
                   , help = """Output file path. When set to None, will use
                   inputFile path.""")

import sys,os
if len(sys.argv)==1:
  parser.print_help()
  sys.exit(1)
args = parser.parse_args()


from RingerCore import load,save
from RingerCore import changeExtension, ensureExtension, appendToFileName, progressbar, mkdir_p
from itertools import product
import numpy as np
if args.outputPath is None:
  args.outputPath = os.path.dirname(args.inputFile)
  if not os.path.isdir( args.outputPath ): mkdir_p( args.outputPath )
f = load(args.inputFile)
# Copy all metada information
baseDict = { k : f[k] for k in f.keys() if not '_etBin_' in k and not '_etaBin_' in k }
nEtBins = f['nEtBins'].item()
nEtaBins = f['nEtaBins'].item()
for etIdx, etaIdx in progressbar( product(xrange(nEtBins), xrange(nEtaBins))
                                , nEtBins*nEtaBins
                                , logger = mainLogger 
                                , prefix = 'Juicing file '):
  binDict= {k:f[k] for k in f.keys()  if 'etBin_%d_etaBin_%d'%(etIdx,etaIdx) in k}
  binDict.update(baseDict)
  outFile = os.path.join( args.outputPath, os.path.basename( appendToFileName(args.inputFile, 'et%d_eta%d' % (etIdx, etaIdx) ) ) )
  #save(binDict, outFile, protocol = 'savez_compressed' )
  save(binDict, outFile )

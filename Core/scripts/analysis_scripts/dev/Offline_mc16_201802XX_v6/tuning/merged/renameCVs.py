#!/usr/bin/env python


from rDev.Event          import EventLooper
from rDev.dataframe      import ElectronCandidate
from TuningTools.dataframe.EnumCollection  import Dataframe as DataframeEnum
from RingerCore                            import LoggingLevel, Logger, csvStr2List, expandFolders


import argparse
mainLogger = Logger.getModuleLogger("job")
parser = argparse.ArgumentParser(description = '', add_help = False)
parser = argparse.ArgumentParser()

parser.add_argument('-d','--data', action='store', 
    dest='data', required = True, nargs='+',
    help = "The input tuning files.")



import sys,os
if len(sys.argv)==1:
  parser.print_help()
  sys.exit(1)
args = parser.parse_args()

# Take all files
paths = csvStr2List ( args.data )
paths = expandFolders( paths )

from RingerCore import load,save, appendToFileName
for f in paths:
  ff = load(f)
  for k in ff.keys():
    if 'SP' in k:
      etBin = ff[k]['etBinIdx']
      etaBin = ff[k]['etaBinIdx']
  print 'etBin = ', etBin, ', etaBin = ',etaBin
  outname = f.split('/')[len(f.split('/'))-2]
  cOutputName = appendToFileName( outname, ('et%d_eta%d')%(etBin,etaBin) )
  save( ff, cOutputName, compress=True )


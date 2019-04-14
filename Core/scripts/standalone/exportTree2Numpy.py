#!/usr/bin/env python

from RingerCore import csvStr2List, \
                       expandFolders, Logger, \
                       progressbar, LoggingLevel

from TuningTools.parsers import argparse, loggerParser, LoggerNamespace

mainParser = argparse.ArgumentParser(description = 'Export files pdfs into unique file.',
                                     add_help = False)
mainMergeParser = mainParser.add_argument_group( "Required arguments", "")
mainMergeParser.add_argument('-i','--inputFiles', action='store', 
    metavar='InputFiles', required = True, nargs='+',
    help = "The input files that will be used to generate a numpy file")
mainMergeParser.add_argument('-o','--outputFiles', action='store', 
    metavar='Output', required = False, nargs='+',
    help = "The corresponding output files.")
mainMergeParser.add_argument('-t','--treePath', action='store', 
    required = False, default=['CollectionTree'],
    help = "Path of the tree on the file to export.")
mainMergeParser.add_argument('-b','--branches', action='store', 
    required = False, default=None, nargs='+',
    help = "Branches in the tree to be exported")
mainMergeParser.add_argument('-c','--change-output-folder', action='store', 
    required = False, default=None,
    help = "Change output folder to be in the specified path instead using the same input dir as input file.")
mainMergeParser.add_argument('-s','--selection', action='store', 
    required = False, default=None,
    help = "Only include entries fulfilling this condition.")
mainLogger = Logger.getModuleLogger(__name__)
parser = argparse.ArgumentParser(description = 'Save files on matlab format.',
                                 parents = [mainParser, loggerParser],
                                 conflict_handler = 'resolve')

try:
  import root_numpy as rnp
except ImportError:
  raise ImportError("root_numpy is not available. Please install it following the instructions at https://rootpy.github.io/root_numpy/install.html")

import sys
if len(sys.argv)==1:
  parser.print_help()
  sys.exit(1)

## Retrieve parser args:
args = parser.parse_args( namespace = LoggerNamespace() )
mainLogger.setLevel( args.output_level )
if mainLogger.isEnabledFor( LoggingLevel.DEBUG ):
  from pprint import pprint
  pprint(args.inputFiles)

import ROOT, numpy as np

## Treat special arguments
if len( args.inputFiles ) == 1:
  args.inputFiles = csvStr2List( args.inputFiles[0] )
args.inputFiles = expandFolders( args.inputFiles )
mainLogger.verbose("All input files are:")
if mainLogger.isEnabledFor( LoggingLevel.VERBOSE ):
  pprint(args.inputFiles)

for idx, inFile in progressbar(enumerate(args.inputFiles), len(args.inputFiles),
                          logger = mainLogger, prefix = "Processing files "):
  # Treat output file name:
  from RingerCore import checkExtension, changeExtension, save, ensureExtension
  if checkExtension( inFile, "root" ):
    cOutputName = ensureExtension( args.outputFiles[idx] if args.outputFiles and idx < len(args.outputFiles) else changeExtension( inFile, '.npz' ), '.npz' )
    if args.change_output_folder:
      import os.path
      cOutputName = os.path.join( os.path.abspath(args.change_output_folder) , os.path.basename(cOutputName) )
    f = ROOT.TFile( inFile, 'r' )
    mainLogger.debug("Reading key: %s", args.treePath)
    tree = f.Get(args.treePath)
    if not isinstance(tree, ROOT.TTree): 
      mainLogger.error("Path %s does not contain a TTree object", args.treePath)
      continue
    shortKey = args.treePath.split('/')[-1]
    # TODO Save each numpy object key instead of the collection tree:
    data = rnp.tree2array( tree, branches=args.branches, selection=args.selection )

    toSave = { key : (data[key] if key != 'elCand2_ringer_rings' else np.concatenate( data['elCand2_ringer_rings'] ).reshape(-1,100)) for key in data.dtype.names }
    #toSave = { shortKey : rnp.tree2array( tree, branches=args.branches, selection=args.selection ) }
    savedPath = save(toSave, cOutputName, protocol = 'savez_compressed')
    mainLogger.info("Successfully created numpy file: %s", cOutputName)
  else:
    mainLogger.error("Cannot transform file '%s' to numpy format." % inFile)
# end of (for fileCollection)



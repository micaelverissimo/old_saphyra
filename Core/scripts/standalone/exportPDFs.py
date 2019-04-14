#!/usr/bin/env python

from RingerCore import ( csvStr2List, emptyArgumentsPrintHelp
                       , expandFolders, Logger
                       , progressbar, LoggingLevel, ArgumentParser)

from TuningTools.parsers import loggerParser, LoggerNamespace

mainParser = ArgumentParser(description = 'Export files pdfs into unique file.',
                                     add_help = False)
mainMergeParser = mainParser.add_argument_group( "Required arguments", "")
mainMergeParser.add_argument('-i','--inputFiles', action='store', 
    metavar='InputFiles', required = True, nargs='+',
    help = "The input files that will be used to generate a matlab file")
mainMergeParser.add_argument('-f','--filter-keys', action='store', 
    required = False, default=[''], nargs='+',
    help = "Filter histogram keys to be exported.")
mainMergeParser.add_argument('-e','--exclude-keys', action='store', 
    required = False, default=[], nargs='+',
    help = "Exclude histogram keys matching pattern.")
mainMergeParser.add_argument('-c','--change-output-folder', action='store', 
    required = False, default=None,
    help = "Change output folder to be in the specified path instead using the same input dir as input file.")
mainLogger = Logger.getModuleLogger(__name__)
parser = ArgumentParser(description = 'Save files on matlab format.',
                        parents = [mainParser, loggerParser],
                        conflict_handler = 'resolve')
parser.make_adjustments()

try:
  import root_numpy as rnp
except ImportError:
  raise ImportError("root_numpy is not available. Please install it following the instructions at https://rootpy.github.io/root_numpy/install.html")

emptyArgumentsPrintHelp( parser )

## Retrieve parser args:
args = parser.parse_args( namespace = LoggerNamespace() )
mainLogger.setLevel( args.output_level )
if mainLogger.isEnabledFor( LoggingLevel.DEBUG ):
  from pprint import pprint
  pprint(args.inputFiles)

import ROOT

def getall(d, basepath="/"):
  """
  Generator function to recurse into a ROOT file/dir and yield (path, obj) pairs
  Taken from: https://root.cern.ch/phpBB3/viewtopic.php?t=11049 
  """
  try:
    for key in d.GetListOfKeys():
      kname = key.GetName()
      if key.IsFolder():
        for i in getall(d.Get(kname), basepath+kname+"/"):
          yield i
      else:
        yield basepath+kname, d.Get(kname)
  except AttributeError, e:
    mainLogger.debug("Ignore reading object of type %s.", type(d))

## Treat special arguments
if len( args.inputFiles ) == 1:
  args.inputFiles = csvStr2List( args.inputFiles[0] )
args.inputFiles = expandFolders( args.inputFiles )
mainLogger.verbose("All input files are:")
if mainLogger.isEnabledFor( LoggingLevel.VERBOSE ):
  pprint(args.inputFiles)

for inFile in progressbar(args.inputFiles, len(args.inputFiles),
                          logger = mainLogger, prefix = "Processing files "):
  # Treat output file name:
  from RingerCore import checkExtension, changeExtension, save
  if checkExtension( inFile, "root" ):
    cOutputName = changeExtension( inFile, '.npz' )
    if args.change_output_folder:
      import os.path
      cOutputName = os.path.join( os.path.abspath(args.change_output_folder) , os.path.basename(cOutputName) )
    f = ROOT.TFile( inFile, 'r' )
    data = {}
    for keyName, obj in getall(f):
      mainLogger.debug("Reading key: %s", keyName)
      shortKey = keyName.split('/')[-1]
      if not issubclass(type(obj), ROOT.TH1): 
        mainLogger.verbose("Ignoring key: %s", shortKey )
        continue
      hist = obj
      result = [exclude in shortKey for exclude in args.exclude_keys]
      if result and all( result ):
        mainLogger.debug("key <%s> does not match any filter", shortKey )
        continue
      if result and all( result ):
        mainLogger.debug("key <%s> matches exclude pattern", shortKey )
        continue
      if not hist:
        mainLogger.warning("Couldn't retrieve histogram with key: %s", shortKey )
      data[ shortKey ] = rnp.hist2array( hist, include_overflow=True, return_edges=True )
    savedPath = save(data, cOutputName, protocol = 'savez_compressed')
    mainLogger.info("Successfully created numpy file: %s", cOutputName)
  else:
    mainLogger.error("Cannot transform file '%s' to numpy format." % inFile)
# end of (for fileCollection)



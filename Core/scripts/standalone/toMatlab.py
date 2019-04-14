#!/usr/bin/env python

from RingerCore import ( csvStr2List, emptyArgumentsPrintHelp
                       , expandFolders, Logger
                       , progressbar, LoggingLevel, BooleanStr )

from TuningTools.parsers import ArgumentParser, loggerParser, LoggerNamespace

mainParser = ArgumentParser(description = 'Merge files into unique file.',
                                     add_help = False)
mainMergeParser = mainParser.add_argument_group( "Required arguments", "")
mainMergeParser.add_argument('-i','--inputFiles', action='store', 
    metavar='InputFiles', required = True, nargs='+',
    help = "The input files that will be used to generate a matlab file")
mainMergeParser.add_argument('-c','--change-output-folder', action='store', 
    required = False, default=None,
    help = "Change output folder to be in the specified path instead using the same input dir as input file.")
mainMergeParser.add_argument('--compress', action='store',  default=True, type= BooleanStr,
                              help="Whether to compress file with scipy.savemat")
mainLogger = Logger.getModuleLogger(__name__)
parser = ArgumentParser(description = 'Save files on matlab format.',
                        parents = [mainParser, loggerParser],
                        conflict_handler = 'resolve')
parser.make_adjustments()

emptyArgumentsPrintHelp( parser )

## Retrieve parser args:
args = parser.parse_args( namespace = LoggerNamespace() )
mainLogger.setLevel( args.output_level )
if mainLogger.isEnabledFor( LoggingLevel.DEBUG ):
  from pprint import pprint
  pprint(args.inputFiles)
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
    from RingerCore import checkExtension, changeExtension, load, save
  #if checkExtension( inFile, "tgz|tar.gz|pic" ):
    cOutputName = changeExtension( inFile, '.mat' )
    if args.change_output_folder:
      import os.path
      cOutputName = os.path.join( os.path.abspath(args.change_output_folder) , os.path.basename(cOutputName) )
    data = load( inFile, useHighLevelObj = False )
    from scipy.io import savemat
    try:
      savemat( cOutputName, data, do_compression=args.compress )
    except ImportError:
      self._logger.fatal(("Cannot save matlab file, it seems that scipy is not "
          "available."), ImportError)
    mainLogger.info("Successfully created matlab file: %s", cOutputName)
  #else:
  #  mainLogger.error("Cannot transform files '%s' to matlab." % inFile)
# end of (for fileCollection)


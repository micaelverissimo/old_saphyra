#!/usr/bin/env python


from Gaugi import csvStr2List, str_to_class, NotSet, BooleanStr, emptyArgumentsPrintHelp
from Gaugi import ArgumentParser, loggerParser, LoggerNamespace
from pandas import GridJobFilter
from tableboard import tableBoardParser

parser = ArgumentParser(description = 'Retrieve performance information from the Cross-Validation method.',
                       parents = [tableBoardParser, loggerParser])
parser.make_adjustments()

emptyArgumentsPrintHelp( parser )

# Retrieve parser args:
args = parser.parse_args(namespace = LoggerNamespace() )

from RingerCore import Logger, LoggingLevel, printArgs
logger = Logger.getModuleLogger( __name__, args.output_level )

printArgs( args, logger.debug )


#Find files
from Gaugi import expandFolders, ensureExtension,keyboard
logger.info('Expand folders and filter')
paths = expandFolders(args.file)
paths = filterPaths(paths, args.grid)


from pprint import pprint
logger.info('Grid mode is: %s',args.grid)
pprint(paths)


#Loop over job grid, basically loop over user...
for jobID in paths:
  logger.info( ('Start from job tag: %s')%(jobID))
  output = args.output
  monitoring = TableBoard( paths[jobID]['pic'], 
                           paths[jobID]['root'], 
                           dataPath = args.dataPath,
                           level = args.output_level)
  monitoring(
              output       = output,
              overwrite    = True)

  del monitoring





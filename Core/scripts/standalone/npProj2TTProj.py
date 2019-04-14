#!/usr/bin/env python

from TuningTools.parsers import loggerParser, LoggerNamespace
from RingerCore import emptyArgumentsPrintHelp

parser = ArgumentParser( description = """Change data memory representation 
																											 without changing its dimensions.""",
																		  parents = [loggerParser])
parser.add_argument('inputs', action='store', 
    metavar='INPUT',  nargs='+',
    help = "Files to change representation")

emptyArgumentsPrintHelp( parser )

args = parser.parse_args( namespace = LoggerNamespace() )

from RingerCore import Logger, LoggingLevel, save, load, expandFolders, traverse
import numpy as np
from TuningTools import npCurrent, fixPPCol
npCurrent.level = args.output_level
logger = Logger.getModuleLogger( __name__, args.output_level )

files = expandFolders( args.inputs )

from zipfile import BadZipfile
from copy import deepcopy
for f in files:
  logger.info("Turning numpy matrix file '%s' into pre-processing file...", f)
  fileparts = f.split('/')
  folder = '/'.join(fileparts[0:-1]) + '/'
  fname = fileparts[-1]
  try:
    data = dict(load(f))
  except BadZipfile, e:
    logger.warning("Couldn't load file '%s'. Reason:\n%s", f, str(e))
    continue
  logger.debug("Finished loading file '%s'...", f)
  for key in data:
    if key == 'W':
      ppCol = deepcopy( data['W'] )
      from TuningTools.PreProc import *
      for obj, idx,  parent, _, _ in traverse(ppCol,
                                              tree_types = (np.ndarray,),
                                              max_depth = 3):
        parent[idx] = PreProcChain( RemoveMean(), Projection(matrix = obj), UnitaryRMS() )
      # Turn arrays into mutable objects:
      ppCol = ppCol.tolist()
      ppCol = fixPPCol( ppCol, len(ppCol[0][0]),
                               len(ppCol[0]),
                               len(ppCol))
  if fname.endswith('.npz'):
    fname = fname[:-4]
  newFilePath = folder + fname + '.pic'
  logger.info('Saving to: "%s"...', newFilePath) 
  place = PreProcArchieve( newFilePath, ppCol = ppCol ).save( compress = False )
  logger.info("File saved at path: '%s'", place)

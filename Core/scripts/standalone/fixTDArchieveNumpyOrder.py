#!/usr/bin/env python

from TuningTools.parsers import ArgumentParser, loggerParser, LoggerNamespace
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
from TuningTools.coreDef import npCurrent
npCurrent.level = args.output_level
logger = Logger.getModuleLogger( __name__, args.output_level )

files = expandFolders( args.inputs ) # FIXME *.npz

from zipfile import BadZipfile
for f in files:
  logger.info("Changing representation of file '%s'...", f)
  try:
    data = dict(load(f))
  except BadZipfile, e:
    logger.warning("Couldn't load file '%s'. Reason:\n%s", f, str(e))
    continue
  logger.debug("Finished loading file '%s'...", f)
  for key in data:
    if key == 'W':
      for obj, idx,  parent, _, _ in traverse(data[key],
                                              tree_types = (np.ndarray,),
                                              max_depth = 3):
        parent[idx] = obj.T
    elif type(data[key]) is np.ndarray:
      logger.debug("Checking key '%s'...", key)
      data[key] = npCurrent.toRepr(data[key])
  path = save(data, f, protocol = 'savez_compressed')
  logger.info("Overwritten file '%s'",f)

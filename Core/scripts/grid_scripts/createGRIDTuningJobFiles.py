#!/usr/bin/env python

from TuningTools.parsers import (ArgumentParser, outGridParser, loggerParser,
                                tuningJobFileParser, TuningToolGridNamespace)
from RingerCore import Logger, printArgs, conditionalOption, emptyArgumentsPrintHelp

outGridParser.delete_arguments('outputs')
outGridParser.suppress_arguments(grid__nJobs = 1)
tuningJobFileParser.suppress_arguments(compress = 0)
## The main parser
parser = ArgumentParser(description = 'Generate input file for TuningTool on GRID',
                        parents = [tuningJobFileParser, outGridParser, loggerParser],
                        conflict_handler = 'resolve')
parser.make_adjustments()

## Now the job really starts
emptyArgumentsPrintHelp(parser)

args = parser.parse_args( namespace = TuningToolGridNamespace('prun') )
mainLogger = Logger.getModuleLogger( __name__, args.output_level )

# Retrieve outputs containers
outputs = []
if any(val in args.fileType for val in ("all","ConfigFiles")):
  outputs.append('Config:job.*')

if any(val in args.fileType for val in ("all","CrossValidFile")):
  outputs.append('CrossValid:crossValid*')

if any(val in args.fileType for val in ("all","ppFile")):
  outputs.append('ppFile:ppFile*')
# Merge it to the grid arguments:
args.grid_outputs = '"' + ','.join(outputs) + '"'

printArgs( args, mainLogger.debug )

# Prepare to run
args.setExec(r"""source ./setrootcore.sh; 
               {gridCreateTuningFiles}
                 {fileType}
                 --jobConfiFilesOutputFolder=\".\"
                 --neuronBounds {neuronBounds}
                 --sortBounds {sortBounds}
                 --nInits={nInits}
                 --nNeuronsPerJob={nNeuronsPerJob}
                 --nSortsPerJob={nSortsPerJob}
                 --nInitsPerJob={nInitsPerJob}
                 --crossValidOutputFile="crossValid"
                 --nSorts={nSorts}
                 --nBoxes={nBoxes}
                 --nTrain={nTrain}
                 --nValid={nValid}
                 --nTest={nTest}
                 --preProcOutputFile=\"ppFile\"
                 --compress={compress}
                 -ppCol=\"{ppCol}\"
             """.format( gridCreateTuningFiles = "\$ROOTCOREBIN/user_scripts/TuningTools/standalone/createTuningJobFiles.py",
                         fileType=' '.join(args.fileType),
                         neuronBounds=' '.join([str(i) for i in args.neuronBounds]),
                         sortBounds=' '.join([str(i) for i in args.sortBounds]),
                         nInits=args.nInits,
                         nNeuronsPerJob=args.nNeuronsPerJob,
                         nSortsPerJob=args.nSortsPerJob,
                         nInitsPerJob=args.nInitsPerJob,
                         nSorts=args.nSorts,
                         nBoxes=args.nBoxes,
                         nTrain=args.nTrain,
                         nValid=args.nValid,
                         nTest=args.nTest,
                         ppCol=args.ppCol,
                         compress=args.compress,
                       ) 
            )

# And run
args.run_cmd()


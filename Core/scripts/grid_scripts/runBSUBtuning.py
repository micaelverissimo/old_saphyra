#!/usr/bin/env python

from TuningTools.parsers import argparse, ArgumentParser

from RingerCore import emptyArgumentsPrintHelp

parser = ArgumentParser(description = 'Run training job on grid')
parser.add_argument('-d','--data', action='store', 
    required = True,
    help = "The file containing data for discriminator tunning")
parser.add_argument('-o','--output', action='store', 
    required = True,
    help = "The output base string for the discriminator file.")
parser.add_argument('-op','--outputPlace', action='store', 
    required = True,
    help = "The output place to a lxplus tmp.")
parser.add_argument('-i','--inputConfig',
    metavar='InputFolder', 
    help = "Folder to loop upon files to retrieve configuration.")
parser.add_argument('--ppFile',  default = None, help = "Pre-processing file.")
parser.add_argument('--crossValidFile', default = None, help = "Cross-validation file.")
parser.add_argument('--debug',  
    action='store_true',
    help = "Set queue to 1nh, and run for 3 files only.")
parser.add_argument('--local',  
    action='store_true',
    help = "For developing purproses only.")
parser.add_argument('--queue', 
    default='1nw',  
    help = "Choose queue if debug is not set.")
parser.add_argument('--pause', 
    default=5, type=int,
    help = "Time to wait between each submission.")

emptyArgumentsPrintHelp( parser )

# Retrieve parser args:
args = parser.parse_args()

if args.debug:
  limitFiles = 3
else:
  limitFiles = None

from RingerCore import printArgs, conditionalOption, Logger
logger = Logger.getModuleLogger(__name__)
printArgs( args, logger.info )

import os
#os.system('rcSetup -u')
inputConfig = os.path.abspath(args.inputConfig)
if os.path.isdir(inputConfig):
  files = [ os.path.join(inputConfig,f) for f in os.listdir(inputConfig) if os.path.isfile(os.path.join(inputConfig,f)) ]
elif os.path.isfile(inputConfig):
  files = [ inputConfig ]
else:
  raise RuntimeError("Unexpected inputConfig: %s" % inputConfig)

for n, f in enumerate(files):
  if limitFiles and n == limitFiles:
    break
  exec_str = """\
        env -i {bsub} \\
          {bsub_script} \\ 
            --jobConfig {jobFile} \\
            {ppFile} \\
            {crossValidFile} \\
            --datasetPlace {data} \\
            --output {output} \\
            --outputPlace {outputPlace}
      """.format(bsub = "bsub -q {queue} -u \"\" -J pyTrain -n 8 -R \"span[ptile=8]\"".format(queue = args.queue) if not args.local \
                   else "",
                 bsub_script = os.path.expandvars("$ROOTCOREBIN/user_scripts/TuningTools/run_on_grid/bsub_script.sh"),
                 data = args.data,
                 jobFile = f,
                 ppFile = conditionalOption('--ppFile', args.ppFile),
                 crossValidFile = conditionalOption('--crossValidFile', args.crossValidFile),
                 output = args.output,
                 outputPlace = args.outputPlace,
                 )
  logger.info("Executing following command:\n%s", exec_str)
  import re
  exec_str = re.sub(' +',' ',exec_str)
  exec_str = re.sub('\\\\','',exec_str) # FIXME We should be abble to do this only in one line...
  exec_str = re.sub('\n','',exec_str)
  #logger.info("Command without spaces:\n%s", exec_str)
  os.system(exec_str)
  import time
  time.sleep(args.pause)


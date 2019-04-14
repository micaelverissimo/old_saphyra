#!/usr/bin/env python

import time

from TuningTools.parsers import argparse, ArgumentParser

from RingerCore import emptyArgumentsPrintHelp

parser = ArgumentParser(description = 'Retry failed jobs on bsub')
parser.add_argument('-l','--logFile', action='store', required = True,
    help = "The log file containing the commands submitted.")
parser.add_argument('-perm-op','--permanentOutputPlace', action='store', required = True,
    help = "The permanent output place where the tuned classifiers should be found.")
parser.add_argument('--queue', default=None,  
    help = "Change queue if defined.")
parser.add_argument('--pause', default=5, type=int,
    help = "Time to wait between each submission.")
parser.add_argument('--checkForMissingJobs',  action='store_true',
    help = "Check if there are any missing job, and submit it.")
parser.add_argument('--overrideOutputPlace',  default = None,
    help = "If the job is submitted by another user, then it is needed to override the output place.")
parser.add_argument('-i','--inputFolder',  default = None, metavar='InputFolder', 
    help = "Folder to loop upon files to retrieve configuration (only needed if using checkForMissingJobs is set.")
parser.add_argument('-b','--bsubJobsQueue',  default = None, metavar='JOBS-QUEUE', 
    help = "Jobs from --logFile which pending or running on bsub and shouldn't be searched for the output file.")

emptyArgumentsPrintHelp( parser )

# Retrieve parser args:
args = parser.parse_args()

from RingerCore import printArgs, Logger
logger = Logger.getModuleLogger(__name__)
printArgs( args, logger.info )

if args.checkForMissingJobs and not args.inputFolder:
  logger.fatal("--checkForMissingJobs is set, please specify --inputFolder.")

import os
#os.system('rcSetup -u')
oPlace = os.path.abspath(args.permanentOutputPlace)
ofiles = [ os.path.join(oPlace,f) for f in os.listdir(oPlace) if os.path.isfile(os.path.join(oPlace,f)) ]

import re
executeLine = re.compile('.*Executing following command:')
submissionLine = re.compile('(\s+env -i bsub -q )(\S*)( -u "" -J .+\\\\)')
commandLine = re.compile('\s+\S+\s+\\\\')
jobLine = re.compile('\s+--jobConfig\s+(\S+.n(\d+).sl(\d+).su(\d+).il(\d+).iu(\d+).pic)\s+\\\\')
dataPlaceLine = re.compile('\s+--datasetPlace\s+(\S+)\s+\\\\')
outputLine = re.compile('\s+--output\s+(\S+)\s+\\\\')
outputPlaceLine = re.compile('(\s+--outputPlace\s+)(\S+)(\s+)')
jobSubmittedLine = re.compile('Job <(\d+)> is submitted to queue <\S+>.')

# Parser pending jobs files:
pendingJobs = []
bsubPendingLine = re.compile('(\d+)((?:\s+\S+){8,9})')
if args.bsubJobsQueue:
  with open(args.bsubJobsQueue, "r") as f:
    while True:
      line = f.readline()
      if not line:
        break
      m = bsubPendingLine.match(line)
      if m:
        pendingJobs.append(int(m.group(1)))
else:
  import subprocess
  try:
    output = subprocess.check_output("bjobs",stderr=subprocess.STDOUT,shell=True).split('\n')
    for line in output:
      m = bsubPendingLine.match(line)
      if m:
        pendingJobs.append(int(m.group(1)))
    print pendingJobs
  except subprocess.CalledProcessError,e:
    logger.warning("Couldn't retrieve running jobs, reason: %s", e)

def repl_queue(m): # This could be changed to a string with "'\1%s\3' % args.queue", which would be quite better to understand
  return m.group(1) + args.queue + m.group(3)

def repl_outputPlace(m):
  return m.group(1) + args.overrideOutputPlace + m.group(3)

submittedJobFiles = []
nJobsFailure = 0
# Parse log file:
with open(args.logFile, "r") as f:
  while True:
    line = f.readline()
    if not line:
      break
    if executeLine.match(line):
      cmd = []
      line = f.readline()

      # Check submission line:
      m = submissionLine.match(line)
      if m:
        if args.queue:
          line = submissionLine.sub(repl_queue,line)
        cmd.append(line)
      else:
        raise RuntimeError("It was expected to retrieve SubmissionLine, but no match found for \"%s\"" % line)

      # Check commandLine:
      line = f.readline()
      m = commandLine.match(line)
      if m:
        cmd.append(os.path.expandvars("          $ROOTCOREBIN/user_scripts/TuningTools/run_on_grid/bsub_script.sh \\\n"))
      else:
        raise RuntimeError("It was expected to retrieve CommandLine, but no match found for \"%s\"" % line)

      # Check jobLine:
      line = f.readline()
      m = jobLine.match(line)
      if m:
        # Append file to submited jobs:
        submittedJobFiles.append( m.group(1) )
        # From jobLine retrieve configurations:
        neurons = int(m.group(2))
        sl = int(m.group(3))
        su = int(m.group(4))
        il = int(m.group(5))
        iu = int(m.group(6))
        cmd.append(line)
      else:
        raise RuntimeError("It was expected to retrieve jobLine, but no match found for \"%s\"" % line)

      # Check dataPlaceLine:
      line = f.readline()
      m = dataPlaceLine.match(line)
      if m:
        data=m.group(1) 
        cmd.append(line)
      else:
        raise RuntimeError("It was expected to retrieve dataPlaceLine, but no match found for \"%s\"" % line)

      # Check for outputLine:
      line = f.readline()
      m = outputLine.match(line)
      if m:
        baseOutputFile=m.group(1)
        cmd.append(line)
      else:
        raise RuntimeError("It was expected to retrieve outputLine, but no match found for \"%s\"" % line)

      # Check for outputPlaceLine:
      line = f.readline()
      m = outputPlaceLine.match(line)
      if m:
        outputPlace = m.group(2)
        if args.overrideOutputPlace:
          line = outputPlaceLine.sub(repl_outputPlace,line)
        cmd.append(line)
      else:
        raise RuntimeError("It was expected to retrieve outputPlaceLine, but no match found for \"%s\"" % line)

      # Check for submitted job:
      f.readline()
      line = f.readline()
      m = jobSubmittedLine.match(line)
      if m:
        jobNumber = int(m.group(1))
        if jobNumber in pendingJobs:
          logger.info("Job %d is pending, will not search its output.", jobNumber)
          pendingJobs.remove(jobNumber)
          continue
      else:
        m = re.match('Request aborted by esub. Job not submitted.', line)
        if not m:
          raise RuntimeError("It was expected to retrieve jobSubmittedLine, but no match found for \"%s\"" % line)

      # Parsed command correctly, now check if the output was retrieven on permanentOutputPlace
      for sort in range( sl, su+1 ):
        searchFile='%s.n%04d.s%04d.id%04d.iu%04d.pic' % ( baseOutputFile, neurons, sort, il, iu )
        #logger.info('Searching for file %s', searchFile)
        for ofile in ofiles:
          if re.match( searchFile, os.path.basename(ofile) ):
            #logger.info("File found.")
            # Remove file from check list (we don't execute same job twice):
            ofiles.remove(ofile)
            break
        else:
          logger.info("Executing following command:\n%s",''.join(cmd))
          cmd = ''.join(cmd)
          cmd = re.sub(' +',' ',cmd)
          cmd = re.sub('\\\\|\n','',cmd)
          os.system(cmd)
          time.sleep(args.pause)
          nJobsFailure += 1
          break
    # end of while

if len(ofiles) != 0:
  logger.warning("Those files were not found to be submitted by any job (maybe the pending jobs is not updated):\n%r", ofiles)

if args.checkForMissingJobs:
  # Submit files which were not already submitted:
  iPlace = os.path.abspath(args.inputFolder)
  ifiles = [ os.path.join(iPlace,f) for f in os.listdir(iPlace) if os.path.isfile(os.path.join(iPlace,f)) ]
  missingJobs = 0
  for f in ifiles:
    if not f in submittedJobFiles:
      exec_str = """\
            env -i {bsub} \\
              {bsub_script} \\ 
                --jobConfig {jobFile} \\
                --datasetPlace {data} \\
                --output {output} \\
                --outputPlace {outputPlace}
          """.format(bsub = "bsub -q {queue} -u \"\" -J pyTrain".format(queue = args.queue),
                     bsub_script = os.path.expandvars("$ROOTCOREBIN/user_scripts/TuningTools/run_on_grid/bsub_script.sh"),
                     data = data,
                     jobFile = f,
                     output = baseOutputFile,
                     outputPlace = args.overrideOutputPlace if args.overrideOutputPlace else outputPlace,
                     )
      logger.info("Executing following command:\n%s", exec_str)
      import re
      exec_str = re.sub(' +',' ',exec_str)
      exec_str = re.sub('\\\\|\n','',exec_str)
      #logger.info("Command without spaces:\n%s", exec_str)
      os.system(exec_str)
      time.sleep(args.pause)
      missingJobs += 1
  logger.info('Submitted a total of %d missing jobs', missingJobs)

logger.info("Retried a total of %d jobs which failed.", nJobsFailure)


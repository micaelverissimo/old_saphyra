#!/usr/bin/env python


from RingerCore                            import LoggingLevel, Logger, csvStr2List, expandFolders


import argparse
mainLogger = Logger.getModuleLogger("job")
parser = argparse.ArgumentParser(description = '', add_help = False)
parser = argparse.ArgumentParser()

parser.add_argument('-d','--data', action='store', 
    dest='data', required = True,
    help = "The input tuning files.")

parser.add_argument('-c','--command', action='store', 
    dest='command', required = True,
    help = "The command job")

parser.add_argument('-n','--maxJobs', action='store', 
    dest='maxJobs', required = False, default = 10,
    help = "The number of jobs inside of the pipe.")



import sys,os
if len(sys.argv)==1:
  parser.print_help()
  sys.exit(1)
args = parser.parse_args()

# Take all files
paths = csvStr2List ( args.data )
paths = expandFolders( paths )

#from TuningTools import MixedJobBinnedFilter
#filter = MixedJobBinnedFilter()
#jobIDs = filter(paths)
#mainLogger.info('Found a total of (%d) jobs: [%s]', len(jobIDs), ', '.join(map(str,jobIDs) ))

#sys.exit(1)
process_pipe = []

import subprocess
from pprint import pprint

while len(paths) > 0:
  if len(process_pipe) < int(args.maxJobs):
    job_id = len(paths)
    tag = paths.pop()
    command = args.command
    #command += (' -d %s --binFilters %s') % (args.data, tag)
    command += (' -d %s') % (tag)
    mainLogger.info( ('adding process into the stack with id %d')%(job_id), extra={'color':'0;35'})
    pprint(command)
    print command.split(' ')
    proc = subprocess.Popen(command.split(' '))
    #thread = Thread(group=None, target=lambda:os.system(command))
    #thread.run()
    process_pipe.append( (job_id, proc) )

  for proc in process_pipe:
    if not proc[1].poll() is None:
      mainLogger.info( ('pop process id (%d) from the stack')%(proc[0]), extra={'color':'0;35'})
      # remove proc from the pipe
      process_pipe.remove(proc)


# Check pipe process
# Protection for the last jobs
while len(process_pipe)>0:
  for proc in process_pipe:
    if not proc[1].poll() is None:
      mainLogger.info( ('pop process id (%d) from the stack')%(proc[0]), extra={'color':'0;35'})
      # remove proc from the pipe
      process_pipe.remove(proc)



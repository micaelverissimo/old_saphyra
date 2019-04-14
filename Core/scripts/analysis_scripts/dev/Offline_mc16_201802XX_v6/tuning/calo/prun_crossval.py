




cmd = """\
crossValStatAnalysis.py -d /home/jodafons/Public/ringer/root/TuningTools/scripts/analysis_scripts/Offline_mc16_201802XX_v6/data/tuning/user.jodafons.nn.mc16a.zee.20M.jf17.20M.offline.binned.calo.wdatadrivenlh.v6.t0002_td -r /home/jodafons/Public/ringer/root/TuningTools/scripts/analysis_scripts/Offline_mc16_201802XX_v6/data/files/mc16calo_lhgrid_v3/mc16a.zee.20M.jf17.20M.offline.binned.calo.wdatadrivenlh_eff.npz --operation Offline_LH_DataDriven2016_Rel21_Medium --crossFile /home/jodafons/Public/ringer/root/TuningTools/scripts/analysis_scripts/Offline_mc16_201802XX_v6/data/files/user.jodafons.crossValid.10sorts.pic.gz/crossValid.10sorts.pic.gz --doMatlab 1 --doMonitoring 1 --always-use-SP-network --pile-up-ref nvtx --expandOP --data /home/jodafons/Public/ringer/root/TuningTools/scripts/analysis_scripts/Offline_mc16_201802XX_v6/data/files/mc16calo_lhgrid_v3/mc16a.zee.20M.jf17.20M.offline.binned.calo.wdatadrivenlh.npz --binFilters {JOBID}\
"""

#cmd = """\
#crossValStatAnalysis.py -d ../data/tuning/user.jodafons.nn.mc16a.zee.20M.jf17.20M.offline.binned.calo.wdatadrivenlh.v6.t0002_td -r ../data/files/mc16calo_lhgrid_v3/mc16a.zee.20M.jf17.20M.offline.binned.calo.wdatadrivenlh_eff.npz --operation Offline_CutBased_Medium --crossFile ../data/files/user.jodafons.crossValid.10sorts.pic.gz/crossValid.10sorts.pic.gz --doMatlab 1 --doMonitoring 1 --always-use-SP-network --expandOP --binFilters {JOBID}"""
          

#!/usr/bin/env python


from TuningTools.dataframe.EnumCollection  import Dataframe as DataframeEnum
from RingerCore                            import LoggingLevel, Logger, csvStr2List, expandFolders


import argparse
mainLogger = Logger.getModuleLogger("job")
parser = argparse.ArgumentParser(description = '', add_help = False)
parser = argparse.ArgumentParser()

parser.add_argument('-i','--inputFiles', action='store', 
    dest='fList', required = True, nargs='+',
    help = "The input files.")

parser.add_argument('-n','--maxJobs', action='store', 
    dest='maxJobs', required = False, default = 3,
    help = "The number of jobs inside of the pipe.")

parser.add_argument('-c','--cores', action='store', 
    dest='cores', required = False, default = 4,
    help = "The number of cores processor per job")



import sys,os
if len(sys.argv)==1:
  parser.print_help()
  sys.exit(1)
args = parser.parse_args()

defaultCore = os.environ["OMP_NUM_THREADS"] 
os.environ["OMP_NUM_THREADS"]  = args.cores


# Take all files
fList = csvStr2List ( args.fList )
fList = expandFolders( fList )

from TuningTools import GridJobFilter
gridJobFilter = GridJobFilter()
fList = gridJobFilter( fList )


process_pipe = []
output_stack = []
import subprocess
from pprint import pprint

while len(fList) > 0:

  if len(process_pipe) < int(args.maxJobs):
    job_id = len(fList)
    f = fList.pop()
    mainLogger.info( ('adding process into the stack with id %d')%(job_id), extra={'color':'0;35'})
    command = cmd.format(JOBID=f)
    pprint(command)
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



os.environ["OMP_NUM_THREADS"]  = defaultCore

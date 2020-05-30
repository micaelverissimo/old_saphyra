#!/usr/bin/env python

import os, sys, subprocess as sp, time, re
from panda import GridNamespace


from panda import SecondaryDatasetCollection, SecondaryDataset, GridOutputCollection, \
                   GridOutput, clusterManagerParser, ClusterManager, clusterManagerConf


from Gaugi import ( printArgs, NotSet, conditionalOption, Holder, MatlabLoopingBounds, Logger, LoggingLevel
                    , emptyArgumentsPrintHelp, argparse, getFiles, progressbar, BooleanStr,appendToFileName )

preInitLogger = Logger.getModuleLogger( __name__ )

# This parser is dedicated to have the specific options which should be added
# to the parent parsers for this job
from Gaugi.parsers import loggerParser, ArgumentParser
parentParser = ArgumentParser(add_help = True)


parentReqParser = parentParser.add_argument_group("required arguments", '')

#parentReqParser.add_argument('-pp','--ppFileDS', metavar='PP_DS', required = True, action='store',
#                             help = """The pre-processing files container.""")

#parentReqParser.add_argument('-x','--crossValidDS', metavar='CrossValid_DS', required = True, action='store',
#                             help = """The cross-validation files container.""")

#parentReqParser.add_argument('-m','--modelDS', required = True, metavar='MODEL', action='store',
#                             help = "The dataset model file to be used in the tuning process.")

parentReqParser.add_argument('-d','--dataDS', required = True, metavar='DATA', action='store',
                             help = "The dataset with the data for discriminator tuning.")

parentReqParser.add_argument('-c','--configFileDS', metavar='Config_DS', required = True, action='store', dest = 'grid__inDS',
                             help = """Input dataset to loop upon files to retrieve configuration. There
                                       will be one job for each file on this container.""")

parentReqParser.add_argument('-r','--refDS', required = True, metavar='REF', action='store',
                             help = "The ref file to be used in the tuning process.")

parentReqParser.add_argument('-j','--jobPath', required = True, metavar='JOB_PATH', action='store',
                             help = "The path to the job (python script file).")


parentReqParser.add_argument('--db_url', requered=False, metavar='db_url', action='store', default=None,
                            help = "DB url" )







from panda import ioGridParser, GridOutputCollection, GridOutput
# Suppress/delete the following options in the grid parser:
ioGridParser.delete_arguments('grid__inDS', 'grid__nJobs')
ioGridParser.suppress_arguments( grid__mergeOutput          = False # We disabled it since late 2017, where GRID
    # added a limited to the total memory and processing time for merging jobs.
                               , grid_CSV__outputs          = GridOutputCollection( [ GridOutput('td','tunedDiscr.pic.gz'),
                                                                                      #GridOutput('plog', 'pilotlog.txt')
                                                                                      ] )
                               #, grid_CSV__outputs          = GridOutputCollection( [  ] )
                               , grid__nFiles               = None
                               , grid__nFilesPerJob         = 1
                               , grid__forceStaged          = True
                               , grid__forceStagedSecondary = True
                               #, grid__nCore                = None
                               , grid__noBuild              = True
                               )




from argparse import SUPPRESS
clusterParser = ioGridParser
namespaceObj = GridNamespace('prun')



## We finally create the main parser
parser = ArgumentParser(description = 'Tune discriminators using input data on the GRID', add_help=True,
                        parents = [parentParser, clusterParser, loggerParser],
                        conflict_handler = 'resolve')
parser.make_adjustments()
emptyArgumentsPrintHelp(parser)


# Retrieve parser args:
args = parser.parse_args( namespace = namespaceObj )
mainLogger = Logger.getModuleLogger( __name__, args.output_level )
mainLogger.write = mainLogger.info
printArgs( args, mainLogger.debug )



args.set_job_submission_option('inTarBall', args.get_job_submission_option('outTarBall') )
args.set_job_submission_option('outTarBall', None )
args.append_to_job_submission_option( 'secondaryDSs'
                                      , SecondaryDatasetCollection (
                                        [
                                          #SecondaryDataset( key = "PP"      , nFilesPerJob = 1, container = args.ppFileDS     , reusable = True) ,
                                          #SecondaryDataset( key = "CROSSVAL", nFilesPerJob = 1, container = args.crossValidDS , reusable = True) ,
                                          #SecondaryDataset( key = "MODEL"   , nFilesPerJob = 1, container = args.modelDS      , reusable = True) ,
                                          SecondaryDataset( key = "REF"    , nFilesPerJob = 1, container = args.refDS        , reusable = True) ,
                                          SecondaryDataset( key = "DATA"   , nFilesPerJob = 1, container = args.dataDS       , reusable = True) ,
                                        ] 
                                        )
                                      )

# Use db
if args.db_url:

  # Get the list of files from rucio
  from panda import get_list_of_files_from_rucio
  files = get_list_if_files_from_rucio( args.Config_DS )
  print("Set %d jobs into the task %s" % (len(files), args.output_DS))

  from ringerdb import DBContext
  db = DBContext( args.db_url, 'jodafons' )
  task = db.createTask( args.output_DS, cluster='cern', status='registered', etBinIdx=args.etBinIdx, etaBinIdx=args.etaBinIdx)

  # Create the task





from panda import SecondaryDataset, SecondaryDatasetCollection

args.setExec("""sh -c '. /setup_envs.sh && python {JOB_PATH} -o tunedDiscr -d %DATA -c %IN -r %REF'""".format(JOB_PATH=args.jobPath)  )
# And run
args.run()



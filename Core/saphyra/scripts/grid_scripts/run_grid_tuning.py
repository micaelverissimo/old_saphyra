#!/usr/bin/env python

import os, sys, subprocess as sp, time, re
from pandas import GridNamespace


from pandas import SecondaryDatasetCollection, SecondaryDataset, GridOutputCollection, \
                   GridOutput, clusterManagerParser, ClusterManager, clusterManagerConf


from Gaugi import ( printArgs, NotSet, conditionalOption, Holder, MatlabLoopingBounds, Logger, LoggingLevel
                    , emptyArgumentsPrintHelp, argparse, getFiles, progressbar, BooleanStr,appendToFileName )

preInitLogger = Logger.getModuleLogger( __name__ )

# This parser is dedicated to have the specific options which should be added
# to the parent parsers for this job
from Gaugi.parsers import loggerParser, ArgumentParser
parentParser = ArgumentParser(add_help = True)


parentReqParser = parentParser.add_argument_group("required arguments", '')


parentReqParser.add_argument('-pp','--ppFileDS', metavar='PP_DS', required = True, action='store',
                             help = """The pre-processing files container.""")

parentReqParser.add_argument('-x','--crossValidDS', metavar='CrossValid_DS', required = True, action='store',
                             help = """The cross-validation files container.""")

parentReqParser.add_argument('-d','--dataDS', required = True, metavar='DATA', action='store',
                             help = "The dataset with the data for discriminator tuning.")

parentReqParser.add_argument('-c','--configFileDS', metavar='Config_DS', required = True, action='store', dest = 'grid__inDS',
                             help = """Input dataset to loop upon files to retrieve configuration. There
                                       will be one job for each file on this container.""")

parentReqParser.add_argument('-m','--modelDS', required = True, metavar='MODEL', action='store',
                             help = "The dataset model file to be used in the tuning process.")




from pandas import ioGridParser, GridOutputCollection, GridOutput
# Suppress/delete the following options in the grid parser:
ioGridParser.delete_arguments('grid__inDS', 'grid__nJobs')
ioGridParser.suppress_arguments( grid__mergeOutput          = False # We disabled it since late 2017, where GRID
    # added a limited to the total memory and processing time for merging jobs.
                               , grid_CSV__outputs          = GridOutputCollection( [ GridOutput('td','tunedDiscr*') ] )
                               #, grid_CSV__outputs          = GridOutputCollection( [  ] )
                               , grid__nFiles               = None
                               , grid__nFilesPerJob         = 1
                               , grid__forceStaged          = True
                               , grid__forceStagedSecondary = True
                               , grid__nCore                = None
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
                                          SecondaryDataset( key = "PP"      , nFilesPerJob = 1, container = args.ppFileDS     , reusable = True) ,
                                          SecondaryDataset( key = "CROSSVAL", nFilesPerJob = 1, container = args.crossValidDS , reusable = True) ,
                                          SecondaryDataset( key = "MODEL"   , nFilesPerJob = 1, container = args.modelDS      , reusable = True) ,
                                          SecondaryDataset( key = "DATA"    , nFilesPerJob = 1, container = args.dataDS       , reusable = True) ,
                                        ] 
                                        )
                                      )




from pandas import SecondaryDataset, SecondaryDatasetCollection


args.setExec("""sh -c 'python /home/atlas/saphyra/saphyra/scripts/standalone/job_tuning.py -o tunedDiscr -x %CROSSVAL -d %DATA -m %MODEL -pp %PP -i %IN"""  )

# And run
args.run()



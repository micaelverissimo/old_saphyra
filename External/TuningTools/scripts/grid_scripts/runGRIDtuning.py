#!/usr/bin/env python

import os, sys, subprocess as sp, time, re

from TuningTools import coreConf, TuningToolCores, tuningJobParser
from pandas import TuningToolGridNamespace


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

from TuningTools import tuningJobParser
# Suppress/delete the following options in the main-job parser:
tuningJobParser.delete_arguments( 'outputFileBase', 'data', 'crossFile', 'confFileList'
                                , 'neuronBounds', 'sortBounds', 'initBounds', 'ppFile'
                                , 'refFile', 'outputDir', 'crossValidShuffle', 'expert_networks')
tuningJobParser.suppress_arguments(compress = 'False')

from pandas import ioGridParser, GridOutputCollection, GridOutput
# Suppress/delete the following options in the grid parser:
ioGridParser.delete_arguments('grid__inDS', 'grid__nJobs')
ioGridParser.suppress_arguments( grid__mergeOutput          = False # We disabled it since late 2017, where GRID
    # added a limited to the total memory and processing time for merging jobs.
                               , grid_CSV__outputs          = GridOutputCollection( [ GridOutput('td','tunedDiscr*.pic') ] )
                               #, grid_CSV__outputs          = GridOutputCollection( [  ] )
                               , grid__nFiles               = None
                               , grid__nFilesPerJob         = 1
                               , grid__forceStaged          = True
                               , grid__forceStagedSecondary = True
                               , grid__nCore                = None
                               , grid__noBuild              = True
                               )


## Create dedicated arguments for the panda job:
# WARNING: Groups can be used to replace conflicting options -o/-d and so on
parentReqParser.add_argument('-d','--dataDS', required = True, metavar='DATA',
    action='store', nargs='+',
    help = "The dataset with the data for discriminator tuning.")

parentReqParser.add_argument('-r','--refDS', required = False, metavar='REF',
    action='store', nargs='+', default = None,
    help = "The reference values used to tuning all discriminators.")

parentLoopParser = parentParser.add_argument_group("Looping configuration", '')

parentLoopParser.add_argument('-c','--configFileDS', metavar='Config_DS',
    required = True, action='store', nargs='+', dest = 'grid__inDS',
    help = """Input dataset to loop upon files to retrieve configuration. There
              will be one job for each file on this container.""")

parentPPParser = parentParser.add_argument_group("Pre-processing configuration", '')

parentPPParser.add_argument('-pp','--ppFileDS',
    metavar='PP_DS', required = True, action='store', nargs='+',
    help = """The pre-processing files container.""")

parentCrossParser = parentParser.add_argument_group("Cross-validation configuration", '')

parentCrossParser.add_argument('-x','--crossValidDS',
    metavar='CrossValid_DS', required = True, action='store', nargs='+',
    help = """The cross-validation files container.""")

parentCrossParser.add_argument('-xs','--subsetDS', default = None,
    metavar='subsetDS', required = False, action='store', nargs='+',
    help = """The cross-validation subset file container.""")


miscParser = parentParser.add_argument_group("Misc configuration", '')

miscParser.add_argument('--multi-files', type=BooleanStr,
    help= """Use this option if your input dataDS was split into one file per bin.""")

miscParser.add_argument('--expert-networks',  nargs='+',required = False,
    help= """The Cross-Valid summary data file with the expert networks.""")

from argparse import SUPPRESS
miscParser.add_argument('--expert-paths',  nargs='+',required = False,
    help= SUPPRESS)

clusterParser = ioGridParser
namespaceObj = TuningToolGridNamespace('prun')



parentBinningParser = parentParser.add_argument_group("Binning configuration", '')

parentBinningParser.add_argument('--et-bins', nargs='+', default = NotSet, type = int,
        help = """The et bins to use within this job.
            When not specified, all bins available on the file will be tuned
            in a single job in the GRID, otherwise each bin available is
            submited separately.
            If specified as a integer or float, it is assumed that the user
            wants to run a single job using only for the specified bin index.
            In case a list is specified, it is transformed into a
            MatlabLoopingBounds, read its documentation on:
              http://nbviewer.jupyter.org/github/wsfreund/RingerCore/blob/master/readme.ipynb#LoopingBounds
            for more details.
        """)

parentBinningParser.add_argument('--eta-bins', nargs='+', default = NotSet, type = int,
        help = """ The eta bins to use within grid job. Check et-bins
            help for more information.  """)


## We finally create the main parser
parser = ArgumentParser(description = 'Tune discriminators using input data on the GRID', add_help=True,
                        parents = [tuningJobParser, parentParser, clusterParser, loggerParser],
                        conflict_handler = 'resolve')


parser.make_adjustments()
emptyArgumentsPrintHelp(parser)


# Retrieve parser args:
args = parser.parse_args( namespace = namespaceObj )

mainLogger = Logger.getModuleLogger( __name__, args.output_level )
mainLogger.write = mainLogger.info
printArgs( args, mainLogger.debug )



if args.expert_paths:
  mainLogger.warning("--expert-paths option is deprecated, use --expert-networks instead.")
  args.expert_networks = args.expert_paths


def getBinIdxLimits(fileDescr):
  from rucio.client import DIDClient
  didClient = DIDClient()
  scope, dataset = extract_scope(fileDescr)
  gen = didClient.list_dids(scope, {'name': appendToFileName(dataset, '*') })
  reEtaEt = re.compile(r'.*_et(\d+)_eta(\d+)')
  nEtaBins = -1
  nEtBins = -1
  for ds in gen:
    m = reEtaEt.match(ds)
    if m:
      nEtBins = max(nEtBins, int(m.group(1)))
      nEtaBins = max(nEtaBins, int(m.group(2)))
  if nEtaBins == -1 or nEtBins == -1:
    mainLogger.fatal("Couldn't automatically retrieve et/eta bins using rucio, have you uploaded fileJuicer output files?", RuntimeError)
  return [0, nEtBins], [0, nEtaBins]


if args.eta_bins is NotSet:
  if args.multi_files:
    _, args.eta_bins = getBinIdxLimits(args.dataDS[0])
  else:
    mainLogger.fatal( "Currently runGRIDtuning cannot automatically retrieve eta bins when not using multi-files.", NotImplementedError)

if args.et_bins is NotSet:
  if args.multi_files:
    args.et_bins, _ = getBinIdxLimits(args.dataDS[0])
  else:
    mainLogger.fatal( "Currently runGRIDtuning cannot automatically retrieve et bins when not using multi-files.", NotImplementedError)

setrootcore = 'source ./setrootcore.sh'


dataStr, configStr, ppStr, crossFileStr, expertNetworksStr = '', '%IN', '%PP', '%CROSSVAL', ''


for i in range(len(args.dataDS)):  dataStr += '%DATA_'+str(i)+' '

if args.expert_networks:
  for i in range(len(args.expert_networks)):  expertNetworksStr += '%EXPERTPATH_'+str(i)+' '
else:  expertNetworksStr = None

refStr = subsetStr = None

if args.get_job_submission_option('debug') is not None:
  args.set_job_submission_option('nFiles', 10)

from pandas import SecondaryDataset, SecondaryDatasetCollection

# Build secondary datasets input
dataDS_SecondaryDatasets = []
for idx, dataDS in enumerate(args.dataDS):
  dataDS = dataDS if not args.multi_files else appendToFileName(args.dataDS[idx],'_et%d_eta%d' % (args.et_bins[0], args.eta_bins[0])) # dummy et/eta
  dataDS_SecondaryDatasets.append( SecondaryDataset( key = "DATA_%d"%idx, nFilesPerJob = 1, container = dataDS, reusable=True))

# Build secondary datasets expert neural networks configurations
expertPaths_SecondaryDatasets = []
if args.expert_networks:
  for idx, expertPath in enumerate(args.expert_networks):
    expertPath = expertPath if not args.multi_files else appendToFileName(args.expert_networks[idx],'_et%d_eta%d' % (args.et_bins[0], args.eta_bins[0]))
    expertPaths_SecondaryDatasets.append( SecondaryDataset( key = "EXPERTPATH_%d"%idx, nFilesPerJob = 1, container = expertPath, reusable=True))

args.append_to_job_submission_option( 'secondaryDSs'
                                    , SecondaryDatasetCollection (
                                      dataDS_SecondaryDatasets +
                                      expertPaths_SecondaryDatasets +
                                      [
                                        SecondaryDataset( key = "PP",       nFilesPerJob = 1, container = args.ppFileDS[0],     reusable = True) ,
                                        SecondaryDataset( key = "CROSSVAL", nFilesPerJob = 1, container = args.crossValidDS[0], reusable = True) ,
                                      ] )
                                    )
if not args.refDS is None:
  args.append_to_job_submission_option( 'secondaryDSs', SecondaryDataset( key = "REF", nFilesPerJob = 1, container = args.refDS[0], reusable = True) )
  refStr = '%REF'
if not args.subsetDS is None:
  args.append_to_job_submission_option( 'secondaryDSs', SecondaryDataset( key = "SUBSET", nFilesPerJob = 1, container = args.subsetDS[0], reusable = True) )
  subsetStr = '%SUBSET'


# Binning
if args.et_bins is not None:
  if len(args.et_bins)  == 1: args.et_bins  = args.et_bins[0]
  if type(args.et_bins) in (int,float):
    args.et_bins = [args.et_bins, args.et_bins]
  args.et_bins = MatlabLoopingBounds(args.et_bins)
  args.set_job_submission_option('allowTaskDuplication', True)
else:
  args.et_bins = Holder([ args.et_bins ])

if args.eta_bins is not None:
  if len(args.eta_bins) == 1: args.eta_bins = args.eta_bins[0]
  if type(args.eta_bins) in (int,float):
    args.eta_bins = [args.eta_bins, args.eta_bins]
  args.eta_bins = MatlabLoopingBounds(args.eta_bins)
  args.set_job_submission_option('allowTaskDuplication', True)
else:
  args.eta_bins = Holder([ args.eta_bins ])


#TODO: Do something elegant here
if hasattr( args, 'outputDir' ):
  _outputDir=args.outputDir
else:
  _outputDir=""

memoryVal = args.get_job_submission_option('memory')


# Prepare to run
from itertools import product
for etBin, etaBin in progressbar( product( args.et_bins(),
                                  args.eta_bins() ),
                                  count = len(list(args.et_bins()))*len(list(args.eta_bins())) if args.et_bins() else 1,
                                  logger = mainLogger,
                                ):

  args.set_job_submission_option('memory', memoryVal )
  secondaryDSs = args.get_job_submission_option( 'secondaryDSs' )

  if args.multi_files: ###NOTE: Fix all et/eta multi file names
    for s in secondaryDSs:  s.container = re.sub(r'_et\d+_eta\d+',r'_et%d_eta%d' % (etBin, etaBin), s.container )

  args.setExec("""sh -c 'python /home/atlas/saphyra/Core/scripts/standalone/runTuning.py
                    --data {DATA}
                    --confFileList {CONFIG}
                    --ppFile {PP}
                    --crossFile {CROSS}
                    --outputFileBase tunedDiscr
                    {SUBSET}
                    {EXPERTNETWORKS}
                    {REF}
                    {OUTPUTDIR}
                    {COMPRESS}
                    {SHOW_EVO}
                    {MAX_FAIL}
                    {EPOCHS}
                    {DO_PERF}
                    {BATCH_SIZE}
                    {BATCH_METHOD}
                    {ALGORITHM_NAME}
                    {NETWORK_ARCH}
                    {COST_FUNCTION}
                    {SHUFFLE}
                    {SEED}
                    {DO_MULTI_STOP}
                    {OPERATION}
                    {ET_BINS}
                    {ETA_BINS}
                    {OUTPUT_LEVEL}
                    {CORE}'
               """.format(
                           DATA             = dataStr,
                           CONFIG           = configStr,
                           PP               = ppStr,
                           CROSS            = crossFileStr,
                           SUBSET           = conditionalOption("--clusterFile",    subsetStr           ) ,
                           EXPERTNETWORKS   = conditionalOption("--expert-networks",expertNetworksStr   ) ,
                           REF              = conditionalOption("--refFile",        refStr              ) ,
                           OUTPUTDIR        = conditionalOption("--outputDir",      _outputDir          ) ,
                           COMPRESS         = conditionalOption("--compress",       args.compress       ) ,
                           SHOW_EVO         = conditionalOption("--show-evo",       args.show_evo       ) ,
                           MAX_FAIL         = conditionalOption("--max-fail",       args.max_fail       ) ,
                           EPOCHS           = conditionalOption("--epochs",         args.epochs         ) ,
                           DO_PERF          = conditionalOption("--do-perf",        args.do_perf        ) ,
                           BATCH_SIZE       = conditionalOption("--batch-size",     args.batch_size     ) ,
                           BATCH_METHOD     = conditionalOption("--batch-method",   args.batch_method   ) ,
                           ALGORITHM_NAME   = conditionalOption("--algorithm-name", args.algorithm_name ) ,
                           NETWORK_ARCH     = conditionalOption("--network-arch",   args.network_arch   ) ,
                           COST_FUNCTION    = conditionalOption("--cost-function",  args.cost_function  ) ,
                           SHUFFLE          = conditionalOption("--shuffle",        args.shuffle        ) ,
                           SEED             = conditionalOption("--seed",           args.seed           ) ,
                           DO_MULTI_STOP    = conditionalOption("--do-multi-stop",  args.do_multi_stop  ) ,
                           OPERATION        = conditionalOption("--operation",      args.operation      ) ,
                           ET_BINS          = conditionalOption("--et-bin",         etBin               ) ,
                           ETA_BINS         = conditionalOption("--eta-bin",        etaBin              ) ,
                           OUTPUT_LEVEL     = conditionalOption("--output-level",   args.output_level   ) \
                               if LoggingLevel.retrieve( args.output_level ) is not LoggingLevel.INFO else '',
                           CORE             = conditionalOption("--core",           coreConf() ) ,
                         )
              )
  # And run
  args.run()
  # FIXME We should want something more sofisticated
  if args.get_job_submission_option('debug') is not None:
    break
# Finished submitting all bins

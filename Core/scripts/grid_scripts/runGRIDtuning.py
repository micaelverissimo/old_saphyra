#!/usr/bin/env python

import os, sys, subprocess as sp, time, re
from TuningTools.parsers import ( ArgumentParser, ioGridParser, loggerParser
                                , createDataParser, TuningToolGridNamespace
                                , tuningJobParser )
from TuningTools import coreConf, TuningToolCores, TuningToolsGit
from RingerCore import ( printArgs, NotSet, conditionalOption, Holder
                       , MatlabLoopingBounds, Logger, LoggingLevel
                       , SecondaryDatasetCollection, SecondaryDataset
                       , GridOutputCollection, GridOutput, emptyArgumentsPrintHelp
                       , clusterManagerParser, ClusterManager, argparse
                       , lsfParser, pbsParser, mkdir_p, LocalClusterNamespace
                       , BooleanOptionRetrieve, clusterManagerConf
                       , EnumStringOptionRetrieve, OptionRetrieve, SubOptionRetrieve
                       , getFiles, progressbar, ProjectGit, RingerCoreGit
                       , BooleanStr,appendToFileName, MultiThreadGridConfigure
                       , extract_scope, Development, DevParser
                       )

preInitLogger = Logger.getModuleLogger( __name__ )

def printVersion(configureObj, moduleType = 'package'):
  if not configureObj.is_clean():
    f = preInitLogger.warning
    s = 'NOT '
  else:
    f = preInitLogger.info
    s = ''
  f('%susing clean %s: %s', s, moduleType, configureObj.tag)
printVersion( ProjectGit, moduleType = 'project')
printVersion( RingerCoreGit )
printVersion( TuningToolsGit )

TuningToolsGit.ensure_clean()
RingerCoreGit.ensure_clean()

# This parser is dedicated to have the specific options which should be added
# to the parent parsers for this job
parentParser = ArgumentParser(add_help = False)
parentReqParser = parentParser.add_argument_group("required arguments", '')

if clusterManagerConf() is ClusterManager.Panda:
  # Suppress/delete the following options in the main-job parser:
  tuningJobParser.delete_arguments( 'outputFileBase', 'data', 'crossFile', 'confFileList'
                                  , 'neuronBounds', 'sortBounds', 'initBounds', 'ppFile'
                                  , 'refFile', 'outputDir', 'crossValidShuffle', 'expert_networks')
  tuningJobParser.suppress_arguments(compress = 'False')

  # Suppress/delete the following options in the grid parser:
  ioGridParser.delete_arguments('grid__inDS', 'grid__nJobs')
  ioGridParser.suppress_arguments( grid__mergeOutput          = False # We disabled it since late 2017, where GRID
      # added a limited to the total memory and processing time for merging jobs.
                                 , grid_CSV__outputs          = GridOutputCollection( [ GridOutput('td','tunedDiscr*.pic') ] )
                                 , grid__nFiles               = None
                                 , grid__nFilesPerJob         = 1
                                 , grid__forceStaged          = True
                                 , grid__forceStagedSecondary = True
                                 , grid__nCore = None
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
  miscParser.add_argument('-mt','--multi-thread', required = False,
      type = MultiThreadGridConfigure(),
      help = """Whether to run multi-thread job or single-thread.""")
  miscParser.add_argument('--send-memory-estimation', required = False,
      type = BooleanStr,
      help = """Use memory estimation calculated from multi-thread estimator
      as a requirement for the job sent to the grid.""")
  miscParser.add_argument('--multi-files', type=BooleanStr,
      help= """Use this option if your input dataDS was split into one file per bin.""")
  miscParser.add_argument('--expert-networks',  nargs='+',required = False,
      help= """The Cross-Valid summary data file with the expert networks.""")
  from argparse import SUPPRESS
  miscParser.add_argument('--expert-paths',  nargs='+',required = False,
      help= SUPPRESS)
  clusterParser = ioGridParser
  namespaceObj = TuningToolGridNamespace('prun')
elif clusterManagerConf() in (ClusterManager.PBS, ClusterManager.LSF,):
  # Suppress/delete the following options in the main-job parser:
  tuningJobParser.delete_arguments( 'outputFileBase', 'confFileList', 'outputDir'
                                  , 'neuronBounds', 'sortBounds', 'initBounds' )
  tuningJobParser.suppress_arguments( compress = 'False' )

  namespaceObj = LocalClusterNamespace()
  if clusterManagerConf() is ClusterManager.PBS:
    # TODO Make job array:
    # https://wikis.nyu.edu/display/NYUHPC/Tutorial+-+Submitting+a+job+using+qsub
    from RingerCore import PBSOutputMerging
    clusterParser = pbsParser
    # Suppress/delete the following options in the pbs parser:
    clusterParser.suppress_arguments( pbs__copy_environment     = BooleanOptionRetrieve( option = '-V', value=True ) )
    clusterParser.set_defaults( pbs__job_name             = OptionRetrieve( option = '-N', value="tuningJob", addEqual=False )
                              , pbs__combine_stdout_sterr = EnumStringOptionRetrieve( option = '-j', type=PBSOutputMerging, value=PBSOutputMerging.oe )
                              , pbs__walltime = SubOptionRetrieve( option = '-l'
                                                                 , suboption='walltime'
                                                                 , value = ( ':'.join(['24','00','00']) ) )
                              )
  elif clusterManagerConf() is ClusterManager.LSF:
    clusterParser = lsfParser
  parentReqParser.add_argument('-c','--configFileDir', metavar='Config_Dir',
      required = True, action='store',
      help = """Directory containing the configuration files to be used
                when running then configuration to loop upon files to retrieve configuration. There
                will be one job for each file on this container.""")
  parentReqParser.add_argument('-o','--outputDir', action='store', required = True,
      help = """Output directory path. When not specified, output will be created in PWD.""")
elif clusterManagerConf() in (None,NotSet):
  preInitLogger.fatal("""Could not identify an available ClusterManager to use,
      either specify it manually via --cluster-manager or make sure that you
      have set your environment accordingly (e.g. setup panda).""")
else:
  preInitLogger.fatal("%s cluster manager is not yet implemented.",
                      clusterManagerConf(),
                      NotImplementedError)

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
parser = ArgumentParser(description = 'Tune discriminators using input data on the GRID',
    parents = [tuningJobParser, parentParser, clusterParser, loggerParser, DevParser()],
                        conflict_handler = 'resolve')
parser.make_adjustments()
emptyArgumentsPrintHelp(parser)

# Retrieve parser args:
args = parser.parse_args( namespace = namespaceObj )

mainLogger = Logger.getModuleLogger( __name__, args.output_level )
mainLogger.write = mainLogger.info
printArgs( args, mainLogger.debug )

if clusterManagerConf() is ClusterManager.Panda:
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
  if args.multi_thread.configured():
    nCores = args.multi_thread.get()
    if nCores < 1:
      mainLogger.fatal("Attempted to dispatch job with invalid number of cores (%d)", nCores )
    setrootcore_opts = '--grid --ncpus={CORES} --no-color;'.format( CORES = args.multi_thread.get() )
    args.set_job_submission_option('nCore', args.multi_thread.get())
  tuningJob = '\$ROOTCOREBIN/user_scripts/TuningTools/standalone/runTuning.py'

  dataStr, configStr, ppStr, crossFileStr, expertNetworksStr = '', '%IN', '%PP', '%CROSSVAL', ''


  for i in range(len(args.dataDS)):  dataStr += '%DATA_'+str(i)+' '
  if args.expert_networks:
    for i in range(len(args.expert_networks)):  expertNetworksStr += '%EXPERTPATH_'+str(i)+' '
  else:  expertNetworksStr = None

  refStr = subsetStr = None

  if args.get_job_submission_option('debug') is not None:
    args.set_job_submission_option('nFiles', 10)

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


elif clusterManagerConf() in (ClusterManager.PBS, ClusterManager.LSF):
  #if args.core_framework is TuningToolCores.keras:
    # Keras run single-threaded
    #args.set_job_submission_option('ncpus', SubOptionRetrieve( option = '-l', suboption = 'ncpus', value=1 )  )
  # Make sure we have permision to create the directory:
  if not args.dry_run:
    mkdir_p( args.outputDir )
  rootcorebin = os.environ.get('ROOTCOREBIN')
  #setrootcore = os.path.join(rootcorebin,'../setrootcore.sh')
  setrootcore = ''
  # TODO Add to setrootcore the number of cores in the job
  # TODO Set the OMP_NUM_CLUSTER environment to the same value as the one in the job.
  #setrootcore_opts = '--ncpus=%d' % args.get_job_submission_option('ncpus')
  setrootcore_opts = ''
  expandArg = lambda x: ' '.join(x) if x else ''
  tuningJob = os.path.join(rootcorebin, 'user_scripts/TuningTools/standalone/runTuning.py')
  dataStr,   configStr,        ppStr,       crossFileStr,   refStr,       subsetStr,        expertNetworksStr = \
  expandArg(args.data), '{CONFIG_FILES}', args.ppFile, args.crossFile, args.refFile, args.clusterFile, expandArg(args.expert_networks)
  configFileDir = os.path.abspath(args.configFileDir)
  if os.path.isdir(configFileDir):
    configFiles = getFiles( configFileDir )
  elif os.path.isfile(configFileDir):
    configFiles = [ configFileDir ]
  else:
    raise RuntimeError("Unexpected configFileDir: %s" % configFileDir)
  if args.debug:
    args.nFiles = 1

# Binning
if args.et_bins is not None:
  if len(args.et_bins)  == 1: args.et_bins  = args.et_bins[0]
  if type(args.et_bins) in (int,float):
    args.et_bins = [args.et_bins, args.et_bins]
  args.et_bins = MatlabLoopingBounds(args.et_bins)
  if clusterManagerConf() is ClusterManager.Panda:
    args.set_job_submission_option('allowTaskDuplication', True)
else:
  args.et_bins = Holder([ args.et_bins ])
if args.eta_bins is not None:
  if len(args.eta_bins) == 1: args.eta_bins = args.eta_bins[0]
  if type(args.eta_bins) in (int,float):
    args.eta_bins = [args.eta_bins, args.eta_bins]
  args.eta_bins = MatlabLoopingBounds(args.eta_bins)
  if clusterManagerConf() is ClusterManager.Panda:
    args.set_job_submission_option('allowTaskDuplication', True)
else:
  args.eta_bins = Holder([ args.eta_bins ])

#TODO: Do something elegant here
if hasattr( args, 'outputDir' ):
  _outputDir=args.outputDir
else:
  _outputDir=""

if clusterManagerConf() is ClusterManager.Panda:
  memoryVal = args.get_job_submission_option('memory')

# Prepare to run
from itertools import product
startBin = True
for etBin, etaBin in progressbar( product( args.et_bins(),
                                  args.eta_bins() ),
                                  count = len(list(args.et_bins()))*len(list(args.eta_bins())) if args.et_bins() else 1,
                                  logger = mainLogger,
                                ):
  if clusterManagerConf() is ClusterManager.Panda:
    # When running multiple bins, dump workspace to a file and re-use it:
    if etBin is not None or etaBin is not None:
      if startBin:
        if args.get_job_submission_option('outTarBall') is None and not args.get_job_submission_option('inTarBall'):
          args.set_job_submission_option('outTarBall', 'workspace.tar')
        startBin = False
      else:
        if args.get_job_submission_option('outTarBall') is not None:
          # Swap outtar with intar
          args.set_job_submission_option('inTarBall', args.get_job_submission_option('outTarBall') )
          args.set_job_submission_option('outTarBall', None )

  if clusterManagerConf() is ClusterManager.Panda:
    args.set_job_submission_option('memory', memoryVal )
    secondaryDSs = args.get_job_submission_option( 'secondaryDSs' )

    if args.multi_files: ###NOTE: Fix all et/eta multi file names
      for s in secondaryDSs:  s.container = re.sub(r'_et\d+_eta\d+',r'_et%d_eta%d' % (etBin, etaBin), s.container )

    if not args.multi_thread.configured():
      args.multi_thread.inputFile = secondaryDSs[0]
      #nCores = args.multi_thread.get()
      nCores =1
      if nCores < 1:
        mainLogger.fatal("Attempted to dispatch job with invalid number of cores (%d)", nCores )
      setrootcore_opts = '--grid --ncpus={CORES} --no-color;'.format( CORES = nCores )
      args.set_job_submission_option('nCore', nCores)
      if args.send_memory_estimation and args.multi_thread.mt_job:
        args.set_job_submission_option('memory', int(round(args.multi_thread.job_memory_consumption)))

  args.setExec("""{setrootcore} {setrootcore_opts}
                  {tuningJob}
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
                    {CORE}
                    {PROJECTTAG}
                    {RINGERCORETAG}
                    {TUNINGTOOLTAG}
                    {DEVELOPMENT}
               """.format( setrootcore      = setrootcore,
                           setrootcore_opts = setrootcore_opts,
                           tuningJob        = tuningJob,
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
                           PROJECTTAG       = ProjectGit.dumpToParser(),
                           RINGERCORETAG    = RingerCoreGit.dumpToParser(),
                           TUNINGTOOLTAG    = TuningToolsGit.dumpToParser(),
                           DEVELOPMENT      = "--development" if Development() else ''
                         )
              )

  if clusterManagerConf() is ClusterManager.Panda:
    # And run
    args.run()
    # FIXME We should want something more sofisticated
    if args.get_job_submission_option('debug') is not None:
      break
  elif clusterManagerConf() in (ClusterManager.PBS, ClusterManager.LSF):
    lExec = args.exec_
    for idx, configFile in progressbar( enumerate(configFiles)
                                      , len(configFiles)
                                      , logger = mainLogger
                                      , ):
      if clusterManagerConf() is ClusterManager.PBS:
        while True:
          process = sp.Popen(["qstat", "-a"], stdout=sp.PIPE)
          grep_process = sp.Popen(["grep", str(args.get_job_submission_option("job_name")).replace('-N ', '') ], stdin=process.stdout, stdout=sp.PIPE)
          wc_process = sp.Popen(["wc", "-l" ], stdin=grep_process.stdout, stdout=sp.PIPE)
          process.stdout.close()  # Allow process to receive a SIGPIPE if grep_process exits.
          grep_process.stdout.close()  # Allow grep_process to receive a SIGPIPE if wc_process exits.
          output = wc_process.communicate()[0]
          nJobs = int(output)
          if nJobs >= args.max_job_slots:
            mainLogger.info("Sleeping for 2 minutes as all job slots were reached..." )
            time.sleep( 120 )
          else:
            break
      args.setExec( lExec.format( CONFIG_FILES = configFile ) )
      return_code = args.run()
      if return_code is not None and return_code:
        while return_code:
          mainLogger.warning("Retrying command in 120s...")
          time.sleep( 120 )
          return_code = args.run()
      if args.nFiles == idx + 1:
        break
    if args.debug:
      break
# Finished submitting all bins

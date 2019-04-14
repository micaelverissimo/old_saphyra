#!/usr/bin/env python

import os, sys, subprocess as sp, time, re, stat
from TuningTools import coreConf, TuningToolCores, TuningToolsGit
from TuningTools.parsers import ( ArgumentParser, ioGridParser, loggerParser
                                , createDataParser, TuningToolGridNamespace, crossValStatsJobParser
                                )
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
                       , extract_scope, Development, DevParser, expandFolders
                       , select, expandPath
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

parentParser = ArgumentParser(add_help = False)
## Create our paser
# Add base parser options (this is just a wrapper so that we can have this as
# the first options to show, as they are important options)
parentReqParser = parentParser.add_argument_group("required arguments", '')

if clusterManagerConf() is ClusterManager.Panda:
  clusterParser = ioGridParser
  namespaceObj = TuningToolGridNamespace('prun')
  crossValStatsJobParser.suppress_arguments( doMatlab = True
                                           , test = False 
                                           , doCompress = False
                                           )
  crossValStatsJobParser.delete_arguments( 'binFilters', 'discrFiles', 'refFile', 'outputs')
  ioGridParser.delete_arguments( 'grid__inDS', 'grid__reusableSecondary'
                               , 'grid__nFiles', 'grid__antiMatch'
                               )
  ioGridParser.suppress_arguments( grid_CSV__outputs = GridOutputCollection()
                                 , grid__match = False
                                 , grid__writeInputToTxt = 'IN:input.csv'
                                 , grid__allowTaskDuplication = True
                                 , grid__nFiles = None
                                 , grid__nFilesPerJob = 1
                                 , grid__nJobs = 1
                                 , grid__maxNFilesPerJob = 1
                                 , grid__forceStaged = True
                                 , grid__forceStagedSecondary = True
                                 , grid__crossSite = 1
                                 , grid__secondaryDS = SecondaryDatasetCollection()
                                 )
  parentReqParser.add_argument('-d','--discrFilesDS', 
      required = True, metavar='DATA', action='store', dest = 'grid__inDS',
      help = "The dataset with the tuned discriminators.")
  parentOptParser = parentParser.add_argument_group("optional arguments", '')
  parentOptParser.add_argument('-r','--refFileDS', metavar='REF_FILE', 
      required = False,  default = None, action='store',
      help = """Input dataset to loop upon files to retrieve configuration. There
                will be one job for each file on this container.""")
elif clusterManagerConf() in (ClusterManager.PBS, ClusterManager.LSF,):
  # Suppress/delete the following options in the main-job parser:
  crossValStatsJobParser.delete_arguments( 'discrFiles' )

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
  # -c -o etc. 
  parentReqParser.add_argument('-d', '--discrFiles', action='store', 
      metavar='files', required = True,
      help = """The tuned discriminator data files or folders that will be used to run the
            cross-validation analysis.""")
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

parser = ArgumentParser(description = 'Retrieve performance information from the Cross-Validation method on the GRID.',
                        parents = [crossValStatsJobParser, parentParser, clusterParser, loggerParser],
                        conflict_handler = 'resolve')
parser.make_adjustments()

emptyArgumentsPrintHelp(parser)

# Retrieve parser args:
args = parser.parse_args( namespace = namespaceObj )
mainLogger = Logger.getModuleLogger( __name__, args.output_level )
printArgs( args, mainLogger.debug )

if clusterManagerConf() is ClusterManager.Panda:
  # Set primary dataset number of files:
  try:
    # The input files can be send via a text file to avoid very large command lines?
    mainLogger.info(("Retrieving files on the data container to separate "
                    "the jobs accordingly to each tunned bin reagion."))
    from rucio.client import DIDClient
    from rucio.common.exception import DataIdentifierNotFound
    didClient = DIDClient()
    parsedDataDS = args.grid__inDS.split(':')
    did = parsedDataDS[-1]
    if len(parsedDataDS) > 1:
      scope = parsedDataDS
    else:
      import re
      pat = re.compile(r'(?P<scope>user.[a-zA-Z]+)\..*')
      m = pat.match(did)
      if m:
        scope = m.group('scope')
      else:
        import os
        scope = 'user.%s' % os.path.expandvars('$USER')
    try:
      files = [d['name'] for d in didClient.list_files(scope, did)]
      from TuningTools import GridJobFilter
      ffilter = GridJobFilter()
      jobFilters = ffilter( files )
      mainLogger.info('Found following filters: %r', jobFilters)
      jobFileCollection = select( files, jobFilters, popListInCaseOneItem = False ) 
      nFilesCollection = [len(l) for l in jobFileCollection]
      mainLogger.info("A total of %r files were found.", nFilesCollection )
    except DataIdentifierNotFound, e:
      raise RuntimeError("Could not retrieve number of files on informed data DID. Rucio error:\n%s" % str(e))
  except ImportError, e:
    raise ImportError("rucio environment was not set, please set rucio and try again. Full error:\n%s" % str(e))

  # Fix secondaryDSs string if using refFile
  refStr = ""
  if args.refFileDS:
    args.append_to_job_submission_option( 'secondaryDSs', SecondaryDataset( key = "REF_FILE", nFilesPerJob = 1, container = args.refFileDS, reusable = True) )
    refStr = "%REF_FILE"

  # Set output:
  args.append_to_job_submission_option('outputs', GridOutputCollection(
                                                    [ GridOutput('pic','crossValStat.pic')
                                                    , GridOutput('mat','crossValStat.mat')
                                                    ]
                                                  )
                                      )
  args.setBExec('source ./buildthis.sh --grid --with-scipy --no-color || source ./buildthis.sh --grid --with-scipy --no-color')
  # FIXME The default is to create the root files. Change this to a more automatic way.
  if args.doMonitoring is NotSet or args.doMonitoring:
    args.append_to_job_submission_option('outputs', GridOutput('root','crossValStat_monitoring.root'))
  setrootcore = 'source ./setrootcore.sh'
  setrootcore_opts = '--grid --ncpus=1 --no-color;'.format( CORES = args.multi_thread.get() )
  tunedDataStr = "@input.csv"
  debug = ( args.get_job_submission_option('debug') is not None )
  crossValStatAnalysis = '\$ROOTCOREBIN/user_scripts/TuningTools/standalone/crossValStatAnalysis.py'
elif clusterManagerConf() in (ClusterManager.PBS, ClusterManager.LSF,):
  #
  if args.outputFileBase:
    args.outputFileBase = os.path.join( args.outputDir. args.outputFileBase )
  else:
    args.outputFileBase = os.path.join( args.outputDir, 'crossValStat' )
  from itertools import repeat
  files = expandFolders( args.discrFiles )
  from TuningTools import MixedJobBinnedFilter
  ffilter = MixedJobBinnedFilter()
  jobFilters = ffilter( files )
  mainLogger.info('Found following filters: %r', jobFilters)
  jobFileCollection = select( files, jobFilters, popListInCaseOneItem = False ) 
  nFilesCollection = [len(l) for l in jobFileCollection]
  tunedDataStr, refStr, binFilterStr = args.discrFiles, args.refFile, '--binFilters {BIN_FILTER}'
  debug = args.test
  rootcorebin = os.environ.get('ROOTCOREBIN')
  crossValStatAnalysis = os.path.join(rootcorebin, 'user_scripts/TuningTools/standalone/crossValStatAnalysis.py')
  #setrootcore = 'source ' + os.path.join(rootcorebin, '../setrootcore.sh;')
  setrootcore = ''
  setrootcore_opts = ''
  if args.tmpFolder:
    args.tmpFolder = expandPath( args.tmpFolder )
    mkdir_p( args.tmpFolder )
    import tempfile
    tempfile.tempdir = args.tmpFolder


startBin = True
for jobFiles, nFiles, jobFilter in zip(jobFileCollection, nFilesCollection, jobFilters):
  if clusterManagerConf() is ClusterManager.Panda:
    if startBin:
      if args.get_job_submission_option('outTarBall') is None and not args.get_job_submission_option('inTarBall'):
        args.set_job_submission_option('outTarBall', 'workspace.tar')
      startBin = False
    else:
      if args.get_job_submission_option('outTarBall') is not None:
        # Swap outtar with intar
        args.set_job_submission_option('inTarBall', args.get_job_submission_option('outTarBall') )
        args.set_job_submission_option('outTarBall', None )
    ## Now set information to grid argument
    if args.get_job_submission_option('debug') is not None:
      args.set_job_submission_option('nFiles', 1)
      args.set_job_submission_option('nFilesPerJob', 1)
    else:
      args.set_job_submission_option('nFilesPerJob', nFiles)
    args.set_job_submission_option( 'match', '"' + jobFilter + '"')
  # Set execute:
  args.setExec("""{setrootcore} {setrootcore_opts}
                  {crossValStatAnalysis} 
                    -d {TUNED_DATA} 
                    {BIN_FILTER}
                    {OUTPUT_FILE_BASE}
                    {REF_FILE}
                    {OPERATION}
                    {DO_MONITORING}
                    {DO_MATLAB}
                    {TMP_DIR}
                    {DO_COMPRESS}
                    {DEBUG}
                    {OUTPUT_LEVEL}
                    {EPSILON}
                    {AUC_EPSILON}
                    {ROC_METHOD}
                    {MODEL_METHOD}
                    {INIT_MODEL_METHOD}
                    {EXPAND_OP}
                    {ALWAYS_USE_SP_NETWORK}
                    {FULL_DUMP_NEURONS}
                    {OVERWRITE}
                    {DATA_LOCATION}
                    {PP_FILE}
                    {CROSS_VALID_FILE}
                    {CLUSTER_FILE}
                    {CROSS_VALID_METHOD}
                    {CROSS_VALID_SHUFFLE}
                    {REDO_DECISION_MAKING}
                    {THRES_ET_BINS}
                    {THRES_ETA_BINS}
                    {DECISION_MAKING_METHOD}
                    {PILEUP_REF}
                    {PILEUP_LIMITS}
                    {MAX_CORR}
               """.format( setrootcore            = setrootcore,
                           setrootcore_opts       = setrootcore_opts,
                           crossValStatAnalysis   = crossValStatAnalysis,
                           TUNED_DATA             = tunedDataStr,
                           BIN_FILTER             = binFilterStr,
                           OUTPUT_FILE_BASE       = conditionalOption("--outputFileBase",         args.outputFileBase         ) ,
                           REF_FILE               = conditionalOption("--refFile",                refStr                      ) ,
                           OPERATION              = conditionalOption("--operation",              args.operation              ) ,
                           DO_MONITORING          = conditionalOption("--doMonitoring",           args.doMonitoring           ) if args.doMonitoring is not NotSet else '',
                           DO_MATLAB              = conditionalOption("--doMatlab",               args.doMatlab               ) if args.doMatlab is not NotSet else '',
                           TMP_DIR                = conditionalOption("--tmpDir",                 args.tmpFolder              ) ,
                           EPSILON                = conditionalOption("--epsilon",                args.epsilon                ) ,
                           AUC_EPSILON            = conditionalOption("--AUC-epsilon",            args.AUC_epsilon            ) ,
                           ROC_METHOD             = conditionalOption("--roc-method",             args.roc_method             ) ,
                           MODEL_METHOD           = conditionalOption("--model-method",           args.model_method           ) ,
                           INIT_MODEL_METHOD      = conditionalOption("--init-model-method",      args.init_model_method      ) ,
                           EXPAND_OP              = conditionalOption("--expandOP",               args.expandOP               ) ,
                           ALWAYS_USE_SP_NETWORK  = conditionalOption("--always-use-SP-network",  args.always_use_SP_network  ) ,
                           FULL_DUMP_NEURONS      = conditionalOption("--fullDumpNeurons",        args.fullDumpNeurons        ) ,
                           OVERWRITE              = conditionalOption("--overwrite",              args.overwrite              ) ,
                           # Data Curator Args                                                                                  ,
                           DATA_LOCATION          = conditionalOption("--data",                   args.data                   ) ,
                           PP_FILE                = conditionalOption("--ppFile",                 args.ppFile                 ) ,
                           CROSS_VALID_FILE       = conditionalOption("--crossFile",              args.crossFile              ) ,
                           CLUSTER_FILE           = conditionalOption("--clusterFile",            args.clusterFile            ) ,
                           CROSS_VALID_METHOD     = conditionalOption("--crossValidMethod",       args.crossValidMethod       ) ,
                           CROSS_VALID_SHUFFLE    = conditionalOption("--crossValidShuffle",      args.crossValidShuffle      ) ,
                           # Decision making args:                                                                              ,
                           REDO_DECISION_MAKING   = conditionalOption("--redo_decision_making",   args.redo_decision_making   ) ,
                           THRES_ET_BINS          = conditionalOption("--thres_et_bins",          args.thres_et_bins          ) ,
                           THRES_ETA_BINS         = conditionalOption("--thres_eta_bins",         args.thres_eta_bins         ) ,
                           DECISION_MAKING_METHOD = conditionalOption("--decision-making-method", args.decision_making_method ) ,
                           PILEUP_REF             = conditionalOption("--pile-up-ref",            args.pile_up_ref            ) ,
                           PILEUP_LIMITS          = conditionalOption("--pile-up-limits",         args.pile_up_limits         ) ,
                           MAX_CORR               = conditionalOption("--max_corr",               args.max_corr               ) ,
                           DO_COMPRESS            = conditionalOption("--doCompress",             args.doCompress             ) ,
                           OUTPUT_LEVEL           = conditionalOption("--output-level",           args.output_level           ) if args.output_level is not LoggingLevel.INFO else '',
                           DEBUG                  = "--test" if debug or args.test else '',
                         )
              )
  # And run

  if clusterManagerConf() is ClusterManager.Panda:
    # And run
    args.run()
    # FIXME We should want something more sofisticated
    if args.get_job_submission_option('debug') is not None:
      break
  elif clusterManagerConf() in (ClusterManager.PBS, ClusterManager.LSF):
    lExec = args.exec_
    args.setExec( lExec.format( BIN_FILTER = jobFilter ) )
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
      fpath=tempfile.mktemp()+'.sh'
      with open(fpath,'w') as f:
        f.write( '#!env zsh\n')
        #f.write( 'source ~/DotFiles/shell/zshrc;\n' )
        f.write( '\n'.join(["export {KEY}='{VALUE}'".format(KEY=key, VALUE=value) for key,value in os.environ.iteritems() 
          if key is not '_' and "'" not in value and '"' not in value ]) + '\n' )
        f.write( 'set -x\n')
        #full_cmd_str = re.sub('\\\\ *\n','', args.parse_exec())
        #full_cmd_str = re.sub(' +',' ', full_cmd_str)
        full_cmd_str = re.sub('^ +','', args.parse_exec())
        f.write( full_cmd_str + '\n')
        f.write('rm ' + fpath + '\n')
      with open(fpath,'r') as f:
        mainLogger.info('File %s content is:\n%s', fpath, f.read())
      lExec = fpath
      st = os.stat(fpath)
      os.chmod(fpath, st.st_mode | stat.S_IEXEC)
      args.setExec(lExec)
      args.run()
    if args.debug:
      break
# Finished submitting all bins
# Finished running all bins

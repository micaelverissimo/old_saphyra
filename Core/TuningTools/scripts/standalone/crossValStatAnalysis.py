#!/usr/bin/env python

from time import time
start = time()

#from RingerCore import ( csvStr2List, str_to_class, NotSet, BooleanStr
from Gaugi import ( csvStr2List, str_to_class, NotSet, BooleanStr
                       , Logger, LoggingLevel, emptyArgumentsPrintHelp
                       , expandPath, mkdir_p )

from TuningTools.parsers import ( ArgumentParser, loggerParser,
                                  crossValStatsJobParser )

from TuningTools import ( CrossValidStatAnalysis, GridJobFilter, BenchmarkEfficiencyArchieve
                        , ReferenceBenchmark, ReferenceBenchmarkCollection )

parser = ArgumentParser( description = 'Retrieve performance information from the Cross-Validation method.'
                       , parents = [crossValStatsJobParser, loggerParser] )
parser.make_adjustments()

emptyArgumentsPrintHelp( parser )

## Retrieve parser args:
args = parser.parse_args( )
mainLogger = Logger.getModuleLogger(__name__)
mainLogger.level = args.output_level

# Overwrite tempfile in the beginning of the job:
if args.tmpFolder:
  args.tmpFolder = expandPath( args.tmpFolder )
  mkdir_p( args.tmpFolder )
  import tempfile
  tempfile.tempdir = args.tmpFolder

if mainLogger.isEnabledFor( LoggingLevel.DEBUG ):
  import cProfile, pstats, StringIO
  pr = cProfile.Profile()
  pr.enable()

## Treat special arguments
# Check if binFilters is a class
if args.binFilters is not NotSet:
  try:
    args.binFilters = str_to_class( "TuningTools.CrossValidStat", args.binFilters )
  except (TypeError, AttributeError,):
    args.binFilters = csvStr2List( args.binFilters )

# Retrieve reference benchmark:
call_kw = {}
if args.refFile is not None:
  # If user has specified a reference performance file:
  mainLogger.info("Loading reference file...")
  effArchieve = BenchmarkEfficiencyArchieve.load(args.refFile, loadCrossEfficiencies = True)
  refBenchmarkCol = ReferenceBenchmarkCollection([])
  if args.operation is None:
    args.operation = effArchieve.operation
  from TuningTools.dataframe import RingerOperation
  refLabel = RingerOperation.tostring( args.operation )
  from TuningTools import getEfficiencyKeyAndLabel
  efficiencyKey, refLabel = getEfficiencyKeyAndLabel( args.refFile, args.operation )
  from itertools import product
  for etBin, etaBin in product( range( effArchieve.nEtBins if effArchieve.isEtDependent else 1 ),
                                range( effArchieve.nEtaBins if effArchieve.isEtaDependent else 1 )):
    # Make sure that operation is valid:
    refArgs = []
    try:
      try:
        benchmarks = (effArchieve.signalEfficiencies[efficiencyKey][etBin][etaBin],
                      effArchieve.backgroundEfficiencies[efficiencyKey][etBin][etaBin])
        if benchmarks[0]._readVersion is 2:
          benchmarks[0]._etBin = etBin; benchmarks[0]._etaBin = etaBin
          benchmarks[1]._etBin = etBin; benchmarks[1]._etaBin = etaBin
          mainLogger.warning('Patched bug in version 2 of BranchEffCollector, please ignore related error messages.')
      except TypeError:
        mainLogger.fatal("Could not retrieve %r efficiencies.", efficiencyKey)
      refArgs.extend( benchmarks )
    except KeyError:
      mainLogger.fatal("Could not retrieve operation point %s at efficiency file. Available options are: %r"
                      , refLabel, effArchieve.signalEfficiencies.keys() )
    #try:
    #  crossBenchmarks = (effArchieve.signalCrossEfficiencies[refLabel][etBin][etaBin],
    #                     effArchieve.backgroundCrossEfficiencies[refLabel][etBin][etaBin])
    #  refArgs.extend( crossBenchmarks )
    #except KeyError, AttributeError:
    # Add the signal efficiency and background efficiency as goals to the
    # tuning wrapper:
    # FIXME: Shouldn't this be a function or class?
    opRefs = [ReferenceBenchmark.SP, ReferenceBenchmark.Pd, ReferenceBenchmark.Pf]
    refBenchmarkList = ReferenceBenchmarkCollection([])
    for ref in opRefs:
      refBenchmarkList.append( ReferenceBenchmark( "OperationPoint_" + refLabel.replace('Accept','') + "_"
                                                   + ReferenceBenchmark.tostring( ref ),
                                                   ref, *refArgs ) )
    refBenchmarkCol.append( refBenchmarkList )
  del effArchieve
  call_kw['refBenchmarkCol'] = refBenchmarkCol
elif args.redo_decision_making or (args.redo_decision_making  in (None,NotSet) and args.data):
  if args.pile_up_ref in (None,NotSet):
    mainLogger.fatal("Cannot redo decision making without specifying --pile-up-ref.")

stat = CrossValidStatAnalysis(
    args.discrFiles
    , binFilters = args.binFilters
    , binFilterIdxs = args.binFilterIdx
    , level = args.output_level
    )

    # Optional Arguments
stat( outputName              = args.outputFileBase
    , doMonitoring            = args.doMonitoring
    , doCompress              = args.doCompress
    , toMatlab                = args.doMatlab
    , test                    = args.test
    , epsCol                  = args.epsilon
    , aucEpsCol               = args.AUC_epsilon
    , rocPointChooseMethodCol = args.roc_method
    , modelChooseMethodCol    = args.model_method
    , modelChooseInitMethod   = args.init_model_method
    , expandOP                = args.expandOP
    , alwaysUseSPNetwork      = args.always_use_SP_network
    , fullDumpNeurons         = args.fullDumpNeurons
    , overwrite               = args.overwrite
    # Data curator arguments:
    , dataLocation            = args.data
    , ppFile                  = args.ppFile
    , crossValidFile          = args.crossFile
    , clusterFile             = args.clusterFile
    , crossValidMethod        = args.crossValidMethod
    , shuffle                 = args.crossValidShuffle
    #, operationPoint          = args.operation
    # Decision making arguments:
    , redoDecisionMaking      = args.redo_decision_making
    , thresEtBins             = args.thres_et_bins
    , thresEtaBins            = args.thres_eta_bins
    , decisionMakingMethod    = args.decision_making_method
    , pileupRef               = args.pile_up_ref
    , pileupLimits            = args.pile_up_limits
    , maxCorr                 = args.max_corr
    , frMargin                = args.fr_margin
    # Reference benchmark collection overwrite (not done using data curator):
    , **call_kw
    )

if mainLogger.isEnabledFor( LoggingLevel.DEBUG ):
  pr.disable()
  s = StringIO.StringIO()
  sortby = 'cumulative'
  ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
  ps.print_stats()
  mainLogger.debug('\n' + s.getvalue())
  end = time()
  mainLogger.debug("Job took %.2fs.", end - start)

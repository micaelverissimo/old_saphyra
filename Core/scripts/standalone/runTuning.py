#!/usr/bin/env python

from TuningTools.parsers import ArgumentParser, LoggerParser, TuningJobParser
from RingerCore import emptyArgumentsPrintHelp, NotSet, LoggingLevel, DevParser

parser = ArgumentParser(description = 'Tune discriminators using input data.',
                        parents = [TuningJobParser(), LoggerParser(), DevParser()])
parser.make_adjustments()

emptyArgumentsPrintHelp( parser )

# Retrieve parser args:
args = parser.parse_args()

## Treating special args:
# Configuration
conf_kw = {}
if args.neuronBounds not in (None, NotSet): conf_kw['neuronBoundsCol'] = args.neuronBounds
if args.sortBounds   not in (None, NotSet): conf_kw['sortBoundsCol']   = args.sortBounds
if args.initBounds   not in (None, NotSet): conf_kw['initBoundsCol']   = args.initBounds
if args.confFileList not in (None, NotSet): conf_kw['confFileList']    = args.confFileList
# Binning
from RingerCore import printArgs, NotSet, Logger, LoggingLevel
if not(args.et_bins is NotSet) and len(args.et_bins)  == 1: args.et_bins  = args.et_bins[0]
if not(args.eta_bins is NotSet) and len(args.eta_bins) == 1: args.eta_bins = args.eta_bins[0]

logger = Logger.getModuleLogger( __name__, args.output_level )

printArgs( args, logger.debug )

# Submit job:
from TuningTools import TuningJob
tuningJob = TuningJob()
tuningJob( args.data,
           level                  = args.output_level,
					 compress               = args.compress,
					 outputFileBase         = args.outputFileBase,
           outputDirectory        = args.outputDir,
           saveMatPP              = args.saveMatPP,
           overwrite              = args.overwrite,
           # Other data curator args
           operationPoint         = args.operation,
           refFile                = args.refFile,
           clusterFile            = args.clusterFile,
           expertPaths            = args.expert_networks,
           # Cross validation args
					 crossValidFile         = args.crossFile,
					 crossValidMethod       = args.crossValidMethod,
					 crossValidShuffle      = args.crossValidShuffle,
           # Pre Processing
           ppFile                 = args.ppFile,
           # Binning configuration
           etBins                 = args.et_bins,
           etaBins                = args.eta_bins,
					 # Tuning CORE args
           showEvo                = args.show_evo,
           maxFail                = args.max_fail,
           epochs                 = args.epochs,
           doPerf                 = args.do_perf,
           batchSize              = args.batch_size,
           batchMethod            = args.batch_method,
           seed                   = args.seed,
           doMultiStop            = args.do_multi_stop,
           addPileupToOutputLayer = args.add_pileup,
           # ExMachina CORE args
           algorithmName          = args.algorithm_name,
           networkArch            = args.network_arch,
           costFunction           = args.cost_function,
           shuffle                = args.shuffle,
					 # Looping configuration args
           **conf_kw
				 )

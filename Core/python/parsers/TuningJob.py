__all__ = ['TuningJobParser', 'tuningJobParser',
           'TuningExpertParser', 'tuningExpertParser']

from RingerCore import NotSet, ArgumentParser, BooleanStr

from TuningTools.coreDef import hasFastnet, hasExmachina
from TuningTools.TuningJob import BatchSizeMethod
from TuningTools.parsers.BaseModuleParser import CoreFrameworkParser
from TuningTools.parsers.DataCuration import DataCurationParser
from TuningTools.parsers.Binning import addBinningOptions

################################################################################
# Create tuningJob file related objects
################################################################################
def TuningJobParser():
  tuningJobParser = ArgumentParser(add_help = False
                                  ,description = 'Tune discriminator for a specific TuningTool data.'
                                  ,conflict_handler = 'resolve'
                                  ,parents = [CoreFrameworkParser(), DataCurationParser()])
  tuningOptArgs = tuningJobParser.add_argument_group( "optional arguments", "")
  tuningOptArgs.add_argument('--outputFileBase', action='store', default = NotSet,
      help = """Base name for the output file, e.g. 'nn-tuned', 'tunedDiscr' etc.""")
  tuningOptArgs.add_argument('-odir','--outputDir', action='store', default = NotSet,
      help = """Output directory path. When not specified, output will be created in PWD.""")
  tuningOptArgs.add_argument('--overwrite', type=BooleanStr, default = NotSet,
      help = """Whether to overwrite output files.""")
  tuningLoopVars = tuningJobParser.add_argument_group( "Looping configuration", "")
  tuningLoopVars.add_argument('-c','--confFileList', nargs='+', default = None,
      help = """A python list or a comma separated list of the
            root files containing the configuration to run the jobs. The files can
            be generated using a CreateConfFiles instance which can be accessed via
            command line using the createTuningJobFiles.py script.""")
  tuningLoopVars.add_argument('--neuronBounds', nargs='+', type=int, default = None,
                          help = """
                              Input a sequential bounded list to be used as the
                              neuron job range, the arguments should have the
                              same format from the seq unix command or as the
                              Matlab format. If not specified, the range will
                              start from 1.  I.e 5 2 9 leads to [5 7 9] and 50
                              leads to 1:50
                                 """)
  tuningLoopVars.add_argument('--sortBounds', nargs='+', type=int, default = None,
                         help = """
                            Input a sequential bounded list using seq format to
                            be used as the sort job range, but the last bound
                            will be opened just as happens when using python
                            range function. If not specified, the range will
                            start from 0.  I.e. 5 2 9 leads to [5 7] and 50 leads
                            to range(50)
                                """)
  tuningLoopVars.add_argument('--initBounds', nargs='+', type=int, default = None,
                         help = """
                            Input a sequential bounded list using seq format to
                            be used as the inits job range, but the last bound
                            will be opened just as happens when using python
                            range function. If not specified, the range will
                            start from 0.  I.e. 5 2 9 leads to [5 7] and 50 leads
                            to range(50)
                                """)
  tuningDepVars = tuningJobParser.add_argument_group( "Binning configuration", "")
  addBinningOptions(  tuningDepVars )
  tuningOptArgs.add_argument('--compress', type=BooleanStr, default=NotSet,
            help = """Whether to compress output files.""")
  tuningArgs = tuningJobParser.add_argument_group( "Tuning CORE configuration", "")
  tuningArgs.add_argument('--show-evo', type=int, default = NotSet,
            help = """The number of iterations where performance is shown.""")
  tuningArgs.add_argument('--max-fail', type=int, default = NotSet,
            help = """Maximum number of failures to imrpove performance over
            validation dataset that is tolerated.""")
  tuningArgs.add_argument('--epochs', type=int, default = NotSet,
            help = """Number of iterations where the tuning algorithm can run the
            optimization.""")
  tuningArgs.add_argument('--do-perf', type=int, default = NotSet,
            help = """Whether we should run performance
              testing under convergence conditions, using test/validation dataset
              and also estimate operation condition.""")
  tuningArgs.add_argument('--batch-size', type=int, default = NotSet,
            help = """Set the batch size used during tuning.""")
  tuningArgs.add_argument('--batch-method', type=BatchSizeMethod,
            default = NotSet,
            help = """Set the batch size method to be used during tuning.
                      If batch size is set this will be overwritten by Manual
                      method. """)
  tuningArgs.add_argument('--expert-networks', nargs='+', default = NotSet,
            help = """The Cross-Valid summary data file with the expert networks.""")
  if hasExmachina:
    exMachinaArgs = tuningJobParser.add_argument_group( "ExMachina CORE configuration", "")
    exMachinaArgs.add_argument('--algorithm-name', default = NotSet,
              help = """The tuning method to use.""")
    exMachinaArgs.add_argument('--network-arch', default = NotSet,
              help = """The neural network architeture to use.""")
    exMachinaArgs.add_argument('--cost-function', default = NotSet,
              help = """The cost function used by ExMachina.""")
    exMachinaArgs.add_argument('--shuffle', default = NotSet,
              help = """Whether to shuffle datasets while training.""")
  else:
    tuningJobParser.set_defaults( algorithm_name = NotSet
                                , network_arch   = NotSet
                                , cost_function  = NotSet
                                , shuffle        = NotSet )
  if hasFastnet:
    fastNetArgs = tuningJobParser.add_argument_group( "FastNet CORE configuration", "")
    fastNetArgs.add_argument('--seed', default = NotSet,
              help = """The seed to be used by the tuning algorithm.""")
    fastNetArgs.add_argument('--do-multi-stop', default = NotSet,  type=BooleanStr,
              help = """Tune classifier using P_D, P_F and
              SP when set to True. Uses only SP when set to False.""")
    fastNetArgs.add_argument('--add-pileup', default = None, type=BooleanStr,
                         help = """Propagate pile-up to the network hidden layer.""")
  else:
    tuningJobParser.set_defaults( seed          = NotSet
                                , do_multi_stop = NotSet )
  return tuningJobParser
tuningJobParser = TuningJobParser()

################################################################################
# Create tuningExpert file related objects
################################################################################
def TuningExpertParser():
  tuningExpertParser = ArgumentParser(add_help = False
                                     ,description = 'Tune expert discriminator for a specific TuningTool data.'
                                     ,conflict_handler = 'resolve'
                                     ,parents = [TuningJobParser()])

  tuningExpertParser.delete_arguments( 'data' )
  tuningExpertParser.suppress_arguments( core = 'keras' )

  tuneExpDataArgs = tuningExpertParser.add_argument_group( "required arguments", "")
  tuneExpDataArgs.add_argument('-dc', '--data-calo', action='store',
                               metavar='data_calo', required = True,
                               help = "The calorimeter data file that will be used to tune the discriminators")
  tuneExpDataArgs.add_argument('-dt', '--data-track', action='store',
                               metavar='data_track', required = True,
                               help = "The tracking data file that will be used to tune the discriminators")
  tuneExpDataArgs.add_argument('-nc', '--network-calo', action='store',
                               metavar='nn_calo', required = True,
                               help = """List of files of the calorimeter neural networks performance analysis.
                                         There must be one file per bin and they must be ordered from the first
                                         et bin to the last, and for each et the eta bins must also be ordered.
                                         Example:
                                         For et-bins 0 and 1 and eta-bins 0, 1 and 2 the files must be in the
                                         order: Et0 Eta0, Et0 Eta1, Et0 Eta2, Et1 Eta0, Et1 Eta1, Et1 Eta2.
                                         In order to obtain such files, it is necessary to run the executable
                                         crossValidStatAnalysis.py.""")
  tuneExpDataArgs.add_argument('-nt', '--network-track', action='store',
                               metavar='nn_track', required = True,
                               help = """List of files of the tracking neural networks performance analysis.
                                         For more information see explanation of network_calo argument.""")
  return tuningExpertParser
tuningExpertParser = TuningExpertParser()

__all__ = ['CrossValStatsJobParser', 'crossValStatsJobParser']

from RingerCore import ArgumentParser, BooleanStr, NotSet

from TuningTools.dataframe.EnumCollection import RingerOperation, PileupReference
from TuningTools.TuningJob import ChooseOPMethod
from TuningTools.parsers.Binning import addBinningOptions
from TuningTools.parsers.DataCuration import DataCurationParser
from TuningTools.DecisionMaking import DecisionMakingMethod

################################################################################
# Create cross valid stats job parser file related objects
################################################################################
def CrossValStatsJobParser():
  extraDescr = """NOTE: Only valid when --redo-decision-making flag to be set."""
  crossValStatsJobParser = ArgumentParser(add_help = False, 
                                         description = 'Retrieve cross-validation information and tuned discriminators performance.',
                                         conflict_handler = 'resolve',
                                         parents=[DataCurationParser( False, extraDescr)])
  ################################################################################
  reqArgs = crossValStatsJobParser.add_argument_group( "required arguments", "")
  reqArgs.add_argument('-d', '--discrFiles', action='store', 
      metavar='files', required = True,
      help = """The tuned discriminator data files or folders that will be used to run the
            cross-validation analysis.""")
  ################################################################################
  decisionMakingArgs = crossValStatsJobParser.add_argument_group( "Decision making configuration", extraDescr)
  addBinningOptions( decisionMakingArgs, 'thres' )
  decisionMakingArgs.add_argument('--redo-decision-making', default = NotSet, type = BooleanStr
                            , help = """Whether to overwrite decision making process using
                            specified method and data. When NotSet, its value will be set
                            accordingly to --data.""" )
  decisionMakingArgs.add_argument('-dmm', '--decision-making-method', default = NotSet, type = DecisionMakingMethod
                            , help = """Specify which method should be used in the decision making process.""" )
  decisionMakingArgs.add_argument('-pup', '--pile-up-ref', default = NotSet, type = PileupReference
                                 , help = """Specify the pileup reference to be used. This will be used 
                                 to determine the label in the plots using pile-up and the limits if not specified.""" )
  decisionMakingArgs.add_argument('--fr-margin', default = NotSet, type = float, nargs = '+'
                                 , help = """Specify the fake rate margin
                                 multipliers to calculate the correction range
                                 estimators.""")
  decisionMakingArgs.add_argument('--max-corr', default = NotSet, type = float
                                 , help = """Specify the maximum correction limit.""" )
  decisionMakingArgs.add_argument('--pile-up-limits', default = NotSet, nargs = '+', type = float
                                 , help = """Specify the limits for calculating
                                 the linear correction method. It must have
                                 size equal exactly to 3.""" )
  ################################################################################
  optArgs = crossValStatsJobParser.add_argument_group( "optional arguments", "")
  # TODO Reset this when running on the Grid to the GridJobFilter
  optArgs.add_argument('--binFilters', action='store', default = NotSet, 
      help = """This option filter the files types from each job. It can be a string
      with the name of a class defined on python/CrossValidStat dedicated to automatically 
      separate the files or a comma separated list of patterns that identify unique group 
      of files for each bin. A python list can also be speficied. 
      E.g.: You can specify 'group001,group002' if you have file001.group001.pic, 
      file002.group001, file001.group002, file002.group002 available and group001 
      specifies one binning limit, and group002 another, both of them with 2 files 
      available in this case.
      When not set, all files are considered to be from the same binning. 
      """)
  optArgs.add_argument('-idx','--binFilterIdx', default = None, nargs='+',type = int,
          help = """The index of the bin job to run. e.g. two bins, idx will be: 0 and 1"""
          )
  optArgs.add_argument('--doMonitoring', default=NotSet,
      help = "Enable or disable monitoring file creation.", type=BooleanStr,
         )
  optArgs.add_argument('--doMatlab', default=NotSet,
      help = "Enable or disable matlab file creation.", type=BooleanStr,
         )
  optArgs.add_argument('--doCompress', default=NotSet, type=BooleanStr,
      help = "Enable or disable raw output file compression."
         )
  optArgs.add_argument('-r','--refFile', default = None,
                       help = """The performance reference file to retrieve the operation points.""")
  optArgs.add_argument('-op','--operation', default = None, type=RingerOperation,
                       help = """The Ringer operation determining in each Trigger 
                       level or what is (are) the offline operation point reference(s)."""
                       )
  optArgs.add_argument('-rocm','--roc-method', nargs='+', default = NotSet, type=ChooseOPMethod,
                       help = """The method to be used to choose the operation
                       point on the ROC. Usually it will come in the following order:
                       SP Pd Pf."""
                       )
  optArgs.add_argument('-eps','--epsilon', nargs='+', default = NotSet, type=float,
                       help = """The value is used to calculate the limits in
                       which a point is accept as valid. Usually it will come in the following order:
                       SP Pd Pf."""
                       )
  optArgs.add_argument('-modelm','--model-method', nargs='+', default = NotSet, type=ChooseOPMethod,
                       help = """The method to be used to choose the best model to operate from
                       all models available operating at the chosen operation point by the roc method.
                       Usually it will come in the following order: SP Pd Pf.
                       """
                       )
  optArgs.add_argument('-imodelm','--init-model-method',  default = NotSet, #ChooseOPMethod.MSE, type=ChooseOPMethod,
                       help = """Whether to overwrite, for all operation points,
                       the initialization model choice method by the one specified
                       here. If not set, it will use the same value as modelm.
                       """
                       )
  optArgs.add_argument('-aeps','--AUC-epsilon', nargs='+', default = NotSet, type=float,
                       help = """The Area Under the ROC Curve epsilon value. This
                       value is used as a delta from the reference in which the value is calculated.
                       Usually it will come in the following order: SP Pd Pf.
                       """)
  optArgs.add_argument('--expandOP', default = NotSet, type=BooleanStr,
                       help = """If the tune was done using --do-multi-stop set to false, then 
                       this option will try to expand the operation point to derive the best
                       models for each OP case, using the target Pd/Pf/SP. If no target Pd/Pf 
                       is available, then it will print a warning and choose only one model
                       via SP maximization.
                       """)
  optArgs.add_argument('--always-use-SP-network', default = NotSet, type=BooleanStr,
                       help = """If the tune was done using --do-multi-stop set to true, then 
                       this option will force all operation points to be derived using the bestSP
                       neural network epoch.
                       """)
  optArgs.add_argument('--outputFileBase', action='store', default = NotSet, 
      help = """Base name for the output file.""")
  optArgs.add_argument('--fullDumpNeurons', nargs='+', type=int, default = NotSet,  
                          help = """
                              For debuging purporses, input a sequential bounded
                              list to be used as the neurons to be fully dumped
                              by the monitoring. 
                                 """)
  optArgs.add_argument('--overwrite', default = NotSet, type=BooleanStr,
                          help = """
                              Whether to overwrite files or just skip those which
                              already exist.
                                 """
      )
  optArgs.add_argument('--tmpFolder', '--tmpDir', default = None, 
                          help = """
                              Specify tmp folder for tar files extraction.
                              Consider using this option if you are facing disk
                              space issues. Please also note that failing jobs
                              won't delete the created temporary files, so the
                              user might need to take action by doing (assuming
                              that the default tmp folder is /tmp):

                              rm $(find /tmp -name "*.pic")
                                 """
      )
  optArgs.add_argument('--test', type=BooleanStr, 
                        help = "Set debug mode.")
  return crossValStatsJobParser 
crossValStatsJobParser = CrossValStatsJobParser()

#!/usr/bin/env python

from RingerCore import save, NotSet, str_to_class, emptyArgumentsPrintHelp, printArgs, Logger

from TuningTools.parsers import ( ArgumentParser, loggerParser
                                , tuningJobFileParser, JobFileTypeCreation)

parser = ArgumentParser(description = 'Generate input file for TuningTool on GRID',
                       parents = [tuningJobFileParser, loggerParser],
                       conflict_handler = 'resolve')
parser.make_adjustments()

emptyArgumentsPrintHelp( parser )

args = parser.parse_args()

# Transform fileType to the enumeration type from the string:
args.fileType = [JobFileTypeCreation.fromstring(conf) for conf in args.fileType]

# Make sure that the user didn't specify all with other file creations:
if JobFileTypeCreation.all in args.fileType and len(args.fileType) > 1:
  raise ValueError(("Chosen to create all file types and also defined another"
    " option."))

logger = Logger.getModuleLogger(__name__, args.output_level )
printArgs( args, logger.debug )


################################################################################
# Check if it is required to create the cross validation file:
if JobFileTypeCreation.all in args.fileType or \
    JobFileTypeCreation.CrossValidFile in args.fileType:
  from TuningTools import CrossValid, CrossValidArchieve
  crossValid = CrossValid(method=args.method,
                          nSorts=args.nSorts,
                          nBoxes=args.nBoxes,
                          nTrain=args.nTrain, 
                          nValid=args.nValid,
                          nTest=args.nTest,
                          seed=args.seed,
                          level=args.output_level)
  place = CrossValidArchieve( args.crossValidOutputFile,
                              crossValid = crossValid ).save( args.compress )
  logger.info('Created cross-validation file at path %s', place )

################################################################################
# Check if it is required to create the configuration files:
if JobFileTypeCreation.all in args.fileType or \
    JobFileTypeCreation.ConfigFiles in args.fileType:
  logger.info('Creating configuration files at folder %s', 
              args.jobConfiFilesOutputFolder )
  from TuningTools import createTuningJobFiles
  sortBounds  = args.sortBounds
  if sortBounds is NotSet:
    try:
      sortBounds  = crossValid.nSorts()
    except NameError:
      pass
  createTuningJobFiles( outputFolder   = args.jobConfiFilesOutputFolder,
                        neuronBounds   = args.neuronBounds,
                        sortBounds     = sortBounds,
                        nInits         = args.nInits,
                        nNeuronsPerJob = args.nNeuronsPerJob,
                        nInitsPerJob   = args.nInitsPerJob,
                        nSortsPerJob   = args.nSortsPerJob,
                        level          = args.output_level,
                        compress       = args.compress )

class NoBinInfo( RuntimeError ):
  """
  Error thrown when no pp-binning information is input by the user.
  """
  def __init__( self , binStr ):
    RuntimeError.__init__(self, ("Cannot generate ppInfo without determining the number of %s bins!") % binStr )

################################################################################
# Check if it is required to create the ppFile:
if JobFileTypeCreation.all in args.fileType or \
    JobFileTypeCreation.ppFile in args.fileType:
  from TuningTools.PreProc import *
  from TuningTools import CrossValid 
  if args.pp_nEtaBins is NotSet and args.pp_nEtBins is NotSet:
    logger.info('Not using any binning information. This pp configuration will be cloned for all bins')
    args.pp_nEtaBins = 1
    args.pp_nEtBins = 1
  elif args.pp_nEtBins is NotSet :
    raise NoBinInfo('et')
  elif args.pp_nEtaBins is NotSet :
    raise NoBinInfo('eta')
  # Retrieve information:
  import ast, re
  replacer = re.compile("(\w+(\(.*?\))?)")
  args.ppCol = replacer.sub(r'"\1"', args.ppCol)
  ppCol = ast.literal_eval(args.ppCol)
  from RingerCore import traverse
  class_str_re = re.compile("(\w+)(\(.*?\))?")
  fix_args = re.compile("(\([^{}]+)((?<!,)\))")
  dict_args = re.compile("(\{.*\})")
  for str_, idx, parent, _, _ in traverse(ppCol):
    m = class_str_re.match(str_)
    if m:
      # The class representation in string:
      class_str = m.group(1)
      # Retrieve the class itself (must be from PreProc module)
      tClass = str_to_class( "TuningTools.PreProc", class_str)
      # Retrieve the arguments, if available
      class_attr = m.group(2)
      if class_attr:
        # Fix the arguments:
        m2 = fix_args.search( m.group(2) )
        if m2:
          class_attr = m2.expand(r'\1,\2')
          # Parse it:
          class_attr_parsed = ast.literal_eval( class_attr )
          # And create the instance
          inst = tClass( *class_attr_parsed )
        else:
          m3 = dict_args.search(str_)
          if m3:
            d = m3.group(1)
            kwargs = ast.literal_eval( m3.group(1) )
            inst = tClass( **kwargs )
          else:
            inst = tClass()
      else:
        inst = tClass()
      # Substitute the instance with the string
      if parent is not None:
        parent[idx] = inst
      else: 
        ppCol = inst
    else:
      raise RuntimeError("Couldn't parse '%s'" % str_)
  from TuningTools import fixPPCol
  pp_nSorts = args.pp_nSorts
  if pp_nSorts is NotSet:
    try:
      pp_nSorts  = crossValid.nSorts()
    except NameError:
      pass
  ppCol = fixPPCol( ppCol, pp_nSorts, args.pp_nEtaBins, args.pp_nEtBins )
  place = PreProcArchieve( args.preProcOutputFile, ppCol = ppCol ).save( args.compress )
  logger.info('Created pre-processing file at path %s', place )

logger.info('Finished creating tuning job files.')

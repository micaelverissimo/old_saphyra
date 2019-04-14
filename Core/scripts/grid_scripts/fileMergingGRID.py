#!/usr/bin/env python

from RingerCore import ( csvStr2List, str_to_class, NotSet, BooleanStr, WriteMethod,
                         expandFolders, Logger, getFilters, select,
                         appendToFileName, ensureExtension, progressbar, LoggingLevel,
                         printArgs, conditionalOption, GridOutputCollection, GridOutput,
                         emptyArgumentsPrintHelp )

from TuningTools.parsers import (ArgumentParser, ioGridParser, loggerParser, 
                                 TuningToolGridNamespace )

from TuningTools import GridJobFilter

ioGridParser.suppress_arguments( grid_CSV__outputs = GridOutputCollection(GridOutput('td','merge.TunedDiscr.tgz'))
                               , grid__forceStaged = True
                               , grid__forceStagedSecondary = True
                               , grid__mergeOutput = True
                               , grid__allowTaskDuplication = True
                               , grid__nFiles = None
                               , grid__nFilesPerJob = None
                               , grid__maxNFilesPerJob = None
                               , grid__match = None
                               , grid__antiMatch = None
                               )
parser = ArgumentParser(description = 'Merge files into unique file on the GRID.',
                        parents = [ioGridParser, loggerParser],
                        conflict_handler = 'resolve')
parser.make_adjustments()

emptyArgumentsPrintHelp(parser)

args = parser.parse_args( namespace = TuningToolGridNamespace('prun') )

mainLogger = Logger.getModuleLogger( __name__, args.output_level )
printArgs( args, mainLogger.debug )

# Set primary dataset number of files:
import os.path
user_scope = 'user.%s' % os.path.expandvars('$USER')
try:
  # The input files can be send via a text file to avoid very large command lines?
  mainLogger.info(("Retrieving files on the data container to separate "
                  "the jobs accordingly to each tunned bin region."))
  from rucio.client import DIDClient
  if len(parsedDataDS) > 1:
    scope = parsedDataDS
  else:
    import re
    pat = re.compile(r'(?P<scope>user.[a-zA-Z]+)\..*')
    m = pat.match(did)
    if m:
      scope = m.group('scope')
    else:
      scope = user_scope
  try:
    files = [d['name'] for d in didClient.list_files(scope, did)]
    from TuningTools import GridJobFilter
    ffilter = GridJobFilter()
    jobFilters = ffilter( files )
    mainLogger.info('Found following filters: %r', jobFilters)
    jobFileCollection = select( files, jobFilters )
    nFilesCollection = [len(l) for l in jobFileCollection]
    mainLogger.info("A total of %r files were found.", nFilesCollection )
  except DataIdentifierNotFound, e:
    mainLogger.fatal("Could not retrieve number of files on informed data DID. Rucio error:\n%s" % str(e))
except ImportError, e:
  mainLogger.fatal("rucio environment was not set, please set rucio and try again. Full error:\n%s" % str(e))

args.setMergeExec("""source ./setrootcore.sh --grid --no-color;
                     {fileMerging}
                      -i %IN
                      -o %OUT
                      {OUTPUT_LEVEL}
                  """.format( 
                              fileMerging  = r"\\\$ROOTCOREBIN/user_scripts/TuningTools/standalone/fileMerging.py" ,
                              OUTPUT_LEVEL = conditionalOption("--output-level",   args.output_level   ) if args.output_level is not LoggingLevel.INFO else '',
                            )
                 )


startBin = True
for jobFiles, nFiles, jobFilter in zip(jobFileCollection, nFilesCollection, jobFilters):
  #output_file = '{USER_SCOPE}.{MERGING_JOBID}.merge._000001.tunedDiscrXYZ.tgz'.format(
  #                USER_SCOPE = user_scope,
  #                MERGING_JOBID = jobFilter)
  if startBin:
    if args.get_job_submission_option('outTarBall') is None and not args.get_job_submission_option('inTarBall'):
      args.set_job_submission_option('outTarBall', 'workspace.tar')
    startBin = False
  else:
    if args.get_job_submission_option('outTarBall') is not None:
      # Swap outtar with intar
      args.set_job_submission_option('inTarBall', args.get_job_submission_option('outTarBall') )
      args.set_job_submission_option('outTarBall', None )
  # Now set information to grid argument
  args.set_job_submission_option('nFiles', nFiles)
  if args.gridExpand_debug is not None and args.get_job_submission_option('nFiles') > 800:
    args.set_job_submission_option('nFiles', 800)
  args.set_job_submission_option('nFilesPerJob', args.get_job_submission_option('nFiles'))
  args.set_job_submission_option('maxNFilesPerJob', args.get_job_submission_option('nFiles'))
  args.set_job_submission_option('match', '"' + jobFilter + '"')
  args.setExec("""source ./setrootcore.sh --grid --no-color;
                  {fileMerging} 
                    -i %IN
                    -o {OUTPUT_FILE}
                    {OUTPUT_LEVEL}
               """.format( fileMerging = "\$ROOTCOREBIN/user_scripts/TuningTools/standalone/fileMerging.py" ,
                           OUTPUT_FILE = output_file,
                           OUTPUT_LEVEL   = conditionalOption("--output-level",   args.output_level   ) 
                              if LoggingLevel.retrieve( args.output_level ) is not LoggingLevel.INFO else '',
                         )
              )
  # And run
  args.run_cmd()
  # FIXME We should want something more sofisticated
  if args.get_job_submission_option('debug') is not None:
    break
# Finished submitting all bins

#!/usr/bin/env python

from RingerCore import ( csvStr2List, str_to_class, NotSet, BooleanStr, WriteMethod
                       , get_attributes, expandFolders, Logger, getFilters, select
                       , appendToFileName, ensureExtension, progressbar, LoggingLevel
                       , printArgs, conditionalOption, emptyArgumentsPrintHelp, ArgumentParser)

from TuningTools.parsers import loggerParser

from TuningTools import GridJobFilter

mainParser = ArgumentParser( add_help = False)
mainGroup = mainParser.add_argument_group( "Required arguments", "")
mainGroup.add_argument('--inDS','-i', action='store',
                       required = True, dest = 'grid_inDS',
                       help = "The input Dataset ID (DID)")
mainGroup.add_argument('--outDS','-o', action='store',
                       required = True, dest = 'grid_outDS',
                       help = "The output Dataset ID (DID)")
parser = ArgumentParser(description = 'Attach the input container files to the output dataset, creating it if necessary.',
                       parents = [mainParser, loggerParser],
                       conflict_handler = 'resolve')
parser.make_adjustments()


emptyArgumentsPrintHelp(parser)

## Retrieve parser args:
args = parser.parse_args()

mainLogger = Logger.getModuleLogger(__name__, args.output_level)

try:
  from rucio.client import DIDClient, RuleClient
  from rucio.common.exception import DataIdentifierNotFound
  didClient = DIDClient()
  parsedInDataDS = args.grid_inDS.split(':')
  inDID = parsedInDataDS[-1]
  if len(parsedInDataDS) > 1:
    scope = parsedInDataDS[0]
  else:
    import re
    pat = re.compile(r'(?P<scope>user.[a-zA-Z]+)\..*')
    m = pat.match(inDID)
    if m:
      scope = m.group('scope')
    else:
      scope = user_scope
  try:
    files = [d['name'] for d in didClient.list_files(scope, inDID)]
    mainLogger.info("Found a total of %d files in the input container.", len(files))
    if mainLogger.isEnabledFor( LoggingLevel.VERBOSE ):
      from pprint import pprint
      pprint( files )
    #files = didClient.list_files(scope, inDID)
  except DataIdentifierNotFound, e:
    mainLogger.fatal("Could not retrieve number of files on informed data DID. Rucio error:\n%s" % str(e))
  #didClient.add_did(scope=scope, name=args.grid_outDS, type="dataset", dids=files, )
  from subprocess import Popen, PIPE
  add_ds_ps = Popen(('rucio','add-dataset',args.grid_outDS),stdout = PIPE, bufsize = 1)
  for line in iter(add_ds_ps.stdout.readline, b''):
    line = line.rstrip('\n')
    mainLogger.info( line )
  add_ds_ps.wait()
  rucioAttach=['rucio','attach',args.grid_outDS]
  rucioAttach.extend(files)
  attach_ps = Popen(rucioAttach, stdout = PIPE, bufsize = 1)
  for line in iter(attach_ps.stdout.readline, b''):
    line = line.rstrip('\n')
    mainLogger.info( line )
  attach_ps.wait()
  rule_ps = Popen(('rucio','add-rule', "--lifetime", str(120*24*3600), args.grid_outDS, "1", "CERN-PROD_SCRATCHDISK"), stdout = PIPE, bufsize = 1)
  for line in iter(rule_ps.stdout.readline, b''):
    line = line.rstrip('\n')
    mainLogger.info( "Added rule for \"CERN-PROD_SCRATCHDISK\": %s", line )
  rule_ps.wait()
  rule_ps = Popen(('rucio','add-rule', "--lifetime", str(120*24*3600), args.grid_outDS, "1", "BNL-OSG2_SCRATCHDISK"), stdout = PIPE, bufsize = 1)
  for line in iter(rule_ps.stdout.readline, b''):
    line = line.rstrip('\n')
    mainLogger.info( "Added rule for \"BNL-OSG2_SCRATCHDISK\": %s", line )
  rule_ps.wait()
except ImportError, e:
  mainLogger.fatal("rucio environment was not set, please set rucio and try again. Full error:\n%s" % str(e), ImportError)



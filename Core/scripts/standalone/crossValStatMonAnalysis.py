#!/usr/bin/env python




def filterPaths(paths, grid=False):
  oDict = dict()
  import re
  from RingerCore import checkExtension
  if grid is True:
    #pat = re.compile(r'.*user.[a-zA-Z0-9]+.(?P<jobID>[0-9]+)\..*$')
    pat = re.compile(r'.*crossValStat_(?P<jobID>[0-9]+)(_monitoring)?\..*$')
    jobIDs = sorted(list(set([pat.match(f).group('jobID')  for f in paths if pat.match(f) is not None]))) 
    for jobID in jobIDs:
      oDict[jobID] = dict()
      for xname in paths:
        if jobID in xname and checkExtension( xname, '.root'): oDict[jobID]['root'] = xname
        if jobID in xname and checkExtension( xname, '.pic|.pic.gz|.pic.tgz'): oDict[jobID]['pic'] = xname
  else:

    #pat = re.compile(r'.*crossValStat_(?P<jobID>[0-9]+)(_monitoring)?\..*$')
    pat = re.compile(r'.+(?P<binID>et(?P<etBinIdx>\d+).eta(?P<etaBinIdx>\d+))\..+$')
   # jobIDs = sorted(list(set([pat.match(f).group('jobID')  for f in paths if pat.match(f) is not None]))) 
    jobIDs = sorted(list(set([pat.match(f).group('binID')  for f in paths if pat.match(f) is not None]))) 
    if not len( jobIDs):
      oDict['unique'] = {'root':'','pic':''}
      for xname in paths:
        if xname.endswith('.root'): oDict['unique']['root'] = xname
        if '.pic' in xname: oDict['unique']['pic'] = xname
    else:
      for jobID in jobIDs:
        oDict[jobID] = dict()
        for xname in paths:
          if jobID in xname and checkExtension( xname, '.root'): oDict[jobID]['root'] = xname
          if jobID in xname and checkExtension( xname, '.pic|.pic.gz|.pic.tgz'): oDict[jobID]['pic'] = xname
       

  return oDict


from RingerCore import csvStr2List, str_to_class, NotSet, BooleanStr, emptyArgumentsPrintHelp
from TuningTools.parsers import ArgumentParser, loggerParser, crossValStatsMonParser, LoggerNamespace
from TuningTools import GridJobFilter

parser = ArgumentParser(description = 'Retrieve performance information from the Cross-Validation method.',
                       parents = [crossValStatsMonParser, loggerParser])
parser.make_adjustments()

emptyArgumentsPrintHelp( parser )

# Retrieve parser args:
args = parser.parse_args(namespace = LoggerNamespace() )

from RingerCore import Logger, LoggingLevel, printArgs
logger = Logger.getModuleLogger( __name__, args.output_level )

printArgs( args, logger.debug )


#Find files
from RingerCore import expandFolders, ensureExtension,keyboard
logger.info('Expand folders and filter')
paths = expandFolders(args.file)
print paths
paths = filterPaths(paths, args.grid)


from pprint import pprint
logger.info('Grid mode is: %s',args.grid)
pprint(paths)

from TuningTools import MonitoringTool


csummaryList = []
etBinMax=0; etaBinMax=0
#Loop over job grid, basically loop over user...
for idx, jobID in enumerate(paths):
  logger.info( ('Start from job tag: %s [%d/%d]')%(jobID,idx+1,len(paths)))
  #If files from grid, we must put the bin tag
  output = args.output
  #Create the monitoring object
  monitoring = MonitoringTool( paths[jobID]['pic'], 
                               paths[jobID]['root'], 
                               level = args.output_level,
                               )
  c = monitoring(dirname=args.output, doBeamer=args.doBeamer)
  if c['etBinIdx']  > etBinMax:  etBinMax=c['etBinIdx']
  if c['etaBinIdx'] > etaBinMax: etaBinMax=c['etaBinIdx']
  csummaryList.append( c )
  del monitoring

### list to binned grid

summary = [[None for _ in range(etaBinMax+1) ] for __ in range(etBinMax+1)]
for c in csummaryList:
  summary[c['etBinIdx']][c['etaBinIdx']] = c


print 'saving summary...'
from RingerCore import save
### Save this for backup
save( summary, args.output+'/summary')
print 'loading...'
### Built the final table
MonitoringTool.ttReport( args.output+'/summary.pic.gz', args.dataPath, outname= args.output+'/'+args.output, title=args.output, toPDF=False ) 
MonitoringTool.ttReport( args.output+'/summary.pic.gz', args.dataPath, outname= args.output+'/'+args.output, title=args.output, toPDF=True ) 
#MonitoringTool.ttReport( args.output+'_summary.pic.gz', args.dataPath, args.output, toPDF=True ) 






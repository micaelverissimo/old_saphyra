

from Gaugi import Logger

class Summary(Logger):
  
  def __init__(self, benchmark, summary):
    Logger.__init__(self)
    self._summary = summary
    self._benchmark = benchmark
    self._initBounds=None

  def neuronBounds(self):
    neuronBounds = [int(neuron.replace('config_','')) for neuron in self._summary.keys() if 'config_' in neuron]
    neuronBounds.sort()
    return neuronBounds

  def sortBounds(self, neuron):
    sortBounds = [int(sort.replace('sort_','')) for sort in self._summary['config_'+str(neuron).zfill(3)].keys() \
                  if 'sort_' in sort]
    sortBounds.sort()
    return sortBounds

  def setInitBounds( self, v ):
    self._initBounds=v

  def initBounds(self, neuron, sort):
    if self._initBounds:
      return self._initBounds
    else:
      def GetInits(sDict):
        initBounds = list(set([sDict['infoOpBest']['init'], sDict['infoOpWorst']['init'], \
                       sDict['infoTstBest']['init'], sDict['infoTstWorst']['init']]))
        initBounds.sort()
        return initBounds
      return GetInits(self._summary['config_'+str(neuron).zfill(3)]['sort_'+str(sort).zfill(3)])

  def benchmark(self):
    return self._benchmark

  def reference(self):
    return self._summary['rawBenchmark']['reference']

  def etBinIdx(self):
    return self._summary['etBinIdx']

  def etaBinIdx(self):
    return self._summary['etaBinIdx']

  def etBin(self):
    return self._summary['etBin']

  def etaBin(self):
    return self._summary['etaBin']

  def rawSummary(self):
    return self._summary

  def __getitem__(self, key):
    return self._summary[key]

  def thresholdType(self):
    return self._summary['infoOpBest']['cut']['class']


def filterPaths(paths, grid=False):
  oDict = dict()
  import re
  from Gaugi import checkExtension
  if grid is True:
    pat = re.compile(r'.*user.[a-zA-Z0-9]+.(?P<jobID>[0-9]+)\..*$')
    jobIDs = sorted(list(set([pat.match(f).group('jobID')  for f in paths if pat.match(f) is not None]))) 
    for jobID in jobIDs:
      oDict[jobID] = dict()
      for xname in paths:
        if jobID in xname and checkExtension( xname, '.root'): oDict[jobID]['root'] = xname
        if jobID in xname and checkExtension( xname, '.pic|.pic.gz|.pic.tgz'): oDict[jobID]['pic'] = xname
  else:

    pat = re.compile(r'.*crossValStat_(?P<jobID>[0-9]+)(_monitoring)?\..*$')
    jobIDs = sorted(list(set([pat.match(f).group('jobID')  for f in paths if pat.match(f) is not None]))) 
    if not len( jobIDs):
      oDict['unique'] = {'root':'','pic':''}
      for xname in paths:
        if xname.endswith('.root'): oDict['unique']['root'] = xname
        if '.pic' in xname: oDict['unique']['pic'] = xname
    else:
      for jobID in jobIDs:
        print jobID
        oDict[jobID] = dict()
        for xname in paths:
          if jobID in xname and checkExtension( xname, '.root'): oDict[jobID]['root'] = xname
          if jobID in xname and checkExtension( xname, '.pic|.pic.gz|.pic.tgz'): oDict[jobID]['pic'] = xname
  return oDict




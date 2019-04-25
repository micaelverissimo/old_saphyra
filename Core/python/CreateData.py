__all__ = ['TuningDataArchieve', 'CreateData', 'createData','BenchmarkEfficiencyArchieve'
          ,'BranchCrossEffCollector','BranchEffCollector']

_noProfilePlot = False
try:
  import scipy.stats
except ImportError as _noProfileImportError:
  _noProfilePlot = True
try:
  import matplotlib as mpl
  mpl.use('Agg')
  import matplotlib.pyplot as plt
  import matplotlib.patches as patches
except (ImportError, OSError) as _noProfileImportError:
  _noProfilePlot = True

from Gaugi import ( Logger, checkForUnusedVars, reshape, save, load, traverse
                       , retrieve_kw, NotSet, appendToFileName, LoggerRawDictStreamer
                       , RawDictCnv, LoggerStreamable, ensureExtension, secureExtractNpItem
                       , progressbar, RawDictStreamer, RawDictStreamable, csvStr2List
                       , expandFolders
                       )

from TuningTools.coreDef import npCurrent
from TuningTools.dataframe import Dataset
import numpy as np
import ROOT

class BranchEffCollectorRDS( RawDictStreamer ):
  def treatDict(self, obj, raw):
    """
    Add efficiency value to be readable in matlab
    """
    raw['efficiency'] = obj.efficiency
    #raw['__version '] = obj._version
    raw['etBin'] = '' if obj.etBin is None else obj.etBin
    raw['etaBin'] = '' if obj.etaBin is None else obj.etaBin
    return RawDictStreamer.treatDict( self, obj, raw )

class BranchEffCollectorRDC( RawDictCnv ):
  def treatObj( self, obj, d ):
    from Gaugi import keyboard
    if obj._readVersion is 2:
      self._verbose("BranchEffCollector etBin has the same value of etaBin due to a bug, please move to a newer file unless you know what you are doing.")
    obj._etBin = None if d['etBin'] is '' else d['etBin']
    obj._etaBin = None if d['etaBin'] is '' else d['etaBin']
    return obj

class BranchEffCollector(object):
  """
    Simple class for counting passed events using input branch

    - Version 3: Fixed bug when saving etaBin
    - Version 2: Save None as ''
  """

  __metaclass__ = RawDictStreamable
  _streamerObj  = BranchEffCollectorRDS( toPublicAttrs = {'_etaBin', '_etBin'} )
  _cnvObj       = BranchEffCollectorRDC( ignoreAttrs = {'efficiency'}, toProtectedAttrs = {'_etaBin', '_etBin'}, )
  _version      = 3

  def __init__(self, name = '', branch = '', etBin = -1, etaBin = -1, crossIdx = -1, ds = Dataset.Unspecified):
    self._ds = ds if ds is None else Dataset.retrieve(ds)
    self.name = name
    self._branch = branch
    self._etBin = etBin
    self._etaBin = etaBin
    self._crossIdx = crossIdx
    self._passed = 0
    self._count = 0

  @property
  def etBin(self):
    return self._etBin

  @property
  def etaBin(self):
    return self._etaBin

  @property
  def crossIdx(self):
    return self._crossIdx

  @property
  def ds(self):
    return self._ds

  @property
  def printName(self):
    return (Dataset.tostring(self.ds) + '_' if self.ds not in (None,Dataset.Unspecified) else '') + \
        self.name + \
        (('_etBin%d') % self.etBin if self.etBin not in (None,-1) else '') + \
        (('_etaBin%d') % self.etaBin if self.etaBin not in (None,-1) else '') + \
        (('_x%d') % self.crossIdx if self.crossIdx not in (None,-1) else '')

  def update(self, event, total = None):

    # helper function to get the decision bool value
    def get_dec(v):
      # list of bool values
      if type(v) is ROOT.std.vector:
        return any(stdvector_to_list(v))
      else: # bool single value
        return v

    " Update the counting. "
    if total is not None:
      self._passed += event
      self._count += total
      return
    elif get_dec(getattr(event,self._branch)):
      self._passed += 1
    self._count += 1

  @property
  def efficiency(self):
    " Returns efficiency in percentage"
    if self._count:
      return self._passed / float(self._count) * 100.
    else:
      return 0.

  def setEfficiency(self, percentage):
    "Set efficiency in percentage"
    self._passed = (percentage/100.);
    self._count = 1

  @property
  def passed(self):
    "Total number of passed occurrences"
    return self._passed

  @property
  def count(self):
    "Total number of counted occurrences"
    return self._count

  def eff_str(self):
    "Retrieve the efficiency string"
    return '%.6f (%d/%d)' % ( self.efficiency,
                              self._passed,
                              self._count )
  def __str__(self):
    return (self.printName + " : " + self.eff_str() )

class BranchCrossEffCollectorRDS(RawDictStreamer):

  def __init__(self, **kw):
    RawDictStreamer.__init__( self, transientAttrs = {'_output'}, toPublicAttrs = {'_etaBin', '_etBin'}, **kw )
    self.noChildren = False

  def treatDict(self, obj, raw):
    """
    Method dedicated to modifications on raw dictionary
    """
    raw['__version'] = obj._version
    # Treat special members:
    if self.noChildren:
      raw.pop('_crossVal')
    self.deepCopyKey( raw, '_branchCollectorsDict')
    if raw['_branchCollectorsDict']:
      from copy import deepcopy
      raw['_branchCollectorsDict'] = deepcopy( raw['_branchCollectorsDict'] )
      for cData, idx, parent, _, _ in traverse(raw['_branchCollectorsDict'].values()):
        if self.noChildren:
          parent[idx] = cData.efficiency
        else:
          parent[idx] = cData.toRawObj()
    else:
      raw['_branchCollectorsDict'] = ''
    # And now add the efficiency member
    raw['efficiency'] = { Dataset.tostring(key) : val for key, val in obj.allDSEfficiency.iteritems() }
    if not raw['efficiency']:
      raw['efficiency'] = ''
    raw['etBin'] = '' if obj.etBin is None else obj.etBin
    raw['etaBin'] = '' if obj.etaBin is None else obj.etaBin
    raw['_crossVal'] = '' if obj._crossVal is None else obj._crossVal
    # Use default treatment
    RawDictStreamer.treatDict(self, obj, raw)
    return raw

class BranchCrossEffCollectorRDC( RawDictCnv ):

  def __init__(self, **kw):
    RawDictCnv.__init__( self, ignoreAttrs = {'efficiency'}, toProtectedAttrs = {'_etaBin', '_etBin'}, **kw )

  def treatObj( self, obj, d ):
    if obj._readVersion is 3:
      self._error("BranchCrossEffCollector object etBin has the same value of etaBin due to a bug, please move to a newer file unless you know what you are doing.")
    if not 'version' in d:
      obj._readVersion = 0
    obj._crossVal = None
    if '_crossVal' in d:
      if type(d['_crossVal']) is dict: # Treat old files
        from TuningTools.CrossValid import CrossValid
        obj._crossVal = CrossValid.fromRawObj( d['_crossVal'] )
    if type( obj._branchCollectorsDict ) is dict:
      for cData, idx, parent, _, _ in traverse(obj._branchCollectorsDict.values()):
        if not 'version' in d:
          # Old version
          parent[idx] = BranchEffCollector.fromRawObj( cData )
        else:
          from Gaugi import retrieveRawDict
          parent[idx] = retrieveRawDict( cData )
        if parent[idx] is cData:
          break
    else:
      obj._branchCollectorsDict = {}
    if obj._readVersion < 2:
      obj._valAsTst = True
    obj._etBin = None if d['etBin'] is '' else d['etBin']
    obj._etaBin = None if d['etaBin'] is '' else d['etaBin']
    return obj

class BranchCrossEffCollector(object):
  """
  Object for calculating the cross-validation datasets efficiencies

  - Version 4: Fixed bug when saving etaBin
  - Version 3: Save None as ''
  - Version 2: added _valAsTst
  """

  __metaclass__ = RawDictStreamable
  _streamerObj  = BranchCrossEffCollectorRDS()
  _cnvObj       = BranchCrossEffCollectorRDC()
  _version      = 4

  dsList = [ Dataset.Train,
             Dataset.Validation,
             Dataset.Test, ]

  def __init__(self, nevents=-1, crossVal=None, name='', branch='', etBin=-1, etaBin=-1):
    self.name = name
    self._count = 0
    self._branch = branch
    self._output = npCurrent.flag_ones(nevents) * -1 if nevents > 0 else npCurrent.flag_ones([])
    self._etBin = etBin
    self._etaBin = etaBin
    self._valAsTst = crossVal.nTest() if crossVal is not None else False
    from TuningTools.CrossValid import CrossValid
    if crossVal is not None and not isinstance(crossVal, CrossValid):
      self._fatal('Wrong cross-validation object.')
    self._crossVal = crossVal
    self._branchCollectorsDict = {}
    if self._crossVal is not None:
      for ds in BranchCrossEffCollector.dsList:
        if ds == Dataset.Test and self._valAsTst: continue
        self._branchCollectorsDict[ds] = \
            [BranchEffCollector(name, branch, etBin, etaBin, sort, ds) \
               for sort in range(self._crossVal.nSorts())]

  @property
  def etBin(self):
    return self._etBin

  @property
  def etaBin(self):
    return self._etaBin

  @property
  def allDSEfficiency(self):
    return self.efficiency()

  @property
  def allDSCount(self):
    return self.count()

  @property
  def allDSPassed(self):
    return self.passed()

  @property
  def allDSEfficiencyList(self):
    return self.efficiencyList()

  @property
  def allDSListCount(self):
    return self.countList()

  @property
  def allDSPassedList(self):
    return self.passedList()

  @property
  def printName(self):
    return self.name + \
        (('_etBin%d') % self.etBin if self.etBin is not None else '') + \
        (('_etaBin%d') % self.etaBin if self.etaBin is not None else '')

  def update(self, event):
    " Update the looping data. "
    if getattr(event,self._branch):
      self._output[self._count] = 1
    else:
      self._output[self._count] = 0
    self._count += 1

  def finished(self):
    " Call after looping is finished"
    # Strip uneeded values
    self._output = self._output[self._output != -1]
    #print 'Stripped output is (len=%d: %r)' % (len(self._output), self._output)
    maxEvts = len(self._output)
    for sort in range(self._crossVal.nSorts()):
      for ds, val in self._branchCollectorsDict.iteritems():
        for box in self._crossVal.getBoxIdxs(ds, sort):
          startPos, endPos = self._crossVal.getBoxPosition(sort, box, maxEvts=maxEvts )
          #print 'sort %d: startPos, endPos (%d,%d)' % (sort, startPos, endPos)
          boxPassed = np.sum( self._output[startPos:endPos] == 1 )
          boxTotal = endPos - startPos
          val[sort].update( boxPassed, boxTotal )
          #print '%s_%s=%d/%d' % ( self.name, Dataset.tostring(ds), boxPassed, boxTotal)
    # Release data, not needed anymore
    self._output = None

  def __retrieveInfo(self, attr, ds = Dataset.Unspecified, sort = None):
    "Helper function to retrieve cross-validation reference mean/std information"
    if ds is Dataset.Unspecified:
      retDict = {}
      for ds, branchEffCol in self._branchCollectorsDict.iteritems():
        if sort is not None:
          retDict[ds] = getattr(branchEffCol[sort], attr)
        else:
          info = self.__retrieveInfoList(attr, ds)
          retDict[ds] = (np.mean(info), np.std(info))
      return retDict
    else:
      if ds is Dataset.Test and not self._valAsTst:
        ds = Dataset.Validation
      if sort is not None:
        return getattr(self._branchCollectorsDict[ds][sort], attr)
      else:
        info = self.__retrieveInfoList(attr, ds)
        return (np.mean(info), np.std(info))

  def __retrieveInfoList(self, attr, ds = Dataset.Unspecified, ):
    " Helper function to retrieve cross-validation information list"
    if ds is Dataset.Unspecified:
      retDict = {}
      for ds, branchEffCol in self._branchCollectorsDict.iteritems():
        retDict[ds] = [ getattr( branchEff, attr) for branchEff in branchEffCol ]
      return retDict
    else:
      if ds is Dataset.Test and not self._valAsTst:
        ds = Dataset.Validation
      return [ getattr( branchEff, attr ) for branchEff in self._branchCollectorsDict[ds] ]

  def efficiency(self, ds = Dataset.Unspecified, sort = None):
    " Returns efficiency in percentage"
    return self.__retrieveInfo( 'efficiency', ds, sort )

  def passed(self, ds = Dataset.Unspecified, sort = None):
    " Returns passed counts"
    return self.__retrieveInfo( 'passed', ds, sort )

  def count(self, ds = Dataset.Unspecified, sort = None):
    " Returns total counts"
    return self.__retrieveInfo( 'count', ds, sort )

  def efficiencyList(self, ds = Dataset.Unspecified ):
    " Returns efficiency in percentage"
    return self.__retrieveInfoList( 'efficiency', ds)

  def passedList(self, ds = Dataset.Unspecified):
    "Total number of passed occurrences"
    return self.__retrieveInfoList( 'passed', ds )

  def countList(self, ds = Dataset.Unspecified):
    "Total number of counted occurrences"
    return self.__retrieveInfoList( 'count', ds )

  def eff_str(self, ds = Dataset.Unspecified, format_ = 'long'):
    "Retrieve the efficiency string"
    if ds is Dataset.Unspecified:
      retDict = {}
      for ds, val in self._branchCollectorsDict.iteritems():
        eff = self.efficiency(ds)
        passed = self.passed(ds)
        count = self.count(ds)
        retDict[ds] = '%.6f +- %.6f (count: %.4f/%.4f +- %.4f/%.4f)' % ( eff[0], eff[1],
                                  passed[0], count[0],
                                  passed[1], count[1],)
      return retDict
    else:
      if ds is Dataset.Test and \
          not self._crossVal.nTest():
        ds = Dataset.Validation
      eff = self.efficiency(ds)
      passed = self.passed(ds)
      count = self.count(ds)
      return '%.6f +- %.6f (count: %.4f/%.4f +- %.4f/%.4f)' % ( eff[0], eff[1],
                                passed[0], count[0],
                                passed[1], count[1],)

  def __str__(self):
    "String representation of the object."
    # FIXME check itertools for a better way of dealing with all of this
    trnEff = self.efficiency(Dataset.Train)
    valEff = self.efficiency(Dataset.Validation)
    return self.printName + ( " : Train (%.6f +- %.6f) | Val (%6.f +- %.6f)" % \
         (trnEff[0], trnEff[1], valEff[0], valEff[1]) ) \
         + ( " Test (%.6f +- %.6f)" % self.efficiency(Dataset.Test) if self._valAsTst else '')

  def dump(self, fcn, **kw):
    "Dump efficiencies using log function."
    printSort = kw.pop('printSort', False)
    sortFcn = kw.pop('sortFcn', None)
    if printSort and sortFcn is None:
      self._fatal(('When the printSort flag is True, it is also needed to '
          'specify the sortFcn.'), TypeError)
    for ds, str_ in self.eff_str().iteritems():
      fcn(self.printName +  " : " + str_)
      if printSort:
        for branchCollector in self._branchCollectorsDict[ds]:
          sortFcn('%s', branchCollector)

class BenchmarkEfficiencyArchieveRDS( LoggerRawDictStreamer ):
  """
  The BenchmarkEfficiencyArchieve RawDict Streamer
  """

  def __init__(self, **kw):
    LoggerRawDictStreamer.__init__( self,
        transientAttrs = {'_readVersion', '_signalPatterns', '_backgroundPatterns',
                          '_signalBaseInfo', '_backgroundBaseInfo',
                          '_etaBinIdx', '_etBinIdx',} | kw.pop('transientAttrs', set()),
        toPublicAttrs = {'_signalEfficiencies','_backgroundEfficiencies',
                         '_signalCrossEfficiencies','_backgroundCrossEfficiencies',
                         '_etaBins', '_etBins', '_operation', '_nEtBins','_nEtaBins',
                         '_isEtaDependent', '_isEtDependent',
                        } | kw.pop('toPublicAttrs', set()),
        **kw )

  def treatDict(self, obj, raw):
    """
    Method dedicated to modifications on raw dictionary
    """
    from TuningTools import RingerOperation
    raw['operation'] = RingerOperation.retrieve(raw['operation'])
    # Handle efficiencies
    if obj._signalEfficiencies and obj._backgroundEfficiencies:
      self.deepCopyKey(raw, 'signalEfficiencies')
      self.deepCopyKey(raw, 'backgroundEfficiencies')
      TuningDataArchieveRDS.efficiencyToRaw(raw['signalEfficiencies'])
      TuningDataArchieveRDS.efficiencyToRaw(raw['backgroundEfficiencies'])
    if obj._signalCrossEfficiencies and obj._backgroundCrossEfficiencies:
      self.deepCopyKey(raw, 'signalCrossEfficiencies')
      self.deepCopyKey(raw, 'backgroundCrossEfficiencies')
      TuningDataArchieveRDS.efficiencyToRaw(raw['signalCrossEfficiencies'])
      TuningDataArchieveRDS.efficiencyToRaw(raw['backgroundCrossEfficiencies'])
    #import TuningTools, RingerCore
    #raw['RingerCore__version__'], raw['TuningTools__version__'] = RingerCore.__version__, TuningTools.__version__
    #raw['Project__version__'] = ProjectGit.tag
    return raw
  # end of getData

  @staticmethod
  def efficiencyToRaw(d):
    for key, val in d.iteritems():
      for cData, idx, parent, _, _ in traverse(val):
        if parent is None:
          d[key] = cData.toRawObj()
        else:
          parent[idx] = cData.toRawObj()

class BenchmarkEfficiencyArchieveRDC( RawDictCnv ):
  """
  The Benchmark Efficiency RawDict Converter
  """

  def __init__(self, **kw):
    RawDictCnv.__init__( self,
                         ignoreAttrs = {'type|version',
              '(signal|background)(Patterns|Et|Eta|Nvtx|avgmu|_patterns|_rings).*',
                                        '(eta|et)_bins'} | kw.pop('ignoreAttrs', set()),
                         toProtectedAttrs = {'_etaBins', '_etBins', '_operation', '_nEtBins','_nEtaBins',
                                             '_isEtaDependent','_isEtDependent',} | kw.pop('toProtectedAttrs', set()),
                         **kw )
    self.etaBinIdx = None
    self.etBinIdx = None
    self.loadEfficiencies = True
    self.loadCrossEfficiencies = False
    self.sgnEffKey, self.bkgEffKey  = 'signalEfficiencies', 'backgroundEfficiencies'
    self.sgnCrossEffKey, self.bkgCrossEffKey = 'signalCrossEfficiencies', 'backgroundCrossEfficiencies'

  def checkBins(self, isEtaDependent, isEtDependent, nEtaBins, nEtBins ):
    """
    Check if self._etaBinIdx and self._etBinIdx are ok, through otherwise.
    """
    # FIXME Use new format...
    # Check if eta/et bin requested can be retrieved.
    errmsg = ""

    etaBinIdx = self.etaBinIdx
    if type(self.etaBinIdx) in (list,tuple):
      etaBinIdx = self.etaBinIdx[-1]
    etBinIdx = self.etBinIdx
    if type(self.etBinIdx) in (list,tuple):
      etBinIdx = self.etBinIdx[-1]
    if etaBinIdx >= nEtaBins:
      errmsg += "Cannot retrieve etaBin(%d). %s" % (etaBinIdx,
          ('Eta bin size: ' + str(nEtaBins) + '. ') if isEtaDependent else 'Cannot use eta bins. ')
    if etBinIdx >= nEtBins:
      errmsg += "Cannot retrieve etBin(%d). %s" % (etBinIdx,
          ('E_T bin size: ' + str(nEtBins) + '. ') if isEtDependent else ' Cannot use E_T bins. ')
    if errmsg:
      self._fatal(errmsg)

  def retrieveRawEff(self, d, etBins = None, etaBins = None, cl = None, renewCross = False):
    if cl is None: cl = BranchEffCollector
    if d is not None:
      if type(d) is np.ndarray:
        d = d.item()
      for key, val in d.iteritems():
        if etBins is None or etaBins is None:
          for cData, idx, parent, _, _ in traverse(val):
            if parent is None:
              d[key] = cl.fromRawObj(cData)
            else:
              parent[idx] = cl.fromRawObj(cData)
        else:
          isItrEt = isinstance(etBins,(list,tuple))
          isItrEta = isinstance(etaBins,(list,tuple))
          if isItrEt or isItrEta:
            if not isItrEt: etBins = [etBins]
            if not isItrEta: etaBins = [etaBins]
            d[key] = []
            for cEtBin, etBin in enumerate(etBins):
              d[key].append([])
              for etaBin in etaBins:
                d[key][cEtBin].append(cl.fromRawObj(val[etBin][etaBin]))
                if renewCross:
                  effCol = d[key][cEtBin][-1]
                  from copy import copy
                  effCol._crossValid = effCol._crossValid._cnvObj.treatObj( effCol._crossValid, copy( effCol._crossValid.__dict__ ) )
          else:
            if all(val):
              d[key] = cl.fromRawObj(val[etBins][etaBins])
            else:
              d.pop(key)
    return d

  def treatObj( self, obj, npData ):
    if 'version' in npData:
      # Treat versions 1 -> 5
      obj._readVersion = npData['version']
    if not '__version' in npData and not 'version' in npData and any(['backgroundPatterns_' in k for k in npData]):
      obj._readVersion = np.array(5)
      obj._etBins = npCurrent.fp_array( npData['etBins'] if 'etBins' in npData else npCurrent.array([]) )
      self._warning("Reading TuningDataArchieve version 5, it may be that current eta information is invalid. If you face issues when accessing eta information, please contact the developers.")
      obj._etaBins = npCurrent.fp_array( [0, 0.8, 1.37, 1.54, 2.5] )
      from TuningTools.dataframe import RingerOperation
      obj._operation = RingerOperation.L2Calo

    if self.loadEfficiencies:
      if obj._readVersion <= np.array(5) and not any(['backgroundPatterns_' in k for k in npData]):
        self.sgnEffKey, self.bkgEffKey  = 'signal_efficiencies', 'background_efficiencies'
        self.sgnCrossEffKey, self.bkgCrossEffKey = 'signal_cross_efficiencies','background_cross_efficiencies',
    if obj._readVersion < np.array(6):
      if 'et_bins' in npData:
        obj._etBins = npCurrent.fp_array( npData['et_bins'] if 'et_bins' in npData else npCurrent.array([]) )
        obj._etaBins = npCurrent.fp_array( npData['eta_bins'] if 'eta_bins' in npData else npCurrent.array([]) )
      else:
        obj._etBins = npCurrent.fp_array( npData['etBins'] if 'etBins' in npData else npCurrent.array([]) )
        obj._etaBins = npCurrent.fp_array( npData['etaBins'] if 'etaBins' in npData else npCurrent.array([]) ) if not any(['backgroundPatterns_' in k for k in npData]) else npCurrent.array([0, 0.8, 1.37, 1.54, 2.5])
      obj._nEtBins  = obj.etBins.size - 1 if obj.etBins.size - 1 > 0 else 0
      obj._nEtaBins = obj.etaBins.size - 1 if obj.etaBins.size - 1 > 0 else 0
      obj._isEtDependent = obj.etBins.size > 0
      obj._isEtaDependent = obj.etaBins.size > 0
    if obj._readVersion < np.array(4):
      from TuningTools.dataframe import RingerOperation
      obj._operation = RingerOperation.EFCalo
    # Check if requested bins are ok
    self.checkBins(obj.isEtaDependent, obj.isEtDependent, obj.nEtaBins, obj.nEtBins)
    if self.loadEfficiencies:
      try:
        obj._signalEfficiencies = self.retrieveRawEff(npData[self.sgnEffKey], self.etBinIdx, self.etaBinIdx)
      except KeyError:
        self._logger.error("Signal efficiencies information is not available!")
      try:
        if obj._readVersion == np.array(5) and any(['backgroundPatterns_' in k for k in npData]):
          from collections import OrderedDict
          if self.etBinIdx is not None:
            obj._backgroundEfficiencies = OrderedDict([(branch, BranchEffCollector( branch, branch, self.etBinIdx, self.etaBinIdx, ), ) for branch in ('L2CaloAccept', 'L2ElAccept', 'EFCaloAccept', 'HLTAccept',) ])
          else:
            obj._backgroundEfficiencies = OrderedDict([(branch, [[BranchEffCollector( branch, branch, etidx, etaidx, ) for etidx in xrange(obj._nEtBins)] for etaidx in xrange(obj._nEtaBins)], ) for branch in ('L2CaloAccept', 'L2ElAccept', 'EFCaloAccept', 'HLTAccept',) ])
          for b in obj._backgroundEfficiencies.itervalues():
            if isinstance(b,list):
              from Gaugi import straverse
              for bb in straverse(b): bb.setEfficiency( 5. )
            else:
              b.setEfficiency( 5. )
        else:
          obj._backgroundEfficiencies = self.retrieveRawEff(npData[self.bkgEffKey], self.etBinIdx, self.etaBinIdx)
      except KeyError:
        self._logger.error("Background efficiencies information is not available!")
      if self.loadCrossEfficiencies:
        try:
          obj._signalCrossEfficiencies = self.retrieveRawEff(npData[self.sgnCrossEffKey],
                                                             self.etBinIdx, self.etaBinIdx,
                                                             BranchCrossEffCollector, obj._readVersion < 4)
        except (KeyError, IndexError):
          # NOTE: Do we want to create a special exception and raise it to be
          # sure to be handling the right cases?
          self._info("No signal cross efficiency information.")
        try:
          obj._backgroundCrossEfficiencies = self.retrieveRawEff(npData[self.bkgCrossEffKey],
                                                                 self.etBinIdx, self.etaBinIdx,
                                                                 BranchCrossEffCollector, obj._readVersion < 4)
            # Renew CrossValid objects that are being read using pickle:
        except (KeyError, IndexError):
          self._info("No background cross efficiency information.")
    # Check etBins and etaBins:
    lEtBinIdxs = self.etBinIdx if self.etBinIdx is not None else range(obj.nEtBins)
    lEtaBinIdxs = self.etaBinIdx if self.etaBinIdx is not None else range(obj.nEtaBins)
    if type(lEtBinIdxs) not in (list,tuple): lEtBinIdxs = [lEtBinIdxs]
    if type(lEtaBinIdxs) not in (list,tuple): lEtaBinIdxs = [lEtaBinIdxs]
    if obj.isEtDependent:
      indexes = list(lEtBinIdxs[:]); indexes.append(indexes[-1]+1)
      obj._etBins = obj.etBins[indexes]
    if obj.isEtaDependent:
      indexes = list(lEtaBinIdxs[:]); indexes.append(indexes[-1]+1)
      obj._etaBins = obj.etaBins[indexes]
    # Add binning information
    obj._etBinIdx = self.etBinIdx
    obj._etaBinIdx = self.etaBinIdx
    # Check if numpy information fits with the information representation we
    # need:
    obj._etaBins = npCurrent.fix_fp_array(obj._etaBins)
    obj._etBins = npCurrent.fix_fp_array(obj._etBins)
    return obj

class BenchmarkEfficiencyArchieve( LoggerStreamable ):
  """
    Efficiency template file containing the benchmarks to be used.
  """

  _streamerObj = BenchmarkEfficiencyArchieveRDS()
  _cnvObj = BenchmarkEfficiencyArchieveRDC()
  _version = 8 # Changes in both archieves should increase versioning control.

  def __init__(self, d = {}, **kw):
    d.update(kw)
    Logger.__init__(self, d)
    self._etaBins                     = d.pop( 'etaBins',                     npCurrent.fp_array([]) )
    self._etBins                      = d.pop( 'etBins',                      npCurrent.fp_array([]) )
    self._signalEfficiencies          = d.pop( 'signalEfficiencies',          None                   )
    self._backgroundEfficiencies      = d.pop( 'backgroundEfficiencies',      None                   )
    self._signalCrossEfficiencies     = d.pop( 'signalCrossEfficiencies',     None                   )
    self._backgroundCrossEfficiencies = d.pop( 'backgroundCrossEfficiencies', None                   )
    self._etaBinIdx                   = d.pop( 'etaBinIdx',                   None                   )
    self._etBinIdx                    = d.pop( 'etBinIdx',                    None                   )
    self._operation                   = d.pop( 'operation',                   None                   )
    self._label                       = d.pop( 'label',                       NotSet                 )
    self._collectGraphs = []
    checkForUnusedVars( d, self._warning )
    self._nEtaBins = self._etaBins.size - 1 if self._etaBins.size - 1 > 0 else 0
    self._nEtBins  = self._etBins.size - 1 if self._etBins.size - 1 > 0 else 0
    self._isEtaDependent = self._etaBins.size > 0
    self._isEtDependent = self._etBins.size > 0
    self._etaBins = npCurrent.fp_array(self._etaBins)
    self._etBins  = npCurrent.fp_array(self._etBins)

  @property
  def etaBinIdx( self ):
    return secureExtractNpItem( self._etaBinIdx )

  @property
  def etBinIdx( self ):
    return secureExtractNpItem( self._etBinIdx )

  @property
  def etaBins( self ):
    return self._etaBins

  @property
  def etBins( self ):
    return self._etBins

  @property
  def isEtDependent( self ):
    return secureExtractNpItem( self._isEtDependent )

  @property
  def isEtaDependent( self ):
    return secureExtractNpItem( self._isEtaDependent )

  @property
  def maxEtBinIdx(self):
    "Return maximum eta bin index. If variable is not dependent on bin, return None."
    return self.nEtBin - 1

  @property
  def nEtBins(self):
    "Return number of et bins. If variable is not dependent on bin, return None."
    return secureExtractNpItem( self._nEtBins )

  @property
  def maxEtaBinIdx(self):
    "Return maximum eta bin index. If variable is not dependent on bin, return None."
    return self.nEtaBin - 1

  @property
  def nEtaBins(self):
    "Return maximum eta bin index. If variable is not dependent on bin, return None."
    return secureExtractNpItem( self._nEtaBins )

  @property
  def signalEfficiencies( self ):
    return secureExtractNpItem( self._signalEfficiencies )

  @property
  def backgroundEfficiencies( self ):
    return secureExtractNpItem( self._backgroundEfficiencies )

  @property
  def signalCrossEfficiencies( self ):
    return secureExtractNpItem( self._signalCrossEfficiencies )

  @property
  def backgroundCrossEfficiencies( self ):
    return secureExtractNpItem( self._backgroundCrossEfficiencies )

  @property
  def operation( self ):
    return secureExtractNpItem( self._operation )

  def getBinStr(self, etBinIdx, etaBinIdx):
    return 'etBin_' + str(etBinIdx) + '_etaBin_' + str(etaBinIdx)

  def checkForCompatibleBinningFile(self, filePath):
    binInfo = self.__class__.load(filePath, retrieveBinsInfo = True)
    mBinInfo = (self.isEtDependent, self.isEtaDependent, self.nEtBins, self.nEtaBins)
    if any([fInfo != mInfo for fInfo, mInfo in zip(binInfo, mBinInfo)]):
      return False
    else:
      return True

  def save(self, filePath, toMatlab = False):
    """
    Save the TunedDiscrArchieve object to disk.
    """
    return save( self.toRawObj(), filePath, protocol = 'savez_compressed')

  @classmethod
  def load(cls, filePath, retrieveBinsInfo = False,
           etaBinIdx = None, etBinIdx = None, loadCrossEfficiencies = False,
           loadEfficiencies = True, retrieveVersion = False):
    """
    Load this class information.
    """
    lLogger = Logger.getModuleLogger( cls.__name__ )
    # Open file:
    rawObj = load( filePath, useHighLevelObj = False )
    if retrieveBinsInfo or retrieveVersion:
      try:
        version = secureExtractNpItem( rawObj['__version'] )
      except KeyError:
        try:
          version = secureExtractNpItem( rawObj['version'] )
        except KeyError:
          if any(['backgroundPatterns_' in k for k in rawObj]):
            version = np.array(5)
          else:
            lLogger.fatal('Cannot retrieve version on numpy file.')
      ret = None
      if retrieveBinsInfo:
        if version >= np.array(6):
          ret = secureExtractNpItem( rawObj['isEtDependent'] ), secureExtractNpItem( rawObj['isEtaDependent'] ), \
                secureExtractNpItem( rawObj['nEtBins'] ),       secureExtractNpItem( rawObj['nEtaBins'] )
        else:
          if version >= np.array(5) and any(['backgroundPatterns_' in k for k in rawObj]):
            etBins = npCurrent.fp_array( rawObj['etBins'] if 'etBins' in rawObj else npCurrent.array([]) )
            # NOTE: Do we need to better handle this?
            #etaBins = npCurrent.fp_array( rawObj['etaBins'] if 'etaBins' in rawObj else npCurrent.array([]) )
            etaBins = npCurrent.fp_array( [0, 0.8, 1.37, 1.54, 2.5] )
          else:
            etBins = npCurrent.fp_array( rawObj['et_bins'] if 'et_bins' in rawObj else npCurrent.array([]) )
            etaBins = npCurrent.fp_array( rawObj['eta_bins'] if 'eta_bins' in rawObj else npCurrent.array([]) )
          nEtBins  = etBins.size - 1 if etBins.size - 1 > 0 else 0
          nEtaBins = etaBins.size - 1 if etaBins.size - 1 > 0 else 0
          isEtDependent = etBins.size > 0
          isEtaDependent = etaBins.size > 0
          ret = isEtDependent, isEtaDependent, nEtBins, nEtaBins
      if retrieveVersion:
        if ret: ret = ret + (version,)
        else: ret = version
      return ret
    else:
      if cls is BenchmarkEfficiencyArchieve and loadEfficiencies == False:
        lLogger.fatal("It is not possible to set loadEfficiencies to False when using BenchmarkEfficiencyArchieve.")
      return cls.fromRawObj(rawObj, etaBinIdx = etaBinIdx,
                                    etBinIdx = etBinIdx,
                                    loadCrossEfficiencies = loadCrossEfficiencies,
                                    loadEfficiencies = loadEfficiencies )

class TuningDataArchieveRDS( BenchmarkEfficiencyArchieveRDS ):
  """
  The TuningData RawDict Streamer
  """
  def __init__(self, **kw):
    BenchmarkEfficiencyArchieveRDS.__init__( self,
        transientAttrs = {'_signalPatterns', '_backgroundPatterns',
                          '_signalBaseInfo', '_backgroundBaseInfo',} | kw.pop('transientAttrs', set()),
        toPublicAttrs = set() | kw.pop('toPublicAttrs', set()),
        **kw )

  def treatDict(self, obj, raw):
    """
    Method dedicated to modifications on raw dictionary
    """
    raw = BenchmarkEfficiencyArchieveRDS.treatDict( self, obj, raw )
    from TuningTools.dataframe import BaseInfo
    # Handle patterns:
    if not obj.isEtaDependent and not obj.isEtDependent:
      raw['signalPatterns']       = obj.signalPatterns
      for idx in range(BaseInfo.nInfo):
        name = BaseInfo.tostring( idx )
        raw['signal' + name + '_' + binStr]   = obj.signalBaseInfo[idx]
      raw['backgroundPatterns']   = obj.backgroundPatterns
      for idx in range(BaseInfo.nInfo):
        name = BaseInfo.tostring( idx )
        raw['background' + name + '_' + binStr]   = obj.backgroundBaseInfo[idx]
    else:
      for etBin in range( obj.nEtBins ):
        for etaBin in range( obj.nEtaBins ):
          binStr = obj.getBinStr(etBin, etaBin)
          raw['signalPatterns_' + binStr]     = obj.signalPatterns[etBin][etaBin]
          for idx in range(BaseInfo.nInfo):
            name = BaseInfo.tostring( idx )
            raw['signal' + name + '_' + binStr]   = obj.signalBaseInfo[idx][etBin][etaBin]
          raw['backgroundPatterns_' + binStr] = obj.backgroundPatterns[etBin][etaBin]
          for idx in range(BaseInfo.nInfo):
            name = BaseInfo.tostring( idx )
            raw['background' + name + '_' + binStr]   = obj.backgroundBaseInfo[idx][etBin][etaBin]
        # eta loop
      # et loop
    return raw
  # end of getData

class TuningDataArchieveRDC( BenchmarkEfficiencyArchieveRDC ):
  """
  The TuningData file RawDict Converter
  """

  def __init__(self, **kw):
    BenchmarkEfficiencyArchieveRDC.__init__( self, **kw )

  def preCall( self, obj, d ):
    import re
    needSet = ( hasattr(self,'etBinIdx') and self.etBinIdx is not None) or (hasattr(self,'etaBinIdx') and self.etaBinIdx is not None)
    if needSet:
      t = type(self.ignoreAttrs)
      self.ignoreAttrs = set(self.ignoreAttrs)
    if hasattr(self,'etBinIdx') and self.etBinIdx is not None:
      _etBinIdx = self.etBinIdx
      if not isinstance(self.etBinIdx, (tuple, list)):
        _etBinIdx = [self.etBinIdx]
      self.ignoreAttrs |= {re.compile('(signal|background)(Patterns|_patterns)_etBin_[%s].*' % ''.join([str(s) for s in _etBinIdx])) ,}
    if hasattr(self,'etaBinIdx') and self.etaBinIdx is not None:
      _etaBinIdx = self.etaBinIdx
      if not isinstance(self.etaBinIdx, (tuple, list)):
        _etaBinIdx = [self.etaBinIdx]
      self.ignoreAttrs |= {re.compile('(signal|background)(Patterns|_patterns).*_etaBin_[%s].*' % ''.join([str(s) for s in _etaBinIdx])) ,}
    if needSet:
      self.ignoreAttrs = t(self.ignoreAttrs)
    return obj, d

  def treatObj( self, obj, npData ):
    # Check the efficiencies base keys:
    obj = BenchmarkEfficiencyArchieveRDC.treatObj(self, obj, npData)
    # Check the patterns base keys:
    if obj._readVersion <= np.array(4):
      sgnBaseKey, bkgBaseKey = 'signal_rings', 'background_rings'
    elif obj._readVersion == np.array(5):
      if any(['backgroundPatterns_' in k for k in npData]):
        sgnBaseKey, bkgBaseKey = 'signalPatterns', 'backgroundPatterns'
      else:
        sgnBaseKey, bkgBaseKey = 'signal_patterns', 'background_patterns'
    else:
      sgnBaseKey, bkgBaseKey = 'signalPatterns', 'backgroundPatterns'
    # Check the efficiencies base keys:
    # Retrieve data patterns:
    if obj._readVersion >= np.array(3):
      lEtBinIdxs = self.etBinIdx if self.etBinIdx is not None else range(obj.nEtBins)
      lEtaBinIdxs = self.etaBinIdx if self.etaBinIdx is not None else range(obj.nEtaBins)
      if type(lEtBinIdxs) not in (list,tuple): lEtBinIdxs = [lEtBinIdxs]
      if type(lEtaBinIdxs) not in (list,tuple): lEtaBinIdxs = [lEtaBinIdxs]
      sgnList, bkgList = [], []
      for etBinIdx in lEtBinIdxs:
        sgnLocalList, bkgLocalList = [], []
        for etaBinIdx in lEtaBinIdxs:
          binStr = obj.getBinStr(etBinIdx, etaBinIdx)
          sgnKey = sgnBaseKey + '_' + binStr; bkgKey = bkgBaseKey + '_' + binStr
          sgnLocalList.append(npData[sgnKey]); bkgLocalList.append(npData[bkgKey])
        # Finished looping on eta
        sgnList.append(sgnLocalList); bkgList.append(bkgLocalList)
      obj._signalPatterns     = sgnList
      obj._backgroundPatterns = bkgList
      if obj._readVersion >= np.array(6):
        from TuningTools.dataframe import BaseInfo
        for idx in range(BaseInfo.nInfo ):
          name = BaseInfo.tostring(idx)
          sgnBaseList, bkgBaseList = [], []
          for etBinIdx in lEtBinIdxs:
            binStr = obj.getBinStr(etBinIdx, etaBinIdx)
            sgnLocalBaseList, bkgLocalBaseList = [], []
            for etaBinIdx in lEtaBinIdxs:
              if obj._readVersion < np.array(8) and idx is BaseInfo.Phi:
                sgnLocalBaseList.append( None )
                bkgLocalBaseList.append( None )
              else:
                sgnLocalBaseList.append( npData['signal' + name + '_' + binStr]     )
                bkgLocalBaseList.append( npData['background' + name + '_' + binStr] )
            sgnBaseList.append(sgnLocalBaseList); bkgBaseList.append(bkgLocalBaseList)
          obj._signalBaseInfo.append( sgnBaseList )
          obj._backgroundBaseInfo.append( bkgBaseList )
        # Finished retrieving obj
      if type(self.etBinIdx) is int and type(self.etaBinIdx) is int:
        obj._signalPatterns, obj._backgroundPatterns = obj.signalPatterns[0][0], obj.backgroundPatterns[0][0]
        if obj._readVersion >= np.array(6):
          obj._signalBaseInfo, obj._backgroundBaseInfo = [sgnBase[0][0] for sgnBase in obj.signalBaseInfo], [bkgBase[0][0] for bkgBase in obj.backgroundBaseInfo]
    else:
      obj._signalPatterns = npData['signal_rings']
      obj._backgroundPatterns = npData['background_rings']
    # Check if numpy information fits with the information representation we
    # need:
    if type(obj.signalPatterns) is list:
      for cData, idx, parent, _, _ in traverse((obj.signalPatterns, obj.backgroundPatterns), (list,tuple,np.ndarray), max_depth_dist=2):
        cData = npCurrent.fix_fp_array(cData)
        parent[idx] = cData
    else:
      obj._signalPatterns = npCurrent.fix_fp_array(obj.signalPatterns)
      obj._backgroundPatterns = npCurrent.fix_fp_array(obj.backgroundPatterns)
    #from RingerCore import keyboard
    #keyboard
    return obj


class TuningDataArchieve( BenchmarkEfficiencyArchieve ):
  """
  File manager for Tuning Data
  Version 6: - Adds luminosity, eta and Et information.
               Makes profit of RDS and RDC functionality.
               Splits efficiency and data information on BenchmarkEfficiencyArchieve and TuningDataArchieve.
               Changes snake_case for cammelCase
               Uses rawDict for matlab information dumping
  Version 5: - Changes _rings for _patterns
  Version 4: - keeps the operation requested by user when creating data
  Version 3: - added eta/et bins compatibility
             - added benchmark efficiency information
             - improved fortran/C integration
             - loads only the indicated bins to memory
  Version 2: - started fotran/C order integration
  Version 1: - save compressed npz file
             - removed target information: classes are flaged as
               signal_rings/background_rings
  Version 0: - save pickle file with numpy data
  """

  _streamerObj  = TuningDataArchieveRDS()
  _cnvObj       = TuningDataArchieveRDC()
  _version = 8 # Changes in both archieves should increase versioning control.

  def __init__(self, d = {}, **kw):
    d.update(kw)
    self._signalPatterns     = d.pop( 'signalPatterns',              npCurrent.fp_array([]) )
    self._backgroundPatterns = d.pop( 'backgroundPatterns',          npCurrent.fp_array([]) )
    self._signalBaseInfo     = d.pop( 'signalBaseInfo',              []                     )
    self._backgroundBaseInfo = d.pop( 'backgroundBaseInfo',          []                     )
    BenchmarkEfficiencyArchieve.__init__(self, d)
    checkForUnusedVars( d, self._warning )
    # Make some checks:
    if type(self._signalPatterns) != type(self._backgroundPatterns):
      self._fatal("Signal and background types do not match.", TypeError)
    if type(self._signalPatterns) == list:
      if len(self._signalPatterns) != len(self._backgroundPatterns) \
          or len(self._signalPatterns[0]) != len(self._backgroundPatterns[0]):
        self._fatal("Signal and background patterns lenghts do not match.",TypeError)

  @property
  def signalPatterns( self ):
    return self._signalPatterns

  @property
  def backgroundPatterns( self ):
    return self._backgroundPatterns

  @property
  def signalBaseInfo( self ):
    return self._signalBaseInfo

  @property
  def backgroundBaseInfo( self ):
    return self._backgroundBaseInfo

  def drawProfiles(self):
    from itertools import product
    for etBin, etaBin in progressbar(product(range(self.nEtBins),range(self.nEtaBins)), self.nEtBins*self.nEtaBins,
                                     logger = self._logger, prefix = "Drawing profiles "):
      sdata = self._signalPatterns[etBin][etaBin]
      bdata = self._backgroundPatterns[etBin][etaBin]
      if sdata is not None and not 0 in sdata.shape:
        self._makeGrid(sdata,'signal',etBin,etaBin)
      if bdata is not None and not 0 in bdata.shape:
        self._makeGrid(bdata,'background',etBin,etaBin)


  def _makeGrid(self,data,bckOrSgn,etBin,etaBin):
    colors=[(0.1706, 0.5578, 0.9020),
            (0.1427, 0.4666, 0.7544),
            (0.1148, 0.3754, 0.6069),
            (0.0869, 0.2841, 0.4594),
            (0.9500, 0.3000, 0.3000),
            (0.7661, 0.2419, 0.2419),
            (0.5823, 0.1839, 0.1839)]
    upperBounds= np.zeros(100)
    lowerBounds= np.zeros(100)
    dataT = np.transpose(data)
    underFlows= np.zeros(100)
    overFlows= np.zeros(100)
    nLayersRings= np.array([8,64,8,8,4,4,4])
    layersEdges = np.delete(np.cumsum( np.append(-1, nLayersRings)),0)
    opercent=np.ones(100)
    nonzeros = []
    self._oSeparator(dataT,opercent,nonzeros)

    for i in range(len(nonzeros)):
      if len(nonzeros[i]):
        upperBounds[i]= max(nonzeros[i])
        lowerBounds[i]= min(nonzeros[i])
        self._forceLowerBound(i,lowerBounds,nonzeros)
        self._takeUnderFlows(i,underFlows,lowerBounds,nonzeros)
        self._findParcialUpperBound(i,underFlows,upperBounds,nonzeros)
        self._makeCorrections(i,lowerBounds,upperBounds, layersEdges )
        self._takeOverFlows(i,overFlows,upperBounds,nonzeros)
        self._takeUnderFlows(i,underFlows,lowerBounds,nonzeros)

    for i in range(len(nonzeros)):
      if len(nonzeros[i]):
        if( i <  8*11):
          plt.subplot2grid((8,14), (i%8,i/8))
          self._plotHistogram(np.array( nonzeros[i]), np.where(layersEdges >= i )[0][0],i,lowerBounds,upperBounds,opercent,underFlows,overFlows,colors)
        else:
          plt.subplot2grid((8,14), ((i-88)% 4,(i-88)/4+11 ))
          self._plotHistogram(np.array(nonzeros[i]),np.where(layersEdges >= i )[0][0],i,lowerBounds,upperBounds,opercent,
            underFlows,overFlows,colors)
      else:
        if( i <  8*11):
          plt.subplot2grid((8,14), (i%8,i/8))
          self._representNullRing(i)
        else:
          plt.subplot2grid((8,14), ((i-88)% 4,(i-88)/4+11 ))
          self._representNullRing(i)

    plt.subplot2grid((8,14), (8-4,14-3),colspan=3,rowspan=4)
    verts= [(0,1),(0,0.7),(1,0.7),(1,1)]
    ax= plt.gca()
    ax.add_patch( patches.Rectangle((0,0.7),1,0.3,facecolor='none'))
    aux = bckOrSgn[0].upper()+bckOrSgn[1::]
    color=colors[1] if bckOrSgn == 'signal' else colors[-2]
    plt.text(0.1,0.75,"Rings Energy(MeV)\nhistograms for\n{}\nEt[{}] Eta[{}] ".format(aux,etBin,etaBin),color=color,multialignment='center',
        size='large',fontweight='bold')

    if self._label is not NotSet:
      plt.text(0.25,0.3,'{}'.format(self._label),fontsize=12)

    plt.text(0.1,0.07,'Number of clusters for this\ndataset:\n{}'.format(data.shape[0])
        ,multialignment='center',fontweight='bold',fontsize=9)

    self._makeColorsLegend(colors)

    for line in ax.spines.values() :
      line.set_visible(False)

    for line in ax.yaxis.get_ticklines() + ax.xaxis.get_ticklines():
       line.set_visible(False)

    for tl in ax.get_xticklabels() + ax.get_yticklabels():
      tl.set_visible(False)

    figure = plt.gcf() # get current figure
    figure.set_size_inches(16,9)

    plt.savefig('ring_distribution_{}_etBin{}_etaBin{}.pdf'.format(bckOrSgn,etBin,etaBin),dpi=100,bbox_inches='tight')

  def _makeColorsLegend(self,colors):
    import matplotlib as mpl
    #mpl.use('Agg')
    import matplotlib.pyplot as plt
    plt.text(0.15,0.56
        ,'Layer Color Legend:',fontsize=12)
    text=['PS','EM1','EM2','EM3','HAD1','HAD2','HAD3']
    x0,x = 0.1,0.1
    y0,y = 0.5,0.5
    for i in range(4):
      plt.text(x,y,text[i],color=colors[i])
      x=x+0.2

    y=y-0.05
    x=x0+0.1
    for i in ( np.arange(3)+4):
      plt.text(x,y,text[i],color=colors[i])
      x=x+0.2

  def _oSeparator(self,dataT,opercent,nonzeros):
    for index in range(dataT.shape[0]):
      counter = 0
      ocounter = 0
      no0= np.array([])
      for aux in dataT[index] :
        if( aux != 0):
          no0 = np.append(no0, aux)
        else:
          ocounter = ocounter +1
        counter = counter +1
      liist = no0.tolist()

      nonzeros.append (liist)
      opercent[index] =(ocounter*100.0)/counter

  def _plotHistogram(self,data,layer,ring,lowerBounds,upperBounds,opercent,underFlows,overFlows, colors,nbins=60):
    statistcs = scipy.stats.describe(data)
    if type(statistcs) is tuple:
      class DescribeResult(object):
        def __init__(self, t):
          self.mean = statistcs[2]
          self.variance= statistcs[3]
          self.skewness= statistcs[4]
          self.kurtosis= statistcs[5]
      statistcs = DescribeResult(statistcs)
    m=statistcs.mean
    plotingData=[]
    statstring='{:0.1f}\n{:0.1f}\n{:0.1f}\n{:0.1f}'.format(statistcs.mean,statistcs.variance**0.5,
        statistcs.skewness,statistcs.kurtosis)

    binSize=( upperBounds[ring]-lowerBounds[ring])/(nbins + -2.0)
    underflowbound= lowerBounds[ring]- binSize
    overFlowbound= upperBounds[ring] + binSize

    for n in data:
      if n >   lowerBounds[ring] and  n < upperBounds[ring]:
        plotingData.append(n)
      elif n >upperBounds[ring]:

        plotingData.append( upperBounds[ring] + binSize/2.0)
      else:
        plotingData.append( lowerBounds[ring] - binSize/2.0)

    n, bins, patches = plt.hist(plotingData,nbins,[underflowbound,overFlowbound],edgecolor=colors[layer])
    mbins=[]

    for i in range(nbins):
      mbins.append( (bins[i]+bins[i+1])/2.0)

    plt.axis([underflowbound,overFlowbound,0,max(n)])
    ax  = plt.gca()

    for tl in ax.get_xticklabels() + ax.get_yticklabels():
      tl.set_visible(False)

    of= overFlows[ring]*100.0
    uf=underFlows[ring]*100.0

    plt.ylabel ('#{} U:{:0.1f}% | O:{:0.1f}%'.format(ring+1,uf,of),labelpad=0,fontsize=5 )
    plt.xlabel('{:0.0f}    {:0.1f}%    {:0.0f}'.format(lowerBounds[ring] , opercent[ring],
      upperBounds[ring]),fontsize=5,labelpad=2)

    xtext= underflowbound + (-underflowbound + overFlowbound)*0.75
    ytext= max(n)/1.5

    plt.text(xtext,ytext,statstring,fontsize=4,multialignment='right')

    try:
      mdidx=np.where(n==max(n))[0][0]
      midx = np.where(bins > m)[0][0]-1

      xm=[mbins[midx],mbins[midx]]
      xmd=[mbins[mdidx],mbins[mdidx]]
      x0=[0,0]
      y=[0,max(n)/2]
      plt.plot(x0,y,'k',dashes=(1,1),linewidth=0.5) # 0
      plt.plot(xmd,y,'k',linewidth=0.5,dashes=(5,1)) # mode
      plt.plot(xm,y,'k-',linewidth=0.5) # mean
    except IndexError:
      pass

    for line in ax.yaxis.get_ticklines() + ax.xaxis.get_ticklines():
       line.set_visible(False)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

  def _representNullRing(self,i):
    ax  = plt.gca()
    for tl in ax.get_xticklabels() + ax.get_yticklabels():
      tl.set_visible(False)
    plt.ylabel('#{}'.format(i),multialignment='left',fontsize='5',labelpad=0)
    for line in ax.yaxis.get_ticklines() + ax.xaxis.get_ticklines():
       line.set_visible(False)

  def _lowerPowerofTen(self,x):
    from math import log10,floor
    num = 0
    if x > 0:
      num = x
    else:
      num = - x
    lg=log10(num)
    return floor(lg)

  def _forceLowerBound(self,i,lowerBounds,nonzeros):
    parcial=-500
    while   np.sum(np.array(nonzeros[i])<parcial)/float(len(nonzeros[i])) > (0.005):
      parcial += -500
    lowerBounds[i] = parcial

  def _findParcialUpperBound(self,i,underFlows,upperBounds,nonzeros):
    cMax= upperBounds[i]
    power10= self._lowerPowerofTen (cMax)
    cPerc = 1 - underFlows[i]
    while cPerc > .99:
      if cMax  - 10**(power10-1) < 0.8*cMax:
        power10 -= 1
      cMax  = cMax - 10**(power10-1)
      cPerc = np.sum(nonzeros[i]<=cMax)/float(len(nonzeros[i])) - underFlows[i]
    while cPerc < .99 - 0.001 and cPerc > .99:
      cMax += 10**(power10-2)
      cPerc= np.sum(nonzeros[i]<=cMax)/float(len(nonzeros[i])) - underFlows[i]

    power10= self._lowerPowerofTen(cMax)
    for j  in np.arange(2,11)*10**power10:
      if abs(cMax) < j:
        if cMax<0:
          upperBounds[i]= - j
        else:
          upperBounds[i]= j
        break


  def _makeCorrections(self,i,lowerBounds,upperBounds,LayerEdges):
    if lowerBounds[i] < 0 and -lowerBounds[i] > upperBounds[i] and upperBounds[i]>0:
      lowerBounds[i] = -upperBounds[i]
    if lowerBounds[i] < 0 and -lowerBounds[i] < upperBounds[i] and upperBounds[i] <= 1000 and upperBounds[i]>0:
      lowerBounds[i] = -upperBounds[i]

    if i < 8:
      lidx = 0
    else:
      lidx= LayerEdges[(np.where(LayerEdges < i)[0][-1] ) ] +1

    for j in range( lidx , i):
      if lowerBounds[i]<lowerBounds[j]:
        lowerBounds[j]=lowerBounds[i]

      if upperBounds[i] > upperBounds[j]:
        upperBounds[j] = upperBounds[i]

      if lowerBounds[j]<0 and -lowerBounds[j] > upperBounds[j] and upperBounds[i]>0:
        lowerBounds[j] = -upperBounds[j]

      if lowerBounds[j]<0 and -lowerBounds[j] < upperBounds[j] and upperBounds[j] <= 1000 and upperBounds[i]>0 :
        lowerBounds[j] = -upperBounds[j]


  def _takeUnderFlows(self,i,underFlows,lowerBounds,nonzeros):
    lower= lowerBounds[i]
    underFlows[i] = float(np.sum(np.array(nonzeros[i])<lower))/len(nonzeros[i])

  def _takeOverFlows(self,i,overFlows,upperBounds,nonzeros):
    upper= upperBounds[i]
    overFlows[i] = np.sum(np.array(nonzeros[i])>upper)/float(len(nonzeros[i]))

  def __generateMeanGraph (self, canvas, data, kind, etbounds, etabounds, color, idx = 0):
    from ROOT import TGraph, gROOT, kTRUE
    gROOT.SetBatch(kTRUE)
    xLabel = "Ring #"
    yLabel = "Energy (MeV)"

    if data is None or not len(data):
      self._logger.error("Data is unavaliable")
    else:
      x = np.arange( 100 ) + 1.0
      y = data.mean(axis=0 ,dtype='f8')
      n =data.shape[1]

      canvas.cd(idx)
      canvas.SetGrid()
      graph = TGraph(n , x , y )
      self._collectGraphs.append( graph )
      graph.SetTitle( ( kind + " et = [%d ,  %d] eta = [%.2f,  %.2f]" ) % (etbounds[0],etbounds[1],etabounds[0],etabounds[1]))
      graph.GetXaxis().SetTitle(xLabel)
      graph.GetYaxis().SetTitle(yLabel)
      graph.GetYaxis().SetTitleOffset(1.9)
      graph.SetFillColor(color)
      graph.Draw("AB")

  def plotMeanPatterns(self):
    from ROOT import TCanvas, gROOT, kTRUE
    gROOT.SetBatch(kTRUE)
    for etBin in range(self.nEtBins):
      for etaBin in range(self.nEtaBins):
        c1 = TCanvas("plot_patternsMean_et%d_eta%d" % (etBin, etaBin), "a",0,0,800,400)
        signal = self._signalPatterns[etBin][etaBin]
        background = self._backgroundPatterns[etBin][etaBin]
        if (signal is not None and not 0 in signal.shape) and (background is not None and not 0 in background.shape):
          c1.Divide(2,1)
          etBound = self._etBins[etBin:etBin+2]
          etaBound = self._etaBins[etaBin:etaBin+2]
          self.__generateMeanGraph( c1, signal,     "Signal",     etBound, etaBound, 34, 1 )
          self.__generateMeanGraph( c1, background, "Background", etBound, etaBound, 2,  2 )
        c1.SaveAs('plot_patterns_mean_et_%d_eta%d.pdf' % (etBin, etaBin))
        c1.Close()
    self._collectGraphs = []

  def save(self, filePath, toMatlab = False):
    """
    Save the TunedDiscrArchieve object to disk.
    """
    self._info( 'Saving data using following numpy flags: %r', npCurrent)
    rawObj = self.toRawObj()
    outputPath = save( rawObj, filePath, protocol = 'savez_compressed')
    if toMatlab:
      from copy import copy
      matRawObj = copy( rawObj )
      matRawObj.pop('etBinIdx', None); matRawObj.pop('etaBinIdx', None)
      from TuningTools.dataframe import RingerOperation
      matRawObj['operation'] = RingerOperation.tostring( matRawObj['operation'] )
      try:
        if 'signalCrossEfficiencies' in matRawObj:
          d = matRawObj['signalCrossEfficiencies']
          o = d[d.keys()[0]]
          if type(o) is list:
            if o[0] and o[0][0]['_etaBin'] != -1:
              matRawObj['crossVal'] = o[0][0]['_crossVal']
            else:
              self._debug("Cross-validation object is not available and, thus, will not be added to .mat file")
          else:
            matRawObj['crossVal'] = o['_crossVal']
          if 'crossVal' in matRawObj:
            from TuningTools import CrossValidMethod
            matRawObj['crossVal']['method'] = CrossValidMethod.tostring( matRawObj['crossVal']['method'] )
      except (IndexError, KeyError) as e:
        self._warning("Couldn't retrieve cross-validation object. Reason: %s", e)
      save( matRawObj, filePath, protocol='mat' )
    return outputPath



class CreateData(Logger):

  def __init__( self, logger = None ):
    Logger.__init__( self, logger = logger )

  def __call__(self, sgnFileList, bkgFileList, ringerOperation, **kw):
    """
      Creates a numpy file ntuple with rings and its targets
      Arguments:
        - sgnFileList: A python list or a comma separated list of the root files
            containing the TuningTool TTree for the signal dataset
        - bkgFileList: A python list or a comma separated list of the root files
            containing the TuningTool TTree for the background dataset
        - ringerOperation: Set Operation type to be used by the filter
      Optional arguments:
        - pattern_oFile ['tuningData']: Path for saving the output file
        - efficiency_oFile ['tuningData']: Path for saving the efficiency output file
        - referenceSgn [Reference.Truth]: Filter reference for signal dataset
        - referenceBkg [Reference.Truth]: Filter reference for background dataset
        - treePath [<Same as ReadData default>]: set tree name on file, this may be set to
          use different sources then the default.
        - efficiencyTreePath [None]: Sets tree path for retrieving efficiency
              benchmarks.
            When not set, uses treePath as tree.
        - nClusters [<Same as ReadData default>]: Number of clusters to export. If set to None, export
            full PhysVal information.
        - getRatesOnly [<Same as ReadData default>]: Do not create data, but retrieve the efficiency
            for benchmark on the chosen operation.
        - etBins [<Same as ReadData default>]: E_T bins  (GeV) where the data should be segmented
        - etaBins [<Same as ReadData default>]: eta bins where the data should be segmented
        - ringConfig [<Same as ReadData default>]: A list containing the number of rings available in the data
          for each eta bin.
        - crossVal [<Same as ReadData default>]: Whether to measure benchmark efficiency splitting it
          by the crossVal-validation datasets
        - extractDet [<Same as ReadData default>]: Which detector to export (use Detector enumeration).
        - standardCaloVariables [<Same as ReadData default>]: Whether to extract standard track variables.
        - useTRT [<Same as ReadData default>]: Whether to export TRT information when dumping track
          variables.
        - toMatlab [False]: Whether to also export data to matlab format.
        - efficiencyValues [NotSet]: expert property to force the efficiency values to a new reference.
          This property can be [detection = 97.0, falseAlarm = 2.0] or a matrix with size
          E_T bins X Eta bins where each position is [detection, falseAlarm].
        - plotMeans [True]: Plot mean values of the patterns
        - plotProfiles [False]: Plot pattern profiles
        - label [NotSet]: Adds label to profile plots
        - supportTriggers [True]: Whether reading data comes from support triggers
    """
    """
    # TODO Add a way to create new reference files setting operation points as
    # desired. A way to implement this is:
    #"""
    #    - tuneOperationTargets [['Loose', 'Pd' , #looseBenchmarkRef],
    #                            ['Medium', 'SP'],
    #                            ['Tight', 'Pf' , #tightBenchmarkRef]]
    #      The tune operation targets which should be used for this tuning
    #      job. The strings inputs must be part of the ReferenceBenchmark
    #      enumeration.
    #      Instead of an enumeration string (or the enumeration itself),
    #      you can set it directly to a value, e.g.:
    #        [['Loose97', 'Pd', .97,],['Tight005','Pf',.005]]
    #      This can also be set using a string, e.g.:
    #        [['Loose97','Pd' : '.97'],['Tight005','Pf','.005']]
    #      , which may contain a percentage symbol:
    #        [['Loose97','Pd' : '97%'],['Tight005','Pf','0.5%']]
    #      When set to None, the Pd and Pf will be set to the value of the
    #      benchmark correspondent to the operation level set.
    #"""
    #from TuningTools import TuningToolsGit
    #from RingerCore import RingerCoreGit
    #TuningToolsGit.ensure_clean()
    #RingerCoreGit.ensure_clean()
    from TuningTools.dataframe import FilterType, Reference, Dataset, Dataframe
    pattern_oFile         = retrieve_kw(kw, 'pattern_oFile',         'tuningData'    )
    efficiency_oFile      = retrieve_kw(kw, 'efficiency_oFile',      NotSet          )
    referenceSgn          = retrieve_kw(kw, 'referenceSgn',          Reference.Truth )
    referenceBkg          = retrieve_kw(kw, 'referenceBkg',          Reference.Truth )
    treePath              = retrieve_kw(kw, 'treePath',              NotSet          )
    efficiencyTreePath    = retrieve_kw(kw, 'efficiencyTreePath',    NotSet          )
    l1EmClusCut           = retrieve_kw(kw, 'l1EmClusCut',           NotSet          )
    l2EtCut               = retrieve_kw(kw, 'l2EtCut',               NotSet          )
    efEtCut               = retrieve_kw(kw, 'efEtCut',               NotSet          )
    offEtCut              = retrieve_kw(kw, 'offEtCut',              NotSet          )
    nClusters             = retrieve_kw(kw, 'nClusters',             NotSet          )
    getRatesOnly          = retrieve_kw(kw, 'getRatesOnly',          NotSet          )
    etBins                = retrieve_kw(kw, 'etBins',                NotSet          )
    etaBins               = retrieve_kw(kw, 'etaBins',               NotSet          )
    ringConfig            = retrieve_kw(kw, 'ringConfig',            NotSet          )
    crossVal              = retrieve_kw(kw, 'crossVal',              NotSet          )
    extractDet            = retrieve_kw(kw, 'extractDet',            NotSet          )
    standardCaloVariables = retrieve_kw(kw, 'standardCaloVariables', NotSet          )
    useTRT                = retrieve_kw(kw, 'useTRT',                NotSet          )
    toMatlab              = retrieve_kw(kw, 'toMatlab',              True            )
    efficiencyValues      = retrieve_kw(kw, 'efficiencyValues',      NotSet          )
    plotMeans             = retrieve_kw(kw, 'plotMeans',             True            )
    plotProfiles          = retrieve_kw(kw, 'plotProfiles',          False           )
    label                 = retrieve_kw(kw, 'label',                 NotSet          )
    supportTriggers       = retrieve_kw(kw, 'supportTriggers',       NotSet          )
    doMonitoring          = retrieve_kw(kw, 'doMonitoring',          True            )
    pileupRef             = retrieve_kw(kw, 'pileupRef',             NotSet          )
    dataframe             = retrieve_kw(kw, 'dataframe',             NotSet          )

    # Mute root messages
    from ROOT import TFile, gROOT, kTRUE
    gROOT.SetBatch(kTRUE)
    gROOT.ProcessLine( "gErrorIgnoreLevel = 1001;")

    # Data framework setup
    from TuningTools.coreDef import dataframeConf
    dataframeConf.auto_retrieve_testing_sample( sgnFileList )
    dataframeConf.set( dataframe )
    readData = dataframeConf.api()

    reader = readData

    if plotProfiles and _noProfilePlot:
      self._logger.error("Cannot draw profiles! Reason:\n%r", _noProfileImportError)
      plotProfiles = False

    if 'level' in kw:
      self.level = kw.pop('level') # log output level
      reader.level = self.level
    checkForUnusedVars( kw, self._warning )
    # Make some checks:
    if type(treePath) is not list:
      treePath = [treePath]
    if len(treePath) == 1:
      treePath.append( treePath[0] )
    if efficiencyTreePath in (NotSet, None):
      efficiencyTreePath = treePath
    if type(efficiencyTreePath) is not list:
      efficiencyTreePath = [efficiencyTreePath]
    if len(efficiencyTreePath) == 1:
      efficiencyTreePath.append( efficiencyTreePath[0] )
    if etaBins is None: etaBins = npCurrent.fp_array([])
    if etBins is None: etBins = npCurrent.fp_array([])
    if type(etaBins) is list: etaBins=npCurrent.fp_array(etaBins)
    if type(etBins) is list: etBins=npCurrent.fp_array(etBins)
    if efficiency_oFile in (NotSet, None):
      efficiency_oFile = appendToFileName(pattern_oFile, 'eff', separator='-')

    nEtBins  = len(etBins)-1 if not etBins is None else 1
    nEtaBins = len(etaBins)-1 if not etaBins is None else 1
    #useBins = True if nEtBins > 1 or nEtaBins > 1 else False

    #FIXME: problems to only one bin. print eff doest work as well
    useBins=True; getRates=True
    # Checking the efficiency values
    if isinstance(efficiencyValues, np.ndarray) or efficiencyValues not in (None, NotSet):
      getRates=False
      if len(efficiencyValues) == 2 and (type(efficiencyValues[0]) is int or float):
        efficiencyValues = nEtBins * [ nEtaBins * [efficiencyValues] ]
      else:
        if len(efficiencyValues) != nEtBins:
          self._logger.error('The number of etBins (%d) does not match with efficiencyValues (%d)', nEtBins, len(efficiencyValues))
          raise ValueError('The number of etbins must match!')
        if len(efficiencyValues[0]) != nEtaBins:
          self._logger.error('The number of etaBins (%d) does not match with efficiencyValues (%d)', nEtaBins, len(efficiencyValues[0]))
          raise ValueError('The number of etabins must match!')
        if len(efficiencyValues[0][0]) != 2:
          self._logger.error('The reference value must be a list with 2 like: [sgnEff, bkgEff]')
          raise ValueError('The number of references must be two!')

    # TODO Set default pileupRef
    #if pileupRef is NotSet:
    #  if ringerOperation > 0:
    #    pileupRef = PileupReference.avgmu
    #  else:
    #    pileupRef = PileupReference.nvtx
    # List of operation arguments to be propagated
    kwargs = { 'l1EmClusCut':           l1EmClusCut,
               'l2EtCut':               l2EtCut,
               'efEtCut':               efEtCut,
               'offEtCut':              offEtCut,
               'nClusters':             nClusters,
               'etBins':                etBins,
               'etaBins':               etaBins,
               'ringConfig':            ringConfig,
               'crossVal':              crossVal,
               'extractDet':            extractDet,
               'standardCaloVariables': standardCaloVariables,
               'useTRT':                useTRT,
               'supportTriggers':       supportTriggers,
               #'pileupRef':             pileupRef,
             }

    #if doMonitoring is True:
    #  # Create root file to attach all histograms
    #  from RingerCore import StoreGate
    #  monitoring_oFile = appendToFileName(pattern_oFile, 'monitoring', separator='-')
    #  monTool = StoreGate(monitoring_oFile)
    #  reader.bookHistograms(monTool)
    #  kwargs['monitoring'] = monTool

    if efficiencyTreePath[0] == treePath[0] or getRates == False:
      self._info('Extracting signal dataset information')
      npSgn, npBaseSgn, sgnEff, sgnCrossEff  = reader(sgnFileList,
                                                 ringerOperation,
                                                 filterType = FilterType.Signal,
                                                 reference = referenceSgn,
                                                 treePath = treePath[0],
                                                 getRates = getRates,
                                                 **kwargs)
      if npSgn.size: self.__printShapes(npSgn, 'Signal')
    else:
      if not getRatesOnly:
        self._info("Extracting signal data" )
        npSgn, _, _, _ =     reader(sgnFileList,
                                    ringerOperation,
                                    filterType = FilterType.Signal,
                                    reference = referenceSgn,
                                    treePath = treePath[0],
                                    getRates = False,
                                    **kwargs)
        self.__printShapes(npSgn, 'Signal')
      else:
        self._warning("Informed treePath was ignored and used only efficiencyTreePath.")

      self._info("Extracting signal efficiencies")
      _, _, sgnEff, sgnCrossEff  =    reader(sgnFileList,
                                             ringerOperation,
                                             filterType = FilterType.Signal,
                                             reference = referenceSgn,
                                             treePath = efficiencyTreePath[0],
                                             getRatesOnly = True,
                                             **kwargs)

    if efficiencyTreePath[1] == treePath[1] or getRates == False:
      self._info('Extracting background dataset information')
      npBkg, npBaseBkg, bkgEff, bkgCrossEff  = reader(bkgFileList,
                                                 ringerOperation,
                                                 filterType = FilterType.Background,
                                                 reference = referenceBkg,
                                                 treePath = treePath[1],
                                                 getRates = getRates,
                                                 **kwargs)
    else:
      if not getRatesOnly:
        self._info("Extracting background data for treePath" )
        npBkg, _, _, _  =    reader(bkgFileList,
                                    ringerOperation,
                                    filterType = FilterType.Background,
                                    reference = referenceBkg,
                                    treePath = treePath[1],
                                    getRates = False,
                                    **kwargs)
      else:
        self._warning("Informed treePath was ignored and used only efficiencyTreePath.")

      self._info("Extracting background efficiencies")
      _, _, bkgEff, bkgCrossEff  =    reader(bkgFileList,
                                             ringerOperation,
                                             filterType = FilterType.Background,
                                             reference = referenceBkg,
                                             treePath = efficiencyTreePath[1],
                                             getRatesOnly=True,
                                             **kwargs)
    if npBkg.size: self.__printShapes(npBkg, 'Background')

    # Rewrite all effciency values
    if isinstance(efficiencyValues, np.ndarray) or efficiencyValues not in (None, NotSet):
      for etBin in range(nEtBins):
        for etaBin in range(nEtaBins):
          for key in sgnEff.iterkeys():
            sgnEff[key][etBin][etaBin].setEfficiency(efficiencyValues[etBin][etaBin][0])
          for key in bkgEff.iterkeys():
            bkgEff[key][etBin][etaBin].setEfficiency(efficiencyValues[etBin][etaBin][1])
          self._info( "Set bin (et%d:,eta:%d) target efficiency to (Pd:%f,Pf:%f)", etBin, etaBin
                    , sgnEff[key][etBin][etaBin].efficiency
                    , bkgEff[key][etBin][etaBin].efficiency )

    cls = TuningDataArchieve if not getRatesOnly else BenchmarkEfficiencyArchieve
    kwin = {'etaBins':                     etaBins
           ,'etBins':                      etBins
           ,'signalEfficiencies':          sgnEff
           ,'backgroundEfficiencies':      bkgEff
           ,'signalCrossEfficiencies':     sgnCrossEff
           ,'backgroundCrossEfficiencies': bkgCrossEff
           ,'operation':                   ringerOperation
           #,'pileupRef':                   pileupRef
           }

    if not getRatesOnly:
      kwin.update({'signalPatterns' : npSgn
                  ,'backgroundPatterns' : npBkg
                  ,'signalBaseInfo' : npBaseSgn
                  ,'backgroundBaseInfo' : npBaseBkg})


    # Save efficiency file:
    tdArchieve = cls(kwin)
    tdArchieve.__class__ = BenchmarkEfficiencyArchieve
    savedPath = tdArchieve.save(efficiency_oFile)
    tdArchieve.__class__ = cls
    self._info('Saved efficiency file at path: %s', savedPath )
    # Now save data file:
    if not getRatesOnly:
      savedPath = tdArchieve.save(pattern_oFile
                                  ,toMatlab = toMatlab
                                 )
      self._info('Saved data file at path: %s', savedPath )

      #FIXME: Remove self._nEtBins inside of this functions
      # plot number of events per bin
      if npBkg.size and npSgn.size:
        self.plotNSamples(npSgn, npBkg, etBins, etaBins)
      if plotMeans:
        tdArchieve.plotMeanPatterns()
      if plotProfiles:
        tdArchieve.drawProfiles()


    for etBin in range(nEtBins):
      for etaBin in range(nEtaBins):
        # plot ringer profile per bin
        for key in sgnEff.iterkeys():
          sgnEffBranch = sgnEff[key][etBin][etaBin] if useBins else sgnEff[key]
          bkgEffBranch = bkgEff[key][etBin][etaBin] if useBins else bkgEff[key]
          self._info('Efficiency for %s: Det(%%): %s | FA(%%): %s',
                            sgnEffBranch.printName,
                            sgnEffBranch.eff_str(),
                            bkgEffBranch.eff_str() )
          if crossVal not in (None, NotSet):
            for ds in BranchCrossEffCollector.dsList:
              try:
                sgnEffBranchCross = sgnCrossEff[key][etBin][etaBin] if useBins else sgnEff[key]
                bkgEffBranchCross = bkgCrossEff[key][etBin][etaBin] if useBins else bkgEff[key]
                self._info( '%s_%s: Det(%%): %s | FA(%%): %s',
                                  Dataset.tostring(ds),
                                  sgnEffBranchCross.printName,
                                  sgnEffBranchCross.eff_str(ds),
                                  bkgEffBranchCross.eff_str(ds))
              except KeyError, e:
                pass
        # for eff
      # for eta
    # for et

    # dealloc storegate if needed
    #if doMonitoring:
    #  monTool.write()
    #  del monTool
  # end __call__


  @classmethod
  def plotNSamples(cls, npArraySgn, npArrayBkg, etBins, etaBins, outname='nPatterns.pdf' ):
    """Plot number of samples per bin"""
    if type(npArraySgn) is list:  npArraySgn=np.array(npArraySgn)
    if type(npArrayBkg) is list:  npArraySgn=np.array(npArrayBkg)
    logger = Logger.getModuleLogger("PlotNSamples" )
    from ROOT import TCanvas, gROOT, kTRUE, kFALSE, TH2I, TText
    gROOT.SetBatch(kTRUE)
    c1 = TCanvas("plot_patterns_signal", "a",0,0,800,400); c1.Draw();
    shape = npArraySgn.shape #npArrayBkg.shape should be the same
    histo1 = TH2I("text_stats", "#color[4]{Signal}/#color[2]{Background} available statistics", shape[0], 0, shape[0], shape[1], 0, shape[1])
    #histo1 = TH2I("text_stats", "Signal/Background available statistics", shape[0], 0, shape[0], shape[1], 0, shape[1])
    histo1.SetStats(kFALSE)
    histo1.Draw("TEXT")
    histo1.SetXTitle("E_{T}"); histo1.SetYTitle("#eta")
    histo1.GetXaxis().SetTitleSize(0.04); histo1.GetYaxis().SetTitleSize(0.04)
    histo1.GetXaxis().SetLabelSize(0.04); histo1.GetYaxis().SetLabelSize(0.04);
    histo1.GetXaxis().SetTickSize(0); histo1.GetYaxis().SetTickSize(0);
    ttest = TText(); ttest.SetTextAlign(22)
    for etBin in range(shape[0]):
      for etaBin in range(shape[1]):
        ttest.SetTextColor(4)
        #ttest.DrawText( .5 + etBin, .75 + etaBin, str(npArraySgn[etBin][etaBin].shape[npCurrent.odim]) )
        if type(npArraySgn[etBin][etaBin]) is int or float:
          ttest.DrawText( .5 + etBin, .75 + etaBin, 's: ' + str(npArraySgn[etBin][etaBin]) )
        else:
          ttest.DrawText( .5 + etBin, .75 + etaBin, 's: ' + str(npArraySgn[etBin][etaBin].shape[npCurrent.odim]) )
        ttest.SetTextColor(2)
        if type(npArraySgn[etBin][etaBin]) is int or float:
          ttest.DrawText( .5 + etBin, .25 + etaBin, 'b: ' + str(npArrayBkg[etBin][etaBin]) )
        else:
          ttest.DrawText( .5 + etBin, .25 + etaBin, 'b: ' + str(npArrayBkg[etBin][etaBin].shape[npCurrent.odim]) )

        try:
          histo1.GetYaxis().SetBinLabel(etaBin+1, '#bf{%d} : %.2f->%.2f' % ( etaBin, etaBins[etaBin], etaBins[etaBin + 1] ) )
        except Exception:
          logger.error("Couldn't retrieve eta bin %d bounderies.", etaBin)
          histo1.GetYaxis().SetBinLabel(etaBin+1, str(etaBin))
        try:
          histo1.GetXaxis().SetBinLabel(etBin+1, '#bf{%d} : %d->%d [GeV]' % ( etBin, etBins[etBin], etBins[etBin + 1] ) )
        except Exception:
          logger.error("Couldn't retrieve et bin %d bounderies.", etBin)
          histo1.GetXaxis().SetBinLabel(etBin+1, str(etaBin))
    c1.SetGrid()
    c1.Update()
    c1.SaveAs(outname)


  def __printShapes(self, npArray, name):
    "Print numpy shapes"
    if not npArray.dtype.type is np.object_:
      self._info('Extracted %s patterns with size: %r',name, (npArray.shape))
    else:
      shape = npArray.shape
      for etBin in range(shape[0]):
        for etaBin in range(shape[1]):
          self._info( 'Extracted %s patterns (et=%d,eta=%d) with size: %r'
                    , name
                    , etBin
                    , etaBin
                    , (npArray[etBin][etaBin].shape if npArray[etBin][etaBin] is not None else ("None"))
                    )
        # etaBin
      # etBin




createData = CreateData()




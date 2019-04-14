__all__ = [ 'PreProcCurator', 'CrossValidCurator', 'DataCurator'
          , 'getEfficiencyKeyAndLabel', 'CuratedSubset']

from Gaugi import ( Logger, retrieve_kw, NotSet, EnumStringification
                       , firstItemDepth)
from TuningTools.coreDef import npCurrent, coreConf, TuningToolCores
import os

class PreProcCurator( Logger ):
  def __init__(self, logger = None ):
    Logger.__init__( self, logger = logger )

  def getPPObj( self, kw, throw=False, **cKW ):
    ppCol = None
    if 'ppFile' in kw and 'ppCol' in kw:
      self._fatal(("ppFile is mutually exclusive with ppCol, "
          "either use one or another terminology to specify the job "
          "configuration."), ValueError)
    ppFile    = retrieve_kw(kw, 'ppFile', None )
    addDefaultPP = kw.pop('addDefaultPP', True )
    from TuningTools.PreProc import PreProcChain, fixPPCol, PreProcArchieve, Norm1, PreProcMerge

    nSortsVal = cKW.pop('nSortsVal',1)
    nEtaBins  = cKW.pop('nEtaBins',1)
    nEtBins   = cKW.pop('nEtBins',1)

    if not ppFile:
      ppCol = kw.pop( 'ppCol', PreProcChain( Norm1(level = self.level) ) if addDefaultPP else None )
      # Make sure that our pre-processings are PreProcCollection instances and matches
      # the number of sorts, eta and et bins.
      ppCol =  fixPPCol(ppCol,nSortsVal,nEtaBins,nEtBins,level=self.level)
    else:
      if type(ppFile) is list:
        tmpPPCols=[]
        self._logger.info('Merging all preprocs...')
        # Now loop over ppFile and add it to our pp list:
        for f in ppFile:
          self._logger.debug('Opening %s...',f)
          with PreProcArchieve(f) as tmpPPCol:
            tmpPPCol =  fixPPCol(tmpPPCol,nSortsVal,nEtaBins,nEtBins,level=self.level)
            tmpPPCols.append(tmpPPCol)

        ppCol =  fixPPCol(tmpPPCols[0],nSortsVal,nEtaBins,nEtBins,level=self.level)
        for etBinIdx in range(nEtBins):
          for etaBinIdx in range(nEtaBins):
            for sortIdx in range(nSortsVal):
              ppChains = [o[etBinIdx][etaBinIdx][sortIdx] for o in tmpPPCols]
              ppCol[etBinIdx][etaBinIdx][sortIdx] = PreProcChain( [ PreProcMerge(ppChains = ppChains,level=self.level)]  )
      else:
        with PreProcArchieve(ppFile) as ppCol:
          # Make sure that our pre-processings are PreProcCollection instances and matches
          # the number of sorts, eta and et bins.
          ppCol =  fixPPCol(ppCol,nSortsVal,nEtaBins,nEtBins,level=self.level)
    self.ppCol = ppCol

  def hasPP( self, etBinIdx, etaBinIdx, sortIdx ):
    if self.ppCol is None:
      return False
    if etBinIdx > len(self.ppCol):
      return False
    if etaBinIdx > len(self.ppCol[etBinIdx]):
      return False
    if sortIdx > len(self.ppCol[etBinIdx][etaBinIdx]):
      return False
    if not(len(self.ppCol[etBinIdx][etaBinIdx][sortIdx])):
      return False
    return True

  def addPP( self, ppChain, etBinIdx, etaBinIdx, sortIdx ):
    from TuningTools.PreProc import PreProcChain, PreProcCollection
    if self.ppCol is None:
      self.ppCol = PreProcCollection([])
    while etBinIdx >= len(self.ppCol):
      self.ppCol.append( PreProcCollection([]) )
    while etaBinIdx >= len(self.ppCol[etBinIdx]):
      self.ppCol[etBinIdx].append( PreProcCollection([]) )
    while sortIdx >= len(self.ppCol[etBinIdx][etaBinIdx]):
      self.ppCol[etBinIdx][etaBinIdx].append( PreProcChain([]) )
    self.ppCol[etBinIdx][etaBinIdx][sortIdx] = ppChain

class CrossValidCurator( Logger ):
  def __init__(self, logger = None ):
    Logger.__init__( self, logger = logger )

  def getCrossValidObj( self, kw, throw = False, **cKW):
    crossValid = None
    # Make sure that the user didn't try to use both options:
    if 'crossValid' in kw and 'crossValidFile' in kw:
      self._fatal("crossValid is mutually exclusive with crossValidFile, \
          either use or another terminology to specify CrossValid object.", ValueError)
    crossValidFile      = retrieve_kw( kw, 'crossValidFile', None )
    allowDefaultCrossVal = retrieve_kw( kw, 'allowDefaultCrossVal', True )
    from TuningTools.CrossValid import CrossValid, CrossValidArchieve
    if not crossValidFile:
      if not crossValid in kw and not allowDefaultCrossVal:
        self._fatal("Specify cross-validation object!")
      # Cross valid was not specified, read it from crossValid:
      crossValid                 = kw.pop('crossValid',
          CrossValid( level   = self.level
                    , seed    = retrieve_kw(kw, 'crossValidSeed' )
                    , method  = retrieve_kw(kw, 'crossValidMethod' )
                    , shuffle = retrieve_kw(kw, 'crossValidShuffle' ) ) )
    else:
      with CrossValidArchieve( crossValidFile ) as CVArchieve:
        crossValid = CVArchieve
      del CVArchieve
    if crossValid is None and throw:
      raise RuntimeError("Couldn't retrieve crossValid object.")
    self.crossValid = crossValid

class CuratedSubset( EnumStringification ):
  """
  Enumerates possible curated subsets
  """
  trnData        = 1
  valData        = 2
  tstData        = 3
  opData         = 4

  sgnTrnData     = 5
  sgnValData     = 6
  sgnTstData     = 7
  sgnOpData      = 8

  bkgTrnData     = 9
  bkgValData     = 10
  bkgTstData     = 11
  bkgOpData      = 12

  trnBaseInfo    = 13
  valBaseInfo    = 14
  tstBaseInfo    = 15
  opBaseInfo     = 16

  sgnTrnBaseInfo = 17
  sgnValBaseInfo = 18
  sgnTstBaseInfo = 19
  sgnOpBaseInfo  = 20

  bkgTrnBaseInfo = 21
  bkgValBaseInfo = 22
  bkgTstBaseInfo = 23
  bkgOpBaseInfo  = 24

  @classmethod
  def isbinary( cls, val ):
    val = cls.retrieve( val )
    if val <= 4 or 13 <= val <= 16:
      return True
    return False

  @classmethod
  def issgn( cls, val ):
    val = cls.retrieve( val )
    if 4 < val <= 8 or 16 < val <= 20:
      return True
    return False

  @classmethod
  def isbkg( cls, val ):
    val = cls.retrieve( val )
    if 9 < val <= 12 or 20 < val <= 24:
      return True
    return False

  @classmethod
  def isoperation( cls, val ):
    val = cls.retrieve( val )
    if val in (4,8,12,16,20,24):
      return True
    return False

  @classmethod
  def ispattern( cls, val ):
    val = cls.retrieve( val )
    if val <= 12:
      return True
    return False

  @classmethod
  def tosgn( cls, val ):
    val = cls.retrieve( val )
    if   val is CuratedSubset.trnData:        return CuratedSubset.sgnTrnData
    elif val is CuratedSubset.valData:        return CuratedSubset.sgnValData
    elif val is CuratedSubset.tstData:        return CuratedSubset.sgnTstData
    elif val is CuratedSubset.opData:         return CuratedSubset.sgnOpData

    elif val is CuratedSubset.sgnTrnData:     return CuratedSubset.sgnTrnData
    elif val is CuratedSubset.sgnValData:     return CuratedSubset.sgnValData
    elif val is CuratedSubset.sgnTstData:     return CuratedSubset.sgnTstData
    elif val is CuratedSubset.sgnOpData:      return CuratedSubset.sgnOpData

    elif val is CuratedSubset.bkgTrnData:     return CuratedSubset.sgnTrnData
    elif val is CuratedSubset.bkgValData:     return CuratedSubset.sgnValData
    elif val is CuratedSubset.bkgTstData:     return CuratedSubset.sgnTstData
    elif val is CuratedSubset.bkgOpData:      return CuratedSubset.sgnOpData

    elif val is CuratedSubset.trnBaseInfo:    return CuratedSubset.sgnTrnBaseInfo
    elif val is CuratedSubset.valBaseInfo:    return CuratedSubset.sgnValBaseInfo
    elif val is CuratedSubset.tstBaseInfo:    return CuratedSubset.sgnTstBaseInfo
    elif val is CuratedSubset.opBaseInfo:     return CuratedSubset.sgnOpBaseInfo

    elif val is CuratedSubset.sgnTrnBaseInfo: return CuratedSubset.sgnTrnBaseInfo
    elif val is CuratedSubset.sgnValBaseInfo: return CuratedSubset.sgnValBaseInfo
    elif val is CuratedSubset.sgnTstBaseInfo: return CuratedSubset.sgnTstBaseInfo
    elif val is CuratedSubset.sgnOpBaseInfo:  return CuratedSubset.sgnOpBaseInfo

    elif val is CuratedSubset.bkgTrnBaseInfo: return CuratedSubset.sgnTrnBaseInfo
    elif val is CuratedSubset.bkgValBaseInfo: return CuratedSubset.sgnValBaseInfo
    elif val is CuratedSubset.bkgTstBaseInfo: return CuratedSubset.sgnTstBaseInfo
    elif val is CuratedSubset.bkgOpBaseInfo:  return CuratedSubset.sgnOpBaseInfo

  @classmethod
  def tobkg( cls, val ):
    val = cls.retrieve( val )
    if   val is CuratedSubset.trnData:        return CuratedSubset.bkgTrnData
    elif val is CuratedSubset.valData:        return CuratedSubset.bkgValData
    elif val is CuratedSubset.tstData:        return CuratedSubset.bkgTstData
    elif val is CuratedSubset.opData:         return CuratedSubset.bkgOpData

    elif val is CuratedSubset.sgnTrnData:     return CuratedSubset.bkgTrnData
    elif val is CuratedSubset.sgnValData:     return CuratedSubset.bkgValData
    elif val is CuratedSubset.sgnTstData:     return CuratedSubset.bkgTstData
    elif val is CuratedSubset.sgnOpData:      return CuratedSubset.bkgOpData

    elif val is CuratedSubset.bkgTrnData:     return CuratedSubset.bkgTrnData
    elif val is CuratedSubset.bkgValData:     return CuratedSubset.bkgValData
    elif val is CuratedSubset.bkgTstData:     return CuratedSubset.bkgTstData
    elif val is CuratedSubset.bkgOpData:      return CuratedSubset.bkgOpData

    elif val is CuratedSubset.trnBaseInfo:    return CuratedSubset.bkgTrnBaseInfo
    elif val is CuratedSubset.valBaseInfo:    return CuratedSubset.bkgValBaseInfo
    elif val is CuratedSubset.tstBaseInfo:    return CuratedSubset.bkgTstBaseInfo
    elif val is CuratedSubset.opBaseInfo:     return CuratedSubset.bkgOpBaseInfo

    elif val is CuratedSubset.sgnTrnBaseInfo: return CuratedSubset.bkgTrnBaseInfo
    elif val is CuratedSubset.sgnValBaseInfo: return CuratedSubset.bkgValBaseInfo
    elif val is CuratedSubset.sgnTstBaseInfo: return CuratedSubset.bkgTstBaseInfo
    elif val is CuratedSubset.sgnOpBaseInfo:  return CuratedSubset.bkgOpBaseInfo

    elif val is CuratedSubset.bkgTrnBaseInfo: return CuratedSubset.bkgTrnBaseInfo
    elif val is CuratedSubset.bkgValBaseInfo: return CuratedSubset.bkgValBaseInfo
    elif val is CuratedSubset.bkgTstBaseInfo: return CuratedSubset.bkgTstBaseInfo
    elif val is CuratedSubset.bkgOpBaseInfo:  return CuratedSubset.bkgOpBaseInfo

  @classmethod
  def tobinary( cls, val ):
    val = cls.retrieve( val )
    if   val is CuratedSubset.trnData:        return CuratedSubset.trnData
    elif val is CuratedSubset.valData:        return CuratedSubset.valData
    elif val is CuratedSubset.tstData:        return CuratedSubset.tstData
    elif val is CuratedSubset.opData:         return CuratedSubset.opData

    elif val is CuratedSubset.sgnTrnData:     return CuratedSubset.trnData
    elif val is CuratedSubset.sgnValData:     return CuratedSubset.valData
    elif val is CuratedSubset.sgnTstData:     return CuratedSubset.tstData
    elif val is CuratedSubset.sgnOpData:      return CuratedSubset.opData

    elif val is CuratedSubset.bkgTrnData:     return CuratedSubset.trnData
    elif val is CuratedSubset.bkgValData:     return CuratedSubset.valData
    elif val is CuratedSubset.bkgTstData:     return CuratedSubset.tstData
    elif val is CuratedSubset.bkgOpData:      return CuratedSubset.opData

    elif val is CuratedSubset.trnBaseInfo:    return CuratedSubset.trnBaseInfo
    elif val is CuratedSubset.valBaseInfo:    return CuratedSubset.valBaseInfo
    elif val is CuratedSubset.tstBaseInfo:    return CuratedSubset.tstBaseInfo
    elif val is CuratedSubset.opBaseInfo:     return CuratedSubset.opBaseInfo

    elif val is CuratedSubset.sgnTrnBaseInfo: return CuratedSubset.trnBaseInfo
    elif val is CuratedSubset.sgnValBaseInfo: return CuratedSubset.valBaseInfo
    elif val is CuratedSubset.sgnTstBaseInfo: return CuratedSubset.tstBaseInfo
    elif val is CuratedSubset.sgnOpBaseInfo:  return CuratedSubset.opBaseInfo

    elif val is CuratedSubset.bkgTrnBaseInfo: return CuratedSubset.trnBaseInfo
    elif val is CuratedSubset.bkgValBaseInfo: return CuratedSubset.valBaseInfo
    elif val is CuratedSubset.bkgTstBaseInfo: return CuratedSubset.tstBaseInfo
    elif val is CuratedSubset.bkgOpBaseInfo:  return CuratedSubset.opBaseInfo

  @classmethod
  def todataset( cls, val ):
    val = cls.retrieve( val )
    from TuningTools import Dataset
    if   val % 4 is 1: return Dataset.Train
    elif val % 4 is 2: return Dataset.Validation
    elif val % 4 is 3: return Dataset.Test
    elif val % 4 is 0: return Dataset.Operation

  @classmethod
  def fromdataset( cls, val ):
    val = cls.retrieve( val )
    from TuningTools import Dataset
    if   val is Dataset.Train     : return CuratedSubset.trnData
    elif val is Dataset.Validation: return CuratedSubset.valData
    elif val is Dataset.Test      : return CuratedSubset.tstData
    elif val is Dataset.Operation : return CuratedSubset.opData

  @classmethod
  def tobaseinfo( cls, val ):
    val = cls.retrieve( val )
    if val <= 12:
      val += 12
      return val
    return val

  @classmethod
  def topattern( cls, val ):
    val = cls.retrieve( val )
    if val > 12:
      val -= 12
      return val
    return val

class DataCurator( CrossValidCurator, PreProcCurator, Logger ):

  def __init__(self, d = {}, **kw ):
    d.update( kw ); del kw
    PreProcCurator.__init__( self )
    CrossValidCurator.__init__( self )
    Logger.__init__( self, d )
    from TuningTools.CreateData import TuningDataArchieve, BenchmarkEfficiencyArchieve
    # We assume that the number of bins are equal for all files
    dataLocation = retrieve_kw(d, 'dataLocation', NotSet)
    if not isinstance(dataLocation, (list,tuple)):
      dataLocation = [dataLocation]
    # Ensure taht all dataLocation specified is valid:
    for dL in reversed(dataLocation):
      self.isEtDependent, self.isEtaDependent, self.nEtBins, self.nEtaBins, self.tdVersion = \
          TuningDataArchieve.load(dL, retrieveBinsInfo=True, retrieveVersion=True)
    self.dataLocation = dataLocation
    self._debug("Total number of et bins: %d" , self.nEtBins)
    self._debug("Total number of eta bins: %d" , self.nEtaBins)
    # Check whether it is need to retrieve efficiencies from another reference file:
    refFile = None
    refFilePath = retrieve_kw( d, 'refFile', NotSet)
    if not (refFilePath in (None, NotSet)):
      self._info("Reading reference file...")
      refFile = BenchmarkEfficiencyArchieve.load( refFilePath,
                                                  loadCrossEfficiencies = True )
      if not refFile.checkForCompatibleBinningFile( self.dataLocation[0] ):
        self._logger.error("Reference file binning information is not compatible with data file. Ignoring reference file!")
        refFile = None
    self.refFile = refFile
    # Set default operation point
    self.requestedOP = retrieve_kw( d, 'operationPoint',  None )
    if self.requestedOP is None and refFile:
      self.requestedOP = refFile.operation
    # Get transformation objects
    self.getCrossValidObj(d, throw = True)
    self.getPPObj( d, throw =  retrieve_kw(d, 'allowNoPP', True)
                 , nSortsVal = self.crossValid.nSorts() , nEtaBins = self.nEtaBins, nEtBins = self.nEtBins)
    # TODO Probably this is better as part of the crossValid information, with
    # its own et/eta grid
    clusterFile      = retrieve_kw( d, 'clusterFile', None )
    if clusterFile is None:
      clusterCol = retrieve_kw( d, 'cluster', None)
      if clusterCol and (type(clusterCol) is not SubsetGeneratorCollection):
        self._fatal('cluster must be a SubsetGeneratorCollection type.', ValueError)
      if self.tdVersion < 6 and clusterCol is not None:
        self._warning("Cluster collection will be ignored as file version is lower than 6.")
        clusterCol = None
    else:
      with SubsetGeneratorArchieve(clusterFile) as SGArchieve:
        clusterCol = SGArchieve
      if self.tdVersion < 6 and clusterCol is not None:
        self._warning("Cluster collection will be ignored as file version is lower than 6.")
        clusterCol = None
    self.clusterCol = clusterCol
    self.addPileupToOutputLayer = retrieve_kw( d, 'addPileupToOutputLayer', False )

    # Check whether we are exporting pp data
    self.saveMatPP = retrieve_kw( d, 'saveMatPP', False )
    self.ppSavePath = retrieve_kw( d, 'ppSavePath', '' )

    # Set runtime properties:
    self._tuningWrapper = NotSet
    self.releaseBinInfo()
    self.releaseRawPatterns()
    self.releaseSubsets()

  def checkBinPrepared( self, etBinIdx, etaBinIdx, loadEfficiencies, loadCrossEfficiencies ):
    if self.etBinIdx != etBinIdx: return False
    if self.etaBinIdx != etaBinIdx: return False
    if self.loadEfficiencies != loadEfficiencies: return False
    if self.loadCrossEfficiencies != loadCrossEfficiencies: return False
    return True

  def releaseBinInfo( self ):
    self.sort                  = NotSet
    self.ppChain               = NotSet
    self.etBinIdx              = NotSet
    self.etBin                 = NotSet
    self.etaBinIdx             = NotSet
    self.etaBin                = NotSet
    self.loadEfficiencies      = NotSet
    self.loadCrossEfficiencies = NotSet
    self.references            = NotSet
    self.binStr                = NotSet
    self.benchmarks            = NotSet
    self.crossBenchmarks       = NotSet

  def prepareForBin( self, etBinIdx, etaBinIdx, loadEfficiencies = True, loadCrossEfficiencies = True ):
    if self.checkBinPrepared( etBinIdx, etaBinIdx, loadEfficiencies, loadCrossEfficiencies ):
      self._debug("Already prepared et/eta bin: %d, %d", etBinIdx, etaBinIdx)
      return
    # Release previous information
    self.releaseBinInfo()
    self.releaseSubsets()
    self.releaseRawPatterns()
    # Keep track of what is prepared:
    self.etBinIdx              = etBinIdx
    self.etaBinIdx             = etaBinIdx
    self.loadEfficiencies      = loadEfficiencies
    self.loadCrossEfficiencies = loadCrossEfficiencies
    self.binStr = ' (etBinIdx=%d,etaBinIdx=%d)' % (etBinIdx, etaBinIdx) if etBinIdx is not None and etaBinIdx is not None else ''
    # Start job
    self.loadRawPatterns()

    # Set operation point
    self.operationPoint = self.tdArchieve[0].operation if self.requestedOP is None else self.requestedOP
    doMultiStop = self.tuningWrapper.doMultiStop if self.tuningWrapper else False
    #doMultiStop = self.tuningWrapper.doMultiStop if self.tuningWrapper else True

    # Retrieve bin information:
    if self.isEtDependent:
      self.etBin = self.tdArchieve[0].etBins
      self._info('Prepared Et bin: %r', self.etBin)
    if self.isEtaDependent:
      self.etaBin = self.tdArchieve[0].etaBins
      self._info('Prepared eta bin: %r', self.etaBin)

    self.benchmarks      = None
    self.crossBenchmarks = None
    self.references      = None
    # Retrieve benchmarks and crossBenchmarks:
    benchmarks = None
    if loadEfficiencies:
      try:
        from TuningTools.dataframe.EnumCollection import RingerOperation
        #NOTE: We assume that every data has the same version
        efficiencyKey, refLabel = getEfficiencyKeyAndLabel( self.dataLocation[0], self.operationPoint )
        # It may be that version 4 files had efficiency keys saved as strings
        #efficiencyKey = RingerOperation.tostring( efficiencyKey )
        try:
          benchmarks = (self.refFile.signalEfficiencies[efficiencyKey],
                        self.refFile.backgroundEfficiencies[efficiencyKey])
        except (AttributeError, KeyError):
          if self.refFile is not None:
            self._logger.error("Couldn't retrieve efficiencies from reference file. Attempting to use tuning data references instead...")
          benchmarks = (self.tdArchieve[0].signalEfficiencies[efficiencyKey],
                        self.tdArchieve[0].backgroundEfficiencies[efficiencyKey])
      except KeyError, e:
        if doMultiStop:
          self._fatal("Couldn't retrieve benchmark efficiencies! Reason:\n%s", e)
        else:
          self._warning("Couldn't retrieve benchmark efficiencies. Proceeding anyway since no multistop was requested. Failure reason:\n%s", e)
    crossBenchmarks = None
    if loadCrossEfficiencies:
      try:
        #if _tuningWrapper.useTstEfficiencyAsRef:
        try:
          crossBenchmarks = (self.refFile.signalCrossEfficiencies[efficiencyKey],
                             self.refFile.backgroundCrossEfficiencies[efficiencyKey])
        except (AttributeError, KeyError):
          crossBenchmarks = (self.tdArchieve[0].signalCrossEfficiencies[efficiencyKey],
                             self.tdArchieve[0].backgroundCrossEfficiencies[efficiencyKey])
      except (AttributeError, KeyError, TypeError):
        self._info("Cross-validation benchmark efficiencies is not available.")
        crossBenchmarks = None
        if self.tuningWrapper: self.tuningWrapper.useTstEfficiencyAsRef = False
    # Add external access:
    self.benchmarks = benchmarks
    self.crossBenchmarks = crossBenchmarks

    # Add the signal efficiency and background efficiency as goals to the
    # tuning wrapper:
    from TuningTools import ReferenceBenchmark, ReferenceBenchmarkCollection
    references = ReferenceBenchmarkCollection([])
    if loadEfficiencies:
      if doMultiStop:
        opRefs = [ReferenceBenchmark.SP, ReferenceBenchmark.Pd, ReferenceBenchmark.Pf]
      else:
        opRefs = [ReferenceBenchmark.SP]
      for ref in opRefs:
        if type(benchmarks) is tuple and type(benchmarks[0]) is list:
          if crossBenchmarks is not None and (crossBenchmarks[0][etBinIdx]) and crossBenchmarks[1][etBinIdx]:
            references.append( ReferenceBenchmark( "Tuning_" + refLabel.replace('Accept','') + "_"
                                                 + ReferenceBenchmark.tostring( ref ),
                                                   ref, benchmarks[0][etBinIdx][etaBinIdx], benchmarks[1][etBinIdx][etaBinIdx],
                                                   crossBenchmarks[0][etBinIdx][etaBinIdx], crossBenchmarks[1][etBinIdx][etaBinIdx]
                                                  , etBinIdx=etBinIdx, etaBinIdx=etaBinIdx ) )
          elif benchmarks is not None and benchmarks[0][etBinIdx] and benchmarks[1][etBinIdx]:
            references.append( ReferenceBenchmark( "Tuning_" + refLabel.replace('Accept','') + "_"
                                                 + ReferenceBenchmark.tostring( ref ),
                                                   ref, benchmarks[0][etBinIdx][etaBinIdx], benchmarks[1][etBinIdx][etaBinIdx]
                                                  , etBinIdx=etBinIdx, etaBinIdx=etaBinIdx))
          elif not doMultiStop :
            references.append( ReferenceBenchmark( "Tuning_" + refLabel.replace('Accept','') + "_"
                                                 + ReferenceBenchmark.tostring( ref ), ref) )
          else: self._fatal("No benchmark efficiency could be found")
        else:
          if crossBenchmarks is not None and crossBenchmarks[0].etaBin != -1:
            references.append( ReferenceBenchmark( "Tuning_" + refLabel.replace('Accept','') + "_"
                                                 + ReferenceBenchmark.tostring( ref ),
                                                   ref, benchmarks[0], benchmarks[1]
                                                 , crossBenchmarks[0], crossBenchmarks[1], etBinIdx=etBinIdx, etaBinIdx=etaBinIdx) )
          elif benchmarks is not None and benchmarks[0].etaBin != -1:
            references.append( ReferenceBenchmark( "Tuning_" + refLabel.replace('Accept','') + "_"
                                                 + ReferenceBenchmark.tostring( ref ),
                                                   ref, benchmarks[0], benchmarks[1]
                                                 , etBinIdx=etBinIdx, etaBinIdx=etaBinIdx ) )
          elif not doMultiStop :
            references.append( ReferenceBenchmark( "Tuning_" + refLabel.replace('Accept','') + "_"
                                                 + ReferenceBenchmark.tostring( ref ), ref) )
          else: self._fatal("No benchmark efficiency could be found")
      # Add external access:
    self.references = references


  def checkSubsetsAvailable( self, sort ):
    if self.sort != sort: return False
    return self.hasSubsets()

  def cachePP( self, sort, ppChain = None ):
    self.sort = sort; del sort
    self.ppChain = self.ppCol[self.etBinIdx][self.etaBinIdx][self.sort] if ppChain is None else ppChain
    if ppChain and not self.hasPP( self.etBinIdx, self.etaBinIdx, self.sort):
      self.addPP( ppChain, self.etBinIdx, self.etaBinIdx, self.sort )
    from TuningTools.PreProc import Norm1, RingerPU
    if self.addPileupToOutputLayer:
      if self.ppChain.has( Norm1 ):
        # FIXME Hardcoded
        self.ppChain[ [type(n) is Norm1 for n in self.ppChain ].index(True) ] = RingerPU(pileupThreshold = 33.)
      else:
        self._fatal("Do not know how to handle ppChain %s to addPileupToOutputLayer", ppChain)

  def toTunableSubsets(self, sort, ppChain = None ):
    " Transform holden data to tunable patterns "
    if self.checkSubsetsAvailable( sort ):
      self._debug("Already prepared subsets for et/eta bin (%d, %d) and sort idx (%d).", self.etBinIdx, self.etaBinIdx, sort)
      return
    if not self.hasRawPattern():
      if not self.hasSubsets():
        self._fatal("Attempted to retrieve tunable subsets but no data is available!", RuntimeError)
      else:
        self.toRawPatterns()
    self.cachePP( sort, ppChain ); del sort
    lPat = len(self.patterns)
    if self.tdVersion >= 6:
      # We change the patterns since we are going to erase them anyway:
      for pCount in range(lPat):
        self.patterns[pCount], tmp = self.ppChain.psprocessing(self.patterns[pCount], self.baseInfo, pCount = pCount)
      # TODO This may be a good place to place the bagging
      self.baseInfo = tmp; del tmp
    else:
      self._warning("Tuning data version is too old for applying psprocessing.")
    self._info('Extracting patterns cross validation sort %d.', self.sort)
    trnData, valData, tstData = [[None]*len(self.patterns) for _ in range(3)]
    # TODO If merged, join data and keep as curated data only the merged when a
    # flag is specified
    for i in range(lPat):
      trnData[i], valData[i], tstData[i] = self.crossValid( self.patterns[i], self.sort
                                                          , subset=self.clusterCol  )
    # Pop indexes
    if lPat == 1:
      trnData = trnData[0]; valData = valData[0]; tstData = tstData[0]
    elif coreConf() is TuningToolCores.keras:
      self._fatal("Not implemented case for more than 1 dataset when using keras as core.")
    # Now do the same with the base information:
    from TuningTools import BaseInfo
    trnBaseInfo, valBaseInfo, tstBaseInfo = [[(None, None) for _ in range(BaseInfo.nInfo)] for _ in range(3)]
    # FIXME: Use map
    if not(all([b is None for b in self.baseInfo])):
      for idx in range(BaseInfo.nInfo):
        self._info("Extracting base info (%s) cross validation sort %d", BaseInfo.tostring(idx), self.sort)
        trnBaseInfo[idx], valBaseInfo[idx], tstBaseInfo[idx] \
            = self.crossValid( [self.baseInfo[0][idx], self.baseInfo[1][idx]]
                             , self.sort
                             , subset=self.clusterCol )
    self.trnBaseInfo = trnBaseInfo
    self.valBaseInfo = valBaseInfo
    self.tstBaseInfo = tstBaseInfo
    _hasTstBaseInfo = True
    if not(self.tstBaseInfo) or (not all(self.tstBaseInfo)):
      self.tstBaseInfo = self.valBaseInfo
      _hasTstBaseInfo = False
    # Take ppChain parameters on training data:
    def define_set_suffix( d, s ):
      if d is None: return d
      from copy import copy
      d = copy(d)
      d['filename'] = d['filename'] % s
      return d
    savePP = self._getSaveObj( addSort = False, addSuffix = True) if self.ppChain.takesParamsFromData is True else None
    self._info('Tuning pre-processing chain (%s)...', self.ppChain)
    self._debug('Retrieving parameters and applying pp chain to train dataset...')
    trnData = self.ppChain.takeParams( trnData, saveArgsDict = define_set_suffix( savePP, 'trn' ) )
    self._debug('Done tuning pre-processing chain!')
    # Check whether we should save individual mat files
    if not(self.ppChain.takesParamsFromData) and self.saveMatPP:
      # Just a hack to for saving data:
      self[CuratedSubset.opData]
    self._info('Applying pre-processing chain to remaining sets...')
    # Apply self.ppChain:
    self._debug('Applying pp chain to validation dataset...')
    valData = self.ppChain( valData, saveArgsDict = define_set_suffix( savePP, 'val' ) )
    self._debug('Applying pp chain to test dataset...')
    tstData = self.ppChain( tstData, saveArgsDict = define_set_suffix( savePP, 'tst' ) )
    self._debug('Done applying the pre-processing chain to all sets!')
    # Book info for external access:
    self.trnData = trnData
    self.valData = valData
    self.tstData = tstData
    self._updateSubsetInfo()
    if coreConf() is TuningToolCores.FastNet and self.merged:
      import numpy as np
      self.trnData = [np.concatenate([t[didx] for t in self.trnData], axis=npCurrent.pdim).astype(npCurrent.fp_dtype) for didx in range(2)]
      self.valData = [np.concatenate([v[didx] for v in self.valData], axis=npCurrent.pdim).astype(npCurrent.fp_dtype) for didx in range(2)]
      if self.tstData and all(self.tstData):
        self.tstData = [np.concatenate([t[didx] for t in self.tstData], axis=npCurrent.pdim).astype(npCurrent.fp_dtype) for didx in range(2)]
    self.hasTstData = True
    if not(self.tstData) or (not all(self.tstData)):
      self.tstData = self.valData
      self.hasTstData = False
    if self.hasTstData != _hasTstBaseInfo:
      self._fatal("Test data available for pattern or base info and not available for the other case.")
    self._updateSubsetInfo()
    self.releaseRawPatterns()

  def sortData( self, baseInfo ):
    from TuningTools import BaseInfo
    import numpy as np
    # TODO Handle multidataset case
    if self.hasRawPattern():
      try:
        baseInfo = BaseInfo.retrieve( baseInfo )
        idx = [np.argsort( b[baseInfo], axis = npCurrent.odim ).squeeze() for b in self.baseInfo]
      except:
        idx = [np.argsort( np.sum(p, axis=npCurrent.pdim), axis = npCurrent.odim ).squeeze() for p in self.patterns[0]]
      self.baseInfo = [[b[i] for b in p] for p, i in zip(self.baseInfo,idx)]
      self.patterns[0] = [p[npCurrent.access( pidx = ':', oidx = i )] for p, i in zip(self.patterns[0], idx)]
    else:
      self._fatal("Not implemented sorting when not raw pattern is available.")

  def _getSaveObj( self, addSort, addSuffix ):
    # Take ppChain parameters on training data:
    if not self.saveMatPP: return None
    sort = self.sort if addSort else None
    savePP = { 'filename' : os.path.join( self.ppSavePath, 'data.pp' ) }
    from Gaugi import appendToFileName
    savePP['filename'] = appendToFileName( savePP['filename'], 'etBin%d_etaBin%d%s' % (self.etBinIdx,self.etaBinIdx,
      (("_sort%d" % sort) if sort is not None else '')) )
    if addSuffix: savePP['filename'] = savePP['filename'] + '_%s'
    return savePP

  def _updateSubsetInfo( self ):
    depth = firstItemDepth(self.trnData)
    self.merged = depth > 1
    if self.merged:
      self.nInputs = [self.trnData[0][0].shape[npCurrent.pdim], self.trnData[1][0].shape[npCurrent.pdim]]
    else:
      self.nInputs = self.trnData[0].shape[npCurrent.pdim]

  def toRawPatterns(self):
    " Transform holden data to raw patterns "
    if self.isRevertible():
      if self.tuningWrapper and not self.hasSubsets():
        self.retrieveSubsets( self.tuningWrapper )
      patterns = []
      for i in range(len(trnData) if depth == 2 else 1):
        patterns[i] = self.crossValid.revert( self.trnData[i], self.valData[i], self.tstData[i] if self.hasTstData else None, sort = self.sort )
      if depth == 1:
        patterns = patterns[0]
      self.patterns = ppChain( patterns , revert = True )
    else:
      # We cannot revert, reload data:
      self.loadRawPatterns()
    self.releaseSubsets()

  def loadRawPatterns(self):
    self._info('Loading raw data...')
    from TuningTools.CreateData import TuningDataArchieve
    self.tdArchieve = [ TuningDataArchieve.load(dL,
                                            etBinIdx = self.etBinIdx,
                                            etaBinIdx = self.etaBinIdx ) for dL in self.dataLocation]
    self.patterns = [ (t.signalPatterns, t.backgroundPatterns) for t in self.tdArchieve]

    # Retrieve base information:
    if self.tdVersion >= 6:
      self.baseInfo = (self.tdArchieve[0].signalBaseInfo, self.tdArchieve[0].backgroundBaseInfo)
    else:
      self.baseInfo = (None, None)

  def releaseSubsets(self):
    self.trnData     = NotSet
    self.valData     = NotSet
    self.tstData     = NotSet
    self.hasTstData  = NotSet
    self.trnBaseInfo = NotSet
    self.valBaseInfo = NotSet
    self.tstBaseInfo = NotSet
    self.merged      = NotSet
    self.nInputs     = NotSet

  def releaseRawPatterns(self):
    self.tdArchieve = NotSet
    self.patterns   = NotSet
    self.baseInfo   = NotSet

  def hasSubsets(self):
    return self.trnData is not NotSet and self.valData is not NotSet and self.tstData is not NotSet and \
           self.trnBaseInfo is not NotSet and self.valBaseInfo is not NotSet and self.tstBaseInfo is not NotSet

  def hasRawPattern(self):
    return self.patterns is not NotSet

  def isRevertible(self):
    if not self.tuningWrapper and not self.hasSubsets():
      return False
    return self.crossValid.isRevertible() and self.ppChain.isRevertible() and self.clusterCol is NotSet

  def transferSubsets( self, tuningWrapper = None ):
    if tuningWrapper is None: tuningWrapper = self.tuningWrapper
    self.tuningWrapper = tuningWrapper
    tuningWrapper.setTrainData( self.trnData )
    tuningWrapper.setValData  ( self.valData )
    if self.hasTstData > 0:
      tuningWrapper.setTestData( self.tstData )
    else:
      self._debug('Using validation dataset as test dataset.')

  def retrieveSubsets( self, tuningWrapper = None ):
    if tuningWrapper is None: tuningWrapper = self.tuningWrapper
    self.trnData = tuningWrapper.trnData(release = True)
    self.valData = tuningWrapper.valData(release = True)
    self.tstData = tuningWrapper.testData(release = True)
    if not(self.tstData) or (not all(self.tstData)):
      self.tstData = self.valData
      self.hasTstData = False
    self.tuningWrapper = tuningWrapper
    self._updateSubsetInfo()

  @property
  def tuningWrapper( self ):
    return self._tuningWrapper

  @tuningWrapper.setter
  def tuningWrapper( self, value ):
    from TuningTools import TuningWrapper
    if not isinstance(value, TuningWrapper):
      self._fatal("Requested to transfer data to invalid TuningWrapper", ValueError)
    self._tuningWrapper = value
    # Update tuningWrapper to use some of our configuration
    self._tuningWrapper.addPileupToOutputLayer = self.addPileupToOutputLayer

  def get(self, idx):
    return self[idx]

  def getBaseInfo(self, idx, baseInfoIdx):
    from TuningTools import BaseInfo
    baseInfoIdx = BaseInfo.retrieve(baseInfoIdx)
    if CuratedSubset.isbinary( idx ):
      return [pat[baseInfoIdx] for pat in self[CuratedSubset.tobaseinfo(idx)]]
    else:
      return self[CuratedSubset.tobaseinfo(idx)][baseInfoIdx]

  def __getitem__(self, idx):
    idx = CuratedSubset.retrieve( idx )
    self._verbose('Requested subset: %s', CuratedSubset.tostring(idx) )
    # TODO How do we want dataCurator to handle multiple datasets for the expert neural network?
    if not(self.hasSubsets()) and not(CuratedSubset.isoperation(idx)):
        # FIXME Improve error description
      self._fatal("Curated dataset is not available: %s", CuratedSubset.tostring(idx))
    if CuratedSubset.isoperation(idx) and ( not(self.hasSubsets()) and not(self.hasRawPattern() and self.ppChain ) ):
      self._fatal("No prepared data or rawData with ppChain available. Attempted to retrieve curated dataset: %s", CuratedSubset.tostring(idx))
    if CuratedSubset.isoperation(idx) and self.hasRawPattern():
      if len(self.patterns) > 1:
        self._fatal("Cannot handle cases with more than one dataset yet.")
      tPatterns = self.patterns[0] if len(self.patterns) == 1 else self.patterns
      tPatterns, baseInfo = self.ppChain.psprocessing(tPatterns, self.baseInfo, pCount = 0)
      tPatterns = self.ppChain( tPatterns, saveArgsDict = self._getSaveObj( addSort = False, addSuffix = False ) ) # FIXME: getSaveObj is a hack
    if idx is CuratedSubset.trnData:          return self.trnData
    elif idx is CuratedSubset.valData:        return self.valData
    elif idx is CuratedSubset.tstData:        return self.tstData
    elif idx is CuratedSubset.opData:
      # NOTE: To avoid concatenating the numpy arrays, we return instead a list
      # with all datasets
      if self.hasSubsets():
        return [[self.trnData[i], self.valData[i]] + ([self.tstData[i]] if self.hasTstData else []) for i in 2]
      elif self.hasRawPattern():
        return [tPatterns[0]]
    elif idx is CuratedSubset.sgnTrnData:     return self.trnData[0]
    elif idx is CuratedSubset.sgnValData:     return self.valData[0]
    elif idx is CuratedSubset.sgnTstData:     return self.tstData[0]
    elif idx is CuratedSubset.sgnOpData:
      # NOTE: To avoid concatenating the numpy arrays, we return instead a list
      # with all datasets
      if self.hasSubsets():
        return [self.trnData[0], self.valData[0]] + ([self.tstData[0]] if self.hasTstData else [])
      elif self.hasRawPattern():
        return [tPatterns[0]]
    elif idx is CuratedSubset.bkgTrnData:     return self.trnData[1]
    elif idx is CuratedSubset.bkgValData:     return self.valData[1]
    elif idx is CuratedSubset.bkgTstData:     return self.tstData[1]
    elif idx is CuratedSubset.bkgOpData:
      # NOTE: To avoid concatenating the numpy arrays, we return instead a list
      # with all datasets
      if self.hasSubsets():
        return [self.trnData[1], self.valData[1]] + ([self.tstData[1]] if self.hasTstData else [])
      elif self.hasRawPattern():
        return [tPatterns[1]]
    # Evaluated all patterns, now evaluate baseInfo
    from TuningTools import BaseInfo
    opBaseInfo = [self.trnBaseInfo, self.valBaseInfo] + ([self.tstBaseInfo] if self.hasTstData else [])
    if idx is CuratedSubset.trnBaseInfo:
      return [[self.trnBaseInfo[i][j] for i in range(BaseInfo.nInfo)] for j in range(2)]
    elif idx is CuratedSubset.valBaseInfo:
      return [[self.valBaseInfo[i][j] for i in range(BaseInfo.nInfo)] for j in range(2)]
    elif idx is CuratedSubset.tstBaseInfo:
      return [[self.tstBaseInfo[i][j] for i in range(BaseInfo.nInfo)] for j in range(2)]
    elif idx is CuratedSubset.opBaseInfo:
      if self.hasSubsets():
        return [[[info[i][j] for info in opBaseInfo] for i in range(BaseInfo.nInfo)] for j in range(2)]
      elif self.hasRawPattern():
        return [[[i] for i in b] for b in baseInfo] if baseInfo else None
    elif idx is CuratedSubset.sgnTrnBaseInfo:
      return [self.trnBaseInfo[i][0] for i in range(BaseInfo.nInfo)] if len(self.trnBaseInfo) == BaseInfo.nInfo else []
    elif idx is CuratedSubset.sgnValBaseInfo:
      return [self.valBaseInfo[i][0] for i in range(BaseInfo.nInfo)] if len(self.valBaseInfo) == BaseInfo.nInfo else []
    elif idx is CuratedSubset.sgnTstBaseInfo:
      return [self.tstBaseInfo[i][0] for i in range(BaseInfo.nInfo)] if len(self.tstBaseInfo) == BaseInfo.nInfo else []
    elif idx is CuratedSubset.sgnOpBaseInfo:
      if self.hasSubsets():
        return [[info[i][0] for info in opBaseInfo] for i in range(BaseInfo.nInfo)]
      elif self.hasRawPattern():
        return [[i] for i in baseInfo[0]] if baseInfo else None
    elif idx is CuratedSubset.bkgTrnBaseInfo:
      return [self.trnBaseInfo[i][1] for i in range(BaseInfo.nInfo)] if len(self.trnBaseInfo) == BaseInfo.nInfo else []
    elif idx is CuratedSubset.bkgValBaseInfo:
      return [self.valBaseInfo[i][1] for i in range(BaseInfo.nInfo)] if len(self.valBaseInfo) == BaseInfo.nInfo else []
    elif idx is CuratedSubset.bkgTstBaseInfo:
      return [self.tstBaseInfo[i][1] for i in range(BaseInfo.nInfo)] if len(self.tstBaseInfo) == BaseInfo.nInfo else []
    elif idx is CuratedSubset.bkgOpBaseInfo:
      if self.hasSubsets():
        return [[info[i][1] for info in opBaseInfo] for i in range(BaseInfo.nInfo)]
      elif self.hasRawPattern():
        return [[i] for i in baseInfo[1]] if baseInfo else None

def getEfficiencyKeyAndLabel( filePath, operationPoint ):
  from TuningTools.CreateData import TuningDataArchieve, BenchmarkEfficiencyArchieve
  # Retrieve file version:
  effVersion = None
  try:
    tdVersion = TuningDataArchieve.load( filePath, retrieveVersion=True)
  except:
    effVersion = BenchmarkEfficiencyArchieve.load( filePath, retrieveVersion=True)
  from TuningTools.dataframe.EnumCollection import RingerOperation
  efficiencyKey = RingerOperation.retrieve(operationPoint)
  if tdVersion >= 7 or effVersion>1:
    refLabel = RingerOperation.tostring( efficiencyKey )
  else:
    # Retrieve efficiency
    refFile = BenchmarkEfficiencyArchieve.load( filePath, loadCrossEfficiencies=False)
    from TuningTools.coreDef import dataframeConf
    dataframeConf.auto_retrieve_testing_sample( refFile.signalEfficiencies )
    wrapper = _compatibility_version6_dicts()
    refLabel = wrapper[efficiencyKey]
    efficiencyKey = wrapper[efficiencyKey]
  return efficiencyKey, refLabel

def _compatibility_version6_dicts():
  from TuningTools.coreDef import dataframeConf
  from TuningTools import Dataframe, RingerOperation
  if dataframeConf() is Dataframe.PhysVal:
    return { RingerOperation.L2Calo                      : 'L2CaloAccept'
           , RingerOperation.L2                          : 'L2ElAccept'
           , RingerOperation.EFCalo                      : 'EFCaloAccept'
           , RingerOperation.HLT                         : 'HLTAccept'
           , RingerOperation.Offline_LH_VeryLoose        : None
           , RingerOperation.Offline_LH_Loose            : 'LHLoose'
           , RingerOperation.Offline_LH_Medium           : 'LHMedium'
           , RingerOperation.Offline_LH_Tight            : 'LHTight'
           , RingerOperation.Offline_LH                  : ['LHLoose','LHMedium','LHTight']
           , RingerOperation.Offline_CutBased_Loose      : 'CutBasedLoose'
           , RingerOperation.Offline_CutBased_Medium     : 'CutBasedMedium'
           , RingerOperation.Offline_CutBased_Tight      : 'CutBasedTight'
           , RingerOperation.Offline_CutBased            : ['CutBasedLoose','CutBasedMedium','CutBasedTight']
           }
  elif dataframeConf() is Dataframe.PhysVal_v2:
    return { RingerOperation.Trigger                     : 'Efficiency'}

  elif dataframeConf() is Dataframe.SkimmedNtuple:
    return { RingerOperation.L2Calo                  : None
           , RingerOperation.L2                      : None
           , RingerOperation.EFCalo                  : None
           , RingerOperation.HLT                     : None
           , RingerOperation.Offline_LH_VeryLoose    : 'elCand2_isVeryLooseLLH_Smooth_v11' # isVeryLooseLL2016_v11
           , RingerOperation.Offline_LH_Loose        : 'elCand2_isLooseLLH_Smooth_v11'
           , RingerOperation.Offline_LH_Medium       : 'elCand2_isMediumLLH_Smooth_v11'
           , RingerOperation.Offline_LH_Tight        : 'elCand2_isTightLLH_Smooth_v11'
           , RingerOperation.Offline_LH              : ['elCand2_isVeryLooseLLH_Smooth_v11'
                                                       ,'elCand2_isLooseLLH_Smooth_v11'
                                                       ,'elCand2_isMediumLLH_Smooth_v11'
                                                       ,'elCand2_isTightLLH_Smooth_v11']
           , RingerOperation.Offline_CutBased_Loose  : 'elCand2_isEMLoose2015'
           , RingerOperation.Offline_CutBased_Medium : 'elCand2_isEMMedium2015'
           , RingerOperation.Offline_CutBased_Tight  : 'elCand2_isEMTight2015'
           , RingerOperation.Offline_CutBased        : ['elCand2_isEMLoose2015'
                                                       ,'elCand2_isEMMedium2015'
                                                       ,'elCand2_isEMTight2015']
           }

__all__ = ['CrossValidStatAnalysis','GridJobFilter', 'StandaloneJobBinnedFilter','PerfHolder',
           'fixReferenceBenchmarkCollection', 'MixedJobBinnedFilter']

from Gaugi import ( checkForUnusedVars, calcSP, save, load, Logger
                       , LoggingLevel, expandFolders, traverse
                       , retrieve_kw, NotSet, csvStr2List, select, progressbar, getFilters
                       , apply_sort, LoggerStreamable, appendToFileName, ensureExtension
                       , measureLoopTime, checkExtension, MatlabLoopingBounds, mkdir_p
                       , LockFile, EnumStringification )

from TuningTools.TuningJob import ( TunedDiscrArchieve, ReferenceBenchmark, ReferenceBenchmarkCollection
                                  , ChooseOPMethod )
from TuningTools import ( PreProc, PerformancePoint, RawThreshold
                        , ThresholdCollection, PileupLinearCorrectionThreshold )
from TuningTools.dataframe.EnumCollection import Dataset
from TuningTools.PreProc import *
from pprint import pprint
from cPickle import UnpicklingError
from time import time
from copy import deepcopy, copy
import numpy as np, os, sys, re

def _localRetrieveList( l, idx ):
  if len(l) == 1:
    return l[0]
  else:
    return l[idx]

def percentile( data, score ):
  """
  val = percentile( data, score )
  Retrieve the data percentile at score
  """
  size = len(data)
  if size:
    pos = score*size
    if pos % 10 or pos == size:
      return data[pos]
    else:
      return data[pos] + data[pos+1]
  else: return None

def fixReferenceBenchmarkCollection( refCol, nBins, nTuned, level = None ):
  """
    Make sure that input data is a ReferenceBenchmarkCollection( ReferenceBenchmarkCollection([...]) )
    with dimensions [nBins][nTuned] or transform it to that format if it is possible.
  """
  tree_types = (ReferenceBenchmarkCollection, list, tuple )
  try:
    # Retrieve collection maximum depth
    _, _, _, _, depth = traverse(refCol, tree_types = tree_types).next()
  except GeneratorExit:
    depth = 0
  if depth == 0:
    refCol = ReferenceBenchmarkCollection( [deepcopy(refCol) for _ in range(nTuned)] )
    refCol = ReferenceBenchmarkCollection( [deepcopy(refCol) for _ in range(nBins if nBins is not None else 1) ] )
  elif depth == 1:
    lRefCol = len(refCol)
    if lRefCol == 1:
      refCol = ReferenceBenchmarkCollection( [ deepcopy( refCol[0] ) for _ in range(nTuned ) ] )
      refCol = ReferenceBenchmarkCollection( [ deepcopy( refCol    ) for _ in range(nBins if nBins is not None else 1 ) ] )
    elif lRefCol == nTuned:
      refCol = ReferenceBenchmarkCollection( refCol )
      refCol = ReferenceBenchmarkCollection( [ deepcopy( refCol ) for _ in range(nBins if nBins is not None else 1 ) ] )
    elif lRefCol == nBins:
      refColBase = ReferenceBenchmarkCollection( [ deepcopy( ref ) for ref in refCol for _ in range(nTuned) ] )
      refCol = ReferenceBenchmarkCollection([])
      for i in range(nBins): refCol.append( ReferenceBenchmarkCollection( refColBase[i*nTuned:(i+1)*nTuned] ) )
    else:
      self._fatal(("The ReferenceBenchmark collection size does not " \
          "match either the number of tuned operating points or the number of bins."), ValueError)
  elif depth == 2:
    pass
  else:
    self._fatal("Collection dimension is greater than 2!", ValueError)
  from Gaugi import inspect_list_attrs
  refCol = inspect_list_attrs(refCol, 2,                               tree_types = tree_types,                                level = level,         )
  refCol = inspect_list_attrs(refCol, 1, ReferenceBenchmarkCollection, tree_types = tree_types, dim = nTuned, name = "nTuned", allowSpan = True       )
  refCol = inspect_list_attrs(refCol, 0, ReferenceBenchmarkCollection, tree_types = tree_types, dim = nBins,  name = "nBins",  deepcopy = True        )
  return refCol

class JobFilter( object ):
  def __call__(self, paths):
    return []

class GridJobFilter( JobFilter ):
  """
  Filter grid job files returning each unique job id.
  """

  pat = re.compile(r'.*user.[a-zA-Z0-9]+.(?P<jobID>[0-9]+)\..+$')
  #pat = re.compile(r'user.(?P<user>[A-z0-9]*).(?P<jobID>[0-9]+).*\.tgz')

  def __call__(self, paths):
    """
      Returns the unique jobIDs
    """
    jobIDs = sorted(list(set([self.pat.match(f).group('jobID') for f in paths if self.pat.match(f) is not None])))
    return jobIDs

class StandaloneJobBinnedFilter( JobFilter ):
  """
  Filter using each file et/eta bin as saved in standalone jobs.
  """

  pat = re.compile(r'.+(?P<binID>et(?P<etBinIdx>\d+).eta(?P<etaBinIdx>\d+))\..+$')

  def __call__(self, paths):
    """
      Returns the unique et/eta bins
    """
    binIDs = sorted(list(set([self.pat.match(f).group('binID') for f in paths if self.pat.match(f) is not None])))
    return binIDs

class MixedJobBinnedFilter( JobFilter ):
  """
  Filter both standalone and grid jobs.
  """

  pat = re.compile('|'.join([StandaloneJobBinnedFilter.pat.pattern,GridJobFilter.pat.pattern]))

  def __call__(self, paths):
    """
      Returns the unique jobIDs
    """
    mo = filter(lambda x: x is not None, [self.pat.match(f) for f in paths])
    mixIDs = map(lambda x: x.group('binID') or x.group('jobID'), mo)
    return sorted(list(set(mixIDs)))


class ThresholdStrategy(EnumStringification):
  UniqueThreshold = 0
  PileupLinearCorrectionThreshold = 1


class CrossValidStatAnalysis( Logger ):

  ignoreKeys = ( 'benchmark', 'tuningBenchmark', 'eps', 'aucEps'
               , 'modelChooseMethod', 'rocPointChooseMethod', 'etBinIdx', 'etaBinIdx'
               , 'etBin', 'etaBin'
               )

  def __init__(self, paths, **kw):
    """
    Usage:
    # Create object
    cvStatAna = CrossValidStatAnalysis(
                                        paths
                                        [,binFilters=None]
                                        [,logger[,level=INFO]]
                                      )
    # Fill the information and save output file with cross-validation summary
    cvStatAna( refBenchMark, **args...)
    # Call other methods if necessary.
    """
    Logger.__init__(self, kw)
    self._binFilters            = retrieve_kw(kw, 'binFilters',            MixedJobBinnedFilter )
    self._binFilterJobIdxs      = retrieve_kw(kw, 'binFilterIdxs',         None                 )
    self._useTstEfficiencyAsRef = retrieve_kw(kw, 'useTstEfficiencyAsRef', False                )
    checkForUnusedVars(kw, self._warning)
    # Check if path is a file with the paths
    self._paths = csvStr2List( paths )
    # Recursively expand all folders in the given paths so that we have all
    # files lists:
    self._paths = expandFolders( self._paths )
    self._nBins = 1
    if self._binFilters:
      self._debug('All filters are:')
      getFilters( self._binFilters, self._paths, printf = self._debug )
      self._binFilters = getFilters( self._binFilters, self._paths,
                                     idxs = self._binFilterJobIdxs,
                                     printf = self._info )
      if self._binFilters:
        self._paths = select( self._paths, self._binFilters )
        self._nBins = len(self._binFilters)
    if self._nBins is 1:
      self._paths = [self._paths]
    #if self._level <= LoggingLevel.VERBOSE:
    #  for binFilt in self._binFilters if self._binFilters is not None else [None]:
    #    self._verbose("The stored files are (binFilter=%s):", binFilt)
    #    for path in self._paths:
    #      self._verbose("%s", path)
    self._nFiles = [len(l) for l in self._paths]
    self._info("A total of %r files were found.", self._nFiles )
    #alloc variables to the TFile and bool flag
    self._sg = None
    self._sgdirs=list()

  def __addPerformance( self, tunedDiscrInfo, path, ref, benchmarkRef,
                              neuron, sort, init,
                              tunedDiscr, trainEvolution,
                              tarMember, eps, rocPointChooseMethod,
                              modelChooseMethod, aucEps ):
    refName = ref.name
    self._verbose("Adding performance for <ref:%s, config:%r,sort:%s,init:%s>", refName, neuron, sort, init)
    # We need to make sure that the key will be available on the dict if it
    # wasn't yet there
    if not refName in tunedDiscrInfo:
      tunedDiscrInfo[refName] = { 'benchmark':            ref,
                                  'tuningBenchmark':      benchmarkRef if benchmarkRef is not None else '',
                                  'eps':                  eps if eps is not NotSet else ReferenceBenchmark._def_eps,
                                  'aucEps':               aucEps if aucEps is not NotSet else ReferenceBenchmark._def_auc_eps,
                                  'modelChooseMethod':    modelChooseMethod if modelChooseMethod is not NotSet else ReferenceBenchmark._def_model_choose_method,
                                  'rocPointChooseMethod': rocPointChooseMethod if rocPointChooseMethod is not NotSet else ReferenceBenchmark._def_model_choose_method}
      #ref.level = self.level
      #tunedDiscr['benchmark'].level = self.level
    if not neuron in tunedDiscrInfo[refName]:
      tunedDiscrInfo[refName][neuron] = dict()
    if not sort in tunedDiscrInfo[refName][neuron]:
      tunedDiscrInfo[refName][neuron][sort] = { 'headerInfo' : [],
                                                'initPerfTstInfo' : [],
                                                'initPerfOpInfo' : [] }
    perfHolder = PerfHolder( tunedDiscr
                           , trainEvolution
                           #, decisionTaking = self.decisionMaker( tunedDiscr['discriminator'] ) if self.decisionMaker else None
                           , level = self.level )
    # Retrieve operating points:
    tstPerf = perfHolder.getOperatingBenchmarks( ref
                                               , ds                   = Dataset.Test
                                               , eps                  = eps
                                               , modelChooseMethod    = modelChooseMethod
                                               , rocPointChooseMethod = rocPointChooseMethod
                                               , aucEps               = aucEps
                                               , neuron = neuron, sort = sort, init = init
                                               )
    # NOTE: If using decisionMaker below this line for other dataset then Operation, it will
    # need to recalculate performance using train dataset
    opPerf = perfHolder.getOperatingBenchmarks( ref
                                              , ds                   = Dataset.Operation
                                              , eps                  = eps
                                              , modelChooseMethod    = modelChooseMethod
                                              , rocPointChooseMethod = rocPointChooseMethod
                                              , aucEps               = aucEps
                                              , neuron = neuron, sort = sort, init = init
                                              )
    headerInfo = {
                   'discriminator': tunedDiscr['discriminator'],
                   'neuron':        neuron,
                   'sort':          sort,
                   'init':          init,
                   'path':          path,
                   'tarMember':     tarMember
                 }
    # Create performance holders:
    iInfoTst = { 'sp' : tstPerf.sp, 'det' : tstPerf.pd, 'fa' : tstPerf.pf, 'auc' : tstPerf.auc, 'mse' : tstPerf.mse, 'cut' : tstPerf.thres.toRawObj(), }
    iInfoOp  = { 'sp' : opPerf.sp,  'det' : opPerf.pd,  'fa' : opPerf.pf,  'auc' : opPerf.auc,  'mse' : opPerf.mse,  'cut' : opPerf.thres.toRawObj(),  }
    if self._level <= LoggingLevel.VERBOSE:
      self._verbose("Retrieved file '%s' configuration for benchmark '%s' as follows:",
                         os.path.basename(path),
                         ref )
      pprint({'headerInfo' : headerInfo, 'initPerfTstInfo' : iInfoTst, 'initPerfOpInfo' : iInfoOp })
    # Append information to our dictionary:
    tunedDiscrInfo[refName][neuron][sort]['headerInfo'].append( headerInfo )
    tunedDiscrInfo[refName][neuron][sort]['initPerfTstInfo'].append( iInfoTst )
    tunedDiscrInfo[refName][neuron][sort]['initPerfOpInfo'].append( iInfoOp )

  def sgDir( self, refname, neuron, sort, init, extra = None):
    dirname = ('%s/config_%s/sort_%s/init_%d%s') % (refname,str(neuron).zfill(3),str(sort).zfill(3),init, '' if not extra else ('/' + extra))
    if not dirname in self._sgdirs:
      self._sg.mkdir(dirname)
      self._sgdirs.append(dirname)
    if not self._sg.cd(dirname):
      self._fatal("Could not cd to dir %s", dirname )

  def __addMonPerformance( self, discr, trainEvolution, refname, neuron, sort, init):
    self.sgDir( refname, neuron, sort, init )
    perfHolder = PerfHolder(discr, trainEvolution, level = self.level)
    graphNames = [ 'mse_trn', 'mse_val', 'mse_tst',
                   'bestsp_point_sp_val', 'bestsp_point_det_val', 'bestsp_point_fa_val',
                   'bestsp_point_sp_tst', 'bestsp_point_det_tst', 'bestsp_point_fa_tst',
                   'det_point_sp_val'   , 'det_point_det_val'   , 'det_point_fa_val'   , # det_point_det_val is det_fitted
                   'det_point_sp_tst'   , 'det_point_det_tst'   , 'det_point_fa_tst'   ,
                   'fa_point_sp_val'    , 'fa_point_det_val'    , 'fa_point_fa_val'    , # fa_point_fa_val is fa_fitted
                   'fa_point_sp_tst'    , 'fa_point_det_tst'    , 'fa_point_fa_tst'    ,
                   'roc_tst'            , 'roc_operation',]

    # Attach graphs
    for gname in graphNames:
      g = perfHolder.getGraph(gname); g.SetName(gname)
      g.Write()
      #self._sg.attach(g, holdObj = False)
      del g

    # Attach stops
    from Gaugi import createRootParameter
    createRootParameter("double", "mse_stop", perfHolder.epoch_mse_stop ).Write()
    createRootParameter("double", "sp_stop",  perfHolder.epoch_sp_stop  ).Write()
    createRootParameter("double", "det_stop", perfHolder.epoch_det_stop ).Write()
    createRootParameter("double", "fa_stop",  perfHolder.epoch_fa_stop  ).Write()

  def __call__(self, **kw ):
    """
    Hook for loop method.
    """
    self.loop( **kw )

  def loop(self, **kw ):
    """
    Optional args:
      * refBenchmarkCol: a list of reference benchmark objects which will be used
        as the operation points.
      * toMatlab [True]: also create a matlab file from the obtained tuned discriminators
      * outputName ['crossValStat']: the output file name.
      * test [False]: Run only for a small number of files
      * doMonitoring [True]: Whether to do tuning monitoring file or not.
      * doCompress [True]: Whether to compress output files or not.
      * epsCol [NotSet]: epsolon value (in-bound limit) for accepting value within reference (used only for Pd/Pf)
      * aucEpsCol [NotSet]: as above, but used for calculating the ROC when ChooseOPMethod is InBoundAUC
      * rocPointChooseMethod: The method for choosing the operation point in the ROC curve
      * modelChooseMethod: The method for choosing the various models when
      operating at rocPointChooseMethod
      * expandOP: when only one operation point was used during tuning (e.g.
        Pd), expandOP, when set to true, will generate three operation points for
        the derived neural network by setting the targets to Pd/Pf/SP
      * fullDumpNeurons: MatlabLoopingBounds with the neurons to be fully
        dumped for monitoring. If this option is specified, standard monitoring
        is not called.
      * operationPoint: models operating points
    """
    import gc
    # Retrieve reference collection:
    refBenchmarkColKW = 'refBenchmarkCol'
    if not 'refBenchmarkCol' in kw and 'refBenchmarkList' in kw:
      refBenchmarkColKW = 'refBenchmarkList'
    refBenchmarkCol         = retrieve_kw( kw, refBenchmarkColKW,    None           )
    # Optinal arguments:
    toMatlab                = retrieve_kw( kw, 'toMatlab',           True           )
    outputName              = retrieve_kw( kw, 'outputName',         'crossValStat' )
    test                    = retrieve_kw( kw, 'test',               False          )
    doMonitoring            = retrieve_kw( kw, 'doMonitoring',       True           )
    compress                = retrieve_kw( kw, 'doCompress',         True           )
    epsCol                  = retrieve_kw( kw, 'epsCol'                             )
    aucEpsCol               = retrieve_kw( kw, 'aucEpsCol'                          )
    rocPointChooseMethodCol = retrieve_kw( kw, 'rocPointChooseMethodCol'            )
    modelChooseMethodCol    = retrieve_kw( kw, 'modelChooseMethodCol'               )
    modelChooseInitMethod   = retrieve_kw( kw, 'modelChooseInitMethod', None        )
    expandOP                = retrieve_kw( kw, 'expandOP',           True           )
    alwaysUseSPNetwork      = retrieve_kw( kw, 'alwaysUseSPNetwork', False          )
    FullDumpNeurons         = retrieve_kw( kw, 'fullDumpNeurons',    []             )
    overwrite               = retrieve_kw( kw, 'overwrite',           False         )
    # Retrieve decision making options:
    self.redoDecisionMaking = retrieve_kw( kw, 'redoDecisionMaking',  NotSet        )
    self.decisionMaker      = None
    self.dCurator           = None
    if self.redoDecisionMaking in (None,NotSet) and kw.get('dataLocation',None):
      self._info("Setting redoDecisionMaking to True since dataLocation was specified")
      self.redoDecisionMaking = True
    if self.redoDecisionMaking:
      from TuningTools import DataCurator
      self.dCurator = DataCurator( kw, addDefaultPP = False, allowDefaultCrossVal = False )
      self.dCurator.level = self.level
      from TuningTools.DecisionMaking import DecisionMaker
      self.decisionMaker = DecisionMaker( self.dCurator, kw )
      self.decisionMaker.level = self.level
    # Finished, print unused arguments:
    checkForUnusedVars( kw, self._warning ); del kw

    # Treat some arguments:
    if FullDumpNeurons not in (None, NotSet) and not isinstance( FullDumpNeurons, MatlabLoopingBounds ):
      FullDumpNeurons = MatlabLoopingBounds( FullDumpNeurons )
    tuningBenchmarks = ReferenceBenchmarkCollection([])
    if not isinstance( epsCol, (list, tuple) ):                  epsCol                  = [epsCol]
    if not isinstance( aucEpsCol, (list, tuple) ):               aucEpsCol               = [aucEpsCol]
    if not isinstance( rocPointChooseMethodCol, (list, tuple) ): rocPointChooseMethodCol = [rocPointChooseMethodCol]
    if not isinstance( modelChooseMethodCol, (list, tuple) ):    modelChooseMethodCol    = [modelChooseMethodCol]

    if not self._paths:
      self._warning("Attempted to run without any file!")
      return
    if test: self._paths = self._paths[:1]

    pbinIdxList=[]
    isMergedList=[]
    etBinDict=dict()
    etaBinDict=dict()
    etEtaList = []
    toRemove = []
    for binIdx, binPath in enumerate(progressbar(self._paths,
                                                 len(self._paths), 'Retrieving tuned operation points: ', 30, True,
                                                 logger = self._logger)):
      # Detect whether path in binPath is a merged file or not:
      binFilesMergedDict = {}
      isMergedList.append( binFilesMergedDict )
      for path in binPath:
        if checkExtension( path, 'tgz|tar.gz'):
          isMerged = False
          from subprocess import Popen, PIPE
          from Gaugi import is_tool
          tar_cmd = 'gtar' if is_tool('gtar') else 'tar'
          tarlist_ps = Popen((tar_cmd, '-tzif', path,),
                             stdout = PIPE, stderr = PIPE, bufsize = 1)
          start = time()
          for idx, line in enumerate( iter(tarlist_ps.stdout.readline, b'') ):
            if idx > 0 and not(line.startswith('gtar: ')) and not tarlist_ps.returncode:
              isMerged = True
              tarlist_ps.kill()
          if isMerged:
            self._debug("File %s is a merged tar-file.", path)
          else:
            self._debug("File %s is a non-merged tar-file.", path)
          binFilesMergedDict[path] = isMerged
          # NOTE: put this debug inside the loop because the start is reset for each loop. Check this change.
          self._debug("Detecting merged file took %.2fs", time() - start)
        elif checkExtension( path, 'pic' ):
          isMerged = False
          self._debug("File %s is a non-merged pic-file.", path)
          binFilesMergedDict[path] = isMerged

      # Start reading tdArchieve
      tdArchieve = TunedDiscrArchieve.load(binPath[0],
                                           useGenerator = True,
                                           ignore_zeros = False,
                                           skipBenchmark = False).next()


      tunedArchieveDict = tdArchieve.getTunedInfo( tdArchieve.neuronBounds[0],
                                                   tdArchieve.sortBounds[0],
                                                   tdArchieve.initBounds[0] )
      tunedDiscrList = tunedArchieveDict['tunedDiscr']
      etBinIdx  = tdArchieve.etBinIdx
      etaBinIdx = tdArchieve.etaBinIdx
      etBin     = tdArchieve.etBin
      etaBin    = tdArchieve.etaBin
      etBinDict[etBinIdx] =  tdArchieve.etBin
      etaBinDict[etaBinIdx] = tdArchieve.etaBin
      self._debug('This set of jobs et/eta bin is: %d/%d', etBinIdx, etaBinIdx)
      try:
        prevBinPath = etEtaList.index((etBinIdx,etaBinIdx,))
        self._info('Merging this job set of files with job set index %d!', prevBinPath)
      except ValueError: prevBinPath = None
      etEtaList.append((etBinIdx,etaBinIdx))

      try:
        nTuned = len(tunedDiscrList)
        # NOTE: We are assuming that every bin has the same size by using
        # refBenchmarkCol[0]
        nOp = len(refBenchmarkCol[0])
        if nTuned != nOp:
          if not( nTuned == 1 or nOp == 1 ):
            self._fatal("""All bins must have the same number of tuned
            benchmarks, or either one of them must have size equal to one.
            Number of tuned benchmarks are %d, provided %d
            OPs.""",nTuned,nOp)
          else:
            # Then we copy the tunedDiscrList so that it has the same size of the requested refBenchmarkCol
            tunedDiscrList = [deepcopy(tunedDiscrList[0]) for _ in xrange(nOp)]
      except (NameError, AttributeError, TypeError):
        pass
      nTuned = len(tunedDiscrList)
      if not nTuned: self._fatal("Could not retrieve any tuned model operation point.")
      binTuningBench    = ReferenceBenchmarkCollection(
                             [tunedDiscrDict['benchmark'] for tunedDiscrDict in tunedDiscrList]
                          )
      if prevBinPath is not None:
        prevTuningBenchmarks = tuningBenchmarks[prevBinPath]
        if len(binTuningBench) != len(prevTuningBenchmarks) or not all([bT.name == pT.name for bT, pT in zip(binTuningBench,prevTuningBenchmarks)]):
          self._fatal("Found another job filter with same bin but tuning benchmarks are different!")
        self._paths[prevBinPath].extend(binPath)
        toRemove.append(binIdx)
        continue

      # Change output level from the tuning benchmarks
      for bench in binTuningBench: bench.level = self.level
      tuningBenchmarks.append( binTuningBench )

      self._debug("Found a total of %d tuned operation points on bin (et:%d,eta:%d). They are: ",
          nTuned, etBinIdx, etaBinIdx)

      for bench in binTuningBench:
        self._debug("%s", bench)
    for r in toRemove: del self._paths[r]
    del toRemove
    # Make sure everything is ok with the reference benchmark collection (do not check for nBins):
    if refBenchmarkCol is not None:
      refBenchmarkCol = fixReferenceBenchmarkCollection(refBenchmarkCol, nBins = None,
                                                        nTuned = nTuned, level = self.level )

    # FIXME Moved due to crash when loading later.
    from ROOT import TFile, gROOT, kTRUE
    gROOT.SetBatch(kTRUE)

    self._info("Started analysing cross-validation statistics...")
    self._summaryInfo = [ dict() for i in range(self._nBins) ]
    self._summaryPPInfo = [ dict() for i in range(self._nBins) ]

    # Loop over the files
    from itertools import product
    # FIXME If job fails, it will not erase expanded files at temporary folder
    for binIdx, binPath in enumerate(self._paths):
      if self._binFilters:
        self._info("Running bin filter '%s'...",self._binFilters[binIdx])
      # What is the output name we should give for the written files?
      if self._binFilters:
        cOutputName = appendToFileName( outputName, self._binFilters[binIdx] )
      else:
        cOutputName = outputName
      # check if file exists and whether we want to overwrite
      from glob import glob
      if glob( cOutputName + '*' ) and not overwrite:
        self._info("%s already exists and asked not to overwrite.", cOutputName )
        continue
      # Create empty file:
      lockFilePath = os.path.join( os.path.dirname(cOutputName), '.' + os.path.basename(cOutputName) + '.lock' )
      dPath = os.path.dirname(cOutputName)
      if dPath and not os.path.exists(dPath): mkdir_p(dPath)
      try:
        lockFile = LockFile( lockFilePath )
      except IOError:
        if self._binFilters:
          self._info("Skipping bin %s once it is locked.", self._binFilters[binIdx] )
        else:
          self._info("Skipping job once it is locked." )
        self._info("Remove file '%s' if no other node is working on it!", lockFilePath )
        continue
      tunedDiscrInfo = dict()
      cSummaryInfo = self._summaryInfo[binIdx]
      cSummaryPPInfo = self._summaryPPInfo[binIdx]
      binFilesMergedDict = isMergedList[binIdx]

      # Retrieve binning information
      # FIXME: We shouldn't need to read file three times for retrieving basic information...
      tdArchieve = TunedDiscrArchieve.load(binPath[0],
                                           useGenerator = True,
                                           ignore_zeros = False).next()
      # Update etBinIdx and etaBinIdx
      etBin      = tdArchieve.etBin
      etaBin     = tdArchieve.etaBin
      etBinIdx   = tdArchieve.etBinIdx
      etaBinIdx  = tdArchieve.etaBinIdx
      sortBounds = tdArchieve.sortBounds
      if etaBinIdx != -1:
        self._info("File eta bin index (%d) limits are: %r",
                           etaBinIdx,
                           etaBin, )
      if etBinIdx != -1:
        self._info("File Et bin index (%d) limits are: %r",
                           etBinIdx,
                           etBin, )
      self.tuningData = None
      if self.dCurator:
        self.dCurator.prepareForBin( etBinIdx = etBinIdx, etaBinIdx = etaBinIdx
                                   , loadEfficiencies = False, loadCrossEfficiencies = False )
      else:
        self._info("Proceeding with already calculated performance during tuning...")

      self._info("Retrieving summary...")
      # Find the tuned benchmark that matches with this reference
      if etaBinIdx != -1 and etBinIdx != -1:
        try:
          tBenchIdx = [ all([( b.checkEtBinIdx(etBinIdx) and b.checkEtaBinIdx( etaBinIdx ) ) for b in bList ])
                        for bList in tuningBenchmarks ].index( True )
          # Retrieve the tuning benchmark list referent to this binning
          tBenchmarkList = tuningBenchmarks[tBenchIdx]
        except ValueError:
          self._error("Couldn't find any reference with specified et/eta bins in tuned discriminator files.")
          tBenchmarkList = None
        # Retrieved tBenchIdx
      # end of if

      # Search for the reference binning information that is the same from the
      # benchmark
      if refBenchmarkCol is not None:
        if etBinIdx != -1 and etaBinIdx != -1:
          try:
            rBenchIdx = [ all([ ( b is not None and (etBinIdx == b.etBinIdx and etaBinIdx == b.etaBinIdx) ) or ( b is None )
                              for b in bList ])
                          for bList in refBenchmarkCol ].index( True )
            cRefBenchmarkList = refBenchmarkCol[rBenchIdx]
          except ValueError:
            self._fatal( "Couldn't find any reference with the specified et/eta bins in reference file.", IndexError )
        # Retrieve the benchmark list referent to this binning
        if tBenchmarkList is None:
          tBenchmarkList = [None] * len(cRefBenchmarkList)
      else:
        if tBenchmarkList is None:
          self._fatal("Error while retrieving references from discriminator files and no reference file specified.")
        cRefBenchmarkList = [None] * len(tBenchmarkList)

      # Check if user requested for using the tuning benchmark info by setting
      # any reference value to None
      if None in cRefBenchmarkList:
        # Check if we have only one reference and it is set to None.
        # In case the user tuned for the SP or MSE, than replace the tuning benchmark to be set
        # to SP, Pd and Pf
        if len(cRefBenchmarkList) == 1 and  len(tBenchmarkList) == 1 and \
            tBenchmarkList[0].reference in (ReferenceBenchmark.SP, ReferenceBenchmark.MSE):
          refBenchmark = tBenchmarkList[0]
          newRefList = ReferenceBenchmarkCollection( [] )
          # Work the benchmarks to be a list with multiple references, using the Pd, Pf and the MaxSP:
          if refBenchmark.signalEfficiency is not None and refBenchmark.signalEfficiency.count and expandOP:
            self._info("Found a unique tuned MSE or SP reference. Expanding it to SP/Pd/Pf operation points.")
            opRefs = [ReferenceBenchmark.SP, ReferenceBenchmark.Pd, ReferenceBenchmark.Pf]
            for idx, ref in enumerate(opRefs):
              newRef = deepcopy( refBenchmark )
              newRef.updateReference( ref )
              newRef.name = newRef.name.replace('Tuning','OperationPoint')
              newRefList.append( newRef )
          else:
            if expandOP:
              self._warning("Could not expand OP since there is no efficiency available in the reference benchmarks.")
            newRef = deepcopy( refBenchmark )
            # We only substitute reference if its benchmark is set to MSE, to choose using SP
            if refBenchmark is ReferenceBenchmark.MSE:
              targetStr = newRef.name.split("_")[1]
              newRefList[0].name = '_'.join(['OperationPoint'] + ([targetStr] if targetStr else []) + ['SP'] )
              newRefList[0].reference = ReferenceBenchmark.SP
            else:
              newRef.name = newRef.name.replace('Tuning','OperationPoint')
            newRefList.append( newRef )
          # Replace the reference benchmark by the copied list we created:
          cRefBenchmarkList = newRefList
        # Replace the requested references using the tuning benchmarks:
        for idx, refBenchmark in enumerate(cRefBenchmarkList):
          if refBenchmark is None:
            ccRefBenchmarkList = tBenchmarkList[idx]
            cRefBenchmarkList[idx] = ccRefBenchmarkList
            ccRefBenchmarkList.name = ccRefBenchmarkList.name.replace('Tuning_', 'OperationPoint_')
      # finished checking

      #self._info('Using references: %r.', [(ReferenceBenchmark.tostring(ref.reference),ref.refVal) for ref in cRefBenchmarkList])
      self._info('Using references: %r.', [(ref.name,ref.refVal) for ref in cRefBenchmarkList])

      # Finally, we start reading this bin files:
      nBreaks = 0
      cMember = 0
      for cFile, path in progressbar( enumerate(binPath),
                                      self._nFiles[binIdx], 'Reading files: ', 60, 1, True,
                                      logger = self._logger ):
        flagBreak = False
        start = time()
        self._info("Reading file '%s'", path )
        try:
          isMerged = binFilesMergedDict[path]
        except KeyError:
          isMerged = False
        # And open them as Tuned Discriminators:
        try:
          # Try to retrieve as a collection:
          for tdArchieve in measureLoopTime( TunedDiscrArchieve.load(path, useGenerator = True,
                                                                     extractAll = True if isMerged else False,
                                                                     eraseTmpTarMembers = False if isMerged else True,
                                                                    ),
                                             prefix_end = "read all file '%s' members." % path,
                                             prefix = "Reading member",
                                             logger = self._logger ):
            cMember += 1
            if flagBreak: break
            self._info("Retrieving information from %s.", str(tdArchieve))

            if etaBinIdx is not tdArchieve.etaBinIdx:
              self._fatal("File (%s) do not match eta bin index!", tdArchieve.filePath)
            if etBinIdx is not tdArchieve.etBinIdx:
              self._fatal("File (%s) do not match et bin index!", tdArchieve.filePath)

            # Calculate the size of the list
            barsize = len(tdArchieve.neuronBounds.list()) * len(tdArchieve.sortBounds.list()) * \
                      len(tdArchieve.initBounds.list())

            for neuron, sort, init in progressbar( product( tdArchieve.neuronBounds(),
                                                            tdArchieve.sortBounds(),
                                                            tdArchieve.initBounds() ),\
                                                            barsize, 'Reading configurations: ', 60, 1, False,
                                                   logger = self._logger):
              tunedDict      = tdArchieve.getTunedInfo( neuron, sort, init )
              tunedDiscr     = tunedDict['tunedDiscr']
              tunedPPChain   = tunedDict['tunedPP']
              trainEvolution = tunedDict['tuningInfo']
              # Request data curator to prepare the tunable subsets using the
              # ppChain tuned during
              if self.dCurator:
                if test: tunedPPChain = PreProc.PreProcChain( [PreProc.StatReductionFactor(factor = 5.)] + tunedPPChain )
                self.dCurator.addPP( tunedPPChain, etBinIdx, etaBinIdx, sort )
                #self.dCurator.toTunableSubsets( sort, tunedPPChain )
              if not len(tunedDiscr) == nTuned and len(tunedDiscr) != 1:
                self._fatal("File %s contains different number of tunings in the collection.", path, ValueError)
              elif len(tunedDiscr):
                self._debug("Assuming that we have expanded the tunedDiscr to have the same size of the required OPs")
              # We loop on each reference benchmark we have.
              from itertools import izip, count
              for idx, refBenchmark, tuningRefBenchmark in izip(count(), cRefBenchmarkList, tBenchmarkList):
                if   neuron == tdArchieve.neuronBounds.lowerBound() and \
                     sort == tdArchieve.sortBounds.lowerBound() and \
                     init == tdArchieve.initBounds.lowerBound() and \
                     idx == 0:
                  # Check if everything is ok in the binning:
                  if not refBenchmark.checkEtaBinIdx(etaBinIdx):
                    if refBenchmark.etaBinIdx is None:
                      self._warning("TunedDiscrArchieve does not contain eta binning information! Assuming the bins do match!")
                    else:
                      self._fatal("File (%d) eta binning information does not match with benchmark (%r)!",
                          tdArchieve.etaBinIdx,
                          refBenchmark.etaBinIdx)
                  if not refBenchmark.checkEtBinIdx(etBinIdx):
                    if refBenchmark.etaBinIdx is None:
                      self._warning("TunedDiscrArchieve does not contain Et binning information! Assuming the bins do match!")
                    else:
                      self._fatal("File (%d) Et binning information does not match with benchmark (%r)!",
                          tdArchieve.etBinIdx,
                          refBenchmark.etBinIdx)
                # Retrieve some configurations:
                eps                  = _localRetrieveList( epsCol                  , idx )
                aucEps               = _localRetrieveList( aucEpsCol               , idx )
                rocPointChooseMethod = _localRetrieveList( rocPointChooseMethodCol , idx )
                modelChooseMethod    = _localRetrieveList( modelChooseMethodCol    , idx )
                # We always use the first tuned discriminator if we have more
                # than one benchmark and only one tuning
                if type(tunedDiscr) in (list, tuple,):
                  # fastnet core version
                  #discr = tunedDiscr[refBenchmark.reference]
                  if len(tunedDiscr) > 1 and not alwaysUseSPNetwork: discr = tunedDiscr[idx]
                  else: discr = tunedDiscr[0]
                else:
                  # exmachina core version
                  discr = tunedDiscr
                # Retrieve the pre-processing information:
                self.__addPPChain( cSummaryPPInfo,
                                   tunedPPChain,
                                   sort )
                # And the tuning information:
                self.__addPerformance( tunedDiscrInfo = tunedDiscrInfo,
                                       path = tdArchieve.filePath, ref = refBenchmark,
                                       benchmarkRef = tuningRefBenchmark,
                                       neuron = neuron, sort = sort, init = init,
                                       tunedDiscr = discr, trainEvolution = trainEvolution,
                                       tarMember = tdArchieve.tarMember if tdArchieve.tarMember is not None else '',
                                       eps = eps,
                                       rocPointChooseMethod = rocPointChooseMethod,
                                       modelChooseMethod = modelChooseMethod,
                                       aucEps = aucEps )
                # Add bin information to reference benchmark
              # end of references
            # end of configurations
            if test and (cMember - 1) == 3:
              break
          # end of (tdArchieve collection)
        except (UnpicklingError, ValueError, EOFError), e:
          import traceback
          # Couldn't read it as both a common file or a collection:
          self._warning("Ignoring file '%s'. Reason:\n%s", path, traceback.format_exc())
        # end of (try)
        if test and (cMember - 1) == 3:
          break
        # Go! Garbage
        gc.collect()
        elapsed = (time() - start)
        self._debug('Total time is: %.2fs', elapsed)
      # Finished all files in this bin

      # Print information retrieved:
      if self._level <= LoggingLevel.VERBOSE:
        for refBenchmark in cRefBenchmarkList:
          refName = refBenchmark.name
          self._verbose("Retrieved %d discriminator configurations for benchmark '%s':",
              len(tunedDiscrInfo[refName]) - 1,
              refBenchmark)
          for nKey, nDict in tunedDiscrInfo[refName].iteritems():
            if nKey in self.ignoreKeys:
              continue
            self._verbose("Retrieved %d sorts for configuration '%r'", len(nDict), nKey)
            for sKey, sDict in nDict.iteritems():
              self._verbose("Retrieved %d inits for sort '%d'", len(sDict['headerInfo']), sKey)
            # got number of inits
          # got number of sorts
        # got number of configurations
      # finished all references

      # Build monitoring root file
      if doMonitoring:
        import ROOT
        ROOT.TH1.AddDirectory(ROOT.kFALSE)
        ROOT.TH2.AddDirectory(ROOT.kFALSE)
        self._info("Creating monitoring file...")
        # Fix root file name:
        mFName = appendToFileName( cOutputName, 'monitoring' )
        mFName = ensureExtension( mFName, '.root' )
        self._sg = TFile( mFName ,'recreate')
        self._sgdirs=list()

      self._info("Creating summary...")

      # Create summary info object
      iPathHolder = dict()
      extraInfoHolder = dict()
      for refKey, refValue in tunedDiscrInfo.iteritems(): # Loop over operations
        refBenchmark = refValue['benchmark']
        # Create a new dictionary and append bind it to summary info
        rawBenchmark = refBenchmark.toRawObj()
        refDict = { 'rawBenchmark' : rawBenchmark
                  , 'rawTuningBenchmark' : refValue['tuningBenchmark'].toRawObj() if refValue['tuningBenchmark'] else ''
                  , 'etBinIdx' : etBinIdx, 'etaBinIdx' : etaBinIdx
                  , 'etBin' : etBinDict[etBinIdx]
                  , 'etaBin' : etaBinDict[etaBinIdx]
                  , 'removeOutputTansigTF' : self.decisionMaker.removeOutputTansigTF if self.decisionMaker else False
                  }
        headerKeys = refDict.keys()
        eps, modelChooseMethod = refValue['eps'], refValue['modelChooseMethod']
        # Add some extra values in rawBenchmark...
        refDict['rawBenchmark']['eps']=eps
        refDict['rawBenchmark']['modelChooseMethod'] = modelChooseMethod
        refDict['rawBenchmark']['modelChooseInitMethod'] = modelChooseInitMethod if modelChooseInitMethod not in (NotSet,None) else modelChooseMethod
        cSummaryInfo[refKey] = refDict

        for nKey, nValue in refValue.iteritems(): # Loop over neurons
          if nKey in self.ignoreKeys:
            continue
          nDict = dict()
          refDict['config_' + str(nKey).zfill(3)] = nDict

          for sKey, sValue in nValue.iteritems(): # Loop over sorts
            sDict = dict()
            nDict['sort_' + str(sKey).zfill(3)] = sDict
            self._debug("%s: Retrieving test outermost init performance for keys: config_%s, sort_%s",
                refBenchmark, nKey, sKey )
            # Retrieve information from outermost initializations:
            ( sDict['summaryInfoTst'], \
              sDict['infoTstBest'], sDict['infoTstWorst']) = self.__outermostPerf(
                                                                                   sValue['headerInfo'],
                                                                                   sValue['initPerfTstInfo'],
                                                                                   refBenchmark,
                                                                                   eps = eps,
                                                                                   method = modelChooseInitMethod if modelChooseInitMethod not in (NotSet,None) else modelChooseMethod,
                                                                                 )
            self._debug("%s: Retrieving operation outermost init performance for keys: config_%s, sort_%s",
                refBenchmark,  nKey, sKey )
            ( sDict['summaryInfoOp'], \
              sDict['infoOpBest'], sDict['infoOpWorst'])   = self.__outermostPerf(
                                                                                   sValue['headerInfo'],
                                                                                   sValue['initPerfOpInfo'],
                                                                                   refBenchmark,
                                                                                   eps = eps,
                                                                                   method = modelChooseInitMethod if modelChooseInitMethod not in (NotSet,None) else modelChooseMethod,
                                                                                 )
            if self.dCurator:
              self.dCurator.toTunableSubsets( sKey )
              tstBest = sDict['infoTstBest']
              tstDiscr = tstBest['discriminator']
              perfHolderTst = PerfHolder( None, None , decisionTaking = self.decisionMaker( tstDiscr ) if self.decisionMaker else None , level = self.level )
              tstPerf = perfHolderTst.getOperatingBenchmarks( refBenchmark
                                                            , ds                   = Dataset.Test
                                                            , eps                  = eps
                                                            , modelChooseMethod    = modelChooseMethod
                                                            , rocPointChooseMethod = rocPointChooseMethod
                                                            , aucEps               = aucEps
                                                            , neuron = tstBest['neuron'], sort = tstBest['sort'], init = tstBest['init']
                                                            )
              # We then change the best information to the linear correction:
              infoTstBest = { 'sp' : tstPerf.sp, 'det' : tstPerf.pd, 'fa' : tstPerf.pf, 'perf' : tstPerf.toRawObj()
                            , 'auc' : tstPerf.auc, 'mse' : tstPerf.mse, 'cut' : tstPerf.thres.toRawObj(), }
              sDict['infoTstRawBest'] = copy( sDict['infoTstBest'] )
              sDict['infoTstBest'].update(infoTstBest)
              if doMonitoring:
                self.sgDir( refname = refBenchmark.name, neuron = tstBest['neuron'], sort = tstBest['sort'], init = tstBest['init'], extra = 'linearcorr' )
                perfHolderTst.saveDecisionTakingGraphs()
                perfHolderOp = PerfHolder( None, None , decisionTaking = self.decisionMaker( tstDiscr ) if self.decisionMaker else None , level = self.level )
                opPerf = perfHolderOp.getOperatingBenchmarks( refBenchmark
                                                            , ds                   = Dataset.Operation
                                                            , eps                  = eps
                                                            , modelChooseMethod    = modelChooseMethod
                                                            , rocPointChooseMethod = rocPointChooseMethod
                                                            , aucEps               = aucEps
                                                            , neuron = tstBest['neuron'], sort = tstBest['sort'], init = tstBest['init']
                                                            )
                perfHolderOp.saveDecisionTakingGraphs()
              # Repeat, now for operation:
              opBest = sDict['infoOpBest']
              opDiscr = opBest['discriminator']
              if opBest['neuron'] != tstBest['neuron'] or opBest['sort'] != tstBest['sort'] or opBest['init'] != tstBest['init']:
                del tstBest, tstDiscr, perfHolderTst, tstPerf
                perfHolderOp = PerfHolder( None, None, decisionTaking = self.decisionMaker( opDiscr ) if self.decisionMaker else None , level = self.level )
                opPerf = perfHolderOp.getOperatingBenchmarks( refBenchmark
                                                            , ds                   = Dataset.Operation
                                                            , eps                  = eps
                                                            , modelChooseMethod    = modelChooseMethod
                                                            , rocPointChooseMethod = rocPointChooseMethod
                                                            , aucEps               = aucEps
                                                            , neuron = opBest['neuron'], sort = opBest['sort'], init = opBest['init']
                                                            #, rawPerf = PerformancePoint( refBenchmark.name + '_Operation'
                                                            #                            , opBest['sp'], opBest['det'], opBest['fa']
                                                            #                            , RawThreshold.fromRawObj( np.arctanh( opBest['cut'] ) )
                                                            #                            , auc =  opBest['auc']
                                                            #                            )
                                                            )
                if doMonitoring:
                  self.sgDir( refname = refBenchmark.name, neuron = opBest['neuron'], sort = opBest['sort'], init = opBest['init'], extra = 'linearcorr' )
                  perfHolderOp.saveDecisionTakingGraphs()
                  perfHolderTst = PerfHolder( None, None , decisionTaking = self.decisionMaker( opDiscr ) if self.decisionMaker else None , level = self.level )
                  tstPerf = perfHolderTst.getOperatingBenchmarks( refBenchmark
                                                                , ds                   = Dataset.Test
                                                                , eps                  = eps
                                                                , modelChooseMethod    = modelChooseMethod
                                                                , rocPointChooseMethod = rocPointChooseMethod
                                                                , aucEps               = aucEps
                                                                , neuron = opBest['neuron'], sort = opBest['sort'], init = opBest['init']
                                                                )
                  perfHolderTst.saveDecisionTakingGraphs()
                  del perfHolderTst, tstPerf
              # We then change the best information to the linear correction:
              infoOpBest = { 'sp' : opPerf.sp, 'det' : opPerf.pd, 'fa' : opPerf.pf, 'perf' : opPerf.toRawObj()
                            , 'auc' : opPerf.auc, 'mse' : opPerf.mse, 'cut' : opPerf.thres.toRawObj(), }
              sDict['infoOpRawBest'] = copy( sDict['infoOpBest'] )
              sDict['infoOpBest'].update(infoOpBest)
              del opBest, opDiscr, perfHolderOp, opPerf
            wantedKeys = ['infoOpBest', 'infoOpWorst', 'infoTstBest', 'infoTstWorst']
            for key in wantedKeys:
              kDict = sDict[key]
              iPathKey = kDict['path']
              value = (kDict['neuron'], kDict['sort'], kDict['init'], refBenchmark.reference, refBenchmark.name,)
              extraValue = kDict['tarMember']
              if iPathKey in iPathHolder:
                if not(value in iPathHolder[iPathKey]):
                  iPathHolder[iPathKey].append( value )
                  extraInfoHolder[iPathKey].append( extraValue )
              else:
                iPathHolder[iPathKey] = [value]
                extraInfoHolder[iPathKey] = [extraValue]
          ## Loop over sorts
          # Retrieve information from outermost sorts:
          keyVec = [ key for key, sDict in nDict.iteritems() ]
          self._verbose("config_%s unsorted order information: %r", nKey, keyVec )
          sortingIdxs = np.argsort( keyVec )
          sortedKeys  = apply_sort( keyVec, sortingIdxs )
          self._debug("config_%s sorted order information: %r", nKey, sortedKeys )
          allBestTstSortInfo   = apply_sort(
                [ sDict['infoTstBest' ] for key, sDict in nDict.iteritems() ]
              , sortingIdxs )
          allBestOpSortInfo    = apply_sort(
                [ sDict['infoOpBest'  ] for key, sDict in nDict.iteritems() ]
              , sortingIdxs )
          self._debug("%s: Retrieving test outermost sort performance for keys: config_%s",
              refBenchmark,  nKey )
          ( nDict['summaryInfoTst'], \
            nDict['infoTstBest'], nDict['infoTstWorst']) = self.__outermostPerf(
                                                                                 allBestTstSortInfo,
                                                                                 allBestTstSortInfo,
                                                                                 refBenchmark,
                                                                                 eps = eps,
                                                                                 method = modelChooseMethod,
                                                                               )
          self._debug("%s: Retrieving operation outermost sort performance for keys: config_%s",
              refBenchmark,  nKey )
          ( nDict['summaryInfoOp'], \
            nDict['infoOpBest'], nDict['infoOpWorst'])   = self.__outermostPerf(
                                                                                 allBestOpSortInfo,
                                                                                 allBestOpSortInfo,
                                                                                 refBenchmark,
                                                                                 eps = eps,
                                                                                 method = modelChooseMethod,
                                                                               )
        ## Loop over configs
        # Retrieve information from outermost discriminator configurations:
        keyVec = [ key for key, nDict in refDict.iteritems() if key not in headerKeys ]
        self._verbose("Ref %s unsort order information: %r", refKey, keyVec )
        sortingIdxs = np.argsort( keyVec )
        sortedKeys  = apply_sort( keyVec, sortingIdxs )
        self._debug("Ref %s sort order information: %r", refKey, sortedKeys )
        allBestTstConfInfo   = apply_sort(
              [ nDict['infoTstBest' ] for key, nDict in refDict.iteritems() if key not in headerKeys ]
            , sortingIdxs )
        allBestOpConfInfo    = apply_sort(
              [ nDict['infoOpBest'  ] for key, nDict in refDict.iteritems() if key not in headerKeys ]
            , sortingIdxs )
        self._debug("%s: Retrieving test outermost neuron performance", refBenchmark)
        ( refDict['summaryInfoTst'], \
          refDict['infoTstBest'], refDict['infoTstWorst']) = self.__outermostPerf(
                                                                                   allBestTstConfInfo,
                                                                                   allBestTstConfInfo,
                                                                                   refBenchmark,
                                                                                   eps = eps,
                                                                                   method = modelChooseMethod,
                                                                                 )
        self._debug("%s: Retrieving operation outermost neuron performance", refBenchmark)
        ( refDict['summaryInfoOp'], \
          refDict['infoOpBest'], refDict['infoOpWorst'])   = self.__outermostPerf(
                                                                                   allBestOpConfInfo,
                                                                                   allBestOpConfInfo,
                                                                                   refBenchmark,
                                                                                   eps = eps,
                                                                                   method = modelChooseMethod,
                                                                                 )
      # Finished summary information
      #if self._level <= LoggingLevel.VERBOSE:
      #  self._verbose("Priting full summary dict:")
      #  pprint(cSummaryInfo)

      # Build monitoring root file
      if doMonitoring:
        if not FullDumpNeurons:
          for iPath in progressbar(iPathHolder, len(iPathHolder), 'Reading configs: ', 60, 1, True, logger = self._logger):
            start = time()
            infoList, extraInfoList = iPathHolder[iPath], extraInfoHolder[iPath]
            self._info("Reading file '%s' which has %d configurations.", iPath, len(infoList))
            # FIXME Check if extension is tgz, and if so, merge multiple tarMembers
            tdArchieve = TunedDiscrArchieve.load(iPath)
            for (neuron, sort, init, refEnum, refName,), tarMember in zip(infoList, extraInfoList):
              #if self.dCurator: self.dCurator.toTunableSubsets( sort )
              # NOTE: TarMember is not being used, I could tdArchieve =
              # TunedDiscrArchieve.load( iPath, tarMember) and then get the
              # getTunedInfo
              tunedDict      = tdArchieve.getTunedInfo(neuron,sort,init)
              trainEvolution = tunedDict['tuningInfo']
              tunedDiscr     = tunedDict['tunedDiscr']
              if type(tunedDiscr) in (list, tuple,):
                if len(tunedDiscr) == 1:
                  discr = tunedDiscr[0]
                else:
                  discr = tunedDiscr[refEnum]
              else:
                # exmachina core version
                discr = tunedDiscr
              self.__addMonPerformance(discr, trainEvolution, refname = refName
                                      , neuron = neuron, sort = sort, init = init)
            elapsed = (time() - start)
            self._debug('Total time is: %.2fs', elapsed)
        else:
          for cFile, path in progressbar( enumerate(binPath),self._nFiles[binIdx], 'Reading files: ', 60, 1, True,
                                          logger = self._logger ):
            for tdArchieve in TunedDiscrArchieve.load(path, useGenerator = True,
                                                      extractAll = True if isMerged else False,
                                                      eraseTmpTarMembers = False if isMerged else True):
              # Calculate the size of the list
              barsize = len(tdArchieve.neuronBounds.list()) * len(tdArchieve.sortBounds.list()) * \
                        len(tdArchieve.initBounds.list())

              for neuron, sort, init in progressbar( product( tdArchieve.neuronBounds(),
                                                            tdArchieve.sortBounds(),
                                                            tdArchieve.initBounds() ),
                                                            barsize, 'Reading configurations: ', 60, 1, False,
                                                            logger = self._logger):
                if not neuron in FullDumpNeurons: continue
                tunedDict      = tdArchieve.getTunedInfo(neuron,sort,init)
                trainEvolution = tunedDict['tuningInfo']
                tunedDiscr     = tunedDict['tunedDiscr']
                for refBenchmark in cRefBenchmarkList:
                  if type(tunedDiscr) in (list, tuple,):
                    if len(tunedDiscr) == 1:
                      discr = tunedDiscr[0]
                    else:
                      discr = tunedDiscr[refBenchmark.reference]
                  else:
                    # exmachina core version
                    discr = tunedDiscr
                  self.__addMonPerformance( discr = discr, trainEvolution = trainEvolution
                                          , refname = refBenchmark.name
                                          , neuron = neuron, sort = sort, init = init)
            if test and (cFile - 1) == 3:
              break
        self._sg.Close()
      # Do monitoring

      for iPath in iPathHolder:
        # Check whether the file is a original file (that is, it is in binFilesMergedList),
        # or if it was signed as a merged file:
        if os.path.exists(iPath) and binFilesMergedDict.get(iPath, False):
          # Now we proceed and remove all temporary files created
          # First, we need to find all unique temporary folders:
          from shutil import rmtree
          tmpFolder = os.path.dirname( iPath )
          import tempfile
          if iPath.startswith( tempfile.tempdir ):
            self._debug("Removing temporary folder: %s", tmpFolder)
            rmtree( tmpFolder )
          else:
            self._warning("Cowardly refusing to delete possible non-temp folder: %s. Remove it if this is not an analysis file.", tmpFolder)
          # for tmpFolder
      # if isMerged

      #    Don't bother with the following code, just something I was working on in case extractAll is an issue
      #    neuronList, sortList, initList = iPathHolder[iPath]
      #    tarMemberList, refBenchmarkIdxList, refBenchmarkNameList = extraInfoHolder[iPath]
      #    uniqueMemberList, inverseIdxList = np.unique(tarMemberList, return_inverse=True)
      #    # What would happen to tarMember if multiple files are added?
      #    for tdArchieve, cIdx in enumerate( TunedDiscrArchieve.load(iPath, tarMemberList = uniqueMemberList ) ):
      #      repeatIdxList = matlab.find( inverseIdxList == inverseIdxList[cIdx] )
      #      for repeatIdx in repeatIdxList:
      #        neuron, sort, init, refIdx, refName = neuronList[i], sortList[i], initList[i], refBenchmarkIdxList[i], refBenchmarkNameList[i]

      # Strip keys from summary info that are only used for monitoring and
      # shouldn't be at the final file.
      for refKey, refValue in cSummaryInfo.iteritems(): # Loop over operations
        for nKey, nValue in refValue.iteritems():
          if 'config_' in nKey:
            for sKey, sValue in nValue.iteritems():
              if 'sort_' in sKey:
                for key in ['infoOpBest','infoOpWorst','infoTstBest','infoTstWorst','infoOpRawBest','infoTstRawBest',]:
                  try:
                    sValue[key].pop('path',None)
                    sValue[key].pop('tarMember',None)
                  except KeyError, e:
                    if e.args[0] in ('infoOpRawBest', 'infoTstRawBest'):
                      pass
              else:
                sValue.pop('path',None)
                sValue.pop('tarMember',None)
          elif nKey in ['infoOpBest','infoOpWorst','infoTstBest','infoTstWorst','infoOpRawBest','infoTstRawBest',]:
            nValue.pop('path',None)
            nValue.pop('tarMember',None)
      # Remove keys only needed for
      # FIXME There is probably a "smarter" way to do this
      #holdenParents = []
      #for _, key, parent, _, level in traverse(cSummaryInfo, tree_types = (dict,)):
      #  if key in ('path', 'tarMember') and not(parent in holdenParents):
      #    holdenParents.append(parent)


      if self._level <= LoggingLevel.VERBOSE:
        pprint(cSummaryInfo)
      elif self._level <= LoggingLevel.DEBUG:
        for refKey, refValue in cSummaryInfo.iteritems(): # Loop over operations
          self._debug("This is the summary information for benchmark %s", refKey )
          pprint({key : { innerkey : innerval for innerkey, innerval in val.iteritems() if not(innerkey.startswith('sort_'))}
                                              for key, val in refValue.iteritems() if ( type(key) is str
                                                                                   and key not in ('etBinIdx', 'etaBinIdx','etBin','etaBin','removeOutputTansigTF')
                                                                                   )
                 }
                , depth=3
                )

      # Append pp collections
      cSummaryInfo['infoPPChain'] = cSummaryPPInfo
      outputPath = save( cSummaryInfo, cOutputName, compress=compress )
      self._info("Saved file '%s'",outputPath)
      # Save matlab file
      if toMatlab:
        from Gaugi import save
        try:
          save(cSummaryInfo, cOutputName, protocol = 'mat')
        except ImportError:
          self._warning(("Cannot save matlab file, it seems that scipy is not "
              "available."))
          with open(ensureExtension( cOutputName, '.mat'), 'w') as dummy_mat:
            dummy_mat.write("## This is just a dummy file. ##")
      lockFile.delete()
      del lockFile
      # Finished bin
    # finished all files
  # end of loop

  #def __retrieveFileInfo(self, tdArchieve,
  #                             cRefBenchmarkList,
  #                             tunedDiscrInfo,
  #                             cSummaryPPInfo):
  #  """
  #  Retrieve tdArchieve information
  #  """
  # end of __retrieveFileInfo

  def __addPPChain(self, cSummaryPPInfo, tunedPPChain, sort):
    if not( 'sort_' + str(sort).zfill(3) in cSummaryPPInfo ) and tunedPPChain:
      ppData = tunedPPChain.toRawObj()
      cSummaryPPInfo['sort_' + str( sort ).zfill(3) ] = ppData
  # end of __addPPChain

  def __outermostPerf(self, headerInfoList, perfInfoList, refBenchmark, **kw):

    summaryDict = {'cut': [], 'sp': [], 'det': [], 'fa': [], 'auc' : [], 'mse' : []}
    # Fetch all information together in the dictionary:
    for key in summaryDict.keys():
      summaryDict[key] = [ perfInfo[key] for perfInfo in perfInfoList ]
      if key == 'cut':
        # TODO This will need to be updated in the new RCore version
        # (in fact, all this should be review to a use the RawDictStreamable tool)
        sc = summaryDict['cut']
        name = sc[0]['class']
        if name == "RawThreshold":
          summaryDict['cutMean'] = np.mean([s['thres'] for s in sc],axis=0)
          summaryDict['cutStd' ] = np.std([s['thres'] for s in sc],axis=0)
        elif name == "PileupLinearCorrectionThreshold":
          summaryDict['cutInterceptMean'] = np.mean([s['intercept'] for s in sc],axis=0)
          summaryDict['cutInterceptStd' ] = np.std( [s['intercept'] for s in sc],axis=0)
          summaryDict['cutSlopeMean']     = np.mean([s['slope'] for s in sc],axis=0)
          summaryDict['cutSlopeStd' ]     = np.std( [s['slope'] for s in sc],axis=0)
          summaryDict['cutReachMean']     = [np.mean([s['reach'][i] for s in sc],axis=0) for i in xrange(len(sc[0]['reach']))]
          summaryDict['cutReachStd' ]     = [np.std([s['reach'][i] for s in sc],axis=0) for i in xrange(len(sc[0]['reach']))]
          summaryDict['margins']          = sc[0]['margins']
          summaryDict['limits']           = sc[0]['limits']
          summaryDict['pileupStr']        = sc[0]['pileupStr']
      else:
        summaryDict[key + 'Mean'] = np.mean(summaryDict[key],axis=0)
        summaryDict[key + 'Std' ] = np.std( summaryDict[key],axis=0)

    # Put information together on data:
    benchmarks = [summaryDict['sp'], summaryDict['det'], summaryDict['fa'], summaryDict['auc'], summaryDict['mse']]

    # The outermost performances:
    refBenchmark.level = self.level # FIXME Something ignores previous level
                                    # changes, but couldn't discover what...
    bestIdx  = refBenchmark.getOutermostPerf(benchmarks, **kw )
    worstIdx = refBenchmark.getOutermostPerf(benchmarks, cmpType = -1., **kw )
    if self._level <= LoggingLevel.DEBUG:
      self._debug('Retrieved best index as: %d; values: (SP:%f, Pd:%f, Pf:%f, AUC:%f, MSE:%f)', bestIdx,
          benchmarks[0][bestIdx],
          benchmarks[1][bestIdx],
          benchmarks[2][bestIdx],
          benchmarks[3][bestIdx],
          benchmarks[4][bestIdx])
      self._debug('Retrieved worst index as: %d; values: (SP:%f, Pd:%f, Pf:%f, AUC:%f, MSE:%f)', worstIdx,
          benchmarks[0][worstIdx],
          benchmarks[1][worstIdx],
          benchmarks[2][worstIdx],
          benchmarks[3][worstIdx],
          benchmarks[4][worstIdx])

    # Retrieve information from outermost performances:
    def __getInfo( headerInfoList, perfInfoList, idx ):
      info = dict()
      wantedKeys = ['discriminator', 'neuron', 'sort', 'init', 'path', 'tarMember']
      headerInfo = headerInfoList[idx]
      for key in wantedKeys:
        info[key] = headerInfo[key]
      wantedKeys = ['cut','sp', 'det', 'fa', 'auc', 'mse',]
      perfInfo = perfInfoList[idx]
      for key in wantedKeys:
        info[key] = perfInfo[key]
      return info

    bestInfoDict  = __getInfo( headerInfoList, perfInfoList, bestIdx )
    worstInfoDict = __getInfo( headerInfoList, perfInfoList, worstIdx )
    if self._level <= LoggingLevel.VERBOSE:
      self._debug("The best configuration retrieved is: <config:%s, sort:%s, init:%s>",
                           bestInfoDict['neuron'], bestInfoDict['sort'], bestInfoDict['init'])
      self._debug("The worst configuration retrieved is: <config:%s, sort:%s, init:%s>",
                           worstInfoDict['neuron'], worstInfoDict['sort'], worstInfoDict['init'])
    return (summaryDict, bestInfoDict, worstInfoDict)
  # end of __outermostPerf





  def exportDiscrFiles(self, ringerOperation, **kw ):
    """
    Export discriminators operating at reference benchmark list to the
    ATLAS environment using this CrossValidStat information.
    """
    if not self._summaryInfo:
      self._fatal("Create the summary information using the loop method.")
    CrossValidStat.exportDiscrFiles( self._summaryInfo,
                                     ringerOperation,
                                     level = self._level,
                                     **kw )

  @classmethod
  def exportDiscrFiles(cls, summaryInfoList, ringerOperation, **kw):
    """
    Export discriminators operating at reference benchmark list to the
    ATLAS environment using summaryInfo.

    If benchmark name on the reference list is not available at summaryInfo, an
    KeyError exception will be raised.
    """
    from Gaugi import retrieveRawDict
    baseName            = kw.pop( 'baseName',            'tunedDiscr'      )
    refBenchCol         = kw.pop( 'refBenchCol',         None              )
    configCol           = kw.pop( 'configCol',           []                )
    triggerChains       = kw.pop( 'triggerChains',       None              )
    _etBins             = kw.pop( 'EtBins',              None              )
    _etaBins            = kw.pop( 'EtaBins',             None              )
    nEtBins             = kw.pop( 'nEtBins',             None              )
    nEtaBins            = kw.pop( 'nEtaBins',            None              )
    testData            = kw.pop( 'testData',            None              )
    xAODDataSgn         = kw.pop( 'xAODDataSgn',         None              )
    xAODDataBkg         = kw.pop( 'xAODDataBkg',         None              )
    overwrite           = kw.pop( 'overwrite',           False             )
    maxPileupCorrection = kw.pop( 'maxPileupCorrection', None              )
    level         = kw.pop( 'level'         , LoggingLevel.INFO )

    # Initialize local logger
    logger      = Logger.getModuleLogger("exportDiscrFiles", logDefaultLevel = level )
    checkForUnusedVars( kw, logger.warning )

    # etBins is kept only for backward compatibility
    if _etBins is not None:
      logger.warning("etBins is deprecated and should only be used with old summary info")

    # etaBins is kept only for backward compatibility
    if _etaBins is not None:
      logger.warning("etaBins is deprecated and should only be used with old summary info")

    if nEtBins is None:
      nEtBins = len(_etBins) - 1 if nEtBins else 1

    if nEtBins is None:
      nEtaBins = len(_etaBins) - 1 if nEtaBins else 1

    # Treat the summaryInfoList
    if not isinstance( summaryInfoList, (list,tuple)):
      summaryInfoList = [ summaryInfoList ]
    summaryInfoList = list(traverse(summaryInfoList,simple_ret=True))
    nSummaries = len(summaryInfoList)
    if not nSummaries:
      logger.fatal("Summary dictionaries must be specified!")

    if refBenchCol is None:
      refBenchCol = summaryInfoList[0].keys()

    # Treat the reference benchmark list
    if not isinstance( refBenchCol, (list,tuple)):
      refBenchCol = [ refBenchCol ] * nSummaries

    if len(refBenchCol) == 1:
      refBenchCol = refBenchCol * nSummaries

    nRefs = len(list(traverse(refBenchCol,simple_ret=True)))

    # Make sure that the lists are the same size as the reference benchmark:
    nConfigs = len(list(traverse(configCol,simple_ret=True)))
    if nConfigs == 0:
      configCol = [None for i in range(nRefs)]
    elif nConfigs == 1:
      configCol = configCol * nSummaries
    nConfigs = len(list(traverse(configCol,simple_ret=True)))

    if nConfigs != nRefs:
      logger.fatal("Summary size is not equal to the configuration list.", ValueError)

    if nRefs == nConfigs == nSummaries:
      # If user input data without using list on the configuration, put it as a list:
      for o, idx, parent, _, _ in traverse(configCol):
        parent[idx] = [o]
      for o, idx, parent, _, _ in traverse(refBenchCol):
        parent[idx] = [o]

    configCol   = list(traverse(configCol,max_depth_dist=1,simple_ret=True))
    refBenchCol = list(traverse(refBenchCol,max_depth_dist=1,simple_ret=True))
    nConfigs = len(configCol)
    nSummary = len(refBenchCol)

    if nRefs != nConfigs != nSummary:
      logger.fatal("Number of references, configurations and summaries do not match!", ValueError)

    # Retrieve the operation:
    from TuningTools.dataframe import RingerOperation
    ringerOperation = RingerOperation.retrieve(ringerOperation)
    logger.info(('Exporting discrimination info files for the following '
                'operating point (RingerOperation:%s).'),
                RingerOperation.tostring(ringerOperation))

    # Threshold list:
    neuralDictCol = [[None for _ in range(nEtaBins)] for _ in range(nEtBins)]
    thresCol = ThresholdCollection([ThresholdCollection([None for _ in range(nEtaBins)]) for _ in range(nEtBins)])
    ppCol = PreProc.PreProcCollection([PreProc.PreProcCollection([None for _ in range(nEtaBins)]) for _ in range(nEtBins)])
    benchmarkCol = ReferenceBenchmarkCollection([ReferenceBenchmarkCollection([None for _ in range(nEtaBins)]) for _ in range(nEtBins)])
    rawRingsSgn = [[None for _ in range(nEtaBins)] for _ in range(nEtBins)]
    ringsSgn    = [[None for _ in range(nEtaBins)] for _ in range(nEtBins)]
    baseInfoSgn = [[None for _ in range(nEtaBins)] for _ in range(nEtBins)]
    outputsSgn  = [[None for _ in range(nEtaBins)] for _ in range(nEtBins)]
    rawRingsBkg = [[None for _ in range(nEtaBins)] for _ in range(nEtBins)]
    ringsBkg    = [[None for _ in range(nEtaBins)] for _ in range(nEtBins)]
    baseInfoBkg = [[None for _ in range(nEtaBins)] for _ in range(nEtBins)]
    outputsBkg  = [[None for _ in range(nEtaBins)] for _ in range(nEtBins)]
    # infoOpBest

    if ringerOperation is RingerOperation.L2:
      if triggerChains is None:
        triggerChains = "custom"
      if type(triggerChains) not in (list,tuple):
        triggerChains = [triggerChains]
      nExports = len(refBenchCol[0])
      if len(triggerChains) == 1 and nExports != 1:
        baseChainName = triggerChains[0]
        triggerChains = ["%s_chain%d" % (baseChainName,i) for i in range(nExports)]
      if nExports != len(triggerChains):
        self._fatal("Number of exporting chains does not match with number of given chain names.", ValueError)

      #output = open('TrigL2CaloRingerConstants.py','w')
      #output.write('def SignaturesMap():\n')
      #output.write('  signatures=dict()\n')
      outputDict = dict()
    elif ringerOperation is RingerOperation.Offline:
      # Import athena cpp information
      try:
        import cppyy
      except ImportError:
        import PyCintex as cppyy
      try:
        try:
          try:
            cppyy.loadDict('RingerSelectorToolsLib')
          except:
            cppyy.loadDict('RingerSelectorTools')
        except RuntimeError:
          cppyy.loadDict('RingerSelectorTools_Reflex')
      except RuntimeError:
        logger.fatal("Couldn't load RingerSelectorTools dictionary.")
      from ROOT import TFile
      ## Import reflection information
      from ROOT import std # Import C++ STL
      from ROOT.std import vector # Import C++ STL
      # Import Ringer classes:
      from ROOT import Ringer
      from ROOT import MsgStream
      from ROOT import MSG
      #from ROOT.Ringer import IOHelperFcns
      from ROOT.Ringer import PreProcessing
      from ROOT.Ringer.PreProcessing      import Norm
      from ROOT.Ringer.PreProcessing.Norm import Norm1VarDep, ExtraPatternsNorm
      from ROOT.Ringer import IPreProcWrapperCollection
      from ROOT.Ringer import Discrimination
      #from ROOT.Ringer import IDiscrWrapper
      #from ROOT.Ringer import IDiscrWrapperCollection
      from ROOT.Ringer.Discrimination import NNFeedForwardVarDep
      #from ROOT.Ringer import IThresWrapper
      from ROOT.Ringer.Discrimination import UniqueThresholdVarDep, LinearPileupCorrectionThresholdVarDep
      # TODO We can create these vectors later on and createonly a list with
      # the pre-processings and discriminators
      ## Discriminator matrix to the RingerSelectorTools format:
      BaseVec = vector("Ringer::Discrimination::NNFeedForwardVarDep*")
      vec = BaseVec( ); vec += [ NNFeedForwardVarDep() for _ in range(nEtaBins) ]
      vecvec = vector( BaseVec )(); vecvec += [deepcopy(vec) for _ in range(nEtBins) ]
      ringerNNVec = vector( vector( BaseVec ) )() # We are not using longitudinal segmentation
      ringerNNVec.push_back(vecvec)
    else:
      logger.fatal( "Chosen operation (%s) is not yet implemented.", RingerOperation.tostring(ringerOperation) )

    import time
    for summaryInfo, refBenchmarkList, configList in \
                        zip(summaryInfoList,
                            refBenchCol,
                            configCol,
                           ):
      if type(summaryInfo) is str:
        logger.info('Loading file "%s"...', summaryInfo)
        summaryInfo = load(summaryInfo)
      elif type(summaryInfo) is dict:
        pass
      else:
        logger.fatal("Cross-valid summary info is not string and not a dictionary.", ValueError)
      from itertools import izip, count
      for idx, refBenchmarkName, config in izip(count(), refBenchmarkList, configList):
        try:
          key = filter(lambda x: refBenchmarkName in x, summaryInfo)[0]
          refDict = summaryInfo[ key ]
        except IndexError :
          logger.fatal("Could not find reference %s in summaryInfo. Available options are: %r", refBenchmarkName, summaryInfo.keys())
        logger.info("Using Reference key: %s", key )
        # Check if files already exist:
        if ringerOperation is RingerOperation.Offline:
          fdName = baseName + '_Discr_' + refBenchmarkName + ".root"
          ftName = baseName + '_Thres_' + refBenchmarkName + ".root"
          if os.path.exists( fdName ):
            if overwrite:
              os.remove(fdName)
            else:
              logger.error("Discriminator file %s already exists, not dumping any information.", fdName)
              return
          if os.path.exists( ftName ):
            if overwrite:
              os.remove(ftName)
            else:
              logger.error("Threshold file %s already exists, not dumping any information.", ftName)
              return

        ppInfo = summaryInfo['infoPPChain']

        etBinIdx = refDict['etBinIdx']
        etaBinIdx = refDict['etaBinIdx']
        try:
          etBin = refDict['etBin']
          etaBin = refDict['etaBin']
        except KeyError:
          self.warning("Attempting to retrieve bins from etBins/etaBins argument. This should only be needed for old summaryDicts.")
          etBin = _etBins[etBinIdx:etBinIdx+2]
          etaBin = _etaBins[etBinIdx:etBinIdx+2]

        benchmarkCol[etBinIdx][etaBinIdx] = retrieveRawDict( refDict['rawBenchmark'] )

        logger.info('Dumping (<etBinIdx:%d,etaBinIdx:%d>: (%r,%r)',etBinIdx, etaBinIdx, etBin.tolist(), etaBin.tolist())

        #config = configCol[etBinIdx*(len(etaBinIdxs)-1) + etaBinIdx][0]
        info   = refDict['infoOpBest'] if config is None else \
                 refDict['config_' + str(config).zfill(3)]['infoOpBest']

        # Check if user specified parameters for exporting discriminator
        # operation information:
        sort =  info['sort']
        init =  info['init']

        # Get tuned ppChain:
        ppChain = retrieveRawDict( ppInfo[ 'sort_' + str(sort).zfill(3) ] )
        ppCol[etBinIdx][etaBinIdx] = ppChain
        # FIXME Temporary solution
        ppChain.etBin = etBin
        ppChain.etaBin = etaBin

        pyThres = info['cut']
        if isinstance( pyThres, float ):
          pyThres = RawThreshold( thres = pyThres
                                , etBinIdx = etBinIdx, etaBinIdx = etaBinIdx
                                , etBin = etBin, etaBin =  etaBin)
        else:
          pyThres = retrieveRawDict( pyThres )
        if pyThres.etBin in (None,''):
          pyThres.etBin = etBin
        elif isinstance( pyThres.etBin, (list,tuple)):
          pyThres.etBin = np.array( pyThres.etBin)
        if not(np.array_equal( pyThres.etBin, etBin )):
          logger.fatal("etBin does not match for threshold! Should be %r, is %r", pyThres.etBin, etBin )
        if pyThres.etaBin in (None,''):
          pyThres.etaBin = etaBin
        elif isinstance( pyThres.etaBin, (list,tuple)):
          pyThres.etaBin = np.array( pyThres.etaBin)
        if not(np.array_equal( pyThres.etaBin, etaBin )):
          logger.fatal("etaBin does not match for threshold! Should be %r, is %r", pyThres.etaBin, etaBin )

        thresCol[etBinIdx][etaBinIdx] = pyThres

        discrDict = info['discriminator']
        neuralDictCol[etBinIdx][etaBinIdx] = discrDict
        removeOutputTansigTF = refDict.get('removeOutputTansigTF', None )
        discrDict['removeOutputTansigTF'] = removeOutputTansigTF
        # FIXME Temporary solution
        discrDict['etBin'] = etBin
        discrDict['etaBin'] = etaBin

        def tolist(a):
          if isinstance(a,list): return a
          else: return a.tolist()

        ## Write the discrimination wrapper
        if ringerOperation in (RingerOperation.L2, RingerOperation.L2Calo):
          ## Discriminator configuration
          discrData={}
          discrData['datecode']  = time.strftime("%Y-%m-%d %H:%M")
          discrData['configuration']={}
          discrData['configuration']['benchmarkName'] = refBenchmarkName
          discrData['configuration']['etBinIdx']     = etBin.tolist()
          discrData['configuration']['etaBinIdx']    = etaBin.tolist()
          discrData['discriminator'] = discrDict
          discrData['discriminator']['threshold'] = pyThres.thres

          triggerChain = triggerChains[idx]
          if not triggerChain in outputDict:
            cDict={}
            outputDict[triggerChain] = cDict
          else:
            cDict = outputDict[triggerChain]

          discrData['discriminator']['nodes']    = tolist( discrDict['nodes']   )
          discrData['discriminator']['bias']     = tolist( discrDict['bias']    )
          discrData['discriminator']['weights']  = tolist( discrDict['weights'] )
          cDict['et%d_eta%d' % (etBinIdx, etaBinIdx) ] = discrData

        elif ringerOperation is RingerOperation.Offline:
          logger.debug( 'Exporting information for et/eta bin: %d (%f->%f) / %d (%f->%f)', etBinIdx, etBin[0], etBin[1],
                                                                                           etaBinIdx, etaBin[0], etaBin[1] )
          ## Retrieve the discriminator collection:
          # Retrieve discriminator
          tunedDiscr = info['discriminator']
          # And get their weights
          nodes = std.vector("unsigned int")(); nodes += tolist( tunedDiscr['nodes'] )
          weights = std.vector("float")(); weights += tolist( tunedDiscr['weights'] )
          bias = vector("float")(); bias += tolist( tunedDiscr['bias'] )
          ringerDiscr = ringerNNVec[0][etBinIdx][etaBinIdx]
          ringerDiscr.changeArchiteture(nodes, weights, bias)
          ringerDiscr.setEtDep( *etBin )
          ringerDiscr.setEtaDep( *etaBin )
          logger.verbose('Discriminator information: %d/%d (%f->%f) (%f->%f)', etBinIdx, etaBinIdx,
              ringerDiscr.etMin(), ringerDiscr.etMax(), ringerDiscr.etaMin(), ringerDiscr.etaMax())
          if removeOutputTansigTF is not None: ringerDiscr.setRemoveOutputTanh( removeOutputTansigTF )
          print ringerDiscr.name()
          #getattr(ringerDiscr,'print')(MSG.DEBUG)
          # Print information discriminator information:
          ##msg = MsgStream('ExportedNeuralNetwork')
          ##msg.setLevel(LoggingLevel.toC(level))
          ##ringerDiscr.setMsgStream(msg)
          ##getattr(ringerDiscr,'print')(MSG.DEBUG)

        logger.info('neuron = %d, sort = %d, init = %d, thr = %s',
                    info['neuron'],
                    info['sort'],
                    info['init'],
                    pyThres )

      # for benchmark
    # for summay in list

    if ringerOperation in (RingerOperation.L2Calo, RingerOperation.L2):
      #for key, val in outputDict.iteritems():
      #  output.write('  signatures["%s"]=%s\n' % (key, val))
      #output.write('  return signatures\n')
      return outputDict
    elif ringerOperation is RingerOperation.Offline:
      from ROOT.Ringer import RingerProcedureWrapper, ExtraDescriptionPatterns
      ## Create pre-processing wrapper:
      if ppCol.all(PreProc.Norm1) or ppCol.all(PreProc.RingerEtaMu):
        # TODO I could take benefit of the norm1 and save it as a PreProcWrapperNorm1Collection
        RingerNorm1IndepWrapper = RingerProcedureWrapper("Ringer::PreProcessing::Norm::Norm1VarDep",
                                                         "Ringer::EtaIndependent",
                                                         "Ringer::EtIndependent",
                                                         "Ringer::NoSegmentation")
        logger.debug('Initiazing norm1Wrapper...')
        BaseVec = vector("Ringer::PreProcessing::Norm::Norm1VarDep*")
        vec = BaseVec( 1, Norm1VarDep() ); vecvec = vector( BaseVec )( 1, vec )
        norm1Vec = vector( vector( BaseVec ) )() # We are not using longitudinal segmentation
        norm1Vec.push_back(vecvec)
        norm1Wrapper = RingerNorm1IndepWrapper(norm1Vec)
      else:
        ## Retrieve the pre-processing chain:
        #norm1VarDep = norm1Vec[0][etBinIdx][etaBinIdx]
        #norm1VarDep.setEtDep( *etBin )
        #norm1VarDep.setEtaDep( *etaBin )
        logger.fatal("Not implemented pre-processing extraction for collection: %r", ppCol)
      ## Create the vectors which will hold the procedures
      ## Add it to the pre-processing collection chain
      logger.debug('Creating PP-Chain...')
      ringerPPCollection = IPreProcWrapperCollection()
      ringerPPCollection.push_back(norm1Wrapper)
      ## Create the discrimination wrapper:
      RingerNNDepWrapper = RingerProcedureWrapper("Ringer::Discrimination::NNFeedForwardVarDep",
                                                  "Ringer::EtaDependent",
                                                  "Ringer::EtDependent",
                                                  "Ringer::NoSegmentation")
      logger.debug('Exporting RingerNNDepWrapper...')
      from ROOT.Ringer import RingerConfStruct
      rConf = RingerConfStruct()
      rConf.useNvtx = True
      # rConf.useCaloStdPat = True if neuralDictCol[0][0]['numberOfFusedDatasets'] == 3 else False
      # rConf.useTrackPat = True if neuralDictCol[0][0]['numberOfFusedDatasets'] == 2 else False
      nnWrapper = RingerNNDepWrapper( ringerPPCollection, ringerNNVec )
      # Add eta mu normalization if used:
      if ppCol.has( PreProc.RingerEtaMu ):
        logger.debug('Exporting RingerNNDepWrapper...')
        BaseVec = vector("Ringer::PreProcessing::Norm::ExtraPatternsNorm*")
        extraDescriptionNorms = vector(BaseVec)()
        for _ in range(nEtBins):
          vec = BaseVec()
          for etaBinIdx in range(nEtaBins):
            ppChain = ppCol[etBinIdx][etaBinIdx]
            ringerEtaMu = ppChain.get( PreProc.RingerEtaMu )
            vec.push_back( ExtraPatternsNorm( 0., 1.
                                            , ringerEtaMu._etamin, ringerEtaMu._etamax
                                            , ringerEtaMu._pileupThreshold
                                            )
                         )
          extraDescriptionNorms.push_back( vec )
        extraPatternsDescription = ExtraDescriptionPatterns().setFeedEta().setFeedPileupEstimation()
        nnWrapper.setExtraDescriptionPatterns( extraPatternsDescription )
        nnWrapper.setExtraDescriptionNorms( extraDescriptionNorms )
      # Export the discrimination wrapper to a TFile and save it:
      logger.debug('Creating vector collection...')
      discrCol = vector('Ringer::IDiscrWrapper*')()
      logger.debug('Pushing back discriminator wrappers...')
      discrCol.push_back(nnWrapper)
      RingerNNDepWrapper.writeCol(discrCol, fdName )
      logger.info("Successfully created file %s.", fdName)
      logger.debug('Creating vector collection...')
      rConf.writeConf( fdName )

      ## Create threshold wrapper:
      if thresCol.all( RawThreshold ):
        thresType = "Ringer::Discrimination::UniqueThresholdVarDep"
      elif thresCol.all( PileupLinearCorrectionThreshold ):
        thresType = "Ringer::Discrimination::LinearPileupCorrectionThresholdVarDep"
      else:
        thresType = "Ringer::Discrimination::IThreshold"
      logger.info("Using threshold type: %s", thresType )
      RingerThresWrapper = RingerProcedureWrapper( thresType,
                                                  "Ringer::EtaDependent",
                                                  "Ringer::EtDependent",
                                                  "Ringer::NoSegmentation")
      logger.debug('Initiazing Threshold Wrapper:')
      BaseVec = vector( thresType + '*' ); thresVec = vector( BaseVec )()
      if testData:
        from TuningTools import DataCurator
        dCurator = DataCurator( {}
                              , dataLocation = testData
                              , addDefaultPP = False
                              , operationPoint = ringerOperation
                              )
      for etBinIdx in range(nEtBins):
        vec = BaseVec()
        for etaBinIdx in range(nEtaBins):
          # TODO: make pyThres a list of thresholds to allow multiple
          # thresholds
          pyThres = thresCol[etBinIdx][etaBinIdx]
          if pyThres.etBinIdx != -1:
            assert pyThres.etBinIdx == etBinIdx
          if pyThres.etaBinIdx != -1:
            assert pyThres.etaBinIdx == etaBinIdx
          if isinstance(pyThres, RawThreshold):
            thres = UniqueThresholdVarDep( pyThres.thres )
          elif isinstance(pyThres, PileupLinearCorrectionThreshold ):
            args = [pyThres.intercept, pyThres.slope] + (
                   [maxPileupCorrection] if maxPileupCorrection is not None else [])
            thres = LinearPileupCorrectionThresholdVarDep( *args )
          thres.setEtDep( *pyThres.etBin )
          thres.setEtaDep( *pyThres.etaBin )
          if testData:
            neuralSel = ringerNNVec[0][etBinIdx][etaBinIdx]
            from TuningTools import CuratedSubset
            dCurator.prepareForBin( etBinIdx = etBinIdx, etaBinIdx = etaBinIdx
                                  , loadEfficiencies = False, loadCrossEfficiencies = False )
            dCurator.ppChain = ppCol[etBinIdx][etaBinIdx]
            rawRingsSgn[etBinIdx][etaBinIdx]    = dCurator.patterns[0][0]
            rawRingsBkg[etBinIdx][etaBinIdx]    = dCurator.patterns[0][1]
            ringsSgn[etBinIdx][etaBinIdx]    = dCurator[CuratedSubset.sgnOpData]
            ringsBkg[etBinIdx][etaBinIdx]    = dCurator[CuratedSubset.bkgOpData]
            baseInfoSgn[etBinIdx][etaBinIdx] = dCurator[CuratedSubset.sgnOpBaseInfo]
            baseInfoBkg[etBinIdx][etaBinIdx] = dCurator[CuratedSubset.bkgOpBaseInfo]
            from TuningTools.DecisionMaking import DecisionMaker
            decisionMaker = DecisionMaker( dCurator, {}, removeOutputTansigTF = neuralSel.getRemoveOutputTanh
                                         , pileupRef = 'nvtx' )
            decisionTaking = decisionMaker( neuralDictCol[etBinIdx][etaBinIdx] )
            opPoint = decisionTaking.getEffPoint( 'EmulatedEfficiency' , subset = [CuratedSubset.opData, CuratedSubset.opData]
                                                , thres = pyThres
                                                , makeCorr = isinstance(pyThres, PileupLinearCorrectionThreshold) )
            outputsSgn[etBinIdx][etaBinIdx] = decisionTaking._effOutput[0]
            outputsBkg[etBinIdx][etaBinIdx] = decisionTaking._effOutput[1]
            logger.info( "EmulatedEfficiency <et:%r,eta:%r>: %s", pyThres.etBin[0], pyThres.etaBin[0], opPoint )
          logger.info( "Threshold operation benchmark <et:%r,eta:%r> = %s"
                     , pyThres.etBin[0], pyThres.etaBin[0], pyThres )
          if logger.isEnabledFor( LoggingLevel.DEBUG ):
            thresMsg = MsgStream("ExportedThreshold")
            thresMsg.setLevel(LoggingLevel.toC(level))
            thres.setMsgStream(thresMsg)
            getattr(thres,'print')(MSG.DEBUG)
          vec.push_back( thres )
        thresVec.push_back( vec )
      thresWrapper = RingerThresWrapper(thresVec)

      RingerThresWrapper.writeWrapper( thresWrapper, ftName, )
      logger.info("Successfully created file %s.", ftName )
      if xAODDataSgn or xAODDataBkg:
        import ROOT
        ROOT.gROOT.Macro( '$ROOTCOREDIR/scripts/load_packages.C' )
        #ROOT.gROOT.ProcessLine(".x $ROOTCOREDIR/scripts/load_packages.C")
        from ROOT.Ringer import AsgElectronRingerSelector
        from ROOT.Ringer import ElectronTAccept
        from ROOT import AsgElectronLikelihoodTool
        import ROOT
        if xAODDataSgn:
          f = ROOT.TFile.Open(xAODDataSgn)
          t = ROOT.xAOD.MakeTransientTree( f, "CollectionTree")
          rings = ringsSgn; baseInfo = baseInfoSgn, outputs = outputsSgn; rawRings = rawRingsSgn
        elif xAODDataBkg:
          f = ROOT.TFile.Open(xAODDataBkg)
          t = ROOT.xAOD.MakeTransientTree( f, "CollectionTree")
          rings = ringsBkg; baseInfo = baseInfoBkg, outputs = outputsBkg; rawRings = rawRingsBkg
        cutMask = ElectronTAccept.getAppliedCutMsk(Ringer.Medium)
        asgPrevRinger = AsgElectronRingerSelector( "RingerEtaMu_Medium_LH_SP_v0_lhbinned" )
        asgPrevRinger.setDiscrFile("TagAndProbeDevData/RingerSelectorToolsData/data16_ringeretamu_20180217_v0/tunedDiscr_Discr_Offline_LH_DataDriven2016_Rel20pt7_Medium_SP.root")
        asgPrevRinger.setThresFile("TagAndProbeDevData/RingerSelectorToolsData/data16_ringeretamu_20180217_v0/tunedDiscr_Thres_Offline_LH_DataDriven2016_Rel20pt7_Medium_SP.root")
        asgPrevRinger.setRSMetaName("ElectronRingSetsConf")
        asgPrevRinger.setCutMask(cutMask);
        asgPrevRinger.initialize()
        asgLocalRinger = AsgElectronRingerSelector( "LocalRingerEtaMu_Medium_LH_SP_v0_lhbinned" )
        asgLocalRinger.initialize("ElectronRingSetsConf", cutMask, discrCol, thresWrapper, rConf )
        asgLH = AsgElectronLikelihoodTool('MediumLLH_DataDriven_Rel20pt7_Smooth_vTest')
        asgLH.setProperty("ConfigFile","TagAndProbeFrame/LHTunes/DataDriven/Rel20pt7/ElectronLikelihoodMediumOfflineConfig2016_Smooth.conf")
        asgLH.initialize()
        cls.runxAOD(asgPrevRinger, asgLocalRinger, asgLH, ppCol, neuralDictCol, thresCol, rings, rawRings, baseInfo, outputs, t)
      if xAODDataSgn and xAODDataBkg:
        f = ROOT.TFile.Open(xAODDataBkg)
        t = ROOT.xAOD.MakeTransientTree( f, "CollectionTree")
        cls.runxAOD(asgPrevRinger, asgLocalRinger, asgLH, ppCol, neuralDictCol, thresCol, ringsBkg, rawRingsBkg, baseInfoBkg, outputsBkg, t)
    # which operation to export
  # exportDiscrFiles


  @classmethod
  def runxAOD(cls, asgPrevRinger, asgLocalRinger, asgLH, ppCol, rawDiscrCol, thresCol, rings, rawRings, baseInfo, outputs, t):
    logger      = Logger.getModuleLogger("exportDiscrFiles", LoggingLevel.VERBOSE )
    from Gaugi import keyboard, straverse
    discrCol = []
    try:
      from libTuningTools import DiscriminatorPyWrapper
    except ImportError:
      from libTuningToolsLib import DiscriminatorPyWrapper
    for neuralDict in straverse( rawDiscrCol ):
      discr = DiscriminatorPyWrapper( "TuningTool_Discriminator"
                                    , LoggingLevel.toC( LoggingLevel.INFO )
                                    , not(int(os.environ.get('RCM_GRID_ENV',0)) or not(sys.stdout.isatty()))
                                    , neuralDict['nodes'].tolist()
                                    , neuralDict.get('trfFunc',['tansig', 'tansig'])
                                    , neuralDict['weights'].tolist()
                                    , neuralDict['bias'].tolist() )
      if neuralDict['removeOutputTansigTF']: discr.removeOutputTansigTF()
      discr.etBin = neuralDict['etBin']
      discr.etaBin = neuralDict['etaBin']
      discrCol.append(discr)
    import ROOT
    from itertools import count
    vector = ROOT.std.vector("float")
    tcount = ncount = pcount = ocount = lcount = 0.
    nevents = t.GetEntriesFast()
    etaVec = []; pileupVec = [];
    binCounts = [[0]*nEtaBins]*nEtBins
    binIdxs = [[(etBinIdx, etaBinIdx) for etaBinIdx in range(nEtaBinIdx)] for etBinIdx in range(nEtBinIdx)]
    for i in progressbar( range(nevents), nevents, logger=logger ):
      t.GetEntry(i)
      electrons = t.Electrons
      cRings = t.ElectronCaloRings
      for j, (el,cRing) in enumerate(zip(electrons,cRings)):
        et = el.caloCluster().et() * 1e-3
        eta = el.caloCluster().eta()
        pileup = asgPrevRinger.getNPrimVertices()
        if et > 15 and abs(eta) < 2.47:
          lDec = bool(asgLH.accept(el)); lcount += lDec
          lhDiscr = asgLH.getTResult().getResults()[0]
          logger.info("LH discriminant and decision: <%f,%s>", lhDiscr, lDec )
          # Get this AsgElectronRingerSelector answer
          oDec = bool(asgPrevRinger.accept(el)); ocount += oDec
          v = asgPrevRinger.getOutputSpace()
          oOutput = v[0] if len(v) else -999.
          logger.info("Previous ringer output and decision: <%f,%s>", oOutput, oDec )
          nDec = bool(asgLocalRinger.accept(el)); ncount += nDec
          v = asgLocalRinger.getOutputSpace()
          if nDec:
            etaVec.append(eta)
            pileupVec.append(pileup)
          nOutput = v[0] if len(v) else -999.
          logger.info("Ringer to be exported output and decision: <%f,%s>", nOutput, nDec )
          found = False
          for ppChain in straverse( ppCol, tree_types=(PreProc.PreProcCollection,) ):
            if ppChain.etBin[0] < et <= ppChain.etBin[1] and ppChain.etaBin[0] < abs(eta) <= ppChain.etaBin[1]:
              found = True; break
          if not found:
            logger.error("Could not find ppChain."); keyboard()
          found = False
          for discr, trings, trawrings, tbaseinfo, toutputs, binCount, binIdx in straverse( zip( discrCol, rings, rawRings
                                                                                               , baseInfo, outputs, binCounts
                                                                                               , binIdxs ) ):
            if discr.etBin[0] < et <= discr.etBin[1] and discr.etaBin[0] < abs(eta) <= discr.etaBin[1]:
              found = True; break
          if not found:
            logger.error("Could not find discr."); keyboard()
          if trings:
            ptrings = trings[npCurrent.access(oidx=binCount)]
            ptrawrings = trawrings[npCurrent.access(oidx=binCount)]
            ptbaseinfo = [b[npCurrent.access(oidx=binCount)] for b in tbaseinfo]
            ptoutput = toutputs[binCount]
            binCounts[binIdx[0]][binIdx[1]] += 1
          found = False
          for pyThres in straverse( thresCol, tree_types=(ThresholdCollection,) ):
            if pyThres.etBin[0] < et <= pyThres.etBin[1] and pyThres.etaBin[0] < abs(eta) <= pyThres.etaBin[1]:
              found = True; break
          if not found:
            logger.error("Could not find thres."); keyboard()
          rings = vector()
          cRing.exportRingsTo( rings )
          # FIXME use npCurrent
          npRings = np.concatenate([np.frombuffer( rings.data(), dtype=np.float32, count=len(rings) ),
                                   [eta,pileup]]).reshape(1,len(rings)+2)
          normRings = ppChain(npRings)
          pOutput = discr.propagate_np( normRings )
          if abs(nOutput - pOutput) > 1e-4:
            keyboard()
          pDec = pyThres.decide( pOutput, pileup ); pcount += pDec[0]
          logger.info("Python output and decision: <%f,%s>", pOutput, pDec[0] )
          tcount += 1
    logger.info('=====================')
    logger.info('LH selector eficiency: %f%%', (lcount/tcount)*100.)
    logger.info('Previous selector eficiency: %f%%', (ocount/tcount)*100.)
    logger.info('Current selector eficiency: %f%%', (ncount/tcount)*100.)
    logger.info('Python eficiency: %f%%', (pcount/tcount)*100.)
    keyboard()


  @classmethod
  def printTables(cls, confBaseNameList,
                       crossValGrid,
                       configMap):
    "Print tables for the cross-validation data."
    # TODO Improve documentation

    # We first loop over the configuration base names:
    for confIdx, confBaseName in enumerate(confBaseNameList):
      # And then on et/eta bins:
      for crossList in crossValGrid:

        print "{:-^90}".format("  Starting new Et  ")
        for crossFile in crossList:
          # Load file and then search the benchmark references with the configuration name:
          summaryInfo = load(crossFile)
          etIdx = -1
          etaIdx = -1
          for key in summaryInfo.keys():
            try:
              rawBenchmark = summaryInfo[key]['rawBenchmark']
              try:
                etIdx = rawBenchmark['signalEfficiency']['etBin']
                etaIdx = rawBenchmark['signalEfficiency']['etaBin']
              except KeyError:
                etIdx = rawBenchmark['signal_efficiency']['etBin']
                etaIdx = rawBenchmark['signal_efficiency']['etaBin']
              break
            except (KeyError, TypeError) as e:
              pass

          print "{:-^90}".format("  Eta (%d) | Et (%d)  " % (etaIdx, etIdx))

          confPdKey = confSPKey = confPfKey = None

          # Organize the names
          for key in summaryInfo.keys():
            if key == 'infoPPChain': continue
            rawBenchmark = summaryInfo[key]['rawBenchmark']
            reference = rawBenchmark['reference']
            if confBaseName in key:
              if reference == 'Pd':
                confPdKey = key
              if reference == 'Pf':
                confPfKey = key
              if reference == 'SP':
                confSPKey = key

          # Loop over each one of the cases and print ringer performance:
          print '{:^13}   {:^13}   {:^13} |   {:^13}   |  {}  '.format("Pd (%)","SP (%)","Pf (%)","cut","(ReferenceBenchmark)")
          print "{:-^90}".format("  Ringer  ")

          for keyIdx, key in enumerate([confPdKey, confSPKey, confPfKey]):

            confList = configMap[confIdx][etIdx][etaIdx]

            if confList[keyIdx] is None:
              config_str = 'config_'+str(summaryInfo[key]['infoOpBest']['neuron']).zfill(3)
            else:
              config_str = 'config_'+str(confList[0]).zfill(3)

            ringerPerf = summaryInfo[key] \
                                    [config_str] \
                                    ['summaryInfoTst']

            print '%6.3f+-%5.3f   %6.3f+-%5.3f   %6.3f+-%5.3f |   % 5.3f+-%5.3f   |  (%s) ' % (
                ringerPerf['detMean'] * 100.,   ringerPerf['detStd']  * 100.,
                ringerPerf['spMean']  * 100.,   ringerPerf['spStd']   * 100.,
                ringerPerf['faMean']  * 100.,   ringerPerf['faStd']   * 100.,
                ringerPerf['cutMean']       ,   ringerPerf['cutStd']        ,
                key+config_str.replace(', config_','Neuron: '))
            ringerPerf = summaryInfo[key] \
                                    [config_str] \
                                    ['infoOpBest']
            print '{:^13.3f}   {:^13.3f}   {:^13.3f} |   {:^ 13.3f}   |  ({}) '.format(
                ringerPerf['det'] * 100.,
                ringerPerf['sp']  * 100.,
                ringerPerf['fa']  * 100.,
                ringerPerf['cut'],
                key+config_str.replace('config_',', Neuron: '))

          print "{:-^90}".format("  Baseline  ")

          # Retrieve baseline values
          try:# treat some key changes applied
            try:# the latest key is refVal
              reference_pd = rawBenchmark['signalEfficiency']['refVal']
            except:# treat the exception using the oldest key
              reference_pd = rawBenchmark['signalEfficiency']['efficiency']
          except:
            reference_pd = rawBenchmark['signal_efficiency']['efficiency']
          try:
            try:
              reference_fa = rawBenchmark['backgroundEfficiency']['refVal']
            except:
              reference_fa = rawBenchmark['backgroundEfficiency']['efficiency']
          except:
            reference_fa = rawBenchmark['background_efficiency']['efficiency']


          reference_sp = calcSP(
                                reference_pd / 100.,
                                ( 1. - reference_fa / 100. )
                               )
          print '{:^13.3f}   {:^13.3f}   {:^13.3f} |{:@<43}'.format(
                                    reference_pd
                                    ,reference_sp * 100.
                                    ,reference_fa
                                    ,''
                                   )
          print "{:=^90}".format("")




  @classmethod
  def exportDiscrFilesToOnlineFormat(cls, summaryInfoList, **kw):
    """
    Export discriminators operating at reference benchmark list to the
    ATLAS environment using summaryInfo.

    If benchmark name on the reference list is not available at summaryInfo, an
    KeyError exception will be raised.
    """
    from Gaugi import retrieveRawDict
    refBenchCol           = kw.pop( 'refBenchCol',         None              )
    configCol             = kw.pop( 'configCol',           []                )
    maxPileupCorrection   = kw.pop( 'maxPileupCorrection', 100               )
    level                 = kw.pop( 'level'              , LoggingLevel.INFO )
    discrFilename         = kw.pop('discrFilename'       , 'Constants'       )
    thresFilename         = kw.pop('thresFilename'       , 'Thresholds'      )
    muBin                 = kw.pop('muBin'               , [-999,999]        )
    doPileupCorrection    = kw.pop('doPileupCorrection'  , False             )
    _version              = kw.pop('version'             , 2                 ) # the current athena version is 2
    _removeOutputTansigTF = kw.pop('removeOutputTansigTF', False             )



    outputDict = []

    def tolist(a):
      if isinstance(a,list): return a
      else: return a.tolist()

    # Initialize local logger
    logger      = Logger.getModuleLogger("exportDiscrFiles", logDefaultLevel = level )
    checkForUnusedVars( kw, logger.warning )

    # Treat the summaryInfoList
    if not isinstance( summaryInfoList, (list,tuple)):
      summaryInfoList = [ summaryInfoList ]
    summaryInfoList = list(traverse(summaryInfoList,simple_ret=True))
    nSummaries = len(summaryInfoList)
    if not nSummaries:
      logger.fatal("Summary dictionaries must be specified!")

    if refBenchCol is None:
      refBenchCol = summaryInfoList[0].keys()

    # Treat the reference benchmark list
    if not isinstance( refBenchCol, (list,tuple)):
      refBenchCol = [ refBenchCol ] * nSummaries

    if len(refBenchCol) == 1:
      refBenchCol = refBenchCol * nSummaries

    nRefs = len(list(traverse(refBenchCol,simple_ret=True)))

    # Make sure that the lists are the same size as the reference benchmark:
    nConfigs = len(list(traverse(configCol,simple_ret=True)))
    if nConfigs == 0:
      configCol = [None for i in range(nRefs)]
    elif nConfigs == 1:
      configCol = configCol * nSummaries
    nConfigs = len(list(traverse(configCol,simple_ret=True)))

    if nConfigs != nRefs:
      logger.fatal("Summary size is not equal to the configuration list.", ValueError)

    if nRefs == nConfigs == nSummaries:
      # If user input data without using list on the configuration, put it as a list:
      for o, idx, parent, _, _ in traverse(configCol):
        parent[idx] = [o]
      for o, idx, parent, _, _ in traverse(refBenchCol):
        parent[idx] = [o]

    configCol   = list(traverse(configCol,max_depth_dist=1,simple_ret=True))
    refBenchCol = list(traverse(refBenchCol,max_depth_dist=1,simple_ret=True))
    nConfigs = len(configCol)
    nSummary = len(refBenchCol)

    if nRefs != nConfigs != nSummary:
      logger.fatal("Number of references, configurations and summaries do not match!", ValueError)

    # Retrieve the operation:
    logger.info('Exporting discrimination info files for the following the raw Dict strategy')

    import time
    for summaryInfo, refBenchmarkList, configList in \
                        zip(summaryInfoList,
                            refBenchCol,
                            configCol,
                           ):

      if type(summaryInfo) is str:
        logger.info('Loading file "%s"...', summaryInfo)
        summaryInfo = load(summaryInfo)
      elif type(summaryInfo) is dict:
        pass
      else:
        logger.fatal("Cross-valid summary info is not string and not a dictionary.", ValueError)

      from itertools import izip, count
      for idx, refBenchmarkName, config in izip(count(), refBenchmarkList, configList):

        try:
          key = filter(lambda x: refBenchmarkName in x, summaryInfo)[0]
          refDict = summaryInfo[ key ]
        except IndexError :
          logger.fatal("Could not find reference %s in summaryInfo. Available options are: %r", refBenchmarkName, summaryInfo.keys())

        logger.info("Using Reference key: %s", key )

        ppInfo    = summaryInfo['infoPPChain']
        etBinIdx  = refDict['etBinIdx']
        etaBinIdx = refDict['etaBinIdx']

        try:
          etBin = refDict['etBin']
          etaBin = refDict['etaBin']
        except KeyError:
          self.warning("Attempting to retrieve bins from etBins/etaBins argument. This should only be needed for old summaryDicts.")
          etBin = _etBins[etBinIdx:etBinIdx+2]
          etaBin = _etaBins[etBinIdx:etBinIdx+2]


        logger.info('Dumping (<etBinIdx:%d,etaBinIdx:%d>: (%r,%r)',etBinIdx, etaBinIdx, etBin.tolist(), etaBin.tolist())

        from pprint import pprint
        # Get the best config
        info   = refDict['infoOpBest'] if config is None else \
                 refDict['config_' + str(config).zfill(3)]['infoOpBest']

        # Check if user specified parameters for exporting discriminator
        # operation information:
        sort =  info['sort']
        init =  info['init']
        # Get the threshold configuration
        pyThres = info['cut']
        # Get the first preproc object.
        pyPreProc = ppInfo['sort_'+str(sort).zfill(3)]['items'][0]
        pprint(pyPreProc)
        pyPreProc = retrieveRawDict( pyPreProc )


        if isinstance( pyThres, float ):
          doPileipCorrection=True # force to be true
          pyThres = RawThreshold( thres = pyThres
                                , etBinIdx = etBinIdx, etaBinIdx = etaBinIdx
                                , etBin = etBin, etaBin =  etaBin)
        else:
          # Get the object from the raw dict
          pyThres = retrieveRawDict( pyThres )
        if pyThres.etBin in (None,''):
          pyThres.etBin = etBin
        elif isinstance( pyThres.etBin, (list,tuple)):
          pyThres.etBin = np.array( pyThres.etBin)
        if not(np.array_equal( pyThres.etBin, etBin )):
          logger.fatal("etBin does not match for threshold! Should be %r, is %r", pyThres.etBin, etBin )
        if pyThres.etaBin in (None,''):
          pyThres.etaBin = etaBin
        elif isinstance( pyThres.etaBin, (list,tuple)):
          pyThres.etaBin = np.array( pyThres.etaBin)
        if not(np.array_equal( pyThres.etaBin, etaBin )):
          logger.fatal("etaBin does not match for threshold! Should be %r, is %r", pyThres.etaBin, etaBin )


        ### Get the threshold enumeration from the type class
        if isinstance(pyThres,RawThreshold):
          thresType = ThresholdStrategy.UniqueThreshold
          thresValues = [pyThres.thres]
          doPileupCorrection=False # force to be true
        elif isinstance(pyThres, PileupLinearCorrectionThreshold ):
          thresType = ThresholdStrategy.PileupLinearCorrectionThreshold
          doPileupCorrection=True # force to be true
          thresValues = [pyThres.slope, pyThres.intercept, pyThres.rawThres]
        else: # default
          self._logger.fatal('Threshold strategy not found...')

        ### Get the PreProc and data feature configuration
        useCaloRings = False
        useShowerShape = False
        useTrack = False

        if type(pyPreProc) is Norm1:
          ppType = PreProcStrategy.Norm1; useCaloRings=True
        elif type(pyPreProc) is TrackSimpleNorm:
          ppType = PreProcStrategy.TrackSimpleNorm; useTrack=True
        elif type(pyPreProc) is ShowerShapesSimpleNorm:
          ppType = PreProcStrategy.ShowerShapeSimpleNorm; useShowerShape=True
        elif type(pyPreProc) is ExpertNetworksSimpleNorm:
          ppType = PreProcStrategy.ExpertNetworksSimpleNorm; useCaloRings=True; useTrack=True
        elif type(pyPreProc) is ExpertNetworksShowerShapeSimpleNorm:
          ppType = PreProcStrategy.ExpertNetworksShowerShapeSimpleNorm; useCaloRings=True; useShowerShape=True
        elif type(pyPreProc) is ExpertNetworksShowerShapeAndTrackSimpleNorm:
          ppType = PreProcStrategy.ExpertNetworksShowerShapeAndTrackSimpleNorm; useCaloRings=True; useTrack=True; useShowerShape=True
        else:
          self._logger.fatal('PrepProc strategy not found...')


        # Get the discriminator
        discrDict = info['discriminator']
        removeOutputTansigTF = refDict.get('removeOutputTansigTF', _removeOutputTansigTF )

        ## Discriminator configuration
        discrData={}
        discrData['discriminator']={}
        discrData['discriminator']['type']      = [ppType]
        discrData['discriminator']['etBin']     = etBin.tolist()
        discrData['discriminator']['etaBin']    = etaBin.tolist()
        discrData['discriminator']['muBin']     = muBin
        discrData['discriminator']['nodes']     = tolist( discrDict['nodes']   )
        discrData['discriminator']['bias']      = tolist( discrDict['bias']    )
        discrData['discriminator']['weights']   = tolist( discrDict['weights'] )
        discrData['discriminator']['removeOutputTansigTF'] = removeOutputTansigTF
        discrData['threshold'] = {}
        discrData['threshold']['etBin']     = etBin.tolist()
        discrData['threshold']['etaBin']    = etaBin.tolist()
        discrData['threshold']['muBin']     = muBin
        discrData['threshold']['type']      = [thresType]
        discrData['threshold']['thresholds'] = thresValues
        discrData['metadata'] = {}
        discrData['metadata']['pileupThreshold'] = maxPileupCorrection
        discrData['metadata']['useCaloRings'] = useCaloRings
        discrData['metadata']['useTrack'] = useTrack
        discrData['metadata']['useShowerShape'] = useShowerShape
        logger.info('Network type  : ' + PreProcStrategy.tostring( ppType ) )
        logger.info('Threshold type: ' + ThresholdStrategy.tostring( thresType ) )
        logger.info('neuron = %d, sort = %d, init = %d',
                    info['neuron'],
                    info['sort'],
                    info['init'])


        from copy import copy
        outputDict.append( copy(discrData) )
      # for benchmark
    # for summay in list


    def attachToVector( l, vec ):
      vec.clear()
      for value in l: vec.push_back(value)

    def createRootParameter( type_name, name, value):
      from ROOT import TParameter
      return TParameter(type_name)(name,value)

    discrBranches = [
                     ['unsigned int', 'nodes'  , None],
                     ['unsigned int', 'type'   , None],
                     ['double'      , 'weights', None],
                     ['double'      , 'bias'   , None],
                     ['double'      , 'etBin'  , None],
                     ['double'      , 'etaBin' , None],
                     ['double'      , 'muBin'  , None],
                     ]

    thresBranches = [
                     ['double'      , 'thresholds'  , None],
                     ['double'      , 'etBin'       , None],
                     ['double'      , 'etaBin'      , None],
                     ['double'      , 'muBin'       , None],
                     ['unsigned int', 'type'        , None],
                     ]

    discrParams       = {
                      'UseCaloRings'          :useCaloRings         ,
                      'UseShowerShape'        :useShowerShape       ,
                      'UseTrack'              :useTrack             ,
                      'UseEtaVar'             :False                ,
                      'UseLumiVar'            :False                ,
                      'RemoveOutputTansigTF'  :removeOutputTansigTF ,
                      'UseNoActivationFunctionInTheLastLayer' : removeOutputTansigTF,
                      }

    thresParams       = {
                      'DoPileupCorrection'                    :doPileupCorrection   ,
                      'LumiCut'                               : maxPileupCorrection,
                      }

    from ROOT import TFile, TTree
    from ROOT import std

    ### Create the discriminator root object
    fdiscr = TFile(discrFilename+'.root', 'recreate')
    createRootParameter( 'int'   , '__version__', _version).Write()
    fdiscr.mkdir('tuning')
    fdiscr.cd('tuning')
    tdiscr = TTree('discriminators','')

    for idx, b in enumerate(discrBranches):
      b[2] = std.vector(b[0])()
      tdiscr.Branch(b[1], 'vector<%s>'%b[0] ,b[2])

    for discr in outputDict:
      for idx, b in enumerate(discrBranches):
        attachToVector( discr['discriminator'][b[1]],b[2])
      tdiscr.Fill()

    tdiscr.Write()

    ### Create the thresholds root object
    fthres = TFile(thresFilename+'.root', 'recreate')
    createRootParameter( 'int'   , '__version__', _version).Write()
    fthres.mkdir('tuning')
    fthres.cd('tuning')
    tthres = TTree('thresholds','')

    for idx, b in enumerate(thresBranches):
      b[2] = std.vector(b[0])()
      tthres.Branch(b[1], 'vector<%s>'%b[0] ,b[2])

    for discr in outputDict:
      for idx, b in enumerate(thresBranches):
        attachToVector( discr['threshold'][b[1]],b[2])
      tthres.Fill()

    tthres.Write()
    fdiscr.mkdir('metadata'); fdiscr.cd('metadata')
    for key, value in discrParams.iteritems():
      logger.info('Saving metadata %s as %s', key, value)
      createRootParameter( 'int' if type(value) is int else 'bool'   , key, value).Write()

    fthres.mkdir('metadata'); fthres.cd('metadata')
    for key, value in thresParams.iteritems():
      logger.info('Saving metadata %s as %s', key, value)
      createRootParameter( 'int' if type(value) is int else 'bool'   , key, value).Write()

    fdiscr.Close()
    fthres.Close()

    return outputDict
  # exportDiscrFilesToDict




class PerfHolder( LoggerStreamable ):
  """
  Hold the performance values and evolution for a tuned discriminator
  """

  def __init__(self, tunedDiscrData = None, tunedEvolutionData = None, decisionTaking = None, **kw ):
    LoggerStreamable.__init__(self, kw )
    if not(tunedDiscrData) and not(decisionTaking):
      self._fatal('Either tunedEvolutionData or decisionTaking must be informed.')
    self.decisionTaking       = decisionTaking
    if tunedDiscrData:
      self.roc_tst              = tunedDiscrData['summaryInfo']['roc_test']
      self.roc_operation        = tunedDiscrData['summaryInfo']['roc_operation']
    trainEvo                  = tunedEvolutionData
    def toNpArray( obj, key, d, dtype, default = []):
      """
      Set self value to a numpy array of the dict value
      """
      if ':' in key:
        key = key.split(':')
        sKey, dKey = key
      else:
        sKey, dKey = key, key
      setattr(obj, sKey, np.array( d.get(dKey, default), dtype = dtype ) )
    # end of toNpArray

    if trainEvo:
      self.epoch                = np.array( range(len(trainEvo['mse_trn'])),  dtype ='float_')
      self.nEpoch               = len(self.epoch)
      try:
        # Current schema from Fastnet core
        keyCollection = ['mse_trn' ,'mse_val' ,'mse_tst'
                        ,'bestsp_point_sp_val' ,'bestsp_point_det_val' ,'bestsp_point_fa_val' ,'bestsp_point_sp_tst' ,'bestsp_point_det_tst' ,'bestsp_point_fa_tst'
                        ,'det_point_sp_val' ,'det_point_det_val' ,'det_point_fa_val' ,'det_point_sp_tst' ,'det_point_det_tst' ,'det_point_fa_tst'
                        ,'fa_point_sp_val' ,'fa_point_det_val' ,'fa_point_fa_val' ,'fa_point_sp_tst' ,'fa_point_det_tst' ,'fa_point_fa_tst'
                        ]
        # Test if file format is the new one:
        if not 'bestsp_point_sp_val' in trainEvo: raise KeyError
        for key in keyCollection:
          toNpArray( self, key, trainEvo, 'float_' )
      except KeyError:
        # Old schemma
        from Gaugi import calcSP
        self.mse_trn                = np.array( trainEvo['mse_trn'],                                     dtype = 'float_' )
        self.mse_val                = np.array( trainEvo['mse_val'],                                     dtype = 'float_' )
        self.mse_tst                = np.array( trainEvo['mse_tst'],                                     dtype = 'float_' )

        self.bestsp_point_sp_val    = np.array( trainEvo['sp_val'],                                      dtype = 'float_' )
        self.bestsp_point_det_val   = np.array( [],                                                      dtype = 'float_' )
        self.bestsp_point_fa_val    = np.array( [],                                                      dtype = 'float_' )
        self.bestsp_point_sp_tst    = np.array( trainEvo['sp_tst'],                                      dtype = 'float_' )
        self.bestsp_point_det_tst   = np.array( trainEvo['det_tst'],                                     dtype = 'float_' )
        self.bestsp_point_fa_tst    = np.array( trainEvo['fa_tst'],                                      dtype = 'float_' )
        self.det_point_det_val      = np.array( trainEvo['det_fitted'],                                  dtype = 'float_' ) \
                                      if 'det_fitted' in trainEvo else np.array([], dtype='float_')
        self.det_point_fa_val       = np.array( trainEvo['fa_val'],                                      dtype = 'float_' )
        self.det_point_sp_val       = np.array( calcSP(self.det_point_det_val, 1-self.det_point_fa_val), dtype = 'float_' ) \
                                      if 'det_fitted' in trainEvo else np.array([], dtype='float_')
        self.det_point_sp_tst       = np.array( [],                                                      dtype = 'float_' )
        self.det_point_det_tst      = np.array( [],                                                      dtype = 'float_' )
        self.det_point_fa_tst       = np.array( [],                                                      dtype = 'float_' )
        self.fa_point_det_val       = np.array( trainEvo['det_val'],                                     dtype = 'float_' )
        self.fa_point_fa_val        = np.array( trainEvo['fa_fitted'],                                   dtype = 'float_' ) \
                                      if 'fa_fitted' in trainEvo else np.array([],  dtype='float_')
        self.fa_point_sp_val        = np.array( calcSP(self.fa_point_det_val, 1.-self.fa_point_fa_val),  dtype = 'float_' ) \
                                      if 'fa_fitted' in trainEvo else np.array([],  dtype='float_')
        self.fa_point_sp_tst        = np.array( [],                                                      dtype = 'float_' )
        self.fa_point_det_tst       = np.array( [],                                                      dtype = 'float_' )
        self.fa_point_fa_tst        = np.array( [],                                                      dtype = 'float_' )

      # Check if the roc is a raw object
      if type(self.roc_tst) is dict:
        self.roc_tst_det = np.array( self.roc_tst['pds'],              dtype = 'float_'     )
        self.roc_tst_fa  = np.array( self.roc_tst['pfs'],              dtype = 'float_'     )
        self.roc_tst_cut = np.array( self.roc_tst['thresholds'],       dtype = 'float_'     )
        self.roc_op_det  = np.array( self.roc_operation['pds'],        dtype = 'float_'     )
        self.roc_op_fa   = np.array( self.roc_operation['pfs'],        dtype = 'float_'     )
        self.roc_op_cut  = np.array( self.roc_operation['thresholds'], dtype = 'float_'     )
      else: # Old roc save strategy
        self.roc_tst_det = np.array( self.roc_tst.pdVec,        dtype = 'float_'     )
        self.roc_tst_fa  = np.array( self.roc_tst.pfVec,        dtype = 'float_'     )
        self.roc_tst_cut = np.array( self.roc_tst.cutVec,       dtype = 'float_'     )
        self.roc_op_det  = np.array( self.roc_operation.pdVec,  dtype = 'float_'     )
        self.roc_op_fa   = np.array( self.roc_operation.pfVec,  dtype = 'float_'     )
        self.roc_op_cut  = np.array( self.roc_operation.cutVec, dtype = 'float_'     )

      toNpArray( self, 'epoch_mse_stop:epoch_best_mse', trainEvo, 'int_', -1 )
      toNpArray( self, 'epoch_sp_stop:epoch_best_sp',   trainEvo, 'int_', -1 )
      toNpArray( self, 'epoch_det_stop:epoch_best_det', trainEvo, 'int_', -1 )
      toNpArray( self, 'epoch_fa_stop:epoch_best_fa',   trainEvo, 'int_', -1 )


  def getOperatingBenchmarks( self, refBenchmark, **kw ):
    """
      Returns the operating benchmark values for this tunned discriminator
    """
    ds = retrieve_kw( kw, 'ds', Dataset.Test )
    modelChooseMethod = retrieve_kw( kw, 'modelChooseMethod' )
    rocPointChooseMethod = retrieve_kw( kw, 'rocPointChooseMethod' )
    kw['method'] = rocPointChooseMethod
    if modelChooseMethod in ( ChooseOPMethod.InBoundAUC,  ChooseOPMethod.AUC ):
      kw['calcAUCMethod'] = modelChooseMethod
    if self.decisionTaking:
      # Propagate dataset to get performance in the specified dataset
      from TuningTools import CuratedSubset
      subset = CuratedSubset.fromdataset(ds)
      if ds is Dataset.Operation:
        self.decisionTaking( refBenchmark, subset, **kw )
        perf = self.decisionTaking.perf
      else:
        self.decisionTaking( refBenchmark, CuratedSubset.trnData, **kw )
        perf = self.decisionTaking.getEffPoint( refBenchmark.name + '_' + Dataset.tostring(ds)
                                              , subset = [subset, subset], makeCorr = True )
    else:
      if ds is Dataset.Test:
        pdVec = self.roc_tst_det
        pfVec = self.roc_tst_fa
        cutVec = self.roc_tst_cut
      elif ds is Dataset.Operation:
        pdVec = self.roc_op_det
        pfVec = self.roc_op_fa
        cutVec = self.roc_op_cut
      else:
        self._fatal("Cannot retrieve maximum ROC SP for dataset '%s'", ds, ValueError)
      spVec = calcSP( pdVec, 1. - pfVec )
      benchmarks = [spVec, pdVec, pfVec]
      if modelChooseMethod in ( ChooseOPMethod.InBoundAUC,  ChooseOPMethod.AUC ):
        idx, auc = refBenchmark.getOutermostPerf(benchmarks, **kw )
      else:
        idx, auc = refBenchmark.getOutermostPerf(benchmarks, **kw ), -1.
      perf = PerformancePoint( refBenchmark.name + '_' + Dataset.tostring(ds)
                                    , spVec[idx], pdVec[idx], pfVec[idx], RawThreshold( cutVec[idx] )
                                    , auc = auc )
    if hasattr(self,'mse_tst'):
      # Retrieve MSE information for the specified dataset:
      mseVec = self.mse_tst if any(self.det_point_sp_tst>np.finfo(float).eps) else self.mse_val
      if refBenchmark.reference is ReferenceBenchmark.Pd and (self.epoch_det_stop != -1):
        mseLookUp = self.epoch_det_stop
      elif refBenchmark.reference is ReferenceBenchmark.Pf and (self.epoch_fa_stop != -1):
        mseLookUp = self.epoch_fa_stop
      elif refBenchmark.reference is ReferenceBenchmark.SP and (self.epoch_sp_stop != -1):
        mseLookUp = self.epoch_sp_stop
      else:
        mseLookUp = self.epoch_mse_stop
      if ds is Dataset.Operation:
        # FIXME This is wrong, we need to weight it by the number of entries in
        # it set, since we don't have access to it, we do a simple sum instead
        mseVec += self.mse_trn
      perf.mse = mseVec[mseLookUp]
    self._verbose('Retrieved following performance: %s', perf )
    return perf

  def getGraph( self, graphType ):
    """
      Retrieve a TGraph from the discriminator tuning information.
      perfHolder.getGraph( option )
      The possible options are:
        * mse_trn
        * mse_val
        * mse_tst
        * (bestsp,det or fa)_point_sp_val
        * (bestsp,det or fa)_point_sp_tst
        * (bestsp,det or fa)_point_det_val
        * (bestsp,det or fa)_point_det_tst
        * (bestsp,det or fa)_point_fa_val
        * (bestsp,det or fa)_point_fa_tst
        * roc_val
        * roc_op
        * roc_val_cut
        * roc_op_cut
    """
    from ROOT import TGraph, gROOT, kTRUE
    gROOT.SetBatch(kTRUE)
    def epoch_graph( benchmark ):
      """
      Helper function to create graphics containing benchmarks evolution thorugh tuning epochs
      """
      return TGraph(self.nEpoch, self.epoch, benchmark) if len( benchmark ) else TGraph()
    if hasattr(self, graphType):
      if graphType.startswith('roc'):
        if graphType == 'roc_tst'               : return TGraph(len(self.roc_tst_fa), self.roc_tst_fa, self.roc_tst_det )
        elif graphType == 'roc_operation'       : return TGraph(len(self.roc_op_fa),  self.roc_op_fa,  self.roc_op_det  )
        elif graphType == 'roc_tst_cut'         : return TGraph(len(self.roc_tst_cut),
                                                                np.array(range(len(self.roc_tst_cut) ), 'float_'),
                                                                self.roc_tst_cut )
        elif graphType == 'roc_op_cut'          : return TGraph(len(self.roc_op_cut),
                                                             np.array(range(len(self.roc_op_cut) ),  'float_'),
                                                             self.roc_op_cut  )
      else:
        return epoch_graph( getattr(self, graphType) )
    else:
      self._fatal( "Unknown graphType '%s'" % graphType, ValueError )

  def saveDecisionTakingGraphs(self):
    self.decisionTaking.saveGraphs()




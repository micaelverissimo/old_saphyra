__all__ = ['TuningWrapper']

import numpy as np
from Gaugi import ( Logger, LoggingLevel, NotSet, checkForUnusedVars
                       , retrieve_kw, firstItemDepth, expandFolders )
from TuningTools.coreDef      import coreConf, npCurrent, TuningToolCores
from TuningTools.TuningJob    import ReferenceBenchmark,   ReferenceBenchmarkCollection, BatchSizeMethod
from TuningTools.dataframe.EnumCollection     import Dataset, RingerOperation
from TuningTools.DataCurator  import CuratedSubset
from TuningTools.Neural import Neural, DataTrainEvolution, Roc

def _checkSecondaryPP( data, pp=None ):
  if not (pp is NotSet or pp is None):
    if type(pp) is list:
      return [ _pp(data) for _pp in pp ]
    else:
      return pp(data)
  else:
    return data

def _checkData(data,target=None):
  if not npCurrent.check_order(data):
    raise TypeError('order of numpy data is not fortran!')
  if target is not None and not npCurrent.check_order(target):
    raise TypeError('order of numpy target is not fortran!')


class TuningWrapper(Logger):
  """
    TuningTool is the higher level representation of the TuningToolPyWrapper class.
  """

  # FIXME Create a dict with default options for FastNet and for ExMachina

  def __init__( self, dataCurator, **kw ):
    Logger.__init__( self, kw )
    self.references = ReferenceBenchmarkCollection( [] )

    coreframe = coreConf.core_framework()
    print coreframe
    self._toFrame = False
    self.dataCurator = dataCurator
    from TuningTools import DecisionMaker
    #self.decisionMaker         = DecisionMaker( self.dataCurator, kw, removeOutputTansigTF = False, pileupRef = 'nvtx' )
    self.decisionMaker         = None
    self.doPerf                = retrieve_kw( kw, 'doPerf',                True                   )
    self.batchMethod           = BatchSizeMethod.retrieve(
                               retrieve_kw( kw, 'batchMethod', BatchSizeMethod.MinClassSize \
        if not 'batchSize' in kw or kw['batchSize'] is NotSet else BatchSizeMethod.Manual         )
                                 )

    epochs                     = retrieve_kw( kw, 'epochs',                10000                  )
    maxFail                    = retrieve_kw( kw, 'maxFail',               50                     )
    self.useTstEfficiencyAsRef = retrieve_kw( kw, 'useTstEfficiencyAsRef', False                  )
    self._merged               = retrieve_kw( kw, 'merged',                False                  )
    self.expertPaths           = retrieve_kw( kw, 'expertPaths',           NotSet                 )
    self.summaryOPs            = retrieve_kw( kw, 'summaryOPs',            [None for _ in range(len(self.dataCurator.dataLocation))])
    self._doNotCacheExperts    = retrieve_kw( kw, 'doNotCachedExperts',    True                   )
    if self.expertPaths and firstItemDepth( self.expertPaths ) == 1:
      self._debug('Working with the following expert paths: %s', self.expertPaths)
      self.expertPaths = [expandFolders(p,'*.pic.gz') for p in self.expertPaths]
      self._verbose('Expanded expert paths are: %s', self.expertPaths)
    self._saveOutputs          = retrieve_kw( kw, 'saveOutputs',           False                 )
    self.sortIdx = None
    self.addPileupToOutputLayer = False
    if coreConf() is TuningToolCores.FastNet:
      seed = retrieve_kw( kw, 'seed', None )
      self._core = coreframe( level = LoggingLevel.toC(self.level), seed = seed )
      self._core.trainFcn    = retrieve_kw( kw, 'algorithmName', 'trainrp' )
      self._core.showEvo     = retrieve_kw( kw, 'showEvo',       50        )
      self._core.multiStop   = retrieve_kw( kw, 'doMultiStop',   True      )
      self.addPileupToOutputLayer = retrieve_kw( kw, 'addPileupToOutputLayer',   False      )
      if self.addPileupToOutputLayer: self.dataCurator.addPileupToOutputLayer = True
      self._core.epochs      = epochs
      self._core.maxFail     = maxFail
      # TODO Add properties
    elif coreConf() is TuningToolCores.keras:
      self._core = coreframe
      from keras import callbacks
      from keras.optimizers import RMSprop, SGD
      self.trainOptions = dict()
      self.trainOptions['optmin_alg']    = retrieve_kw( kw, 'optmin_alg'          , RMSprop(lr=0.001, rho=0.9, epsilon=1e-08) )
      self.trainOptions['costFunction']  = retrieve_kw( kw, 'binary_crossentropy' , 'mean_squared_error'    ) # 'binary_crossentropy'
      self.trainOptions['metrics']       = retrieve_kw( kw, 'metrics'             , ['accuracy', ]          )
      self.trainOptions['shuffle']       = retrieve_kw( kw, 'shuffle'             , True                    )
      self._multiStop                    = retrieve_kw( kw, 'doMultiStop'         , True                    )
      self._secondaryPP                  = retrieve_kw( kw, 'secondaryPP'         ,  None                   )

      self.trainOptions['nEpochs']       = epochs
      self.trainOptions['nFails']        = 25 #maxFail
    else:
      self._logger.fatal("TuningWrapper not implemented for %s", coreConf)


    self._use_minibatch_generator      = retrieve_kw( kw, 'use_minibatch_generator' , False      )
    self.batchSize                     = retrieve_kw( kw, 'batchSize'               ,  NotSet    )
    checkForUnusedVars(kw, self._debug )
    del kw
    # Set default empty values:
    if coreConf() is TuningToolCores.keras:
      self._emptyData  = npCurrent.fp_array([])
    elif coreConf() is TuningToolCores.FastNet:
      self._emptyData = list()
    self._emptyHandler = None
    if coreConf() is TuningToolCores.keras:
      self._emptyTarget = npCurrent.fp_array([[]]).reshape(
              npCurrent.access( pidx=1,
                                oidx=0 ) )
    elif coreConf() is TuningToolCores.FastNet:
      self._emptyTarget = None


    # Set holders:
    self._trnData    = self._emptyData
    self._valData    = self._emptyData
    self._tstData    = self._emptyData
    self._trnHandler = self._emptyHandler
    self._valHandler = self._emptyHandler
    self._tstHandler = self._emptyHandler
    self._trnTarget  = self._emptyTarget
    self._valTarget  = self._emptyTarget
    self._tstTarget  = self._emptyTarget
    self._expertNNs  = None
    self._cachedExpertNNs = []
  # TuningWrapper.__init__

  def _getExpertNNs(self, etBinIdx, etaBinIdx, sortIdx):
    if not self._cachedExpertNNs:
      raise IndexError(etBinIdx, etaBinIdx, sortIdx)
    self._expertNNs = [self._cachedExpertNNs[expertIdx][etBinIdx][etaBinIdx][sortIdx] for expertIdx in range(len(self.expertPaths)) ]
    self._info("Retrieved expert neural networks for bin (et:%d,eta:%d,sort:%d)", etBinIdx, etaBinIdx, sortIdx )

  def _cacheExpertNN( self, nnModel, expertIdx, etBinIdx, etaBinIdx, sortIdx ):
    if self._cachedExpertNNs is None:
      self._cachedExpertNNs = []
    while expertIdx >= len(self._cachedExpertNNs):
      self._cachedExpertNNs.append([])
    l = self._cachedExpertNNs[expertIdx]
    while etBinIdx >= len(l): l.append( [] )
    l = l[etBinIdx]
    while etaBinIdx >= len(l): l.append( [] )
    l = l[etaBinIdx]
    while sortIdx >= len(l): l.append( [] )
    l[sortIdx] = nnModel
    if self._doNotCacheExperts:
      baseStr = 'Retrieved expertNN with bin and sort: (expert:%d,et:%d,eta:%d,sort:%d)'
    else:
      baseStr = 'Caching expertNN with bin and sort: (expert:%d,et:%d,eta:%d,sort:%d)'
    self._debug( baseStr, expertIdx, etBinIdx, etaBinIdx, sortIdx )

  def retrieveExpert( self ):
    if not self.expertPaths:
      return
    # Remove cached NNs in case we are not caching
    if self._doNotCacheExperts: self._cachedExpertNNs = None
    # Get current tuning information from data curator:
    etBinIdx  = self.dataCurator.etBinIdx
    etaBinIdx = self.dataCurator.etaBinIdx
    sortIdx   = self.dataCurator.sort
    self._info( 'Retrieving expert neural networks for bin indexes and sort: (et:%d,eta:%d,sort:%d)'
              , etBinIdx, etaBinIdx, sortIdx )
    from copy import copy
    # Get current operation points
    summaryOPs = copy(self.summaryOPs)
    if None in summaryOPs:
      summaryOPs = [(v if v is not None else self.dataCurator.operationPoint) for v in summaryOPs]
    summaryOPs = map(RingerOperation.retrieve, summaryOPs)

    # NOTE The grid do not need to be the same, however we would need
    # to change the looping binning to consider the grids of both expert NNs
    # and avoid conflict. Since we do not want this functionality right now
    # I will implement assuming that both networks etBinIdx and etaBinIdx are
    # equivalent
    try:
      self._getExpertNNs(etBinIdx, etaBinIdx, sortIdx)
    except IndexError:
      pass
    from Gaugi import load
    for expertIdx, (expertPath, summaryOP) in enumerate(zip(self.expertPaths,summaryOPs)):
      opName = RingerOperation.tostring(summaryOP)
      for path in expertPath:
        summaryData = load( path )
        wantedKey = 'OperationPoint_%s_%s' % (opName,'SP')
        if not wantedKey in summaryData:
          self._fatal("Could not retrieve OperationPoint %s. Available operation points are:\n%r",
              wantedKey, list(set(map(lambda x: x.replace('_SP','').replace('_Pd','').replace('_Pf','').replace('OperationPoint_','')
                                     , filter(lambda x: x.startswith('OperationPoint'), summaryData.keys())))))
        opSummary = summaryData[wantedKey]
        tEtBinIdx  = opSummary['etBinIdx']
        tEtaBinIdx = opSummary['etaBinIdx']
        if ( self._doNotCacheExperts and ( tEtBinIdx != etBinIdx or tEtaBinIdx != etaBinIdx ) ):
          self._debug( "Ignoring expert configuration %s holding bin (et:%d,eta:%d)", path
                     , tEtBinIdx, tEtaBinIdx )
          continue
        # TODO use this information in assert
        tEtBin     = opSummary['etBin']
        tEtaBin    = opSummary['etaBin']
        # FIXME This is not the best approach
        hn = opSummary['infoTstBest']['neuron']
        for sortKey in summaryData['infoPPChain'].keys():
          tSortIdx = int(sortKey.replace('sort_',''))
          if self._doNotCacheExperts and tSortIdx != sortIdx: continue
          nnModel = self.__dict_to_discr( opSummary['config_%1.3i'%(hn)][sortKey]['infoOpBest']['discriminator']
                                        , 'expertNN_%d' % expertIdx, pruneLastLayer=True )
          self._cacheExpertNN( nnModel, expertIdx, tEtBinIdx, tEtaBinIdx, tSortIdx )
        if tEtBinIdx == etBinIdx and tEtaBinIdx == etaBinIdx:
          break
    self._getExpertNNs(etBinIdx, etaBinIdx, sortIdx)

  def release(self):
    """
    Release holden data, targets and handlers.
    """
    self._trnData = self._emptyData
    self._trnHandler = self._emptyHandler
    self._trnTarget = self._emptyTarget

  @property
  def batchSize(self):
    """
    External access to batchSize
    """
    if coreConf() is TuningToolCores.keras:
      return self.trainOptions.get('batchSize', None)
    elif coreConf() is TuningToolCores.FastNet:
      return self._core.batchSize

  @batchSize.setter
  def batchSize(self, val):
    """
    External access to batchSize
    """
    if val is not NotSet:
      self.batchMethod = BatchSizeMethod.Manual
      if coreConf() is TuningToolCores.keras:
        self.trainOptions['batchSize'] = val
      elif coreConf() is TuningToolCores.FastNet:
        self._core.batchSize   = val
      self._debug('Set batchSize to %d', val )

  def __batchSize(self, val):
    """
    Internal access to batchSize
    """
    if coreConf() is TuningToolCores.keras:
      self.trainOptions['batchSize'] = val
    elif coreConf() is TuningToolCores.FastNet:
      self._core.batchSize   = val
    self._debug('Set batchSize to %d', val )

  @property
  def doMultiStop(self):
    """
    External access to doMultiStop
    """
    if coreConf() is TuningToolCores.keras:
      return self._multiStop
    elif coreConf() is TuningToolCores.FastNet:
      return self._core.multiStop

  def setReferences(self, references):
    # Make sure that the references are a collection of ReferenceBenchmark
    references = ReferenceBenchmarkCollection(references)
    if len(references) == 0:
      self._fatal("Reference collection must be not empty!", ValueError)
    if coreConf() is TuningToolCores.ExMachina:
      self._info("Setting reference target to MSE.")
      if len(references) != 1:
        self._logger.error("Ignoring other references as ExMachina currently works with MSE.")
        references = references[:1]
      self.references = references
      ref = self.references[0]
      if ref.reference != ReferenceBenchmark.MSE:
        self._fatal("Tuning using MSE and reference is not MSE!")
    elif coreConf() is TuningToolCores.FastNet:
      if self.doMultiStop:
        self.references = ReferenceBenchmarkCollection( [None] * 3 )
        # This is done like this for now, to prevent adding multiple
        # references. However, this will be removed when the FastNet is
        # made compatible with multiple references
        retrievedSP = False
        retrievedPD = False
        retrievedPF = False
        for ref in references:
          if ref.reference is ReferenceBenchmark.SP:
            if not retrievedSP:
              retrievedSP = True
              self.references[0] = ref
            else:
              self._warning("Ignoring multiple Reference object: %s", ref)
          elif ref.reference is ReferenceBenchmark.Pd:
            if not retrievedPD:
              retrievedPD = True
              self.references[1] = ref
              self._core.det = self.references[1].getReference()
            else:
              self._warning("Ignoring multiple Reference object: %s", ref)
          elif ref.reference is ReferenceBenchmark.Pf:
            if not retrievedPF:
              retrievedPF = True
              self.references[2] = ref
              self._core.fa = self.references[2].getReference()
            else:
              self._warning("Ignoring multiple Reference object: %s", ref)
        self._info('Set multiStop target [Sig_Eff(%%) = %r, Bkg_Eff(%%) = %r].',
                          self._core.det * 100.,
                          self._core.fa * 100.  )
      else:
        if len(references) != 1:
          self._warning("Ignoring other references when using FastNet with MSE.")
          references = references[:1]
        self.references = references
        ref = self.references[0]
        self._info("Set single reference target to: %s", self.references[0])
        #if ref.reference != ReferenceBenchmark.MSE:
        #  self._fatal("Tuning using MSE and reference is not MSE!")

    elif coreConf() is TuningToolCores.keras:
      self.references = references
      self._info("keras will be using the following references:")
      #from TuningTools.keras_util.metrics import Efficiencies
      def addMetricToKeras( func, name, metrics ):
        from keras import metrics as metrics_module
        setattr( metrics_module, name, func )
        metrics.append( name )
      for idx, bench in enumerate(self.references):
        self._info("Added %s", bench)
      #self._historyCallback.references = references
        #effMetric = Efficiencies( bench )
        # Append functions to module as if they were part of it:
        # NOTE: This has the limitation of only being calculated for the batch size
        # NOTE: At the end of one iteration, keras calculate the performance
        # over all data (?) but using in batches
        # For some reason, it seemed not to be calculating those metrics for validation dataset.
        #addMetricToKeras( effMetric.false_alarm_probability, bench.name + '_pf',  self.trainOptions['metrics'] )
        #addMetricToKeras( effMetric.detection_probability,   bench.name + '_pd',  self.trainOptions['metrics'] )
        #addMetricToKeras( effMetric.sp_index,                bench.name + '_sp',  self.trainOptions['metrics'] )
        #addMetricToKeras( effMetric.threshold,               bench.name + '_cut', self.trainOptions['metrics'] )
        #if idx == 0:
        #  addMetricToKeras( effMetric.auc,                     'auc',               self.trainOptions['metrics'] )

  def setSortIdx(self, sort):
    if coreConf() is TuningToolCores.FastNet:
      if self.doMultiStop and self.useTstEfficiencyAsRef:
        if not len(self.references) == 3 or  \
            not self.references[0].reference == ReferenceBenchmark.SP or \
            not self.references[1].reference == ReferenceBenchmark.Pd or \
            not self.references[2].reference == ReferenceBenchmark.Pf:
          self._fatal("The tuning wrapper references are not correct!")
        self.sortIdx = sort
        self._core.det = self.references[1].getReference( ds = Dataset.Validation, sort = sort )
        self._core.fa = self.references[2].getReference( ds = Dataset.Validation, sort = sort )
        self._info('Set multiStop target [sort:%d | Sig_Eff(%%) = %r, Bkg_Eff(%%) = %r].',
                          sort,
                          self._core.det * 100.,
                          self._core.fa * 100.  )

  def trnData(self, release = False):
    if coreConf() is TuningToolCores.FastNet:
      ret =  self.__separate_patterns(self._trnData,self._trnTarget)
    elif coreConf() is TuningToolCores.keras:
      ret = self._trnData
    if release: self.release()
    return ret

  def setTrainData(self, data, target=None):
    """
      Set train dataset of the tuning method.
    """
    if self._merged:
      data_calo = data[0]
      data_track = data[1]
      self._sgnSize = data_calo[0].shape[npCurrent.odim]
      self._bkgSize = data_track[1].shape[npCurrent.odim]
      if coreConf() is TuningToolCores.keras:
        if target is None:
          data_calo, target = self.__concatenate_patterns(data_calo)
          data_track, _ = self.__concatenate_patterns(data_track)
        _checkData(data_calo, target)
        _checkData(data_track, target)
        data = [data_calo, data_track]
        self._trnData = data
        self._trnTarget = target
        #self._historyCallback.trnData = (data, target)
      elif coreConf() is TuningToolCores.FastNet:
        self._fatal( "Expert Neural Networks not implemented for FastNet core" )
    else:
      self._sgnSize = data[0].shape[npCurrent.odim]
      self._bkgSize = data[1].shape[npCurrent.odim]
      if coreConf() is TuningToolCores.keras:
        if target is None:
          data, target = self.__concatenate_patterns(data)
        _checkData(data, target)
        self._trnData = data
        self._trnTarget = target
        #self._historyCallback.trnData = (data, target)
      elif coreConf() is TuningToolCores.FastNet:
        self._trnData = data
        self._core.setTrainData( data )


  def valData(self, release = False):
    if coreConf() is TuningToolCores.keras:
      ret =  self.__separate_patterns(self._valData,self._valTarget)
    elif coreConf() is TuningToolCores.FastNet:
      ret = self._valData
    if release: self.release()
    return ret

  def setValData(self, data, target=None):
    """
      Set validation dataset of the tuning method.
    """
    if self._merged:
      data_calo = data[0]
      data_track = data[1]
      if coreConf() is TuningToolCores.keras:
        if target is None:
          data_calo, target = self.__concatenate_patterns(data_calo)
          data_track, _ = self.__concatenate_patterns(data_track)
        _checkData(data_calo, target)
        _checkData(data_track, target)
        data = [data_calo, data_track]
        self._valData = data
        self._valTarget = target
        #self._historyCallback.valData = (data, target)
      elif coreConf() is TuningToolCores.FastNet:
        self._fatal( "Expert Neural Networks not implemented for FastNet core" )
    else:
      if coreConf() is TuningToolCores.keras:
        if target is None:
          data, target = self.__concatenate_patterns(data)
        _checkData(data, target)
        self._valData = data
        self._valTarget = target
        #self._historyCallback.valData = (data, target)
      elif coreConf() is TuningToolCores.FastNet:
        self._valData = data
        self._core.setValData( data )

  def testData(self, release = False):
    if coreConf() is TuningToolCores.keras:
      ret =  self.__separate_patterns(self._tstData,self._tstTarget)
    else:
      ret = self._tstData
    if release: self.release()
    return ret


  def setTestData(self, data, target=None):
    """
      Set test dataset of the tuning method.
    """
    if self._merged:
      data_calo = data[0]
      data_track = data[1]
      if coreConf() is TuningToolCores.keras:
        if target is None:
          data_calo, target = self.__concatenate_patterns(data_calo)
          data_track, _ = self.__concatenate_patterns(data_track)
        _checkData(data_calo, target)
        _checkData(data_track, target)
        data = [data_calo, data_track]
        self._tstData = data
        self._tstTarget = target
        #self._historyCallback.tstData = (data, target)
      elif coreConf() is TuningToolCores.FastNet:
        self._fatal( "Expert Neural Networks not implemented for FastNet core" )
    else:
      if coreConf() is TuningToolCores.keras:
        if target is None:
          data, target = self.__concatenate_patterns(data)
        _checkData(data, target)
        self._tstData = data
        self._tstTarget = target
        #self._historyCallback.tstData = (data, target)
      elif coreConf() is TuningToolCores.FastNet:
        self._tstData = data
        self._core.setValData( data )

  def newff(self, nodes, funcTrans = NotSet, model = None):
    """
      Creates new feedforward neural network
    """
    self.retrieveExpert()
    self._debug('Initalizing newff...')
    print coreConf()

    if coreConf() is TuningToolCores.FastNet:
      if funcTrans is NotSet: funcTrans = ['tansig', 'tansig']
      if self.addPileupToOutputLayer: nodes[1] = nodes[1] + 1
      if self._expertNNs:
        expertNodes = sum([n['nodes'] for n in self._expertNNs])
        if nodes[0] != expertNodes[0]:
          self._fatal("Expert input total nodes do not match input dimension available on data. (%d != %d)"%(nodes[0],expertNodes[0]))
        hiddenNodes = expertNodes[1]
        nodes = [nodes[0], int(hiddenNodes)] + nodes[1:]
        funcTrans = [funcTrans[0], 'tansig'] + funcTrans[1:]
        weights = npCurrent.zeros((nodes[0], hiddenNodes))
        frozen = npCurrent.ones((nodes[0], hiddenNodes))
        bias = npCurrent.zeros((hiddenNodes,))
        dim = 0; node = 0;
        for nn in self._expertNNs:
          w = nn['weights']; b = nn['bias']; n = nn['nodes']
          diagMat = w[:n[0]*n[1]].reshape((n[0],n[1]), order='F')
          weights[dim:dim+n[0],node:node+n[1]] = diagMat
          frozen[dim:dim+n[0],node:node+n[1]] = 0
          bias[node:node+n[1]] = b[:n[1]]
          dim += n[0]; node += n[1]
        self._core.fusionff( nodes, np.reshape( weights, (nodes[0]*nodes[1],), order='F').tolist()
                           , np.reshape( frozen, (nodes[0]*nodes[1],), order='F').astype(np.int32).tolist()
                           , bias.tolist(), funcTrans, self._core.trainFcn )
      elif not self._core.newff(nodes, funcTrans, self._core.trainFcn):
        self._fatal("Couldn't allocate new feed-forward!")
      if self.addPileupToOutputLayer: self._core.singletonInputNode( nodes[1] - 1, nodes[0] - 1 )

    elif coreConf() is TuningToolCores.keras:

      from keras.models import Sequential
      from keras.layers.core import Dense, Dropout, Activation
      if not model:
        self._logger.warning('Using default model struture')
        model = Sequential()
        model.add( Dense( nodes[0]
                        , input_dim=nodes[0]
                        , init='identity'
                        , trainable=False
                        , name='dense_1' ) )
        model.add( Activation('linear') )
        model.add( Dense( nodes[1]
                        , input_dim=nodes[0]
                        , init='uniform'
                        , name='dense_2' ) )
        model.add( Activation('tanh') )
        model.add( Dense( nodes[2], init='uniform', name='dense_3' ) )
        model.add( Activation('tanh') )

      model.compile( loss=self.trainOptions['costFunction']
                   , optimizer = self.trainOptions['optmin_alg']
                   , metrics = self.trainOptions['metrics'] )
      self._model = model


  def train_c(self):
    """
      Train feedforward neural network
    """
    mini_batch_gen=64

    self.setSortIdx( self.dataCurator.sort )
    from copy import deepcopy
    # Holder of the discriminators:
    tunedDiscrList = []
    tuningInfo = {}

    # Set batch size:
    if self.batchMethod is BatchSizeMethod.MinClassSize:
      self.__batchSize( self._bkgSize if self._sgnSize > self._bkgSize else self._sgnSize )
    elif self.batchMethod is BatchSizeMethod.HalfSizeSignalClass:
      self.__batchSize( self._sgnSize // 2 )
    elif self.batchMethod is BatchSizeMethod.OneSample:
      self.__batchSize( 1 )

    rawDictTempl = { 'discriminator' : None,
                     'benchmark' : None }

    if coreConf() is TuningToolCores.keras:
      # setting early stopping and save the best callback

      if self._use_minibatch_generator:
        from TuningTools.keras_util.mini_batch import MiniBatchGenerator
        self._logger.info('Using data generator...')
        trnGenerator = MiniBatchGenerator( self._trnData, self._trnTarget, mini_batch_gen, self._secondaryPP, self.trainOptions['shuffle'])
        valGenerator = MiniBatchGenerator( self._valData, self._valTarget, mini_batch_gen, self._secondaryPP, self.trainOptions['shuffle'])
        from TuningTools.keras_util.callbacks import EarlyStopping
        self._earlyStopping = EarlyStopping( patience = self.trainOptions['nFails'],save_the_best=True,
                                             val_generator = valGenerator, level=self._level )
        history = self._model.fit_generator( generator = trnGenerator
                                           , validation_data = valGenerator
                                           , callbacks       = [self._earlyStopping]
                                           , verbose         = 1 if self._level is LoggingLevel.VERBOSE else 0
                                           , epochs          = self.trainOptions['nEpochs']
                                           )

      else:
        from TuningTools.keras_util.callbacks import EarlyStopping
        self._earlyStopping = EarlyStopping( patience = self.trainOptions['nFails'],save_the_best=True, level=self._level )
        history = self._model.fit( _checkSecondaryPP(self._trnData, self._secondaryPP)
                               , self._trnTarget
                               , validation_data = ( _checkSecondaryPP(self._valData,self._secondaryPP) , self._valTarget )
                               , epochs          = self.trainOptions['nEpochs']
                               , batch_size      = self.batchSize
                               , callbacks       = [self._earlyStopping]
                               , verbose         = 1 if self._level is LoggingLevel.VERBOSE else 0
                               , shuffle         = self.trainOptions['shuffle']
                               )

      # Retrieve raw network
      rawDictTempl['discriminator'] = self.__discr_to_dict( self._model )
      rawDictTempl['benchmark'] = self.references[0]
      tunedDiscrList.append( deepcopy( rawDictTempl ) )
      tuningInfo = DataTrainEvolution( history ).toRawObj()



    elif coreConf() is TuningToolCores.FastNet:
      self._debug('executing train_c')
      [discriminatorPyWrapperList, trainDataPyWrapperList] = self._core.train_c()
      self._debug('finished train_c')
      # Transform model tolist of  dict

      if self.doMultiStop:
        for idx, discr in enumerate( discriminatorPyWrapperList ):
          rawDictTempl['discriminator'] = self.__discr_to_dict( discr )
          rawDictTempl['benchmark'] = self.references[idx]
          # FIXME This will need to be improved if set to tune for multiple
          # Pd and Pf values.
          tunedDiscrList.append( deepcopy( rawDictTempl ) )
      else:
        rawDictTempl['discriminator'] = self.__discr_to_dict( discriminatorPyWrapperList[0] )
        rawDictTempl['benchmark'] = self.references[0]
        if self.useTstEfficiencyAsRef and self.sortIdx is not None:
          rawDictTempl['sortIdx'] = self.sortIdx
        tunedDiscrList.append( deepcopy( rawDictTempl ) )
      tuningInfo = DataTrainEvolution( trainDataPyWrapperList ).toRawObj()
      # TODO
    # cores

    # Retrieve performance:
    for idx, tunedDiscrDict in enumerate(tunedDiscrList):
      discr = tunedDiscrDict['discriminator']
      if self.doPerf:
        self._debug('Retrieving performance.')

        if coreConf() is TuningToolCores.keras:
          # propagate inputs:
          import json
          from keras.models import model_from_json
          model = model_from_json( json.dumps(discr['model'], separators=(',', ':'))  )
          model.set_weights( discr['weights'] )

          if self._use_minibatch_generator:
            from TuningTools.keras_util.mini_batch import MiniBatchGenerator
            trnGenerator = MiniBatchGenerator( self._trnData, self._trnTarget, mini_batch_gen, self._secondaryPP, self.trainOptions['shuffle'])
            trnOutput = model.predict_generator(trnGenerator)
            valGenerator = MiniBatchGenerator( self._valData, self._valTarget, mini_batch_gen, self._secondaryPP, self.trainOptions['shuffle'])
            valOutput = model.predict_generator(valGenerator)
            if self._tstData:
              tstGenerator = MiniBatchGenerator( self._valData, self._valTarget, mini_batch_gen, self._secondaryPP, self.trainOptions['shuffle'])
              tstOutput = model.predict_generator(tstGenerator)
            else:
              tstOutput = npCurrent.fp_array([])

          else:
            trnOutput = model.predict(_checkSecondaryPP(self._trnData,self._secondaryPP),batch_size=5000)
            valOutput = model.predict(_checkSecondaryPP(self._valData,self._secondaryPP),batch_size=5000)
            tstOutput = model.predict(_checkSecondaryPP(self._tstData,self._secondaryPP),batch_size=5000) \
                                          if self._tstData else npCurrent.fp_array([])

          try:
            allOutput = np.concatenate([trnOutput,valOutput,tstOutput] )
            allTarget = np.concatenate([self._trnTarget,self._valTarget, self._tstTarget] )
          except ValueError:
            allOutput = np.concatenate([trnOutput,valOutput] )
            allTarget = np.concatenate([self._trnTarget,self._valTarget] )

          # Retrieve Rocs:
          opRoc = Roc( self._earlyStopping.roc(allOutput, allTarget,0.01) )
          if self._tstData: tstRoc = Roc( self._earlyStopping.roc(tstOutput, self._tstTarget) )
          else: tstRoc = Roc( self._earlyStopping.roc(valOutput, self._valTarget) )

        elif coreConf() is TuningToolCores.FastNet:
          perfList = self._core.valid_c( discriminatorPyWrapperList[idx] )
          tstRoc = Roc( perfList[0] )
          opRoc = Roc( perfList[1] )
          #trnRoc( perfList[0] )
        # Add rocs to output information

        # TODO Change this to raw object
        tunedDiscrDict['summaryInfo'] = { 'roc_operation' : opRoc.toRawObj(),
                                          'roc_test'      : tstRoc.toRawObj(),
                                          }
        if self._saveOutputs:
          tunedDiscrDict['summaryInfo']['trnOutput'] = [ npCurrent.fp_array( ar ) for ar in \
              ([perfList[2],perfList[3]] if coreConf() is TuningToolCores.FastNet else trnOutput) ]
          tunedDiscrDict['summaryInfo']['valOutput'] = [ npCurrent.fp_array( ar ) for ar in \
              ([perfList[4],perfList[5]] if coreConf() is TuningToolCores.FastNet else valOutput) ]
          trnOut = tunedDiscrDict['summaryInfo']['trnOutput']
          valOut = tunedDiscrDict['summaryInfo']['valOutput']


        for ref in self.references:
          if coreConf() is TuningToolCores.FastNet:
            # FastNet won't loop on this, this is just looping for keras right now
            ref = tunedDiscrDict['benchmark']

          if idx == 0 and self.decisionMaker:
            from ROOT import TFile, TGraph, TH1F
            f = TFile( "dump.root" ,'recreate')
            mse_trn = np.array(tuningInfo['mse_trn'], dtype='float64'); epochs = np.arange(len(mse_trn), dtype='float64')
            mseGraphTrn = TGraph(len(mse_trn)-1, epochs, mse_trn)
            mseGraphTrn.Write( 'mse_trn')
            mse_val = np.array(tuningInfo['mse_val'], dtype='float64')
            mseGraphTrn = TGraph(len(mse_val)-1, epochs, mse_val)
            mseGraphTrn.Write( 'mse_val')
            pfs = np.array(opRoc.pfs, dtype='float64'); pds = np.array(opRoc.pds, dtype='float64')
            rocGraphOp = TGraph(len(opRoc.pds)-1, pfs, pds)
            rocGraphOp.Write( "rocGraphOp" )
            pfs = np.array(tstRoc.pfs,dtype='float64'); pds = np.array(tstRoc.pds,dtype='float64')
            rocGraphTst = TGraph(len(tstRoc.pds)-1, pfs, pds)
            rocGraphOp.Write( "rocGraphTst" )
            if self._saveOutputs:
              title = 'SgnTrnData NN Output'
              sgnTH1 = TH1F( title, title, 100, -1., 1. )
              for p in trnOut[0]: sgnTH1.Fill( p )
              sgnTH1.Write( 'signalOutputs_trnData' )
              title = 'BkgTrnData NN Output'
              bkgTH1 = TH1F( title, title, 100, -1., 1. )
              for p in trnOut[1]: bkgTH1.Fill( p )
              bkgTH1.Write( 'backgroundOutputs_trnData' )
              title = 'SgnTstData NN Output'
              sgnTH1 = TH1F( title, title, 100, -1., 1. )
              for p in valOut[0]: sgnTH1.Fill( p )
              sgnTH1.Write( 'signalOutputs_tstData' )
              title = 'BkgTstData NN Output'
              bkgTH1 = TH1F( title, title, 100, -1., 1. )
              for p in valOut[1]: bkgTH1.Fill( p )
              bkgTH1.Write( 'backgroundOutputs_tstData' )
            #try:
            decisionTaking = self.decisionMaker( discr )
            decisionTaking( ref, CuratedSubset.trnData, neuron = 10, sort = 0, init = 0 )
            s = CuratedSubset.fromdataset(Dataset.Test)
            tstPointCorr = decisionTaking.getEffPoint( ref.name + '_Test' , subset = [s, s], makeCorr = True )
            decisionTaking.saveGraphs()
            decisionTaking( ref, CuratedSubset.opData, neuron = 10, sort = 0, init = 1 )
            opPointCorr = decisionTaking.perf
            decisionTaking.saveGraphs()
            #except Exception, e:
            #  self.decisionMaker = None
            #  self._error('%s', e )
            f.Close()

          # Print information:
          tstPoint = tstRoc.retrieve( ref )
          self._info( 'Test (%s): sp = %f, pd = %f, pf = %f, thres = %r'
                    , ref.name
                    , tstPoint.sp_value
                    , tstPoint.pd_value
                    , tstPoint.pf_value
                    , tstPoint.thres_value )
          if idx == 0 and self.decisionMaker: self._info( '%s', tstPointCorr )
          opPoint = opRoc.retrieve( ref )
          self._info( 'Operation (%s): sp = %f, pd = %f, pf = %f, thres = %r'
                    , ref.name
                    , opPoint.sp_value
                    , opPoint.pd_value
                    , opPoint.pf_value
                    , opPoint.thres_value )
          if idx == 0 and self.decisionMaker: self._info( '%s', opPointCorr )


          if coreConf() is TuningToolCores.FastNet:
            break

    self._debug("Finished train_c on python side.")

    return tunedDiscrList, tuningInfo
  # end of train_c

  def trainC_Exp( self ):
    """
      Train expert feedforward neural network
    """
    self.setSortIdx( self.dataCurator.sort )
    if coreConf() is TuningToolCores.ExMachina:
      self._fatal( "Expert Neural Networks not implemented for ExMachina" )
    elif coreConf() is TuningToolCores.FastNet:
      self._fatal( "Expert Neural Networks not implemented for FastNet" )
    elif coreConf() is TuningToolCores.keras:
      from copy import deepcopy

      # Set batch size:
      if self.batchMethod is BatchSizeMethod.MinClassSize:
        self.__batchSize( self._bkgSize if self._sgnSize > self._bkgSize else self._sgnSize )
      elif self.batchMethod is BatchSizeMethod.HalfSizeSignalClass:
        self.__batchSize( self._sgnSize // 2 )
      elif self.batchMethod is BatchSizeMethod.OneSample:
        self.__batchSize( 1 )

      references = ['SP','Pd','Pf']

      # Holder of the discriminators:
      tunedDiscrList = []
      tuningInfo = {}

      for idx, ref in enumerate(references):
        rawDictTempl = { 'discriminator' : None,
                         'benchmark' : None }

        history = self._model[ref].fit( self._trnData
                                      , self._trnTarget
                                      , epochs          = self.trainOptions['nEpochs']
                                      , batch_size      = self.batchSize
                                      , callbacks       = [self._historyCallback, self._earlyStopping]
                                      #, callbacks       = [self._earlyStopping]
                                      , verbose         = 0
                                      , validation_data = ( self._valData , self._valTarget )
                                      , shuffle         = self.trainOptions['shuffle']
                                      )
        # Retrieve raw network
        rawDictTempl['discriminator'] = self.__expDiscr_to_dict( self._model[ref] )
        rawDictTempl['benchmark'] = self.references[idx]
        tunedDiscrList.append( deepcopy( rawDictTempl ) )
        tuningInfo[ref] = DataTrainEvolution( history ).toRawObj()

        try:
          from sklearn.metrics import roc_curve
        except ImportError:
          # FIXME Can use previous function that we used here as an alternative
          raise ImportError("sklearn is not available, please install it.")

        # Retrieve performance:
        for idx, tunedDiscrDict in enumerate(tunedDiscrList):
          discr = tunedDiscrDict['discriminator']
          if self.doPerf:
            self._debug('Retrieving performance for %s networks.'%(ref))
            # propagate inputs:
            trnOutput = self._model[ref].predict(self._trnData)
            valOutput = self._model[ref].predict(self._valData)
            tstOutput = self._model[ref].predict(self._tstData) if self._tstData else npCurrent.fp_array([])
            try:
              allOutput = np.concatenate([trnOutput,valOutput,tstOutput] )
              allTarget = np.concatenate([self._trnTarget,self._valTarget, self._tstTarget] )
            except ValueError:
              allOutput = np.concatenate([trnOutput,valOutput] )
              allTarget = np.concatenate([self._trnTarget,self._valTarget] )
            # Retrieve Rocs:
            opRoc = Roc( allOutput, allTarget )
            if self._tstData: tstRoc = Roc( tstOutput, self._tstTarget )
            else: tstRoc = Roc( valOutput, self._valTarget )
            # Add rocs to output information
            # TODO Change this to raw object
            tunedDiscrDict['summaryInfo'] = { 'roc_operation' : opRoc.toRawObj(),
                                              'roc_test' : tstRoc.toRawObj() }

            for ref2 in self.references:
              opPoint = opRoc.retrieve( ref2 )
              tstPoint = tstRoc.retrieve( ref2 )
              # Print information:
              self._info( '%s NETWORKS Operation (%s): sp = %f, pd = %f, pf = %f, thres = %f'
                        , ref
                        , ref2.name
                        , opPoint.sp_value
                        , opPoint.pd_value
                        , opPoint.pf_value
                        , opPoint.thres_value )
              self._info( '%s NETWORKS Test (%s): sp = %f, pd = %f, pf = %f, thres = %f'
                        , ref
                        , ref2.name
                        , tstPoint.sp_value
                        , tstPoint.pd_value
                        , tstPoint.pf_value
                        , tstPoint.thres_value )
        self._info("Finished trainC_Exp for %s networks."%(ref))

    self._debug("Finished trainC_Exp on python side.")

    return tunedDiscrList, tuningInfo
  # end of trainC_Exp

  def __discr_to_dict(self, model):
    """
    Transform discriminators to dictionary
    """
    if coreConf() is TuningToolCores.keras:
      import json
      discrDict = {
                    'model':  json.loads(model.to_json()),
                    'weights': model.get_weights(),
                  }

    elif coreConf() is TuningToolCores.FastNet:
      n = []; w = []; b = [];
      for l in range( model.getNumLayers() ):
        n.append( model.getNumNodes(l) )
      for l in range( len(n) - 1 ):
        for j in range( n[l+1] ):
          for k in range( n[l] ):
            w.append( model.getWeight(l,j,k) )
          b.append( model.getBias(l,j) )
      discrDict = {
                    'nodes':   npCurrent.int_array(n),
                    'weights': npCurrent.fp_array(w),
                    'bias':    npCurrent.fp_array(b)
                  }
    discrDict['numberOfFusedDatasets'] = len(self.dataCurator.dataLocation)
    self._debug('Extracted discriminator to raw dictionary.')
    return discrDict

  def __dict_to_discr( self, discrDict, nnName=None, pruneLastLayer=True ):
    """
    Transform dictionaries of networks into discriminators.
    """
    if coreConf() is TuningToolCores.keras:
      from keras.models import model_from_json
      import json
      model = model_from_json( json.dumps(discrDict['model'], separators=(',', ':'))  )
      model.set_weights( discrDict['weights'] )
      return model
    elif coreConf() is TuningToolCores.FastNet:
      # TODO Implement a class to encapsulate this
      return discrDict

  def __expDiscr_to_dict( self, model ):
    """
    Transform expert discriminators to dictionary
    """
    if coreConf() is TuningToolCores.keras:
      ow, ob = model.get_layer( name='merge_dense_2' ).get_weights()
      hw, hb = model.get_layer( name='merge_dense_1' ).get_weights()
      chw, chb = model.get_layer( name='calo_dense_2' ).get_weights()
      thw, thb = model.get_layer( name='track_dense_2' ).get_weights()
      discrDict = {
                    'nodes':   [[chw.shape[0], thw.shape[0]], [chw.shape[1], thw.shape[1]], hw.shape[0], hw.shape[1], ow.shape[1]],
                    'weights': {
                                'output_layer':         ow,
                                'merged_hidden_layer':  hw,
                                'calo_layer':           chw,
                                'track_layer':          thw
                               },
                    'bias':    {
                                'output_layer':         ob,
                                'merged_hidden_layer':  hb,
                                'calo_layer':           chb,
                                'track_layer':          thb
                               }
                  }
    self._debug('Extracted discriminator to raw dictionary.')
    return discrDict


  def __concatenate_patterns(self, patterns):
    if type(patterns) not in (list,tuple):
      self._fatal('Input must be a tuple or list')
    pSize = [pat.shape[npCurrent.odim] for pat in patterns]
    target = npCurrent.fp_ones(npCurrent.shape(npat=1,nobs=np.sum(pSize)))
    # FIXME Could I use flag_ones?
    target[npCurrent.access(pidx=0,oidx=slice(pSize[0],None))] = -1.
    data = npCurrent.fix_fp_array( np.concatenate(patterns,axis=npCurrent.odim) )
    return data, target


  # FIXME This is not work when I call the undo preproc function.
  # The target is None for some reason...
  def __separate_patterns(self, data, target):
    patterns = list()
    classTargets = [1., -1.] # np.unique(target).tolist()
    for idx, classTarget in enumerate(classTargets):
      patterns.append( data[ npCurrent.access( pidx=':', oidx=np.where(target==classTarget)[0]) ] )
      self._debug('Separated pattern %d shape is %r', idx, patterns[idx].shape)
    return patterns







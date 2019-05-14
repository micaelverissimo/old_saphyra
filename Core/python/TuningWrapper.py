__all__ = ['TuningWrapper']

import numpy as np
from Gaugi import ( Logger, LoggingLevel, NotSet, checkForUnusedVars
                       , retrieve_kw, firstItemDepth, expandFolders )
from Gaugi.messenger.macros import *
from TuningTools.coreDef      import coreConf, npCurrent, TuningToolCores
from TuningTools.TuningJob    import ReferenceBenchmark,   ReferenceBenchmarkCollection, BatchSizeMethod
from TuningTools.dataframe.EnumCollection     import Dataset, RingerOperation
from TuningTools.DataCurator  import CuratedSubset
from TuningTools.Neural import Neural, DataTrainEvolution, Roc

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
    self.dataCurator = dataCurator
    
    self._level                = retrieve_kw( kw, 'level',          LoggingLevel.INFO               )
    epochs                     = retrieve_kw( kw, 'epochs',                 10000                   )
    maxFail                    = retrieve_kw( kw, 'maxFail',                50                      )
    self.doPerf                = retrieve_kw( kw, 'doPerf',                 True                    )

    self.useTstEfficiencyAsRef = retrieve_kw( kw, 'useTstEfficiencyAsRef',  False                   )
    self._saveOutputs          = retrieve_kw( kw, 'saveOutputs',            False                   )
    self.summaryOPs            = retrieve_kw( kw, 'summaryOPs',            [None for _ in range(len(self.dataCurator.dataLocation))])
    
    self.batchMethod           = BatchSizeMethod.retrieve( retrieve_kw( kw, 'batchMethod', BatchSizeMethod.MinClassSize \
                                                           if not 'batchSize' in kw or kw['batchSize'] is NotSet else 
                                                           BatchSizeMethod.Manual) )
    self._merged = retrieve_kw( kw, 'merged', False)
    showEvo  = retrieve_kw( kw, 'showEvo',       50 )
   
    if coreConf() is TuningToolCores.FastNet:
      seed = retrieve_kw( kw, 'seed', None )
      self._core = coreframe( level = LoggingLevel.toC(self._level),seed = seed )
      self._core.trainFcn           = retrieve_kw( kw, 'optmin_alg' , 'trainrp' )
      self._core.showEvo            = showEvo
      self._core.multiStop          = retrieve_kw( kw, 'doMultiStop',   True      )
      self.addPileupToOutputLayer   = retrieve_kw( kw, 'addPileupToOutputLayer',   False      )
      self._core.epochs             = epochs
      self._core.maxFail            = maxFail
      if self.addPileupToOutputLayer: self.dataCurator.addPileupToOutputLayer = True



    
    # TODO Add properties
    elif coreConf() is TuningToolCores.keras:
      from keras.optimizers import RMSprop, SGD
      self._core = coreframe( optmin_alg    = retrieve_kw( kw, 'optmin_alg' , RMSprop(lr=0.001, rho=0.9, epsilon=1e-08) ),
                              secondaryPP   = retrieve_kw( kw, 'secondaryPP'          ,  None                           ),
                              costFunction  = retrieve_kw( kw, 'costFunction'         , 'mean_squared_error'            ), # 'binary_crossentropy'
                              metrics       = retrieve_kw( kw, 'metrics'              , ['accuracy', ]                  ),
                              shuffle       = retrieve_kw( kw, 'shuffle'              , True                            ),
                              multiStop     = retrieve_kw( kw, 'doMultiStop'          , True                            ),
                              epochs        = epochs,
                              nFails        = 25, # maxFail
                              showEvo       = showEvo,
                              level         = self._level,
                              
                              )
    else:
      MSG_FATAL(self, "TuningWrapper not implemented for %s", coreConf)

    self.batchSize             = retrieve_kw( kw, 'batchSize',              NotSet                  )
    checkForUnusedVars(kw, self._warning )
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
    self.sortIdx = None
    self.addPileupToOutputLayer = False

 
  # TuningWrapper.__init__




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
      return self._core.batchSize
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
        self._core.batchSize = val
      elif coreConf() is TuningToolCores.FastNet:
        self._core.batchSize   = val
      MSG_DEBUG(self, 'Set batchSize to %d', val )


  def __batchSize(self, val):
    """
    Internal access to batchSize
    """
    if coreConf() is TuningToolCores.keras:
      self._core.batchSize = val
    elif coreConf() is TuningToolCores.FastNet:
      self._core.batchSize   = val
    MSG_DEBUG(self, 'Set batchSize to %d', val )

  @property
  def doMultiStop(self):
    """
    External access to doMultiStop
    """
    if coreConf() is TuningToolCores.keras:
      return False
    elif coreConf() is TuningToolCores.FastNet:
      return self._core.multiStop


  def setReferences(self, references):
    # Make sure that the references are a collection of ReferenceBenchmark
    references = ReferenceBenchmarkCollection(references)
    if len(references) == 0:
      MSG_FATAL(self, "Reference collection must be not empty!", ValueError)
    
    if coreConf() is TuningToolCores.FastNet:
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
              MSG_WARNING(self, "Ignoring multiple Reference object: %s", ref)
          elif ref.reference is ReferenceBenchmark.Pd:
            if not retrievedPD:
              retrievedPD = True
              self.references[1] = ref
              self._core.det = self.references[1].getReference()
            else:
              MSG_WARNING(self, "Ignoring multiple Reference object: %s", ref)
          elif ref.reference is ReferenceBenchmark.Pf:
            if not retrievedPF:
              retrievedPF = True
              self.references[2] = ref
              self._core.fa = self.references[2].getReference()
            else:
              MSG_WARNING(self, "Ignoring multiple Reference object: %s", ref)
        MSG_INFO(self, 'Set multiStop target [Sig_Eff(%%) = %r, Bkg_Eff(%%) = %r].',
                        self._core.det * 100.,
                        self._core.fa * 100.  )
      else:
        if len(references) != 1:
          MSG_INFO(self, "Ignoring other references when using FastNet with MSE.")
          references = references[:1]
        self.references = references
        ref = self.references[0]
        MSG_INFO(self, "Set single reference target to: %s", self.references[0])


    elif coreConf() is TuningToolCores.keras:
      self.references = references



  def setSortIdx(self, sort):

    if coreConf() is TuningToolCores.FastNet:
      if self.doMultiStop and self.useTstEfficiencyAsRef:
        if not len(self.references) == 3 or  \
            not self.references[0].reference == ReferenceBenchmark.SP or \
            not self.references[1].reference == ReferenceBenchmark.Pd or \
            not self.references[2].reference == ReferenceBenchmark.Pf:
          MSG_FATAL(self, "The tuning wrapper references are not correct!")
        self.sortIdx = sort
        self._core.det = self.references[1].getReference( ds = Dataset.Validation, sort = sort )
        self._core.fa = self.references[2].getReference( ds = Dataset.Validation, sort = sort )
        MSG_INFO(self, 'Set multiStop target [sort:%d | Sig_Eff(%%) = %r, Bkg_Eff(%%) = %r].',
                          sort,
                          self._core.det * 100.,
                          self._core.fa * 100.  )






  def trnData(self, release = False):
    if coreConf() is TuningToolCores.keras:
      ret = [self.__separete_patterns(ds,self._trnTarget) for ds in self._trnData] if self._merged else \
             self.__separete_patterns(self._trnData, self._trnTarget)
    else:
      ret = self._trnData
    if release: self.release()
    return ret


  def setTrainData(self, data, target=None):
    """
      Set test dataset of the tuning method.
    """
    if self._merged:
      if coreConf() is TuningToolCores.keras:
        self._trnData = list()
        for pat in data:
          if target is None:
            ds, target = self.__concatenate_patterns(pat)
          else:
            ds, _ = self.__concatenate_patterns(pat)
          _checkData(ds, target)
          self._trnData.append(ds)
        self._trnTarget = target
      elif coreConf() is TuningToolCores.FastNet:
        MSG_FATAL(self,  "Expert Neural Networks not implemented for FastNet core" )
    else:
      if coreConf() is TuningToolCores.keras:
        if target is None:
          data, target = self.__concatenate_patterns(data)
        _checkData(data, target)
        self._trnData = data
        self._trnTarget = target
      elif coreConf() is TuningToolCores.FastNet:
        self._trnData = data
        self._core.setTrainData( data )


  def valData(self, release = False):
    if coreConf() is TuningToolCores.keras:
      ret = [self.__separete_patterns(ds,self._valTarget) for ds in self._valData] if self._merged else \
             self.__separete_patterns(self._valData, self._valTarget)
    else:
      ret = self._valData
    if release: self.release()
    return ret


  def setValData(self, data, target=None):
    """
      Set test dataset of the tuning method.
    """
    if self._merged:
      if coreConf() is TuningToolCores.keras:
        self._valData = list()
        for pat in data:
          if target is None:
            ds, target = self.__concatenate_patterns(pat)
          else:
            ds, _ = self.__concatenate_patterns(pat)
          _checkData(ds, target)
          self._valData.append(ds)
        self._valTarget = target
      elif coreConf() is TuningToolCores.FastNet:
        MSG_FATAL(self,  "Expert Neural Networks not implemented for FastNet core" )
    else:
      if coreConf() is TuningToolCores.keras:
        if target is None:
          data, target = self.__concatenate_patterns(data)
        _checkData(data, target)
        self._valData = data
        self._valTarget = target
      elif coreConf() is TuningToolCores.FastNet:
        self._valData = data
        self._core.setValData( data )



  def testData(self, release = False):
    if coreConf() is TuningToolCores.keras:
      ret = [self.__separete_patterns(ds,self._tstTarget) for ds in self._tstData] if self._merged else \
             self.__separete_patterns(self._tstData, self._tstTarget)
    else:
      ret = self._tstData
    if release: self.release()
    return ret


  def setTestData(self, data, target=None):
    """
      Set test dataset of the tuning method.
    """
    if self._merged:
      if coreConf() is TuningToolCores.keras:
        self._tstData = list()
        for pat in data:
          if target is None:
            ds, target = self.__concatenate_patterns(pat)
          else:
            ds, _ = self.__concatenate_patterns(pat)
          _checkData(ds, target)
          self._tstData.append(ds)
        self._tstTarget = target
      elif coreConf() is TuningToolCores.FastNet:
        MSG_FATAL(self,  "Expert Neural Networks not implemented for FastNet core" )
    else:
      if coreConf() is TuningToolCores.keras:
        if target is None:
          data, target = self.__concatenate_patterns(data)
        _checkData(data, target)
        self._tstData = data
        self._tstTarget = target
      elif coreConf() is TuningToolCores.FastNet:
        self._tstData = data
        self._core.setTstData( data )




  def newff(self, nodes, funcTrans = NotSet, model = None):
    """
      Creates new feedforward neural network
    """
    MSG_DEBUG(self, 'Initalizing newff...')
    if coreConf() is TuningToolCores.FastNet:
      if funcTrans is NotSet: funcTrans = ['tansig', 'tansig']
      if not self._core.newff(nodes, funcTrans, self._core.trainFcn):
        MSG_FATAL(self, "Couldn't allocate new feed-forward!")
    elif coreConf() is TuningToolCores.keras:
      if not model:
        MSG_FATAL(self, "Keras model must be passed as argument in newff function.")
      self._core.compile(model)


  def train_c(self):
    """
      Train feedforward neural network
    """
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

    rawDictTempl = { 'discriminator'  : None,
                     'benchmark'      : None }

    if coreConf() is TuningToolCores.keras:

      history = self._core.fit( self._trnData, self._trnTarget, self._valData, self._valTarget )
      # Retrieve raw network
      rawDictTempl['discriminator'] = self.__discr_to_dict( self._core.model )
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
          opRoc, tstRoc = self._core.evaluate( self._trnData, self._trnTarget, self._valData, self._valTarget, self._tstData, self._tstTarget)

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

        for ref in self.references:
          if coreConf() is TuningToolCores.FastNet:
            # FastNet won't loop on this, this is just looping for keras right now
            ref = tunedDiscrDict['benchmark']
          # Print information:
          tstPoint = tstRoc.retrieve( ref )
          self._info( 'Test (%s): sp = %f, pd = %f, pf = %f, thres = %r'
                    , ref.name
                    , tstPoint.sp_value
                    , tstPoint.pd_value
                    , tstPoint.pf_value
                    , tstPoint.thres_value )
          opPoint = opRoc.retrieve( ref )
          self._info( 'Operation (%s): sp = %f, pd = %f, pf = %f, thres = %r'
                    , ref.name
                    , opPoint.sp_value
                    , opPoint.pd_value
                    , opPoint.pf_value
                    , opPoint.thres_value )



    self._debug("Finished train_c on python side.")

    return tunedDiscrList, tuningInfo
  # end of train_c




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



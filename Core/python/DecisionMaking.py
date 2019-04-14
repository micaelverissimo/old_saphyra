__all__ = ['DecisionMakingMethod', 'LinearLHThresholdCorrection',
           'DecisionMaker', 'LHThresholdCorrectionData' ]

import os, sys, numpy as np
from Gaugi import ( Logger, retrieve_kw, NotSet, checkForUnusedVars, EnumStringification
                       , LoggerRawDictStreamer, LoggingLevel, calcSP ) 
from TuningTools.coreDef import npCurrent
from TuningTools.DataCurator import CuratedSubset
from TuningTools.dataframe.EnumCollection import BaseInfo, PileupReference, Dataset
from TuningTools.TuningJob import ReferenceBenchmark
from TuningTools.Neural import Roc, RawThreshold, PileupLinearCorrectionThreshold

class DecisionMakingMethod ( EnumStringification ):
  """
  Method to make the decision of an operation point
  """
  _ignoreCase = True
  StandardThreshold = 1
  LHLinearApproach = 2
  #MaxSP_Bins = 3

# TODO For now, we are only using the default bins, specify other options
# and allow user to specify them via string by retrieving classes available in
# the module
defaultNvtxBins = npCurrent.array([-0.5,
    0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5,
    10.5,11.5,12.5,13.5,14.5,15.5,16.5,17.5,18.5,19.5,
    20.5,21.5,22.5,23.5,24.5,25.5,26.5,27.5,28.5,29.5,
    30.5,31.5,32.5,33.5,34.5,35.5,36.5,37.5,38.5,39.5,
    40.5,41.5,42.5,43.5,44.5,45.5,46.5,47.5,48.5,49.5,
    50.5,51.5,52.5,53.5,54.5,55.5,56.5,57.5,58.5,59.5,
    60.5,61.5,62.5,63.5,64.5,65.5,66.5,67.5,68.5,69.5,
    70.5,71.5,72.5,73.5,74.5,75.5,76.5,77.5,78.5,79.5,
    80.5], dtype='float64')

defaultMuBins = npCurrent.array([0.0,
    5.0,10.0,15.0,20.0,25.0,30.0,35.0,40.0,45.0,50.0,
    55.0,60.0,65.0,70.0,75.0,80.0], dtype='float64')


#_npVersion = [int(v) for v in np.__version__.split('.')]
#if not(_npVersion[1] > 9 or _npVersion[0] > 1):
#  raise ImportError('Numpy version is too old. Version 1.09 or greater is needed')

class DecisionMaker( Logger ):

  def __init__( self, dataCurator, d, **kw ):
    Logger.__init__( self, kw )
    d.update( kw ); del kw
    # Define discriminator type (for now we only have one discriminator type):
    # FIXME This chould be configured using coreDef
    try:
      try:
        from libTuningTools import DiscriminatorPyWrapper
      except ImportError:
        from libTuningToolsLib import DiscriminatorPyWrapper
    except ImportError:
      self._fatal("Cannot use FastNet DiscriminatorPyWrapper: library is not available!")
    self.dataCurator    = dataCurator
    # Discriminator parameters:
    self.DiscrClass           = DiscriminatorPyWrapper
    self.removeOutputTansigTF = retrieve_kw(d, 'removeOutputTansigTF', True )
    # Decision making parameters:
    self.thresEtBins       = retrieve_kw( d, 'thresEtBins',  None)
    self.thresEtaBins      = retrieve_kw( d, 'thresEtaBins', None)
    # TODO There is no need to require this from user
    self.method         = DecisionMakingMethod.retrieve( retrieve_kw(d, 'decisionMakingMethod', DecisionMakingMethod.LHLinearApproach ) )
    # Pileup limits specification
    self.pileupRef = None
    self.pileupLimits   = retrieve_kw( d, 'pileupLimits', None)
    self.maxCorr        = retrieve_kw( d, 'maxCorr', None)
    self.frMargin       = retrieve_kw( d, 'frMargin', [1.05, 1.1, 1.15, 1.25, 1.5, 2.0])
    if self.method is DecisionMakingMethod.LHLinearApproach:
      self._info("Using limits: %r", self.pileupLimits)
      if not 'pileupRef' in d:
        self._fatal("pileupRef must specified in order to correctly label the xaxis.")
    if 'pileupRef' in d:
      self.pileupRef      = PileupReference.retrieve( retrieve_kw( d, 'pileupRef' ) )
    # Linear LH Threshold Correction methods
    #self.maxFRMultipler = retrieve_kw( d, 'maxFRMultipler', None)
    #checkForUnusedVars( d )
    # TODO: Add fix fraction allowing to load a module and a table of values
    if self.method is DecisionMakingMethod.LHLinearApproach:
      try:
        import ElectronIDDevelopment
      except ImportError:
        self._warning("Using a standalone version of the pile-up fitting version which may not be the latest.")
      #try:
      #  import scipy
      #except ImportError:
      #  self._fatal("Cannot use LHLinearApproach since scipy is not available")

  def __call__( self, rawDiscr, **kw ):
    discr = self._transformToDiscriminator( rawDiscr )
    if self.method is DecisionMakingMethod.LHLinearApproach:
      linearLHThresholdCorrection = LinearLHThresholdCorrection( discr, self.dataCurator
                                                               , self.pileupRef
                                                               , self.pileupLimits
                                                               , self.maxCorr
                                                               , self.frMargin )
      return linearLHThresholdCorrection
    #elif self.method is DecisionMakingMethod.NoCorrection:
    #  return None
    else:
      self._fatal("Method %s is not implemented!", NotImplementedError)

  def _transformToDiscriminator( self, rawDiscr ):
    self._debug("Transforming dict to discriminator")
    # TODO We might want to have this using RawDictStreamable utility
    discr = self.DiscrClass( "DecisionMaking_Discriminator"
                           , LoggingLevel.toC( LoggingLevel.INFO ) #LoggingLevel.toC( self.level )
                           , not(int(os.environ.get('RCM_GRID_ENV',0)) or not(sys.stdout.isatty()))
                           , rawDiscr['nodes'].tolist()
                           , rawDiscr.get('trfFunc',['tansig']*len(rawDiscr['nodes']))
                           , rawDiscr['weights'].tolist()
                           , rawDiscr['bias'].tolist() )
    if self.removeOutputTansigTF: discr.removeOutputTansigTF()
    discr.removeOutputTansigTF = self.removeOutputTansigTF
    return discr

class LHThresholdCorrectionData( object ):

  def __init__(self, trnHist, eff, thres, limits, fixFraction = 0. ):
    #try:
    #  from ElectronIDDevelopment.LHHelpers import CalculateEfficiencyWithSlope
    #except ImportError:
    from TuningTools.misc.RootLinearFit import CalculateEfficiencyWithSlope
    self.histNum, self.histDen, self.histEff, self.intercept, self.slope, self.graph, self.f1 = \
        CalculateEfficiencyWithSlope( trnHist, eff, thres, limits, fixFraction, getGraph = True, getf1 = True )

  def save( self, name ):
    self.histNum.Write( name + '_histNum' )
    self.histDen.Write( name + '_histDen' )
    self.histEff.Write( name + '_histEff' )
    self.graph.Write( name + '_graph' )
    self.f1.Write( name + '_f1' )

class LinearLHThresholdCorrection( LoggerRawDictStreamer ):
  """
  Applies the likelihood threshold correction method

  -> Version 1: Sets limits, intercept, slope, interceptBkg, slopeBkg
  """
  _streamerObj = LoggerRawDictStreamer( transientAttrs = {'_discr', '_dataCurator'
                                                         , '_baseLabel'
                                                         , 'sgnOut', 'bkgOut'
                                                         , 'sgnHist', 'bkgHist'
                                                         , 'sgnCorrData', 'bkgCorrDataList'
                                                         , '_effSubset', '_effOutput'} )
  _version = 1

  def __init__( self, discriminator = None, dataCurator = None, pileupRef = None
              , limits = None, maxCorr = None, frMargin = None ):
    Logger.__init__( self )
    self._discr            = discriminator
    self._dataCurator      = dataCurator
    self._baseLabel        = ''
    # Decision making parameters: 
    self.pileupRef         = PileupReference.retrieve( pileupRef )
    self.limits            = limits
    self.maxCorr           = maxCorr
    if frMargin is not None: self.frMargin = [1.] + frMargin if frMargin[0] != 1. else frMargin
    self._pileupLabel      = PileupReference.label( self.pileupRef )
    self._pileupShortLabel = PileupReference.shortlabel( self.pileupRef )
    self.subset            = None
    if self.pileupRef is PileupReference.avgmu:
      #limits = [0,26,60]
      self.limits = [15,37.5,60] if limits is None else limits
    elif self.pileupRef is PileupReference.nvtx:
      self.limits = [0,13,30] if limits is None else limits
    # Other transient attributes:
    self.sgnOut          = None
    self.bkgOut          = None
    self.sgnHist         = None
    self.bkgHist         = None
    self.sgnCorrData     = None
    self.bkgCorrDataList = None
    self._effSubset      = None
    self._effOutput      = None
    self._ol              = 12. if self._discr.removeOutputTansigTF else 1.
    # Decision taking parameters: 
    self.intercept       = None
    self.slope           = None
    self.slopeRange      = None
    # Thresholds:
    self.thres           = None
    self.rawThres        = None
    # Performance:
    self.perf            = None
    self.rawPerf         = None
    # Bin information:
    self.etBinIdx        = self._dataCurator.etBinIdx
    self.etaBinIdx       = self._dataCurator.etaBinIdx
    self.etBin           = self._dataCurator.etBin.tolist()   
    self.etaBin          = self._dataCurator.etaBin.tolist()  

  def saveGraphs( self ):
    from ROOT import TH1F
    sStr = CuratedSubset.tostring( self.subset )
    self.sgnCorrData.save( 'signalCorr_' + self._baseLabel + '_' + sStr)
    for i, bkgCorrData in enumerate(self.bkgCorrDataList):
      bkgCorrData.save( 'backgroundCorr_' + str(i) + '_' + self._baseLabel  + '_' + sStr)
    
    sgnPileup = self.getPileup( CuratedSubset.tosgn( self.subset ) )
    sgnPassPileup = sgnPileup[ self.rawThres.getMask( self.sgnOut ) ]
    sgnEff = PileupEffHist( sgnPassPileup, sgnPileup, defaultNvtxBins, 'signalUncorr_' + self._baseLabel  + '_' + sStr )
    sgnEff.Write()
    bkgPileup = self.getPileup( CuratedSubset.tobkg( self.subset ) )
    bkgPassPileup = bkgPileup[ self.rawThres.getMask( self.bkgOut ) ]
    bkgEff = PileupEffHist( bkgPassPileup, bkgPileup, defaultNvtxBins, 'backgroundUncorr_' + self._baseLabel  + '_' + sStr )
    bkgEff.Write()
    # Write 2D histograms:
    self.sgnHist.Write( 'signal2DCorr_' + self._baseLabel  + '_' + sStr)
    self.bkgHist.Write( 'background2DCorr_' + self._baseLabel  + '_' + sStr)
    # Write output histograms:
    title = CuratedSubset.tostring( CuratedSubset.tosgn( self.subset ) ) + ' NN Output'
    sgnTH1 = TH1F( title, title, 100, -self._ol, self._ol ) 
    for p in self.sgnOut: sgnTH1.Fill( p )
    sgnTH1.Write( 'signalOutputs_' + self._baseLabel + '_' + sStr )
    title = CuratedSubset.tostring( CuratedSubset.tobkg( self.subset ) ) + ' NN Output'
    bkgTH1 = TH1F( title, title, 100, -self._ol, self._ol ) 
    for p in self.bkgOut: bkgTH1.Fill( p )
    bkgTH1.Write( 'backgroundOutputs_' + self._baseLabel + '_' + sStr )
    if self._effSubset is not None:
      esubset = CuratedSubset.tobinary( CuratedSubset.topattern( self._effSubset[0] ) ) 
      if esubset is not self.subset:
        sStr = CuratedSubset.tostring( esubset )
        # Here we have also to plot the subset where we have calculated the efficiency
        sgnPileup = self.getPileup( CuratedSubset.tosgn( self._effSubset[0] ) )
        sgnPassPileup = sgnPileup[ self.rawThres.getMask( self._effOutput[0] ) ]
        sgnEff = PileupEffHist( sgnPassPileup, sgnPileup, defaultNvtxBins, 'signalUncorr_' + self._baseLabel  + '_' + sStr )
        sgnEff.Write()
        sgnPassPileup = sgnPileup[ self.thres.getMask( self._effOutput[0], sgnPileup ) ]
        sgnEff = PileupEffHist( sgnPassPileup, sgnPileup, defaultNvtxBins, 'signalCorr_' + self._baseLabel  + '_' + sStr )
        sgnEff.Write()
        bkgPileup = self.getPileup( CuratedSubset.tobkg( self._effSubset[1] ) )
        bkgPassPileup = bkgPileup[ self.rawThres.getMask( self._effOutput[1] ) ]
        bkgEff = PileupEffHist( bkgPassPileup, bkgPileup, defaultNvtxBins, 'backgroundUncorr_' + self._baseLabel  + '_' + sStr )
        bkgEff.Write()
        bkgPassPileup = bkgPileup[ self.thres.getMask( self._effOutput[1], bkgPileup ) ]
        bkgEff = PileupEffHist( bkgPassPileup, bkgPileup, defaultNvtxBins, 'backgroundCorr_' + self._baseLabel  + '_' + sStr )
        bkgEff.Write()
        sgnHist = self.get2DPerfHist( self._effSubset[0], 'signal2DCorr_' + self._baseLabel + '_' + sStr,     outputs = self._effOutput[0] )
        sgnHist.Write('signal2DCorr_' + self._baseLabel + '_' + sStr)
        bkgHist = self.get2DPerfHist( self._effSubset[1], 'background2DCorr_' + self._baseLabel + '_' + sStr, outputs = self._effOutput[1] )
        bkgHist.Write('background2DCorr_' + self._baseLabel + '_' + sStr)
        # 1D output plots
        title = CuratedSubset.tostring( self._effSubset[0] ) + ' NN Output'
        sgnTH1 = TH1F( title, title, 100, -self._ol, self._ol ) 
        for p in self.sgnOut: sgnTH1.Fill( p )
        sgnTH1.Write( 'signalOutputs_' + self._baseLabel + '_' + sStr )
        title = CuratedSubset.tostring( self._effSubset[1] ) + ' NN Output'
        bkgTH1 = TH1F( title, title, 100, -self._ol, self._ol ) 
        for p in self.bkgOut: bkgTH1.Fill( p )
        bkgTH1.Write( 'backgroundOutputs_' + self._baseLabel + '_' + sStr )

  def __call__( self, referenceObj, subset, *args, **kw ):
    " Hook method to discriminantLinearCorrection "
    self.discriminantLinearCorrection( referenceObj, subset, *args, **kw )

  def releasetData( self ):
    self.sgnOut          = None
    self.bkgOut          = None
    self._effOutput      = None
    self.sgnHist         = None
    self.bkgHist         = None
    self.sgnCorrData     = None
    self.bkgCorrDataList = None

  def _getCorrectionData( self, referenceObj, **kw ):
    neuron = kw.get('neuron', None )
    sort   = kw.get('sort', None )
    init   = kw.get('init', None )
    self._baseLabel = "ref%s_etBin%d_etaBin%d%s%s%s" % ( ReferenceBenchmark.tostring( referenceObj.reference )
        , self._dataCurator.etBinIdx
        , self._dataCurator.etaBinIdx
        , ( '_neuron%d' % neuron ) if neuron is not None else ''
        , ( '_sort%d' % sort ) if sort is not None else ''
        , ( '_init%d' % init ) if init is not None else '' )
    self.sgnHist, self.sgnOut = self.get2DPerfHist( CuratedSubset.tosgn(self.subset), 'signal_' + self._baseLabel,     getOutputs = True )
    self.bkgHist, self.bkgOut = self.get2DPerfHist( CuratedSubset.tobkg(self.subset), 'background_' + self._baseLabel, getOutputs = True )
    if not self.rawPerf:
      try:
        from libTuningToolsLib import genRoc
      except ImportError:
        from libTuningTools import genRoc
      # Get raw threshold:
      if referenceObj.reference is ReferenceBenchmark.Pd:
        raw_thres = RawThreshold( - np.percentile( -self.sgnOut, referenceObj.refVal * 100. ) )
      elif referenceObj.reference is ReferenceBenchmark.Pf:
        raw_thres = RawThreshold( - np.percentile( -self.bkgOut, referenceObj.refVal * 100. ) )
      else:
        o = genRoc(self.sgnOut, self.bkgOut, self._ol, -self._ol, 0.001 )
        roc = Roc( o
                 , etBinIdx = self.etBinIdx, etaBinIdx = self.etaBinIdx
                 , etBin = self.etBin, etaBin = self.etaBin )
        self.rawPerf = roc.retrieve( referenceObj )
      if referenceObj.reference in ( ReferenceBenchmark.Pd, ReferenceBenchmark.Pf ):
        self.rawPerf = self.getEffPoint( referenceObj.name
                                       , thres = raw_thres
                                       , makeCorr = False )
        # Here we protect against choosing suboptimal Pd/Pf points:
        o = genRoc(self.sgnOut, self.bkgOut, self._ol, -self._ol, 0.001 )
        roc = Roc( o
                 , etBinIdx = self.etBinIdx, etaBinIdx = self.etaBinIdx
                 , etBin = self.etBin, etaBin = self.etaBin )
        # Check whether we could be performing better:
        if referenceObj.reference is ReferenceBenchmark.Pd:
          mask = roc.pds >= referenceObj.refVal
        elif referenceObj.reference is ReferenceBenchmark.Pf:
          mask = roc.pfs <= referenceObj.refVal
        pds = roc.pds[mask]
        pfs = roc.pfs[mask]
        sps = roc.sps[mask]
        if referenceObj.reference is ReferenceBenchmark.Pd:
          mask = pfs <= ( 1.001 * self.rawPerf.pf )
          sps = sps[mask]
          pfs = pfs[mask]
          if len(sps):
            idx = np.argmax(sps)
            if pfs[idx] < 0.98 * self.rawPerf.pf:
              self._warning('Model is sub-optimal when performing at requested Pd.')
              self._info('Using highest SP operation point with virtually same Pf.')
              raw_thres = RawThreshold( - np.percentile( -self.bkgOut, pfs[idx] * 100. ) )
              self._debug('Previous preformance was: %s', self.rawPerf.asstr( addname = False, perc = True, addthres = False ))
              self.rawPerf = self.getEffPoint( referenceObj.name
                                             , thres = raw_thres
                                             , makeCorr = False )
              self._debug('New preformance was: %s', self.rawPerf.asstr( addname = False, perc = True, addthres = False ))
        elif referenceObj.reference is ReferenceBenchmark.Pf:
          mask = pds >= ( 0.999 * self.rawPerf.pd )
          sps = sps[mask]
          pds = pds[mask]
          if len(sps):
            idx = np.argmax(sps)
            if pds[idx] > 1.005 * self.rawPerf.pd:
              self._warning('Model is sub-optimal when performing at requested Pf.')
              self._info('Using highest SP operation point with virtually same Pd.')
              raw_thres = RawThreshold( - np.percentile( -self.sgnOut, pds[idx] * 100. ) )
              self._debug('Previous preformance was: %s', self.rawPerf.asstr( addname = False, perc = True, addthres = False ))
              self.rawPerf = self.getEffPoint( referenceObj.name
                                             , thres = raw_thres
                                             , makeCorr = False )
              self._debug('New preformance was: %s', self.rawPerf.asstr( addname = False, perc = True, addthres = False ))
    else:
      self._debug('Skipped calculating raw performance since we already have it calculated')
    self.rawThres = self.rawPerf.thres
    # use standard lh method using signal data:
    sgnCorrData = LHThresholdCorrectionData( self.sgnHist, self.rawPerf.pd, self.rawThres.thres, self.limits, 1. )
    return sgnCorrData

  def getPileup(self, subset): 
    baseinfo = self._dataCurator.getBaseInfo(subset, BaseInfo.PileUp)
    if CuratedSubset.isbinary( subset ):
      if CuratedSubset.isoperation( subset ):
        ret = [np.concatenate(b, axis = npCurrent.odim).squeeze().astype(dtype='float64') for b in baseinfo]
      else:
        ret = [b.squeeze().astype(dtype='float64') for b in baseinfo]
    else:
      if CuratedSubset.isoperation( subset ):
        ret = np.concatenate(baseinfo, axis = npCurrent.odim).squeeze().astype(dtype='float64')
      else:
        ret = baseinfo.squeeze().astype(dtype='float64')
    if (ret == 0.).all():
      self._fatal("All pile-up data is zero!")
    return ret

  def getOutput(self, subset): 
    self._verbose('Propagating output for subset: %s', CuratedSubset.tostring(subset))
    data = self._dataCurator[CuratedSubset.topattern( subset )]
    inputDim = self._dataCurator.nInputs
    if inputDim != self._discr.getNumNodes(0):
      self._fatal( "Data number of patterns (%d) do not match with discriminator input dimension (%d)!"
                 ,  inputDim, self._discr.getNumNodes(0))
    if CuratedSubset.isbinary( subset ):
      if CuratedSubset.isoperation( subset ):
        output = [np.concatenate([self._discr.propagate_np(sd) for sd in d], axis  = npCurrent.odim) for d in data]
      else:
        output = [self._discr.propagate_np(d) for d in data]
    else:
      if CuratedSubset.isoperation( subset ):
        output = np.concatenate([self._discr.propagate_np(d) for d in data], axis = npCurrent.odim)
      else:
        output = self._discr.propagate_np(data)
    return output

  def _calcEff( self, subset, output = None, pileup = None, thres = None, makeCorr = True ):
    self._verbose('Calculating efficiency for %s', CuratedSubset.tostring( subset ) )
    pileup = self.getPileup(subset) if pileup is None else pileup
    if output is None: output = self.getOutput(subset)
    if thres is None: thres = self.thres if makeCorr else self.rawThres
    args = (output, pileup) if makeCorr else (output,)
    return thres.getPerf( *args )

  def getEffPoint( self, name, subset = [None, None], outputs = [None, None], pileup = [None,None], thres = None, makeCorr = True ):
    from TuningTools.Neural import PerformancePoint
    auc = self.rawPerf.auc if self.rawPerf else -1
    if not isinstance(subset, (tuple,list)): 
      if subset is None: 
        if not(any([o is None for o in outputs])): self._fatal("Subset must be specified when outputs is used.")
        subset = self.subset
      subset = [CuratedSubset.tosgn(subset),CuratedSubset.tobkg(subset)]
    else:
      if len(subset) is 1:
        if subset[0] is None: 
          if not(any([o is None for o in outputs])): self._fatal("Subset must be specified when outputs is used.")
          subset = [self.subset]
        subset = [CuratedSubset.tosgn(subset[0]),CuratedSubset.tobkg(subset[0])]
      else:
        if any([s is None for s in subset]): 
          if not(any([o is None for o in outputs])): self._fatal("Subset must be specified when outputs is used.")
          subset = [self.subset, self.subset]
        subset = [CuratedSubset.tosgn(subset[0]),CuratedSubset.tobkg(subset[1])]
    self._effSubset = subset
    if any([o is None for o in outputs]):
      #if outputs[0] is None:
      if isinstance(subset, (list,tuple)):
        # FIXME This assumes that sgnOut is cached:
        outputs = [(self.getOutput(CuratedSubset.topattern(s)) if CuratedSubset.tobinary(s) is not self.subset else o )
                   for o, s in zip([self.sgnOut,self.bkgOut], subset)]
      else:
        if CuratedSubset.tobinary(subset) is not self.subset:
          outputs = self.getOutput(CuratedSubset.topattern(subset))
        else:
          outputs = [self.sgnOut,self.bkgOut]
      # NOTE: This can be commented out to improve speed
      try:
        from libTuningToolsLib import genRoc
      except ImportError:
        from libTuningTools import genRoc
      o = genRoc(outputs[0], outputs[1], +self._ol, -self._ol, 0.001 )
      auc = Roc( o ).auc
    self._effOutput = outputs
    if thres is None: thres = self.thres if makeCorr else self.rawThres
    pd = self._calcEff( subset[0], output = outputs[0], pileup = pileup[0], thres = thres, makeCorr = makeCorr )
    pf = self._calcEff( subset[1], output = outputs[1], pileup = pileup[1], thres = thres, makeCorr = makeCorr )
    sp = calcSP(pd, 1. - pf)
    return PerformancePoint( name, sp, pd, pf, thres, perc = False, auc = auc
                           , etBinIdx = self.etBinIdx, etaBinIdx = self.etaBinIdx
                           , etBin = self.etBin, etaBin = self.etaBin )

  def getReach( self, sgnCorrData, bkgCorrDataList ):
    return [( ( ( bkgCorrData.intercept - sgnCorrData.intercept ) / ( sgnCorrData.slope - bkgCorrData.slope )  )
              if ( sgnCorrData.slope - bkgCorrData.slope ) else (999.) ) for bkgCorrData in bkgCorrDataList 
           ]

  def discriminantLinearCorrection( self, referenceObj, subset, **kw ):
    from ROOT import TH2F
    subset = CuratedSubset.tobinary( CuratedSubset.topattern( subset ) )
    if self.subset is subset:
      self._debug("Already retrieved parameters for subset %s.", CuratedSubset.tostring( subset ) )
      return
    self._info('Running linear correction...')
    # Reset raw perf:
    self.rawPerf = kw.pop('rawPerf', None)
    self.subset = subset
    self._verbose('Getting correction data')
    self.sgnCorrData  = self._getCorrectionData( referenceObj, **kw )
    self._verbose('Getting background correction data')
    self.bkgCorrDataList = [LHThresholdCorrectionData( self.bkgHist, self.rawPerf.pf * mult, self.rawThres.thres, self.limits, 1. ) 
                            for mult in self.frMargin]
    # Set final parameters:
    self._verbose('Getting linear correction threshold')
    self.thres = PileupLinearCorrectionThreshold( intercept = self.sgnCorrData.intercept, slope = self.sgnCorrData.slope
                                                , rawThres = self.rawThres.thres
                                                , reach = self.getReach( self.sgnCorrData, self.bkgCorrDataList )
                                                , margins = self.frMargin, limits = self.limits, maxCorr = self.maxCorr
                                                , pileupStr = self._pileupShortLabel
                                                , etBinIdx = self.etBinIdx, etaBinIdx = self.etaBinIdx
                                                , etBin = self.etBin, etaBin = self.etaBin )
    self._verbose('Getting performance')
    self.perf = self.getEffPoint( referenceObj.name, makeCorr = True )
    # Set performance results for monitoring purposes:
    self._debug("Retrieved following parameters and performance values using %s dataset", Dataset.tostring(Dataset.Train)  )
    self._debug("Raw: %s", self.rawPerf.asstr( perc = True, addthres = False ) )
    self._debug("Raw Threshold: %s", self.rawPerf.thresstr() )
    self._debug("<pile-up> limits: %r.", self.limits )
    self._debug("Linear correction: %s", self.perf.asstr( perc = True, addthres = False ) ) 
    self._debug("Linear correction Threshold: %s", self.perf.thresstr() ) 
    self._debug("Reach: %r", tuple(zip( self.frMargin[1:], self.thres.reach[1:])))

  def makePlots(self):
    # TODO Use this method when saving data to monitoring
    ## Plot information
    import ROOT
    ROOT.gROOT.SetBatch(ROOT.kTRUE)
    ROOT.gErrorIgnoreLevel=ROOT.kWarning
    ROOT.TH1.AddDirectory(ROOT.kFALSE)
    from TuningTools.monitoring.plots.PlotFunctions import SetupStyle
    mystyle = SetupStyle()
    #mystyle.SetTitleX(0.5)
    #mystyle.SetTitleAlign(23)
    #mystyle.SetPadBottomMargin(0.13)
    mystyle.SetOptStat(0)
    mystyle.SetOptTitle(0)
    c = PlotLinearEffCorr( sgnEff, self.sgnCorrData.histEff, 'signalEffComp_' + self._baseLabel
                         , xname = self._pileupLabel, limits = self.limits, refValue = eff.pd_value
                         , eff_uncorr = self.rawPerf, eff = self.perf
                         , etBin = None, etaBin = None )
    c.SaveAs( c.GetName() + '.pdf' )
    c = PlotLinearEffCorr( bkgEff, self.bkgCorrDataList[0].histEff, 'backgroundEffComp_' + self._baseLabel
                         , xname = self._pileupLabel, limits = self.limits, refValue = eff.pf_value
                         , eff_uncorr = self.rawPerf, eff = self.perf
                         , etBin = None, etaBin = None )
    c.SaveAs( c.GetName() + '.pdf' )
    # TODO Add background f1's
    c = Plot2DLinearFit( sgnList[0], title = 'signal2DHist_' + self._baseLabel
                       , xname = self._pileupLabel
                       , limits = self.limits, graph = self.sgnCorrData.graph
                       , label = 'Signal Train DS', eff_uncorr = self.rawPerf, eff = self.perf
                       , etBin = None, etaBin = None )
    c.SaveAs( c.GetName() + '.pdf' )
    c = Plot2DLinearFit( bkgList[0], title = 'background2DHist_' + self._baseLabel
                       , xname = self._pileupLabel
                       , limits = self.limits, thres = point.thres_value, graph = self.bkgCorrDataList[0].graph
                       , label = 'Background Train DS', eff_uncorr = self.rawPerf, eff = self.perf
                       , etBin = None, etaBin = None )
    c.SaveAs( c.GetName() + '.pdf' )

  def get2DPerfHist( self, subset, histLabel, outputs = None, getOutputs = False ):
    if outputs is None: outputs = self.getOutput(subset)
    from ROOT import TH2F#, MakeNullPointer
    # These limits are hardcoded for now, we might want to test them:
    hist = TH2F( histLabel, histLabel, 500, -self._ol, self._ol, len(defaultNvtxBins)-1, defaultNvtxBins )
    hist.Sumw2()
    hist.FillN( len(outputs) - 1, outputs.astype(dtype='float64')
              , self.getPileup(subset)
              , npCurrent.ones( outputs.shape, dtype='float64' ) # MakeNullPointer()
              , 1 )
    ret = hist
    if getOutputs:
      ret = (hist, outputs)
    return ret



############################################################################################ 

from TuningTools.monitoring.plots.PlotFunctions import *
from TuningTools.monitoring.plots.TAxisFunctions import *


############################################################################################ 
#################### User this functions in the decisionMaker class ########################
############################################################################################ 

def Plot2DLinearFit( hist2D, title, xname
                   , limits, graph
                   , label, eff_uncorr, eff
                   , etBin = None, etaBin = None ):
  import array as ar
  from ROOT import TCanvas, gStyle, TLegend, kRed, kBlue, kBlack, TLine, kBird, kOrange
  from ROOT import TGraphErrors, TF1, TColor
  pileup_max = hist2D.GetYaxis().GetXmax()
  pileup_min = hist2D.GetYaxis().GetXmin()
  # Retrieve some usefull information
  gStyle.SetPalette(kBird)
  canvas3 = TCanvas(title,title, 500, 500)
  #canvas3.SetTopMargin(0.10)
  canvas3.SetRightMargin(0.12)
  canvas3.SetLeftMargin(0.10)
  #canvas3.SetBottomMargin(0.11)
  FormatCanvasAxes(canvas3, XLabelSize=18, YLabelSize=18, XTitleOffset=0.87, YTitleOffset=1.5)
  #hist2D.SetTitle('Neural Network output as a function o nvtx, '+partition_name)
  #hist2D.GetXaxis().SetTitle('Neural Network output (Discriminant)')
  #hist2D.GetYaxis().SetTitle(xname)
  #hist2D.GetZaxis().SetTitle('Counts')
  #if not useNoActivationFunctionInTheLastLayer: hist2D.SetAxisRange(-1,1, 'X' )
  hist2D.Draw('colz')
  (miny,maxy) = GetYaxisRanges(canvas3,check_all=True,ignorezeros=True,ignoreErrors=True)
  canvas3.SetLogz()
  # Invert graph
  nvtx_points        = ar.array( 'd', graph.GetX(), )
  nvtx_error_points  = ar.array( 'd', graph.GetEX(),)
  discr_points       = ar.array( 'd', graph.GetY(), )
  discr_error_points = ar.array( 'd', graph.GetEY(),)
  g1 = TGraphErrors(len(discr_points), discr_points, nvtx_points, discr_error_points, nvtx_error_points)
  g1.SetLineWidth(1)
  g1.SetLineColor(kBlack)
  g1.SetMarkerColor(kBlack)
  g1.SetMarkerSize(.6)
  g1.Draw("P same")
  tobject_collector.append(g1)
  l2 = TLine(eff_uncorr.thres,miny,eff_uncorr.thres,maxy)
  l2.SetLineColor(kRed)
  l2.SetLineWidth(2)
  l2.Draw("l,same")
  tobject_collector.append(l2)
  f1 = eff.f1
  l3 = TLine(f1.Eval(miny), miny, f1.Eval(maxy), maxy)
  l3.SetLineColor(kBlack)
  l3.SetLineWidth(2)
  l3.Draw("l,same")
  tobject_collector.append(l3)
  SetAxisLabels(canvas3,'Neural Network output (Discriminant)',xname,'Entries')
  t = DrawText(canvas3,[GetAtlasInternalText(), '', FixLength(label,16), '', GetSqrtsText()],.05,.70,.45,.9)
  t.SetTextAlign(12)
  t2 = DrawText(canvas3,[ '#color[2]{%s}' % eff_uncorr.thresstr( 'Fixed Threshold' )
                   , '#color[2]{#varepsilon=%s}' % eff_uncorr.asstr(addname = False, addthres = False )
                   , ''
                   , eff.threstr( prefix = 'Correction' )
                   , '#varepsilon=%s' % eff.asstr(addname = False, addthres = False )
                   ]
          ,.45,.70,.45,.9,totalentries=5, textsize = 14 )
  t2.SetTextAlign(12)
  AutoFixAxes( canvas3, ignoreErrors = True, limitXaxisToFilledBins = True, changeAllXAxis = True )
  return canvas3
  #canvas3.SaveAs(output_name+'_c3.pdf')

def PileupEffHist( pileupPass, pileup, bins, name ):
  from ROOT import TH1F, TF1
  import numpy as np
  htotal = TH1F( name, '', len(bins)-1, bins )
  htotal.Sumw2()
  hpass = htotal.Clone( htotal.GetName() + "_pass" )
  heff = hpass.Clone( htotal.GetName() + "_eff" )
  htotal.FillN( len(pileup) - 1, pileup, np.ones( shape=pileup.shape ) )
  hpass.FillN( len(pileupPass) - 1, pileupPass, np.ones( shape=pileupPass.shape ) )
  heff.Divide( hpass, htotal, 1, 1, 'B' )
  heff.SetStats(0)
  heff.SetMinimum(0)
  heff.SetMaximum(1)
  return heff

def PileupCorrText( var, prefix, intercept, slope = None ): 
  return ('%s%1.3f %s') % ( ( ('%s: ' % prefix ) if prefix else '')
                              ,  intercept
                              , ('%s %1.3f#times%s ' % ('+' if slope > 0 else '-', abs(slope), var )) if slope is not None else '')

def PlotLinearEffCorr( histEff, histEffCorr, title, xname
                     , limits, refValue, eff_uncorr, eff
                     , etBin = None, etaBin = None ):
  from ROOT import TCanvas, gStyle, TLegend, kRed, kBlue, kBlack, TLine, kBird, kOrange
  from ROOT import TGraphErrors, TF1, TColor
  histEff.SetStats(0)
  histEff.SetMinimum(0)
  histEff.SetMaximum(1)
  histEffCorr.SetStats(0)
  histEffCorr.SetMinimum(0)
  histEffCorr.SetMaximum(1)
  # TODO Add labels
  def AddTopLabels(can,legend, legOpt = 'p', quantity_text = '', etlist = None
                       , etalist = None, etidx = None, etaidx = None, legTextSize=10
                       , runLabel = '', extraText1 = None, legendY1=.68, legendY2=.93
                       , maxLegLength = 19, logger=None):
    text_lines = []
    text_lines += [GetAtlasInternalText()]
    text_lines.append( GetSqrtsText(13) )
    if runLabel: text_lines.append( runLabel )
    if extraText1: text_lines.append( extraText1 )
    DrawText(can,text_lines,.30,.68,.70,.93,totalentries=4)
    if legend:
      MakeLegend( can,.73,legendY1,.89,legendY2,textsize=legTextSize
                , names=legend, option = legOpt, squarebox=False
                , totalentries=0, maxlength=maxLegLength )
    try:
      from copy import copy
      extraText = []
      if etlist and etidx is not None:
        # add infinity in case of last et value too large
        etlist=copy(etlist)
        if etlist[-1]>9999:  etlist[-1]='#infty'
        binEt = (str(etlist[etidx]) + ' < E_{T} [GeV] < ' + str(etlist[etidx+1]) if etidx+1 < len(etlist) else
                                 'E_{T} > ' + str(etlist[etidx]) + ' GeV')
        extraText.append(binEt)
      if quantity_text:
        if not isinstance(quantity_text,(tuple,list)): quantity_text = [quantity_text]
        extraText += quantity_text
      if etalist and etaidx is not None:
        binEta = (str(etalist[etaidx]) + ' < #eta < ' + str(etalist[etaidx+1]) if etaidx+1 < len(etalist) else
                                    str(etalist[etaidx]) + ' < #eta < 2.47')
        extraText.append(binEta)
      DrawText(can,extraText,.14,.68,.35,.93,totalentries=4)
    except NameError, e:
      if logger:
        logger.warning("Couldn't print test due to error: %s", e)
      pass
  binLabel = ''
  if etBin is not None and etaBin is not None:
    binLabel = '_'.join( [ str(etBin[0]).zfill(4), str(etaBin[0]).zfill(4) ] )
  canvas1 = TCanvas(title, title, 500, 500)
  histEff.SetTitle(title + ' in: ' + binLabel if binLabel else title )
  histEff.SetLineColor(kGray)
  histEff.SetMarkerColor(kGray)
  # FIXME Care with Transparent 
  histEff.SetFillColor(TColor.GetColorTransparent(kGray, .5))
  histEffCorr.SetLineColor(kBlue+1)
  histEffCorr.SetMarkerColor(kBlue+1)
  histEffCorr.SetFillColor(TColor.GetColorTransparent(kBlue+1, .5))
  drawopt='lpE2'
  AddHistogram(canvas1,histEff,drawopt)
  AddHistogram(canvas1,histEffCorr,drawopt)
  l0 = TLine(limits[0],refValue,limits[2],refValue)
  l0.SetLineColor(kBlack)
  l0.Draw()
  #l1 = TLine(limits[0],refValue_requested,limits[2],refValue_requested)
  #l1.SetLineColor(kGray+2)
  #l1.SetLineStyle(9)
  #l1.Draw()
  AddTopLabels( canvas1, [ eff_uncorr.thresstr( prefix = 'Raw threshold' )
                         , eff.thresstr( prefix = 'Threshold Correction' )
                         ]
              , legOpt='p')
  FormatCanvasAxes(canvas1, XLabelSize=18, YLabelSize=18, XTitleOffset=0.87, YTitleOffset=1.5)
  SetAxisLabels(canvas1, xname, '#epsilon(' + eff.pileupStr + ')' )
  FixYaxisRanges(canvas1, ignoreErrors=False, yminc=-eps)
  AutoFixAxes(canvas1, ignoreErrors=False)
  AddBinLines(canvas1, histEff)
  #canvas1.SaveAs(output_name+'_c1.pdf')
  return canvas1




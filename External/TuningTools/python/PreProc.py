__all__ = ['PreProcStrategy', 'PreProcArchieve', 'PrepObj', 'Projection',  'RemoveMean', 'RingerRp',
           'UndoPreProcError', 'UnitaryRMS', 'FirstNthPatterns', 'KernelPCA',
           'MapStd', 'MapStd_MassInvariant', 'NoPreProc', 'Norm1', 'PCA',
           'PreProcChain', 'PreProcCollection', 'RingerEtaMu', 'RingerFilterMu',
           'StatReductionFactor', 'StatUpperLimit', 'fixPPCol', 'RingerPU',
           'RingerEtEtaMu', 'ShowerShapesSimpleNorm', 'ExpertNetworksShowerShapeSimpleNorm',
           'ExpertNetworksShowerShapeAndTrackSimpleNorm', 'TrackSimpleNorm',
           'ExpertNetworksSimpleNorm',
           'RingerLayerSegmentation','RingerLayer',
           'PreProcMerge',
           ]



from Gaugi import ( Logger, LoggerStreamable, checkForUnusedVars, EnumStringification
                       , save, load, LimitedTypeList, LoggingLevel, LoggerRawDictStreamer
                       , LimitedTypeStreamableList, RawDictStreamer, RawDictCnv )
from TuningTools.coreDef import npCurrent
from copy import deepcopy
import numpy as np



class PreProcStrategy(EnumStringification):
  Norm1 = 0
  TrackSimpleNorm = 1
  ShowerShapeSimpleNorm = 2
  ExpertNetworksSimpleNorm = 3
  ExpertNetworksShowerShapeSimpleNorm = 4
  ExpertNetworksShowerShapeAndTrackSimpleNorm = 5

class RingerLayer(EnumStringification):
  PS = 0
  EM1 = 1
  EM2 = 2
  EM3 = 3
  HAD1 = 4
  HAD2 = 5
  HAD3 = 6

class PreProcArchieve( Logger ):
  """
  Context manager for Pre-Processing archives

  Version 3: - saves raw version of pp collection
  Version 2: - saved a pp collection for each eta/et bin and each sort.
  Version 1: - saved a pre-processing chain.
  """

  _type = 'PreProcFile'
  _version = 3

  def __init__(self, filePath = None, **kw):
    """
    Either specify the file path where the file should be read or the data
    which should be appended to it:

    with PreProcArchieve("/path/to/file") as data:
      BLOCK

    PreProcArchieve( "file/path", ppCol = Norm1() )
    """
    Logger.__init__(self, kw)
    self._filePath = filePath
    self._ppCol = kw.pop( 'ppCol', None )
    checkForUnusedVars( kw, self._warning )

  @property
  def filePath( self ):
    return self._filePath

  def filePath( self, val ):
    self._filePath = val

  @property
  def ppCol( self ):
    return self._ppCol

  def getData( self ):
    if not self._ppCol:
       self._fatal("Attempted to retrieve empty data from PreProcArchieve.")
    return {'type' : self._type,
            'version' : self._version,
            'ppCol' : self._ppCol.toRawObj() }

  def save(self, compress = True):
    return save( self.getData(), self._filePath, compress = compress )

  def __enter__(self):
    from cPickle import PickleError
    try:
      ppColInfo = load( self._filePath )
    except PickleError:
      # It failed without renaming the module, retry renaming old module
      # structure to new one.
      import sys
      sys.modules['FastNetTool.PreProc'] = sys.modules[__name__]
      ppColInfo = load( self._filePath )
    try:
      if ppColInfo['type'] != self._type:
        self._fatal(("Input crossValid file is not from PreProcFile "
            "type."))
      if ppColInfo['version'] == 3:
        ppCol = PreProcCollection.fromRawObj( ppColInfo['ppCol'] )
      elif ppColInfo['version'] == 2:
        ppCol = ppColInfo['ppCol']
      elif ppColInfo['version'] == 1:
        ppCol = PreProcCollection( ppColInfo['ppCol'] )
      else:
        self._fatal("Unknown job configuration version.")
    except RuntimeError, e:
      self._fatal(("Couldn't read PreProcArchieve('%s'): Reason:"
          "\n\t %s" % (self._filePath,e,)))
    return ppCol

  def __exit__(self, exc_type, exc_value, traceback):
    # Remove bound
    self.ppChain = None

class UndoPreProcError(RuntimeError):
  """
    Raised when it is not possible to undo pre-processing.
  """
  def __init__( self, *args ):
    RuntimeError.__init__( self, *args )

class PrepObj( LoggerStreamable ):
  """
    This is the base class of all pre-processing objects.
  """

  # NOTE: Default, should be changed on derived classes otherwise
  takesParamsFromData = True

  def __init__(self, d = {}, **kw):
    d.update( kw )
    LoggerStreamable.__init__(self, d)

  def __call__(self, data, revert = False):
    """
      The revert should be used to undo the pre-processing.
    """
    if revert:
      try:
        self._debug('Reverting %s...', self.__class__.__name__)
        data = self._undo(data)
      except AttributeError:
        self._fatal("It is impossible to revert PreProc ")#%s" % \
        #    self.__class__.___name__)
    else:
      self._debug('Applying %s...', self.__class__.__name__)
      data = self._apply(data)
    return data

  def takeParams(self, data):
    """
      Calculate pre-processing parameters.
    """
    self._debug("No need to retrieve any parameters from data.")
    return self._apply(data)

  def release(self):
    """
      Release calculated pre-proessing parameters.
    """
    self._debug(("No parameters were taken from data, therefore none was "
        "also empty."))

  def psprocessing(self, data, extra, pCount = 0):
    """
      Pre-sort processing
    """
    return data, extra

  def __str__(self):
    """
      Overload this method to return the string representation
      of the pre-processing.
    """
    pass

  def shortName(self):
    """
      Overload this method to return the short string representation
      of the pre-processing.
    """
    pass

  def isRevertible(self):
    """
      Check whether the PreProc is revertible
    """
    import inspect
    return any([a[0] == '_undo' for a in inspect.getmembers(self) ])

  def _apply(self, data):
    """
      Overload this method to apply the pre-processing
    """
    return data



class NoPreProc(PrepObj):
  """
    Do not apply any pre-processing to data.
  """
  takesParamsFromData = False

  def __init__( self, **kw ):
    PrepObj.__init__( self, kw )
    checkForUnusedVars(kw, self._warning )
    del kw

  def __str__(self):
    """
      String representation of the object.
    """
    return "NoPreProc"

  def shortName(self):
    """
      Short string representation of the object.
    """
    return "NoPP"

  def _undo(self, data):
    return data

class Norm1(PrepObj):
  """
    Applies norm-1 to data
  """
  takesParamsFromData = False

  def __init__(self, d = {}, **kw):
    d.update( kw ); del kw
    PrepObj.__init__( self, d )
    checkForUnusedVars(d, self._warning )
    del d

  def _retrieveNorm(self, data):
    """
      Calculate pre-processing parameters.
    """
    if isinstance(data, (tuple, list,)):
      norms = []
      for cdata in data:
        cnorm = np.abs( cdata.sum(axis=npCurrent.pdim).reshape(
            npCurrent.access( pidx=1,
                              oidx=cdata.shape[npCurrent.odim] ) ) )
        cnorm[cnorm==0] = 1
        norms.append( cnorm )
    else:
      norms = np.abs( data.sum(axis=npCurrent.pdim).reshape(
            npCurrent.access( pidx=1,
                              oidx=data.shape[npCurrent.odim] ) ) )
      norms[norms==0] = 1
    return norms

  def __str__(self):
    """
      String representation of the object.
    """
    return "Norm1"

  def shortName(self):
    """
      Short string representation of the object.
    """
    return "N1"

  def _apply(self, data):
    norms = self._retrieveNorm(data)
    if isinstance(data, (tuple, list,)):
      ret = []
      for i, cdata in enumerate(data):
        ret.append( cdata / norms[i] )
    else:
      ret = data / norms
    return ret


class Projection(PrepObj):
  """
    Project data into new base
  """

  # FIXME: This will probably give problematic results if data is saved
  # with one numpy type and executed with other type

  _streamerObj = LoggerRawDictStreamer(toPublicAttrs = {'_mat'})
  _cnvObj = RawDictCnv(toProtectedAttrs = {'_mat'})

  def __init__( self, **kw ):
    PrepObj.__init__( self, kw )
    self._mat = kw.pop( 'matrix', npCurrent.fp_array([[]]) )
    checkForUnusedVars(kw, self._warning )
    del kw

  def __str__(self):
    """
      String representation of the object.
    """
    return "Proj"

  def shortName(self):
    """
      Short string representation of the object.
    """
    return "P"

  def _apply(self, data):
    if isinstance(data, (tuple, list,)):
      ret = []
      for cData in data:
        if npCurrent.useFortran:
          ret.append( np.dot( self._mat, cData ) )
        else:
          ret.append( np.dot( cData, self._mat ) )
    else:
      if npCurrent.useFortran:
        ret = np.dot( self._mat , data )
      else:
        ret = np.dot( data , self._mat )
    return ret

  def takeParams(self, trnData, **kw):
    return self._apply(trnData)

class RemoveMean( PrepObj ):
  """
    Remove data mean
  """
  _streamerObj = LoggerRawDictStreamer(toPublicAttrs = {'_mean'})
  _cnvObj = RawDictCnv(toProtectedAttrs = {'_mean'})

  def __init__(self, means = None, d = {}, **kw):
    d.update( kw ); del kw
    PrepObj.__init__( self, d )
    checkForUnusedVars(d, self._warning )
    del d
    self._mean = npCurrent.fp_array( means ) if means is not None else np.array( [], dtype=npCurrent.dtype )


  @property
  def mean(self):
    return self._mean

  @property
  def params(self):
    return self.mean()

  def takeParams(self, trnData):
    """
      Calculate mean for transformation.
    """
    if not self._mean.size:
      import copy
      data = copy.deepcopy(trnData)
      if isinstance(trnData, (tuple, list,)):
        data = np.concatenate( trnData, axis=npCurrent.odim )
      self._mean = np.mean( data, axis=npCurrent.odim, dtype=data.dtype ).reshape(
              npCurrent.access( pidx=data.shape[npCurrent.pdim],
                                oidx=1 ) )
    return self._apply(trnData)

  def __str__(self):
    """
      String representation of the object.
    """
    return "rm_mean"

  def shortName(self):
    """
      Short string representation of the object.
    """
    return "no_mu"

  def _apply(self, data):
    if not self._mean.size:
      self._fatal("Attempted to apply RemoveMean before taking its parameters.")
    if isinstance(data, (tuple, list,)):
      ret = []
      for cdata in data:
        ret.append( cdata - self._mean )
    else:
      ret = data - self._mean
    return ret

  def _undo(self, data):
    if not self._mean.size:
      self._fatal("Attempted to undo RemoveMean before taking its parameters.")
    if isinstance(data, (tuple, list,)):
      ret = []
      for i, cdata in enumerate(data):
        ret.append( cdata + self._mean )
    else:
      ret = data + self._mean
    return ret

class UnitaryRMS( PrepObj ):
  """
    Set unitary RMS.
  """

  _streamerObj = LoggerRawDictStreamer(toPublicAttrs = {'_invRMS'})
  _cnvObj = RawDictCnv(toProtectedAttrs = {'_invRMS'})

  def __init__(self, d = {}, **kw):
    d.update( kw ); del kw
    PrepObj.__init__( self, d )
    checkForUnusedVars(d, self._warning )
    del d
    self._invRMS  = np.array( [], dtype=npCurrent.dtype )

  @property
  def rms(self):
    return 1 / self._invRMS

  @property
  def params(self):
    return self.rms()

  def takeParams(self, trnData):
    """
      Calculate rms for transformation.
    """
    # Put all classes information into only one representation
    # TODO Make transformation invariant to each class mass.
    import copy
    data = copy.deepcopy(trnData)
    if isinstance(data, (tuple, list,)):
      data = np.concatenate( data, axis=npCurrent.odim )
    tmpArray = np.sqrt( np.mean( np.square( data ), axis=npCurrent.odim ) ).reshape(
                npCurrent.access( pidx=data.shape[npCurrent.pdim],
                                  oidx=1 ) )
    tmpArray[tmpArray==0] = 1
    self._invRMS = 1 / tmpArray
    return self._apply(trnData)

  def __str__(self):
    """
      String representation of the object.
    """
    return "UnitRMS"

  def shortName(self):
    """
      Short string representation of the object.
    """
    return "1rms"

  def _apply(self, data):
    if not self._invRMS.size:
      self._fatal("Attempted to apply UnitaryRMS before taking its parameters.")
    if isinstance(data, (tuple, list,)):
      ret = []
      for cdata in data:
        ret.append( cdata * self._invRMS )
    else:
      ret = ( data * self._invRMS )
    return ret

  def _undo(self, data):
    if not self._invRMS.size:
      self._fatal("Attempted to undo UnitaryRMS before taking its parameters.")
    if isinstance(data, (tuple, list,)):
      ret = []
      for i, cdata in enumerate(data):
        ret.append( cdata / self._invRMS )
    else:
      ret = ( data / self._invRMS )
    return ret



class TrackSimpleNorm( PrepObj ):
  """
    Specific normalization for track parameters in mc14, 13TeV.
    Six variables, normalized through simple multiplications.
  """
  _streamerObj = LoggerRawDictStreamer(toPublicAttrs = {'_factors'})
  _cnvObj = RawDictCnv(toProtectedAttrs = {'_factors'})
  takesParamsFromData = False
  def __init__(self, d = {}, **kw):
    d.update( kw ); del kw
    PrepObj.__init__(self, d)
    checkForUnusedVars(d, self._warning)
    self._factors = [0.05,  # deltaeta1
                     1.0,   # deltaPoverP
                     0.05,  # deltaPhiReescaled
                     6.0,   # d0significance
                     0.2,   # d0pvunbiased
                     1.0  ] # TRT_PID (from eProbabilityHT)
    del d

  def __str__(self):
    """
      String representation of the object.
    """
    return "Tracking data simple normalization"

  def shortName(self):
    """
      Short string representation of the object.
    """
    return "TrackSimple"

  def _apply(self, data):
    # NOTE: is it a problem that I don't deepcopy the data?
    if isinstance(data, (list,tuple)):
      if len(data) == 0: return data
      import numpy as np
      import copy
      ret = []
      for conj in data:
        conj /= np.array(self._factors)
        ret.append(conj)
      return ret
    else:
      self._fatal("Data is not in the right format, must be list or tuple")

  def takeParams(self, trnData):
    return self._apply(trnData)

class ShowerShapesSimpleNorm( PrepObj ):
  """
    Specific normalization for shower shape parameters in mc16, 13TeV.
    Seven variables, normalized through simple multiplications.
  """
  _streamerObj = LoggerRawDictStreamer(toPublicAttrs = {'_factors'})
  _cnvObj = RawDictCnv(toProtectedAttrs = {'_factors'})
  takesParamsFromData = False
  def __init__(self, d = {}, **kw):
    d.update( kw ); del kw
    PrepObj.__init__(self, d)
    checkForUnusedVars(d, self._warning)
    self._factors = [1.0,    # eratio
                     1.0,    # reta
                     1.0,    # rphi
                     0.1,    # rhad
                     0.02,   # weta2
                     0.6,    # f1
                     0.04  ] # f3
    del d

  def __str__(self):
    """
      String representation of the object.
    """
    return "Shower shape data simple normalization"

  def shortName(self):
    """
      Short string representation of the object.
    """
    return "ShShS"

  def _apply(self, data):
    # NOTE: is it a problem that I don't deepcopy the data?
    if isinstance(data, (list,tuple)):
      if len(data) == 0: return data
      import numpy as np
      import copy
      ret = []
      for conj in data:
        conj /= np.array(self._factors)
        ret.append(conj)
      return ret
    else:
      self._fatal("Data is not in the right format, must be list or tuple")

  def takeParams(self, trnData):
    return self._apply(trnData)

class ExpertNetworksShowerShapeSimpleNorm(Norm1):
  """
    Specific normalization for calorimeter and tracking parameters
    to be used in the Expert Neural Networks training.
    Usage of Norm1 normalization for calorimeter data and
    ShowerShapeSimple for shower shape data.
  """
  _streamerObj = LoggerRawDictStreamer(toPublicAttrs = {'_factors'})
  _cnvObj = RawDictCnv(toProtectedAttrs = {'_factors'})
  takesParamsFromData = False
  def __init__(self, d = {}, **kw):
    d.update( kw ); del kw
    PrepObj.__init__(self, d)
    checkForUnusedVars(d, self._warning)
    self._factors = [1.0,    # eratio
                     1.0,    # reta
                     1.0,    # rphi
                     0.1,    # rhad
                     0.02,   # weta2
                     0.6,    # f1
                     0.04  ] # f3
    del d

  def __str__(self):
    """
      String representation of the object.
    """
    return "Expert Neural Networks simple normalization."

  def shortName(self):
    """
      Short string representation of the object.
    """
    return "ExpShSh"

  def _apply(self, data):
    # Take care of different number of samples:
    for i in xrange(len(data[0])):
      if data[1][i].shape[ npCurrent.odim ] != data[0][i].shape[ npCurrent.odim ]:
        self._fatal("Data dimensions are not the same! Make sure to extract using createData from the same ntuples!")
    data_calo = data[0]
    norms = self._retrieveNorm(data_calo)
    if isinstance(data_calo, (tuple, list,)):
      ret_calo = []
      for i, cdata in enumerate(data_calo):
        ret_calo.append( cdata / norms[i] )
    else:
      ret_calo = data_calo / norms

    data_std = data[1]
    if not isinstance(data_std, (list,tuple)):
      self._fatal("Data is not in the right format, must be list or tuple")
    else:
      if len(data_std) == 0:
        ret_std = data_std
      else:
        import numpy as np
        ret_std = []
        for conj in data_std:
          conj /= np.array(self._factors)
          ret_std.append(conj)
    return [ret_calo,ret_std]

class ExpertNetworksShowerShapeAndTrackSimpleNorm(Norm1):
  """
    Specific normalization for calorimeter and tracking parameters
    to be used in the Expert Neural Networks training.
    Usage of Norm1 normalization for calorimeter data and
    TrackSimpleNorm for tracking data.
  """
  _streamerObj = LoggerRawDictStreamer(toPublicAttrs = {'_factors_std','_factors_track'})
  _cnvObj = RawDictCnv(toProtectedAttrs = {'_factors_std','_factors_track'})
  takesParamsFromData = False
  def __init__(self, d = {}, **kw):
    d.update( kw ); del kw
    PrepObj.__init__(self, d)
    checkForUnusedVars(d, self._warning)
    self._factors_std = [1.0,    # eratio
                         1.0,    # reta
                         1.0,    # rphi
                         0.1,    # rhad
                         0.02,   # weta2
                         0.6,    # f1
                         0.04  ] # f3
    self._factors_track = [0.05,  # deltaeta1
                           1.0,   # deltaPoverP
                           0.05,  # deltaPhiReescaled
                           6.0,   # d0significance
                           0.2,   # d0pvunbiased
                           1.0  ] # TRT_PID (from eProbabilityHT)
    del d

  def __str__(self):
    """
      String representation of the object.
    """
    return "Expert Neural Networks shower shape and track normalization"

  def shortName(self):
    """
      Short string representation of the object.
    """
    return "ExpShTr"

  def _apply(self, data):
    # Take care of different number of samples:
    for i in xrange(len(data[0])):
      if data[1][i].shape[ npCurrent.odim ] != data[0][i].shape[ npCurrent.odim ]:
        self._fatal("Data dimensions are not the same! Make sure to extract using createData from the same ntuples!")
    data_calo = data[0]
    norms = self._retrieveNorm(data_calo)
    if isinstance(data_calo, (tuple, list,)):
      ret_calo = []
      for i, cdata in enumerate(data_calo):
        ret_calo.append( cdata / norms[i] )
    else:
      ret_calo = data_calo / norms

    data_std = data[1]
    if not isinstance(data_std, (list,tuple)):
      self._fatal("Data is not in the right format, must be list or tuple")
    else:
      if len(data_std) == 0:
        ret_std = data_std
      else:
        import numpy as np
        ret_std = []
        for conj in data_std:
          conj /= np.array(self._factors_std)
          ret_std.append(conj)

    data_track = data[2]
    if not isinstance(data_track, (list,tuple)):
      self._fatal("Data is not in the right format, must be list or tuple")
    else:
      if len(data_track) == 0:
        ret_track = data_track
      else:
        import numpy as np
        ret_track = []
        for conj in data_track:
          conj /= np.array(self._factors_track)
          ret_track.append(conj)
    return [ret_calo,ret_std,ret_track]

class ExpertNetworksSimpleNorm(Norm1):
  """
    Specific normalization for calorimeter and tracking parameters
    to be used in the Expert Neural Networks training.
    Usage of Norm1 normalization for calorimeter data and
    TrackSimpleNorm for tracking data.
  """
  _streamerObj = LoggerRawDictStreamer(toPublicAttrs = {'_factors'})
  _cnvObj = RawDictCnv(toProtectedAttrs = {'_factors'})
  takesParamsFromData = False
  def __init__(self, d = {}, **kw):
    d.update( kw ); del kw
    PrepObj.__init__(self, d)
    checkForUnusedVars(d, self._warning)
    self._factors = [0.05,  # deltaeta1
                     1.0,   # deltaPoverP
                     0.05,  # deltaPhiReescaled
                     6.0,   # d0significance
                     0.2,   # d0pvunbiased
                     1.0  ] # eProbabilityHT
    del d

  def __str__(self):
    """
      String representation of the object.
    """
    return "Expert Neural Networks simple normalization."

  def shortName(self):
    """
      Short string representation of the object.
    """
    return "ExpTr"

  def _apply(self, data):
    # Take care of different number of samples:
    for i in xrange(len(data[0])):
      if data[1][i].shape[ npCurrent.odim ] != data[0][i].shape[ npCurrent.odim ]:
        self._fatal("Data dimensions are not the same! Make sure to extract using createData from the same ntuples!")
    data_calo = data[0]

    norms = self._retrieveNorm(data_calo)
    if isinstance(data_calo, (tuple, list,)):
      ret_calo = []
      for i, cdata in enumerate(data_calo):
        ret_calo.append( cdata / norms[i] )
    else:
      ret_calo = data_calo / norms

    data_track = data[1]
    if not isinstance(data_track, (list,tuple)):
      self._fatal("Data is not in the right format, must be list or tuple")
    else:
      if len(data_track) == 0:
        ret_track = data_track
      else:
        import numpy as np
        import copy
        ret_track = []
        for conj in data_track:
          conj /= np.array(self._factors)
          ret_track.append(conj)
    return [ret_calo,ret_track]

class _ExpertCaloNetworksNormRDS( LoggerRawDictStreamer ):
  def treatDict(self, obj, raw):
    """
    Add efficiency value to be readable in matlab
    """
    raw['_mean'] = obj._mapStd.mean
    raw['_invRMS'] = obj._mapStd.invRMS
    return RawDictStreamer.treatDict( self, obj, raw )

class _ExpertCaloNetworksNormRDC( RawDictCnv ):
  def treatObj( self, obj, d ):
    obj._mapStd._mean = d['_mean']
    obj._mapStd._invRMS = d['_invRMS']
    return obj

class ExpertNorm1Std(PrepObj):
  """
    Applies norm1 to first dataset and MapStd to second one.
  """
  _streamerObj = _ExpertCaloNetworksNormRDS()
  _cnvObj = _ExpertCaloNetworksNormRDC()
  takesParamsFromData = False

  def __init__(self, d = {}, **kw):
    d.update( kw ); del kw
    PrepObj.__init__(self, d)
    checkForUnusedVars(d, self._warning)
    del d
    # Rings normalization
    self._norm1 = Norm1()
    # Standard quantities normalization
    self._mapStd = MapStd()

  def __str__(self):
    """
      String representation of the object.
    """
    return "ExpertCaloNorm"

  def shortName(self):
    """
      Short string representation of the object.
    """
    return "ExpStdN1"

  def takeParams(self, data):
    """
      Calculate pre-processing parameters.
    """
    # Take care of different number of samples:
    for i in xrange(len(data[0])):
      if data[1][i].shape[ npCurrent.odim ] != data[0][i].shape[ npCurrent.odim ]:
        self._fatal("Data dimensions are not the same! Make sure to extract using createData from the same ntuples!")
    self._debug("No need to retrieve any parameters from data.")
    self._mapStd.takeParams( data[1] )
    self._norm1.takeParams( data[0] )
    return self._apply(data)

  def _apply(self, data):
    retNorm1 = self._norm1._apply( data[0] )
    retMapStd = self._mapStd._apply( data[1] )
    return [retNorm1,retMapStd]

class FirstNthPatterns(PrepObj):
  """
    Get first nth patterns from data
  """

  _streamerObj = LoggerRawDictStreamer(toPublicAttrs = {'_n'})
  _cnvObj = RawDictCnv(toProtectedAttrs = {'_n'})
  takesParamsFromData = False

  def __init__(self, d = {}, **kw):
    d.update( kw ); del kw
    PrepObj.__init__( self, d )
    self._n = d.pop('nth',0)
    checkForUnusedVars(d, self._warning )
    del d

  def __str__(self):
    """
      String representation of the object.
    """
    return "First_%dPat" % self._n

  def shortName(self):
    """
      Short string representation of the object.
    """
    return "F%dP" % self._n

  def _apply(self, data):
    try:
      if isinstance(data, (tuple, list,)):
        ret = []
        for cdata in data:
          ret.append( cdata[npCurrent.access( pidx=slice(0,self._n), oidx=':'  ) ] )
      else:
        ret = data[ npCurrent.access( pidx=slice(0,self._n), oidx=':'  ) ]
    except IndexError, e:
      self._fatal("Data has not enought patterns!\n%s", str(e), IndexError)
    return ret

class RingerRp( Norm1 ):
  """
    Apply ringer-rp reprocessing to data.
  """

  _streamerObj = LoggerRawDictStreamer(toPublicAttrs = {'_alpha', '_beta','_rVec'})
  _cnvObj = RawDictCnv(toProtectedAttrs = {'_alpha','_beta','_rVec'})
  takesParamsFromData = False

  def __init__(self, alpha = 1., beta = 1., d = {}, **kw):
    d.update( kw ); del kw
    Norm1.__init__( self, d )
    checkForUnusedVars(d, self._warning )
    del d
    self._alpha = alpha
    self._beta = beta
    #Layers resolution
    PS      = np.arange(1,9)
    EM1     = np.arange(1,65)
    EM2     = np.arange(1,9)
    EM3     = np.arange(1,9)
    HAD1    = np.arange(1,5)
    HAD2    = np.arange(1,5)
    HAD3    = np.arange(1,5)
    rings   = np.concatenate((PS,EM1,EM2,EM3,HAD1,HAD2,HAD3))
    self._rVec = np.power( rings, self._beta )

  def __str__(self):
    """
      String representation of the object.
    """
    return ("RingerRp_a%g_b%g" % (self._alpha, self._beta)).replace('.','dot')

  def shortName(self):
    """
      Short string representation of the object.
    """
    return "Rp"

  def rVec(self):
    """
      Retrieves the ring pseudo-distance vector
    """
    return self._rVec

  def _apply(self, data):
    self._info('(alpha, beta) = (%f,%f)', self._alpha, self._beta)
    mask = np.ones(100, dtype=bool)
    mask[np.cumsum([0,8,64,8,8,4,4])] = False
    if isinstance(data, (tuple, list,)):
      ret = []
      for i, cdata in enumerate(data):
        rpEnergy = np.sign(cdata)*np.power( abs(cdata), self._alpha )
        #rpEnergy = rpEnergy[ npCurrent.access( pidx=mask, oidx=':') ]
        norms = self._retrieveNorm(rpEnergy)
        rpRings = ( ( rpEnergy * self._rVec ) / norms[ npCurrent.access( pidx=':') ] ).astype( npCurrent.fp_dtype )
        ret.append(rpRings)
    else:
      rpEnergy = np.sign(data)*np.power( abs(cdata), self._alpha )
      #rpEnergy = rpEnergy[ npCurrent.access( pidx=mask, oidx=':') ]
      norms = self._retrieveNorm(rpEnergy)
      rpRings = ( ( rpEnergy * self._rVec ) / norms[ npCurrent.access( pidx=':') ] ).astype( npCurrent.fp_dtype )
      ret = rpRings
    return ret

class MapStd( PrepObj ):
  """
    Remove data mean and set unitary standard deviation.
  """

  _streamerObj = LoggerRawDictStreamer(toPublicAttrs = {'_mean', '_invRMS'})
  _cnvObj = RawDictCnv(toProtectedAttrs = {'_mean','_invRMS'})

  def __init__(self, d = {}, **kw):
    d.update( kw ); del kw
    PrepObj.__init__( self, d )
    checkForUnusedVars(d, self._warning )
    del d
    self._mean = np.array( [], dtype=npCurrent.dtype )
    self._invRMS  = np.array( [], dtype=npCurrent.dtype )

  @property
  def mean(self):
    return self._mean

  @property
  def rms(self):
    return 1 / self._invRMS

  @property
  def invRMS(self):
    return self._invRMS

  def params(self):
    return self.mean(), self.rms()

  def takeParams(self, trnData):
    """
      Calculate mean and rms for transformation.
    """
    # Put all classes information into only one representation
    # TODO Make transformation invariant to each class mass.
    import copy
    data = copy.deepcopy(trnData)
    if isinstance(data, (tuple, list,)):
      data = np.concatenate( data, axis=npCurrent.odim )
    self._mean = np.mean( data, axis=npCurrent.odim, dtype=data.dtype ).reshape(
            npCurrent.access( pidx=data.shape[npCurrent.pdim],
                              oidx=1 ) )
    data = data - self._mean
    tmpArray = np.sqrt( np.mean( np.square( data ), axis=npCurrent.odim ) ).reshape(
                npCurrent.access( pidx=data.shape[npCurrent.pdim],
                                  oidx=1 ) )
    tmpArray[tmpArray==0] = 1
    self._invRMS = 1 / tmpArray
    return self._apply(trnData)

  def __str__(self):
    """
      String representation of the object.
    """
    return "MapStd"

  def shortName(self):
    """
      Short string representation of the object.
    """
    return "std"

  def _apply(self, data):
    if not self._mean.size or not self._invRMS.size:
      self._fatal("Attempted to apply MapStd before taking its parameters.")
    if isinstance(data, (tuple, list,)):
      ret = []
      for cdata in data:
        ret.append( ( cdata - self._mean ) * self._invRMS )
    else:
      ret = ( data - self._mean ) * self._invRMS
    return ret

  def _undo(self, data):
    if not self._mean.size or not self._invRMS.size:
      self._fatal("Attempted to undo MapStd before taking its parameters.")
    if isinstance(data, (tuple, list,)):
      ret = []
      for i, cdata in enumerate(data):
        ret.append( ( cdata / self._invRMS ) + self._mean )
    else:
      ret = ( data / self._invRMS ) + self._mean
    return ret

class MapStd_MassInvariant( MapStd ):
  """
    Remove data mean and set unitary standard deviation but "invariant" to each
    class mass.
  """

  def __init__(self, d = {}, **kw):
    d.update( kw ); del kw
    MapStd.__init__( self, d )
    del d

  def takeParams(self, trnData):
    """
      Calculate mean and rms for transformation.
    """
    # Put all classes information into only one representation
    self._fatal('MapStd_MassInvariant still needs to be validated.')
    #if isinstance(trnData, (tuple, list,)):
    #  means = []
    #  means = np.zeros(shape=( trnData[0].shape[npCurrent.odim], len(trnData) ), dtype=trnData.dtype )
    #  for idx, cTrnData in enumerate(trnData):
    #    means[:,idx] = np.mean( cTrnData, axis=npCurrent.pdim, dtype=npCurrent.fp_dtype )
    #  self._mean = np.mean( means, axis=npCurrent.pdim )
    #  trnData = np.concatenate( trnData )
    #else:
    #  self._mean = np.mean( trnData, axis=0 )
    #trnData = trnData - self._mean
    #self._invRMS = 1 / np.sqrt( np.mean( np.square( trnData ), axis=0 ) )
    #self._invRMS[self._invRMS==0] = 1 # FIXME, not on invRMS, but before dividing it.
    #trnData *= self._invRMS
    #return trnData

  def __str__(self):
    """
      String representation of the object.
    """
    return "MapStd_MassInv"

  def shortName(self):
    """
      Short string representation of the object.
    """
    return "stdI"


class PCA( PrepObj ):
  """
    PCA preprocessing
  """
  def __init__(self, d = {}, **kw):
    d.update( kw ); del kw
    PrepObj.__init__( self, d )
    self.energy = d.pop('energy' , None)

    checkForUnusedVars(d, self._warning )
    from sklearn import decomposition
    self._pca = decomposition.PCA(n_components = self.energy)

    #fix energy value
    if self.energy:  self.energy=int(100*self.energy)
    else:  self.energy=100 #total energy
    del d

  def params(self):
    return self._pca

  def variance(self):
    return self._pca.explained_variance_ratio_

  def cov(self):
    return self._pca.get_covariance()

  def ncomponents(self):
    return self.variance().shape[npCurrent.pdim]

  def takeParams(self, trnData):
    if isinstance(trnData, (tuple, list,)):
      trnData = np.concatenate( trnData )
    self._pca.fit(trnData)
    self._info('PCA are aplied (%d of energy). Using only %d components of %d',
                      self.energy, self.ncomponents(), trnData.shape[np.pdim])
    return trnData

  def __str__(self):
    """
      String representation of the object.
    """
    return "PrincipalComponentAnalysis_"+str(self.energy)

  def shortName(self):
    """
      Short string representation of the object.
    """
    return "PCA_"+str(self.energy)

  def _apply(self, data):
    if isinstance(data, (tuple, list,)):
      ret = []
      for cdata in data:
        # FIXME Test this!
        if npCurrent.isfortran:
          ret.append( self._pca.transform(cdata.T).T )
        else:
          ret.append( self._pca.transform(cdata) )
    else:
      ret = self._pca.transform(data)
      if npCurrent.isfortran:
        ret = self._pca.transform(cdata.T).T
      else:
        ret = self._pca.transform(cdata)
    return ret

  #def _undo(self, data):
  #  if isinstance(data, (tuple, list,)):
  #    ret = []
  #    for i, cdata in enumerate(data):
  #      ret.append( self._pca.inverse_transform(cdata) )
  #  else:
  #    ret = self._pca.inverse_transform(cdata)
  #  return ret


class KernelPCA( PrepObj ):
  """
    Kernel PCA preprocessing
  """
  _explained_variance_ratio = None
  _cov = None

  def __init__(self, d = {}, **kw):
    d.update( kw ); del kw
    PrepObj.__init__( self, d )

    self._kernel                    = d.pop('kernel'                , 'rbf' )
    self._gamma                     = d.pop('gamma'                 , None  )
    self._n_components              = d.pop('n_components'          , None  )
    self._energy                    = d.pop('energy'                , None  )
    self._max_samples               = d.pop('max_samples'           , 5000  )
    self._fit_inverse_transform     = d.pop('fit_inverse_transform' , False )
    self._remove_zero_eig           = d.pop('remove_zero_eig'       , False )


    checkForUnusedVars(d, self._warning )

    if (self._energy) and (self._energy > 1):
      self._fatal('Energy value must be in: [0,1]')

    from sklearn import decomposition
    self._kpca  = decomposition.KernelPCA(kernel = self._kernel,
                                          n_components = self._n_components,
                                          eigen_solver = 'auto',
                                          gamma=self._gamma,
                                          fit_inverse_transform= self._fit_inverse_transform,
                                          remove_zero_eig=self._remove_zero_eig)
    del d

  def params(self):
    return self._kpca

  def takeParams(self, trnData):

    #FIXME: try to reduze the number of samples for large
    #datasets. There is some problem into sklearn related
    #to datasets with more than 20k samples. (lock to 16K samples)
    data = trnData
    if isinstance(data, (tuple, list,)):
      # FIXME Test kpca dimensions
      pattern=0
      for cdata in data:
        if cdata.shape[npCurrent.odim] > self._max_samples*0.5:
          self._warning('Pattern with more than %d samples. Reduce!',self._max_samples*0.5)
          data[pattern] = cdata[
            npCurrent.access( pdim=':',
                              odim=(0,np.random.permutation(cdata.shape[npCurrent.odim])[0:self._max_samples]))
                               ]
        pattern+=1
      data = np.concatenate( data, axis=npCurrent.odim )
      trnData = np.concatenate( trnData, axis=npCurrent.odim )
    else:
      if data.shape[0] > self._max_samples:
        data = data[
          npCurrent.access( pdim=':',
                            odim=(0,np.random.permutation(data.shape[npCurrent.odim])[0:self._max_samples]))
                   ]

    self._info('fitting dataset...')
    # fitting kernel pca
    if npCurrent.isfotran:
      self._kpca.fit(data.T)
      # apply transformation into data
      data_transf = self._kpca.transform(data.T).T
      self._cov = np.cov(data_transf.T)
    else:
      self._kpca.fit(data)
      # apply transformation into data
      data_transf = self._kpca.transform(data)
      self._cov = np.cov(data_transf)
    #get load curve from variance accumulation for each component
    explained_variance = np.var(data_transf,axis=npCurrent.pdim)
    self._explained_variance_ratio = explained_variance / np.sum(explained_variance)
    max_components_found = data_transf.shape[0]
    # release space
    data = []
    data_transf = []

    #fix n components by load curve
    if self._energy:
      cumsum = np.cumsum(self._explained_variance_ratio)
      self._n_components = np.where(cumsum > self._energy)[0][0]
      self._energy=int(self._energy*100) #fix representation
      self._info('Variance cut. Using components = %d of %d',self._n_components,max_components_found)
    #free, the n components will be max
    else:
      self._n_components = max_components_found

    return trnData[:,0:self._n_components]

  def kernel(self):
    return self._kernel

  def variance(self):
    return self._explained_variance_ratio

  def cov(self):
    return self._cov

  def ncomponents(self):
    return self._n_components

  def __str__(self):
    """
      String representation of the object.
    """
    if self._energy:
      return "KernelPCA_energy_"+str(self._energy)
    else:
      return "KernelPCA_ncomp_"+str(self._n_components)


  def shortName(self):
    """
      Short string representation of the object.
    """
    if self._energy:
      return "kPCAe"+str(self._energy)
    else:
      return "kPCAc"+str(self._n_components)


  def _apply(self, data):
    if isinstance(data, (tuple, list,)):
      ret = []
      for cdata in data:
        if npCurrent.isfortran:
          ret.append( self._kpca.transform(cdata.T).T[0:self._n_components,:] )
        else:
          ret.append( self._kpca.transform(cdata)[:,0:self._n_components] )
    else:
      ret = self._kpca.transform(data)[0:self._n_components]
      if npCurrent.isfortran:
        ret = self._kpca.transform(data.T).T[0:self._n_components,:]
      else:
        ret = self._kpca.transform(data)[:,0:self._n_components]
    return ret

  #def _undo(self, data):
  #  if isinstance(data, (tuple, list,)):
  #    ret = []
  #    for i, cdata in enumerate(data):
  #      ret.append( self._kpca.inverse_transform(cdata) )
  #  else:
  #    ret = self._kpca.inverse_transform(cdata)
  #  return ret

class RingerPU(Norm1):
  """
    Applies norm-1 + Pileup normalization
  """
  takesParamsFromData = False

  def __init__(self, d = {}, **kw):
    d.update( kw ); del kw
    PrepObj.__init__( self, d )
    self._pileupThreshold  = d.pop( 'pileupThreshold'  , 60  )
    checkForUnusedVars(d, self._warning )
    del d

  def __str__(self):
    """
      String representation of the object.
    """
    return "RingerPU(pumax=%1.2f"%(self._pileupThreshold)

  def shortName(self):
    """
      Short string representation of the object.
    """
    return "rPU"

  def psprocessing(self, data, extra, pCount = 0):
    self._info('Pre-sort processing...')
    self._pileupThreshold = 0.6
    from TuningTools.dataframe import BaseInfo
    if isinstance(data, (tuple, list,)):
      ret = []
      for i, cdata in enumerate(data):
        cdata = np.concatenate((cdata, extra[i][BaseInfo.PileUp]),axis=1)
        ret.append(cdata)
    else:
      ret = np.concatenate((data, extra[i][BaseInfo.PileUp]),axis=1)
    return ret, extra

  def _apply(self, data):
    if isinstance(data, (tuple, list,)):
      ret = []
      for i, cdata in enumerate(data):
        rings = cdata[npCurrent.access(pidx=(0, 100))]
        rings /= self._retrieveNorm(rings)
        cdata[npCurrent.access(pidx=100)] /= self._pileupThreshold
        ret.append(cdata)
    else:
      data /= np.append( self._retrieveNorm( data[npCurrent.access( pidx=(0, 100))])
                       , self._pileupThreshold )
      ret = data
    return ret

class RingerEtaMu(Norm1):
  """
    Applies norm-1+MapMinMax to data
  """
  takesParamsFromData = False

  def __init__(self, d = {}, **kw):
    d.update( kw ); del kw
    PrepObj.__init__( self, d )
    self._etamin           = d.pop( 'etamin'           , 0   )
    self._etamax           = d.pop( 'etamax'           , 0.6 )
    self._pileupThreshold  = d.pop( 'pileupThreshold'  , 33  )
    checkForUnusedVars(d, self._warning )
    del d

  def __str__(self):
    """
      String representation of the object.
    """
    return "RingerEtaMu(etamin=%1.2f,etamax=%1.2f,mumax=%1.2f)"%(self._etamin,self._etamax,self._pileupThreshold)

  def shortName(self):
    """
      Short string representation of the object.
    """
    return "etapu"


  def psprocessing(self, data, extra, pCount = 0):
    self._info('Pre-sort processing...')
    from TuningTools.dataframe import BaseInfo
    if isinstance(data, (tuple, list,)):
      ret = []
      for i, cdata in enumerate(data):
        cdata = np.concatenate((cdata, extra[i][BaseInfo.Eta], extra[i][BaseInfo.PileUp]),axis=1)
        ret.append(cdata)
    else:
      ret = np.concatenate((data, extra[i][BaseInfo.Eta], extra[i][BaseInfo.PileUp]),axis=1)
    return ret, extra

  def _apply(self, data):

    if isinstance(data, (tuple, list,)):
      ret = []
      #if len(data):
      #  mean = np.mean( np.abs(np.sum(data[0][npCurrent.access(pidx=(0, 100))], axis=npCurrent.pdim ) ), )
      for i, cdata in enumerate(data):
        rings = cdata[npCurrent.access(pidx=(0, 100))]
        rings /= self._retrieveNorm(rings)
        #rings /= mean
        eta = cdata[npCurrent.access(pidx=100)]
        cdata[npCurrent.access(pidx=100)] = (np.abs(eta) - self._etamin)*np.sign(eta)/float(self._etamax-self._etamin)
        cdata[npCurrent.access(pidx=101)] /= self._pileupThreshold
        ret.append(cdata)
    else:
      rings = data[npCurrent.access(pidx=(0, 100))]
      rings /= self._retrieveNorm(rings)
      eta = data[npCurrent.access(pidx=100)]
      data[npCurrent.access(pidx=100)] = (np.abs(eta) - self._etamin)*np.sign(eta)/float(self._etamax-self._etamin)
      data[npCurrent.access(pidx=101)] /= self._pileupThreshold
      ret  = data
    return ret

class RingerEtEtaMu(Norm1):
  """
    Applies norm-1+MapMinMax to data
  """
  takesParamsFromData = False

  def __init__(self, d = {}, **kw):
    d.update( kw ); del kw
    PrepObj.__init__( self, d )
    self._etamin           = d.pop( 'etamin'           , 0      )
    self._etamax           = d.pop( 'etamax'           , 0.6    )
    self._etmin            = d.pop( 'etmin'            , 30000. )
    self._etmax            = d.pop( 'etmax'            , 40000. )
    self._pileupThreshold  = d.pop( 'pileupThreshold'  , 33.    )
    checkForUnusedVars(d, self._warning )
    del d

  def __str__(self):
    """
      String representation of the object.
    """
    return "RingerEtEtaMu(etmin=%d,etmax=%d,etamin=%1.2f,etamax=%1.2f,mumax=%1.2f)"%(self._etmin/1e3,self._etmax/1e3
                                                                                   ,self._etamin,self._etamax
                                                                                   ,self._pileupThreshold)

  def shortName(self):
    """
      Short string representation of the object.
    """
    return "etetapu"


  def psprocessing(self, data, extra, pCount = 0):
    self._info('Pre-sort processing...')
    from TuningTools.dataframe import BaseInfo
    if isinstance(data, (tuple, list,)):
      ret = []
      for i, cdata in enumerate(data):
        cdata = np.concatenate((cdata, extra[i][BaseInfo.Eta], extra[i][BaseInfo.Et], extra[i][BaseInfo.PileUp]),axis=npCurrent.pdim)
        ret.append(cdata)
    else:
      ret = np.concatenate((data, extra[i][BaseInfo.Eta], extra[i][BaseInfo.Et], extra[i][BaseInfo.PileUp]),axis=npCurrent.pdim)
    return ret, extra

  def _apply(self, data):

    if isinstance(data, (tuple, list,)):
      ret = []
      for i, cdata in enumerate(data):
        rings = cdata[npCurrent.access(pidx=(0, 100))]
        rings /= self._retrieveNorm(rings)
        eta = cdata[npCurrent.access(pidx=100)]
        et = cdata[npCurrent.access(pidx=101)]
        cdata[npCurrent.access(pidx=100)] = (np.abs(eta) - self._etamin)*np.sign(eta)/float(self._etamax-self._etamin)
        cdata[npCurrent.access(pidx=101)] = (et - self._etmin)/float(self._etmax-self._etmin)
        cdata[npCurrent.access(pidx=102)] /= self._pileupThreshold
        ret.append(cdata)
    else:
      rings = data[npCurrent.access(pidx=(0, 100))]
      rings /= self._retrieveNorm(rings)
      eta = data[npCurrent.access(pidx=100)];et = data[npCurrent.access(pidx=101)]
      data[npCurrent.access(pidx=100)] = (np.abs(eta) - self._etamin)*np.sign(eta)/float(self._etamax-self._etamin)
      data[npCurrent.access(pidx=101)] = (et - self._etmin)/float(self._etmax-self._etmin)
      data[npCurrent.access(pidx=102)] /= self._pileupThreshold
      ret  = data
    return ret

class RingerFilterMu(PrepObj):
  '''
  Applies a filter at the mu values for training.
  '''

  _streamerObj = LoggerRawDictStreamer(toPublicAttrs = {'_mu_min','_mu_max'})
  _cnvObj = RawDictCnv(toProtectedAttrs = {'_mu_min','_mu_max'})
  takesParamsFromData = False

  def __init__(self, mu_min=0, mu_max=70):
    super(RingerFilterMu, self).__init__()
    self._mu_min = mu_min
    self._mu_max = mu_max

  def __str__(self):
    return 'RingerFilterMu'

  def shortName(self):
    return 'RinFMU'

  def psprocessing(self, data, extra, pCount = 0):
    from TuningTools.dataframe import BaseInfo
    if isinstance(data, (tuple, list,)):
      self._verbose('Data is in list format...')
      ret = []
      for i, (cdata, cextra) in enumerate(zip(data, extra)):
        self._debug('Filtering mu values %d...' % i)
        cdata = cdata[np.squeeze(((cextra[BaseInfo.PileUp] >= self._mu_min) & (cextra[BaseInfo.PileUp] <= self._mu_max)),1)]
        ret.append(cdata)
    else:
      self._debug('Filtering mu values...')
      ret = np.concatenate((data, extra[i][BaseInfo.PileUp]),axis=npCurrent.pdim)
      ret = ret[npCurrent.access(oidx=((ret[:,-1] >= self._mu_min) & (ret[:,-1] <= self._mu_max)))]
    return ret, extra




class RingerLayerSegmentation(PrepObj):
  """
    Get the slice of rings for the selected ATLAS calo layer
  """
  _streamerObj = LoggerRawDictStreamer(toPublicAttrs = {'_layer'})
  _cnvObj = RawDictCnv(toProtectedAttrs = {'_layer'})
  takesParamsFromData = False

  def __init__(self, d = {}, **kw):
    d.update( kw ); del kw
    PrepObj.__init__( self, d )
    self._layer = d.pop('layer' , RingerLayer.PS)
    checkForUnusedVars(d, self._warning )
    del d
    ### Get the slice
    if self._layer is RingerLayer.PS:
      self._slice = (0,7)
    elif self._layer is RingerLayer.EM1:
      self._slice = (8, 71)
    elif self._layer is RingerLayer.EM2:
      self._slice = (72, 79)
    elif self._layer is RingerLayer.EM3:
      self._slice = (80,87)
    elif self._layer is RingerLayer.HAD1:
      self._slice = (88,91)
    elif self._layer is RingerLayer.HAD2:
      self._slice = (92,95)
    elif self._layer is RingerLayer.HAD3:
      self._slice = (96,99)
    else:
      self._logger.fatal('Option not supported: %d', self._layer)

  def __str__(self):
    """
      String representation of the object.
    """
    return "RingerLayer%sPat" % RingerLayer.tostring(self._layer)

  def shortName(self):
    """
      Short string representation of the object.
    """
    return "%sP" % RingerLayer.tostring(self._layer)

  def _apply(self, data):
    self._logger.info('Applying Segmentation between: ring%d->ring%d',self._slice[0],self._slice[1])
    try:
      if isinstance(data, (tuple, list,)):
        ret = []
        for cdata in data:
          ret.append( cdata[npCurrent.access( pidx=slice(self._slice[0],self._slice[1]+1), oidx=':'  ) ] )
      else:
        ret = data[ npCurrent.access( pidx=slice(self._slice[0],self._slice[1]+1), oidx=':'  ) ]
    except IndexError, e:
      self._fatal("Data has not enought patterns!\n%s", str(e), IndexError)
    return ret




class _PreProcMergeRDS( LoggerRawDictStreamer ):
  def treatDict(self, obj, raw):
    """
    Add efficiency value to be readable in matlab
    """
    raw['_ppChains'] = [o.toRawObj() for o in obj._ppChains]
    return RawDictStreamer.treatDict( self, obj, raw )

class _PreProcMergeRDC( RawDictCnv ):
  def treatObj( self, obj, d ):
    from Gaugi.RawDictStreamable import retrieveRawDict
    obj._ppChains = [retrieveRawDict(o) for o in d['_ppChains']]
    #obj._ppchains = [PreProcCollection.fromRawObj(o) for o in d['_ppchains']]
    return obj

class PreProcMerge(PrepObj):
  """
    This class is responsible to merge n preproc chains for
    each dataset. Usually this will used when you have more
    than one dataset passed to the tuning. E.g. calo+track
    where you will have one normalization (ppchain) for each
    data object.
  """
  _streamerObj = _PreProcMergeRDS()
  _cnvObj = _PreProcMergeRDC()
  takesParamsFromData = False

  def __init__(self, d = {}, **kw):
    d.update( kw ); del kw
    PrepObj.__init__( self, d )
    self._ppChains = d.pop('ppChains', [])
    checkForUnusedVars(d, self._warning )
    del d

  def _apply( self, data):
    ret = []
    for i, cdata in enumerate(data):
      ret.append( self._ppChains[i](cdata) )
    return ret

  def __str__(self):
    """
      String representation of the object.
    """
    string = ''
    for pp in self._ppChains:
      string += (str(pp) + ',')
    string = string[:-1]
    return string

  def shortName(self):
    # reduce name
    string = ''; l=list()
    for pp in self._ppChains:
      l.append(pp.shortName())
    for n in set(l):
      string += (str(l.count(n))+n+'-')
    string = string[:-1]
    return string

  def isRevertible(self):
    """
      Check whether the PreProc is revertible
    """
    return False

  def takeParams(self, trnData):
    """
      Take pre-processing parameters for all objects in chain.
    """
    ret = []
    for i, cdata in enumerate(trnData):
      self._logger.debug('Apply %s to data[%d]...',str(self._ppChains[i]),i)
      ret.append( self._ppChains[i].takeParams(cdata) )
    return trnData






class _StateReductionFactorRDS(LoggerRawDictStreamer):
  def treatDict(self, obj, raw):
    """
    Add efficiency value to be readable in matlab
    """
    raw['_generator'] = obj._seed[0]
    raw['_state']     = obj._seed[1]
    raw['_lstate']    = obj._seed[2]
    raw['_idx']       = obj._seed[3]
    raw['_fidx']      = obj._seed[4]
    return LoggerRawDictStreamer.treatDict( self, obj, raw )

class _StateReductionFactorRDC(RawDictCnv):
  def treatObj( self, obj, d ):
    seed = (d['_generator'], d['_state'], d['_lstate'], d['_idx'], d['_fidx'])
    obj._seed = seed
    for key in ('_generator', '_state', '_lstate', '_idx', '_fidx'): obj.__dict__.pop(key)
    return obj

class StatReductionFactor(PrepObj):
  """
    Reduce the statistics available by the specified reduction factor
  """

  _streamerObj = _StateReductionFactorRDS(toPublicAttrs = {'_factor',}, transientAttrs={'_seed',})
  _cnvObj = _StateReductionFactorRDC(toProtectedAttrs = {'_factor',})
  takesParamsFromData = False

  def __init__(self, factor = 1.1, seed = None, d = {}, **kw):
    d.update( kw ); del kw
    PrepObj.__init__( self, d )
    checkForUnusedVars(d, self._warning )
    self._factor = factor
    self._seed = self._genState(seed)
    del d

  @property
  def factor(self):
    return self._factor

  def __str__(self):
    "String representation of the object."
    return "StatReductionFactor(%.2f)" % self._factor

  def shortName(self):
    "Short string representation of the object."
    return ( "SRed%.2f" % self._factor ).replace('.','_')

  def _genState(self, seed = None):
    old_state = np.random.get_state()
    # Generate new state:
    np.random.seed(None)
    state = np.random.get_state()
    np.random.set_state(old_state)
    return state

  def psprocessing(self, data, extra, pCount = 0):
    " Apply stats reduction "
    # We remove stats at random in the beginning of the process, so all sorts
    # have the same statistics available
    from TuningTools import BaseInfo
    # TODO Make sure that all patterns have the same number of observations
    old_state = np.random.get_state()
    np.random.set_state( self._seed )
    if isinstance(data, (tuple, list,)):
      ret = []; ret2 = []
      for i, (cdata,edata) in enumerate(zip(data, extra)):
        # We want to shuffle the observations, since shuffle method only
        # shuffles the first dimension, then:
        osize = cdata.shape[npCurrent.odim]
        p = np.random.permutation( osize )
        nsize = int(round(osize/self._factor))
        self._info("Reducing class %i size from %d to %d", i, osize, nsize)
        p = npCurrent.array(p[:nsize], dtype=np.uint64 )
        cdata = cdata[ npCurrent.access( pidx=':', oidx = p ) ]
        ret.append(cdata)
        ret2.append( [edata[i][npCurrent.access( pidx=':', oidx = p ) ] for i in xrange(BaseInfo.nInfo)] )
    else:
      self._fatal('Cannot reduce classes size with concatenated data input')
    # Recover previous state
    np.random.set_state(old_state)
    return ret, ret2


class StatUpperLimit(PrepObj):
  """
    Reduce the statistics available by the specified reduction factor
  """

  _streamerObj = LoggerRawDictStreamer(toPublicAttrs = {'_signalUpperLimit','_backgroundUpperLimit'})
  _cnvObj = RawDictCnv(toProtectedAttrs = {'_signalUpperLimit','_backgroundUpperLimit'})
  takesParamsFromData = False

  def __init__(self, signalUpperLimit = None, backgroundUpperLimit = None, d = {}, **kw):
    d.update( kw ); del kw
    PrepObj.__init__( self, d )
    checkForUnusedVars(d, self._warning )
    self._signalUpperLimit = signalUpperLimit
    self._backgroundUpperLimit = backgroundUpperLimit
    del d

  @property
  def sgnUL(self):
    return self._signalUpperLimit

  @property
  def bkgUL(self):
    return self._backgroundUpperLimit

  def __str__(self):
    "String representation of the object."
    display = ','.join(filter(lambda x: x != 'None', [str(a) for a in [self.sgnUL, self.bkgUL]]))
    return "StatUpperLimit(%s)" % (display if display else 'NO_LIMIT')

  def shortName(self):
    "Short string representation of the object."
    from Gaugi import reducePowerOf10Str
    l = [k + reducePowerOf10Str(a) for k, a in zip(['s', 'b'],[self.sgnUL, self.bkgUL]) if a is not None]
    display = '_'.join(l)
    return "UL%s" % display if display else '_NOPARAM'

  def concatenate(self, data, _):
    " Apply stats reduction "
    # We remove stats at random in the beginning of the process, so all sorts
    # have the same statistics available
    if isinstance(data, (tuple, list,)):
      ret = []
      for i, cdata in enumerate(data):
        # We want to shuffle the observations, since shuffle method only
        # shuffles the first dimension, then:
        if npCurrent.odim == 0:
          np.random.shuffle( cdata )
        else:
          cdata = cdata.T
          np.random.shuffle( cdata.T )
          cdata = cdata.T
        origSize = cdata.shape[npCurrent.odim]
        newSize = int(round(origSize/self._factor))
        self._info("Reducing class %i size from %d to %d", i, origSize, newSize)
        cdata = cdata[ npCurrent.access( oidx=(0,newSize) ) ]
        ret.append(cdata)
    else:
      self._fatal('Cannot reduce classes size with concatenated data input')
    return ret

class PreProcChain ( Logger ):
  """
    The PreProcChain is the object to hold the pre-processing chain to be
    applied to data. They will be sequentially applied to the input data.
  """

  # Use class factory
  __metaclass__ = LimitedTypeStreamableList
  #_streamerObj  = LoggerLimitedTypeListRDS( level = LoggingLevel.VERBOSE )
  #_cnvObj       = LimitedTypeListRDC( level = LoggingLevel.VERBOSE )

  # These are the list (LimitedTypeList) accepted objects:
  _acceptedTypes = (PrepObj,)

  @property
  def takesParamsFromData( self ):
    #return True
    for pp in self:
      if pp.takesParamsFromData: return True
    return False

  def __init__(self, *args, **kw):
    from Gaugi.LimitedTypeList import _LimitedTypeList____init__
    _LimitedTypeList____init__(self, *args)
    Logger.__init__(self, kw)

  def __call__(self, data, revert = False, saveArgsDict = None):
    """
      Apply/revert pre-processing chain.
    """
    if not self:
      self._warning("No pre-processing available in this chain.")
      return
    for pp in self:
      data = pp(data, revert)
      self._save( data, pp, saveArgsDict )
    return data

  def __str__(self):
    """
      String representation of the object.
    """
    string = 'NoPreProc'
    if self:
      string = ''
      for pp in self:
        string += (str(pp) + '->')
      string = string[:-2]
    return string

  def shortName(self):
    string = 'NoPreProc'
    if self:
      string = ''
      for pp in self:
        string += (pp.shortName() + '-')
      string = string[:-1]
    return string

  def get(self, t):
    " Return first pre-processing of type <t>"
    if not self.has( t ):
      self._fatal( "No pre-proc of type t available", TypeError )
    return self[ [(type(o) is t) for o in self].index(True) ]

  def has(self, t):
    " Return first pre-processing of type <t>"
    for o in self:
      if type(o) is t: return True
    return False

  def isRevertible(self):
    """
      Check whether the PreProc is revertible
    """
    for pp in self:
      if not pp.isRevertible():
        return False
    return True

  def takeParams(self, trnData, saveArgsDict = None):
    """
      Take pre-processing parameters for all objects in chain.
    """
    if not self:
      self._warning("No pre-processing available in this chain.")
      return
    for pp in self:
      trnData = pp.takeParams(trnData)
      self._save( trnData, pp, saveArgsDict )
    return trnData

  def _save(self, data, pp, saveArgsDict):
    if saveArgsDict is not None:
      from Gaugi import save, prependAppendToFileName
      from copy import copy
      if not 'protocol' in saveArgsDict: saveArgsDict['protocol'] = 'mat'
      for s, d in zip(['signal', 'background'],data):
        lDict = copy( saveArgsDict )
        lDict['o'] = { s : d }
        lDict['filename'] = prependAppendToFileName( s, lDict['filename'], str(pp) )
        self._info('Saving %s pre-processing data at path: %s',pp,lDict['filename'])
        save( **lDict )

  def psprocessing(self, trnData, extraData, pCount = 0):
    """
      Pre-sort processing
    """
    if not self:
      self._warning("No pre-processing available in this chain.")
      return
    for pp in self:
      trnData, extraData = pp.psprocessing(trnData, extraData, pCount)

    return trnData, extraData

  def setLevel(self, value):
    """
      Override Logger setLevel method so that we can be sure that every
      pre-processing will have same logging level than that was set for the
      PreProcChain instance.
    """
    for pp in self:
      pp.level = LoggingLevel.retrieve( value )
    self._level = LoggingLevel.retrieve( value )
    self._logger.setLevel(self._level)

  level = property( Logger.getLevel, setLevel )


class PreProcCollection( object ):
  """
    The PreProcCollection will hold a series of PreProcChain objects to be
    tested. The TuneJob will apply them one by one, looping over the testing
    configurations for each case.
  """

  # Use class factory
  __metaclass__ = LimitedTypeStreamableList
  #_streamerObj  = LimitedTypeListRDS( level = LoggingLevel.VERBOSE )
  #_cnvObj       = LimitedTypeListRDC( level = LoggingLevel.VERBOSE )
  _acceptedTypes = type(None),

  def has(self, t):
    " Return first pre-processing of type <t>"
    for o in self:
      if o is not None and o.has(t): return True
    return False

  def all(self, t):
    " Return whether all PreProcessing Chains have type t"
    for o in self:
      if o is None: return False
      elif type(o) is PreProcChain:
        if not o.has(t): return False
      elif not o.all(t): return False
    return True

# The PreProcCollection can hold a collection of itself besides PreProcChains:
PreProcCollection._acceptedTypes = PreProcChain, PreProcCollection, type(None)

def fixPPCol( var, nSorts = 1, nEta = 1, nEt = 1, level = None ):
  """
    Helper method to correct variable to be a looping bound collection
    correctly represented by a LoopingBoundsCollection instance.
  """
  tree_types = (PreProcCollection, PreProcChain, list, tuple )
  from Gaugi import firstItemDepth
  try:
    # Retrieve collection maximum depth
    depth = firstItemDepth(var, tree_types = tree_types)
  except GeneratorExit:
    depth = 0
  if depth < 5:
    if depth == 0:
      var = [[[[var]]]]
    elif depth == 1:
      var = [[[var]]]
    elif depth == 2:
      var = [[var]]
    elif depth == 3:
      var = [var]
    # We also want to be sure that they are in correct type and correct size:
    from Gaugi import inspect_list_attrs
    var = inspect_list_attrs(var, 3, PreProcChain,      tree_types = tree_types, deepcopy = True,               level = level   )
    var = inspect_list_attrs(var, 2, PreProcCollection, tree_types = tree_types, dim = nSorts, name = "nSorts", deepcopy = True )
    var = inspect_list_attrs(var, 1, PreProcCollection, tree_types = tree_types, dim = nEta,   name = "nEta",   deepcopy = True )
    var = inspect_list_attrs(var, 0, PreProcCollection, tree_types = tree_types, dim = nEt,    name = "nEt",    deepcopy = True )
  else:
    raise ValueError("Pre-processing dimensions size is larger than 5.")

  return var




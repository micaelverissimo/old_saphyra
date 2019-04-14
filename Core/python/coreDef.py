__all__ = [ 'hasExmachina', 'hasFastnet', 'hasKeras', 'TuningToolCores'
          , 'AvailableTuningToolCores', 'CoreConfiguration', 'coreConf'
          , 'NumpyConfiguration', 'npCurrent'
          , 'DataframeConfiguration' , 'dataframeConf'
          #, 'TuningToolsGit'
          ]

import os, pkgutil

#hasExmachina = bool( pkgutil.find_loader( 'exmachina' )      )
hasExmachina = False # Force disable, decrepted
hasFastnet   = bool( pkgutil.find_loader( 'libTuningTools' ) or pkgutil.find_loader( 'libTuningToolsLib' ) )
hasKeras     = bool( pkgutil.find_loader( 'keras' )          )

from Gaugi import ( EnumStringification, npConstants, Configure
                       , EnumStringificationOptionConfigure, Holder
                       , NotSet, ArgumentError)

#TuningToolsGit = GitConfiguration(  'TuningToolsGit', __file__, tagArgStr = '--tuning-tools-info')

class TuningToolCores( EnumStringification ):
  _ignoreCase = True
  ShallowMode = 0
  FastNet = 1
  ExMachina = 2
  keras = 3

class AvailableTuningToolCores( EnumStringification ):
  _ignoreCase = True
  ShallowMode = 0
  if hasFastnet: FastNet = 1
  if hasExmachina: ExMachina = 2
  if hasKeras: keras = 3

  @classmethod
  def retrieve(cls, val):
    ret = TuningToolCores.retrieve( val )
    if not cls.tostring( ret ):
      raise ValueError("TuningTool core %s is not available in the current system." % TuningToolCores.tostring( ret ))
    return ret

class _ConfigureCoreFramework( EnumStringificationOptionConfigure ):
  """
  Singleton class for configurating the core framework used tuning data

  It also specifies how the numpy data should be represented for that specified
  core.
  """

  _enumType = TuningToolCores

  core = property( EnumStringificationOptionConfigure.get, EnumStringificationOptionConfigure.set )

  def auto( self ):
    self._logger.debug("Using automatic configuration for core specification.")
    # Check whether we can retrieve from the parser.
    from TuningTools.parsers.BaseModuleParser import coreFrameworkParser
    import sys
    try:
      args, argv = coreFrameworkParser.parse_known_args()
      if args.core_framework not in (None, NotSet):
        if not self.configured(): self.core = args.core_framework
        # Consume option
        sys.argv = sys.argv[:1] + argv
      else:
        self.core = self.default()
    except (ArgumentError, ValueError) as e:
      self._logger.verbose("Ignored argument parsing error:\n %s", e )
      self._logger.debug("Using default TuningTools core (%s).", AvailableTuningToolCores.tostring(self.default()))
      # Couldn't retrieve from the parser, retrieve default:
      self.core = self.default()

  def default( self ):
    if hasFastnet:
      core = TuningToolCores.FastNet
    elif hasKeras:
      core = TuningToolCores.keras
    elif hasExmachina:
      core = TuningToolCores.ExMachina
    else:
      core = TuningToolCores.ShallowMode
      self._debug("No core available.")
    return core

  def numpy_wrapper(self):
    """
    Returns the api instance which is to be used to read the data
    """
    import numpy as np
    if self.core is TuningToolCores.ExMachina:
      # Define the exmachina numpy constants
      kwargs = { 'useFortran' : True, 'fp_dtype' : np.float64, 'int_dtype' : np.int64 }
    elif self.core is TuningToolCores.FastNet:
      kwargs = { 'useFortran' : False, 'fp_dtype' : np.float32, 'int_dtype' : np.int32 }
    elif self.core is TuningToolCores.keras:
      from keras.backend import backend
      if backend() == "theano": # Theano copies data if input is not c-contiguous
        kwargs = { 'useFortran' : False, 'fp_dtype' : np.float32, 'int_dtype' : np.int32 }
      elif backend() == "tensorflow": # tensorflow copies data if input is not fortran-contiguous
        kwargs = { 'useFortran' : False, 'fp_dtype' : np.float32, 'int_dtype' : np.int32 }
    else:
      kwargs = { 'useFortran' : False, 'fp_dtype' : np.float32, 'int_dtype' : np.int32 }
    return npConstants( **kwargs )

  def core_framework(self):
    if self.core is TuningToolCores.FastNet:
      try:
        from libTuningTools import TuningToolPyWrapper as RawWrapper
      except ImportError:
        from libTuningToolsLib import TuningToolPyWrapper as RawWrapper
      import sys, os
      from ctypes import c_uint
      class TuningToolPyWrapper( RawWrapper, object ):
        def __init__( self
                    , level
                    , useColor = not(int(os.environ.get('RCM_GRID_ENV',0)) or not(sys.stdout.isatty()))
                    , seed = None):
          self._doMultiStop = False
          if seed is None:
            RawWrapper.__init__(self, level, useColor)
          else:
            RawWrapper.__init__(self, int(level), bool(useColor), int(seed))

        @property
        def multiStop(self):
          return self._doMultiStop

        @multiStop.setter
        def multiStop(self, value):
          if value:
            self._doMultiStop = True
            self.useAll()
          else:
            self._doMultiStop = False
            self.useSP()

      # End of TuningToolPyWrapper
      return TuningToolPyWrapper
    elif self.core is TuningToolCores.ExMachina:
      import exmachina
      return exmachina
    elif self.core is TuningToolCores.keras:
      import keras
      return keras

# The singleton holder
CoreConfiguration = Holder( _ConfigureCoreFramework() )

# Standard core configuration object
coreConf = CoreConfiguration()

class _ConfigureNumpyWrapper( Configure ):
  """
  Wrapper for numpy module setting defaults accordingly to the core used.
  """

  wrapper = property( Configure.get, Configure.set )

  def auto( self ):
    self._logger.debug("Using automatic configuration for numpy wrapper.")
    self.wrapper = coreConf.numpy_wrapper()
    self._logger.debug("Retrieved the following numpy wrapper:\n%s", self.wrapper)

  def __getattr__(self, attr ):
    if hasattr( self.wrapper, attr ):
      return getattr( self.wrapper, attr )
    else:
      raise AttributeError( attr )

# The singleton holder
NumpyConfiguration = Holder( _ConfigureNumpyWrapper() )

# Standard numpy configuration object
npCurrent = NumpyConfiguration()

from TuningTools.dataframe.EnumCollection import Dataframe as DataframeEnum

class _ConfigureDataframe( EnumStringificationOptionConfigure ):
  """
  Singleton class for configurating the data framework used for reading the
  files and generating the tuning-data
  """

  _enumType = DataframeEnum

  dataframe = property( EnumStringificationOptionConfigure.get, EnumStringificationOptionConfigure.set )

  def auto_retrieve_testing_sample( self, sample ):
    self._sample = sample

  def can_autoconfigure( self ):
    " Returns whether the dataframe can autoconfigure itself"
    if hasattr(self, '_sample') and isinstance(self._sample, (dict, list, basestring)):
      return True
    return False

  def auto( self ):
    self._debug("Using automatic configuration for dataframe specification.")
    # Check whether we can retrieve from the parser.
    from TuningTools.parsers.BaseModuleParser import dataframeParser
    import sys
    try:
      args, argv = dataframeParser.parse_known_args()
      if args.data_framework not in (None, NotSet):
        self.dataframe = args.data_framework
        # Consume option
        sys.argv = sys.argv[:1] + argv
    except (ArgumentError, ValueError) as e:
      self._debug("Ignored argument parsing error:\n %s", e )
      pass
    from Gaugi import csvStr2List, expandFolders
    if not self.configured() and not self.can_autoconfigure():
      self._fatal("Cannot auto-configure which dataframe to use because no sample was specified via the auto_retrieve_sample() method.")
    elif not self.configured():
      if isinstance(self._sample, dict):
        for key in self._sample:
          if 'elCand2_' in key:
            self.dataframe = DataframeEnum.SkimmedNtuple_v2
          else:
            self.dataframe = DataframeEnum.PhysVal_v2
          break
      elif self._sample and isinstance(self._sample, list):
        if not isinstance(self._sample[0], basestring ):
          self._fatal("Cannot autoconfigure dataframe using the following list: %r", self._sample )
        fList = csvStr2List ( self._sample[0] )
        fList = expandFolders( fList )
        for inputFile in fList:
          self._checkFile( inputFile )
          if self.configured(): break
      elif isinstance( self._sample, basestring ):
        if os.path.isdir( self._sample ):
          fList = expandFolders( self._sample )
          for inputFile in fList:
            self._checkFile( inputFile )
            if self.configured(): break
        else:
          self._checkFile( self._sample )
      if not self.configured():
        self._fatal("Couldn't autoconfigure using source: %r", self._sample)

  def _checkFile( self, inputFile ):
    from ROOT import TFile
    f  = TFile.Open(inputFile, 'read')
    if not f or f.IsZombie(): return
    self.dataframe = DataframeEnum.PhysVal
    for key in f.GetListOfKeys():
      if key.GetName == "ZeeCanditate":
        self.dataframe = DataframeEnum.SkimmedNtuple
        break

  def api(self):
    """
    Returns the api instance which is to be used to read the data
    """
    if self.dataframe is DataframeEnum.PhysVal:
      from TuningTools.dataframe.ReadPhysVal import readData
    elif self.dataframe is DataframeEnum.PhysVal_v2:
      from TuningTools.dataframe.ReadPhysVal_v2 import readData
    elif self.dataframe is DataframeEnum.SkimmedNtuple:
      from TuningTools.dataframe.ReadSkimmedNtuple import readData
    elif self.dataframe is DataframeEnum.SkimmedNtuple_v2:
      from TuningTools.dataframe.ReadSkimmedNtuple_v2 import readData
    
    return readData

# The singleton holder
DataframeConfiguration = Holder( _ConfigureDataframe() )

# Standard dataframe configuration object
dataframeConf = DataframeConfiguration()

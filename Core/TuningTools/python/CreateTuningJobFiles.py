__all__ = ['TuningJobConfigArchieve', 'CreateTuningJobFiles', 'createTuningJobFiles']

from Gaugi.LoopingBounds import *
from Gaugi.LoopingBounds import SeqLoopingBounds, SeqLoopingBoundsCollection, transformToSeqBounds

from Gaugi import Logger, checkForUnusedVars, save, load, mkdir_p, retrieve_kw
from TuningTools.coreDef import coreConf,TuningToolCores

class TuningJobConfigArchieve( Logger ):
  """
  Context manager for TuningJob configuration archives
  """

  _type = 'ConfJobFile'
  _version = 2
  _neuronBounds = None
  _sortBounds = None
  _initBounds = None
  _modelBounds = None

  def __init__(self, filePath = None, **kw):
    """
    Either specify the file path where the file should be read or the data
    which should be appended to it:

    with TuningJobConfigArchieve("/path/to/file") as data:
      BLOCK

    TuningJobConfigArchieve( "file/path", neuronBounds = ...,
                                          sortBounds = ...,
                                          initBounds = ... )
    """
    Logger.__init__(self, kw)
    self._filePath = filePath
    self.neuronBounds = kw.pop('neuronBounds', None)
    self._sortBounds = kw.pop('sortBounds', None)
    self._initBounds = kw.pop('initBounds', None)
    # for keras core only
    self._modelBounds = kw.pop('modelBounds', None)

    checkForUnusedVars( kw, self._warning )

  @property
  def filePath( self ):
    return self._filePath

  @filePath.setter
  def filePath( self, val ):
    self._filePath = val

  @property
  def modelBounds( self ):
    return self._neuronBounds

  @modelBounds.setter
  def modelBounds( self, val ):
    if not val is None and not isinstance(val, list):
      self._fatal("Attempted to set modelBounds to an object not of LoopingBounds type.",ValueError)
    else:
      self._modelBounds = val


  @property
  def neuronBounds( self ):
    return self._neuronBounds

  @neuronBounds.setter
  def neuronBounds( self, val ):
    if not val is None and not isinstance(val, LoopingBounds):
      self._fatal("Attempted to set neuronBounds to an object not of LoopingBounds type.",ValueError)
    else:
      self._neuronBounds = val

  @property
  def sortBounds( self ):
    return self._sortBounds

  @sortBounds.setter
  def sortBounds( self, val ):
    if not val is None and not isinstance(val, LoopingBounds):
      self._fatal("Attempted to set sortBounds to an object not of LoopingBounds type.", ValueError)
    else:
      self._sortBounds = val

  @property
  def initBounds( self ):
    return self._initBounds

  @initBounds.setter
  def initBounds( self, val ):
    if not val is None and not isinstance(val, LoopingBounds):
      self._fatal("Attempted to set initBounds to an object not of LoopingBounds type.",ValueError)
    else:
      self._initBounds = val

  def getData( self ):
    if not self._neuronBounds or \
         not self._sortBounds or \
         not self._initBounds:
      self._fatal("Attempted to retrieve empty data from TuningJobConfigArchieve.")
    return {'version' : self._version,
               'type' : self._type,
       'neuronBounds' : transformToMatlabBounds( self._neuronBounds ).getOriginalVec(),
         'sortBounds' : transformToPythonBounds( self._sortBounds ).getOriginalVec(),
         'initBounds' : transformToPythonBounds( self._initBounds ).getOriginalVec(),
         'modelBounds': self._modelBounds}

  def save(self, compress = True):
    return save( self.getData(), self._filePath, compress = compress )

  def __enter__(self):
    # Open file:
    jobConfig = load(self._filePath)
    try:
      if type(jobConfig) is dict:
        if jobConfig['type'] != self._type:
          self._fatal(("Input jobConfig file is not from jobConfig " 
              "type."))
        # Read configuration file to retrieve pre-processing, 
        if jobConfig['version'] >= 1:

          neuronBounds = MatlabLoopingBounds( jobConfig['neuronBounds'] )
          sortBounds   = PythonLoopingBounds( jobConfig['sortBounds']   )
          initBounds   = PythonLoopingBounds( jobConfig['initBounds']   )
          modelBounds  = [None for _ in neuronBounds()] 
          if jobConfig['version'] == 2:
            modelBounds = jobConfig['modelBounds']      

            if modelBounds and coreConf() is TuningToolCores.keras:
              from keras.models import model_from_json
              import json 
              for idx, model in enumerate(modelBounds):
                modelBounds[idx] = model_from_json( json.dumps(model, separators=(',', ':'))) if model else None
        else:
          self._fatal("Unknown job configuration version")
      elif type(jobConfig) is list: # zero version file (without versioning 
        # control):
        neuronBounds  = MatlabLoopingBounds( [jobConfig[0], jobConfig[0]] )
        sortBounds    = MatlabLoopingBounds( jobConfig[1] )
        initBounds    = MatlabLoopingBounds( jobConfig[2] )
        modelBounds   = None
      else:
        self._fatal("Unknown file type entered for config file.")
    except RuntimeError, e:
      self._fatal(("Couldn't read configuration file '%s': Reason:"
          "\n\t %s" % (self._filePath, e)))
    return neuronBounds, sortBounds, initBounds, modelBounds
    
  def __exit__(self, exc_type, exc_value, traceback):
    # Remove bounds
    self.neuronBounds = None 
    self.sortBounds = None 
    self.initBounds = None 
    self.modelBounds = None



class CreateTuningJobFiles(Logger):
  """
    An instance of this class can be used to create all the tuning job
    needed files but the data files (which should be created with CreateData
    instead).
  """

  def __init__( self, logger = None ):
    Logger.__init__( self, logger = logger )

  @classmethod
  def _retrieveJobLoopingBoundsCol( cls, varBounds, varWindow ):
    """
      Create window bounded variables from larger range.
    """
    varIncr = varBounds.incr()
    jobWindowList = LoopingBoundsCollection()
    for jobTuple in varBounds.window( varWindow ):
      if len(jobTuple) == 1:
        jobWindowList += MatlabLoopingBounds(jobTuple[0], jobTuple[0])
      elif len(jobTuple) == 0:
        self._fatal("Retrieved empty window.")
      else:
        jobWindowList += MatlabLoopingBounds(jobTuple[0], 
                                             varIncr, 
                                             jobTuple[-1])
    return jobWindowList


  def __call__(self, **kw):
    """
      Create a collection of tuning job configuration files at the output
      folder.
    """

    # Cross validation configuration
    outputFolder   = retrieve_kw( kw, 'outputFolder',       'jobConfig'       )
    neuronBounds   = retrieve_kw( kw, 'neuronBounds', SeqLoopingBounds(5, 20) )
    sortBounds     = retrieve_kw( kw, 'sortBounds',   PythonLoopingBounds(50) )
    nInits         = retrieve_kw( kw, 'nInits',                100            )
    # Output configuration
    nNeuronsPerJob = retrieve_kw( kw, 'nNeuronsPerJob',         1             )
    nSortsPerJob   = retrieve_kw( kw, 'nSortsPerJob',           1             )
    nInitsPerJob   = retrieve_kw( kw, 'nInitsPerJob',          100            )
    compress       = retrieve_kw( kw, 'compress',              True           )
    prefix         = retrieve_kw( kw, 'prefix'  ,             'job'           )
    # keras input model
    models         = retrieve_kw( kw, 'models'  ,            None             )
    

    # for keras only
    if models and coreConf() is TuningToolCores.keras:
      if not type(models) is list:  models = [models]
      import json
      from keras.models import Sequential
      for idx, model in enumerate(models):
        if type(model) is str:
          models[idx] = json.loads(model)
        elif type(model) is Sequential:
          models[idx] = json.loads(model.to_json())
        elif type(model) is dict:
          continue
        else:
          self._logger.fatal('model type is not supported')
      neuronBounds=[1,len(models)]

 
    if 'level' in kw: self.level = kw.pop('level')
    # Make sure that bounds variables are LoopingBounds objects:
    if not isinstance( neuronBounds, SeqLoopingBounds ):
      neuronBounds = SeqLoopingBounds(neuronBounds)
    if not isinstance( sortBounds, SeqLoopingBounds ):
      sortBounds   = PythonLoopingBounds(sortBounds)
    # and delete it to avoid mistakes:
    checkForUnusedVars( kw, self._warning )
    del kw

    if nInits < 1:
      self._fatal(("Cannot require zero or negative initialization "
          "number."), ValueError)

    # Do some checking in the arguments:
    nNeurons = len(neuronBounds)
    nSorts = len(sortBounds)
    if not nSorts:
      self._fatal("Sort bounds is empty.")
    if nNeuronsPerJob > nNeurons:
      self._warning(("The number of neurons per job (%d) is "
        "greater then the total number of neurons (%d), changing it "
        "into the maximum possible value."), nNeuronsPerJob, nNeurons )
      nNeuronsPerJob = nNeurons
    if nSortsPerJob > nSorts:
      self._warning(("The number of sorts per job (%d) is "
        "greater then the total number of sorts (%d), changing it "
        "into the maximum possible value."), nSortsPerJob, nSorts )
      nSortsPerJob = nSorts

    # Create the output folder:
    mkdir_p(outputFolder)

    # Create the windows in which each job will loop upon:
    neuronJobsWindowList = \
        CreateTuningJobFiles._retrieveJobLoopingBoundsCol( neuronBounds, 
                                                           nNeuronsPerJob )
    sortJobsWindowList = \
        CreateTuningJobFiles._retrieveJobLoopingBoundsCol( sortBounds, 
                                                           nSortsPerJob )
    initJobsWindowList = \
        CreateTuningJobFiles._retrieveJobLoopingBoundsCol( \
          PythonLoopingBounds( nInits ), \
          nInitsPerJob )


    # Loop over windows and create the job configuration
    for idx, neuronWindowBounds in enumerate(neuronJobsWindowList()):
      for sortWindowBounds in sortJobsWindowList():
        for initWindowBounds in initJobsWindowList():
          
          modelWindowBounds = []
          self._debug(('Retrieved following job configuration '
              '(bounds.vec) : '
              '[ neuronBounds=%s, sortBounds=%s, initBounds=%s]'),
              neuronWindowBounds.formattedString('hn'), 
              sortWindowBounds.formattedString('s'), 
              initWindowBounds.formattedString('i'))
          fulloutput = '{outputFolder}/{prefix}.{neuronStr}.{sortStr}.{initStr}'.format( 
                        outputFolder = outputFolder, 
                        prefix = prefix,
                        neuronStr = neuronWindowBounds.formattedString('hn'), 
                        sortStr = sortWindowBounds.formattedString('s'),
                        initStr = initWindowBounds.formattedString('i') )
         
          for neuron in neuronWindowBounds:
            modelWindowBounds.append( models[neuron-1] if models else None )
          
          savedFile = TuningJobConfigArchieve( fulloutput,
                                               modelBounds = modelWindowBounds,
                                               neuronBounds = neuronWindowBounds,
                                               sortBounds = sortWindowBounds,
                                               initBounds = initWindowBounds ).save( compress )
          self._info('Saved job option configuration at path: %s',
                            savedFile )

createTuningJobFiles = CreateTuningJobFiles()


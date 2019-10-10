
__all__ = [ "TrigMultiVarHypo_v3" ]

from Gaugi import Logger
from Gaugi import ( checkForUnusedVars, calcSP, save, load, Logger
                       , LoggingLevel, expandFolders, traverse
                       , retrieve_kw, NotSet, csvStr2List, select, progressbar, getFilters
                       , apply_sort, LoggerStreamable, appendToFileName, ensureExtension
                       , measureLoopTime, checkExtension, MatlabLoopingBounds, mkdir_p
                       , LockFile, EnumStringification )



class TrigMultiVarHypo_v3( Logger ):

  # the athena version
  _version = 3

  # root branches used by the discriminator file
  _discrBranches = [
                   ['unsigned int', 'nodes'  , None],
                   ['double'      , 'weights', None],
                   ['double'      , 'bias'   , None],
                   ['double'      , 'etBin'  , None],
                   ['double'      , 'etaBin' , None],
                   ['double'      , 'muBin'  , None],
                   ]

  # root branches used by the threshold file
  _thresBranches = [
                   ['double'      , 'thresholds'  , None],
                   ['double'      , 'etBin'       , None],
                   ['double'      , 'etaBin'      , None],
                   ['double'      , 'muBin'       , None],
                   ]




  def __init__( self, **kw ):
    
    Logger.__init__(self, **kw)

    self._maxPileupLinearCorrectionValue  = retrieve_kw( kw, 'maxPileupLinearCorrectionValue' , 100   )
    self._removeOutputTansigTF            = retrieve_kw( kw, 'removeOutputTansigTF'           , True  )    
    self._useEtaVar                       = retrieve_kw( kw, 'useEtaVar'                      , False )
    self._useLumiVar                      = retrieve_kw( kw, 'useLumiVar'                     , False )
    self._toPython                        = retrieve_kw( kw, 'toPython'                       , True  )
    self._doPileupCorrection              = retrieve_kw( kw, 'doPileupCorrection'             , True  )


  def create_weights( self, discrList, filename ):

    self._logger.info('Getting weights...')
    
    from TuningTools import TuningToolCores
    modelDict = {}
    modelDict['__version__'] = self._version
    modelDict['__type__']	   = 'Fex'
    modelDict['__core__']	   = TuningToolCores.FastNet
    modelDict['metadata'] 	 = {
                                  'UseEtaVar': self._useEtaVar,
                                  'UseLumiVar':self._useLumiVar,
                               }
    modelDict['tuning']			 = {}
    
    def tolist(a):
      if isinstance(a,list): return a
      else: return a.tolist()
    
    for model in discrList:
      etBinIdx = model['etBinIdx']
      etaBinIdx = model['etaBinIdx']
      ## Discriminator configuration
      discrData={}
      discrData['etBin']     = model['etBin'].tolist()
      discrData['etaBin']    = model['etaBin'].tolist()
      discrData['muBin']     = model['muBin'].tolist()
      discrData['nodes']     = tolist( model['discriminator']['nodes']   )
      discrData['bias']      = tolist( model['discriminator']['bias']    )
      discrData['weights']   = tolist( model['discriminator']['weights'] )
      modelDict['tuning']['et{}_eta{}'.format(etBinIdx,etaBinIdx)] = {'discriminator':discrData}


    if self._toPython:
      self._logger.info('Export weights to python file')
      pyfile = open(appendToFileName(filename,'.py',separator=''),'w')
      pyfile.write('def SignaturesMap():\n')
      pyfile.write('  s=dict()\n')
      for key in modelDict.keys():
      	pyfile.write('  s["%s"]=%s\n' % (key, modelDict[key]))
      pyfile.write('  return s\n')
    
    
    from ROOT import TFile, TTree
    from ROOT import std
    self._logger.info('Export weights to root format...')
    ### Create the discriminator root object
    fdiscr = TFile(appendToFileName(filename,'.root', separator=''), 'recreate')
    self.__createRootParameter( 'int'   , '__version__', self._version).Write()
    self.__createRootParameter( 'int'   , '__core__'   , TuningToolCores.FastNet).Write()
    fdiscr.mkdir('tuning') 
    fdiscr.cd('tuning')
    tdiscr = TTree('discriminators','')
    
    for idx, b in enumerate(self._discrBranches):
      b[2] = std.vector(b[0])()
      tdiscr.Branch(b[1], 'vector<%s>'%b[0] ,b[2])
    
    for key in sorted(modelDict['tuning'].keys()):
      for idx, b in enumerate(self._discrBranches):
        self.__attachToVector( modelDict['tuning'][key]['discriminator'][b[1]],b[2])
      tdiscr.Fill()
    
    tdiscr.Write()
    
    ### Create the thresholds root object
    fdiscr.mkdir('metadata'); fdiscr.cd('metadata')
    for key, value in modelDict['metadata'].iteritems():
      self._logger.info('Saving metadata %s as %s', key, value)
      self.__createRootParameter( 'int' if type(value) is int else 'bool'   , key, value).Write()
    
    
    fdiscr.Close()




  def create_thresholds( self, discrList, filename ):

    self._logger.info('Getting thresholds...')
    
    from TuningTools import TuningToolCores
    modelDict = {}
    modelDict['__version__'] = self._version
    modelDict['__type__']	   = 'Hypo'
    modelDict['__core__']	   = TuningToolCores.FastNet
    modelDict['metadata'] 	 = {
                                'UseNoActivationFunctionInTheLastLayer' : self._removeOutputTansigTF,
                                'DoPileupCorrection'                    : self._doPileupCorrection,
                                'LumiCut'                               : self._maxPileupLinearCorrectionValue,
                                }
    
    modelDict['tuning']	 = {}

    for model in discrList:
      thresData = {}
      etBinIdx                = model['etBinIdx']
      etaBinIdx               = model['etaBinIdx']
      thresData['etBin']      = model['etBin'].tolist()
      thresData['etaBin']     = model['etaBin'].tolist()
      thresData['muBin']      = model['muBin'].tolist()
      thresData['thresholds'] = model['thresholds']
      modelDict['tuning']['et{}_eta{}'.format(etBinIdx,etaBinIdx)] = thresData


    if self._toPython:
      self._logger.info('Export thresholds to python file')
      pyfile = open(appendToFileName(filename,'.py',separator=''),'w')
      pyfile.write('def ThresholdsMap():\n')
      pyfile.write('  s=dict()\n')
      for key in modelDict.keys():
      	pyfile.write('  s["%s"]=%s\n' % (key, modelDict[key]))
      pyfile.write('  return s\n')
      

    from ROOT import TFile, TTree
    from ROOT import std
    

    self._logger.info('Export weights to root format...')
    ### Create the thresholds root object
    fthres = TFile(appendToFileName(filename,'.root',separator=''), 'recreate')
    self.__createRootParameter( 'int'   , '__version__', self._version).Write()
    self.__createRootParameter( 'int'   , '__core__'   , TuningToolCores.FastNet).Write()
    fthres.mkdir('tuning') 
    fthres.cd('tuning')
    tthres = TTree('thresholds','')

    for idx, b in enumerate(self._thresBranches):
      b[2] = std.vector(b[0])()
      tthres.Branch(b[1], 'vector<%s>'%b[0] ,b[2])



    for key in sorted(modelDict['tuning'].keys()):
      for idx, b in enumerate(self._thresBranches):
        self.__attachToVector( modelDict['tuning'][key][b[1]],b[2])
      tthres.Fill()
 

    tthres.Write()

    fthres.mkdir('metadata'); fthres.cd('metadata')
    for key, value in modelDict['metadata'].iteritems():
      self._logger.info('Saving metadata %s as %s', key, value)
      self.__createRootParameter( 'int' if type(value) is int else 'bool'   , key, value).Write()

    fthres.Close()


  
  
  def __attachToVector( self, l, vec ):
    vec.clear()
    for value in l: vec.push_back(value)
  
  def __createRootParameter( self, type_name, name, value):
    from ROOT import TParameter
    return TParameter(type_name)(name,value)

 



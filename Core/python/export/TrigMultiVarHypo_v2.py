
__all__ = [ "TrigMultiVarHypo_v2" ]

from RingerCore import Logger
from RingerCore import ( checkForUnusedVars, calcSP, save, load, Logger
                       , LoggingLevel, expandFolders, traverse
                       , retrieve_kw, NotSet, csvStr2List, select, progressbar, getFilters
                       , apply_sort, LoggerStreamable, appendToFileName, ensureExtension
                       , measureLoopTime, checkExtension, MatlabLoopingBounds, mkdir_p
                       , LockFile, EnumStringification )



class TrigMultiVarHypo_v2( Logger ):

  # the athena version
  _version = 2

  # root branches used by the discriminator file
  _discrBranches = [
                   ['unsigned int', 'nodes'  , None],
                   ['double'      , 'weights', None],
                   ['double'      , 'bias'   , None],
                   ['double'      , 'etBin'  , None],
                   ['double'      , 'etaBin' , None],
                   ]

  # root branches used by the threshold file
  _thresBranches = [
                   ['double'      , 'thresholds'  , None],
                   ['double'      , 'etBin'       , None],
                   ['double'      , 'etaBin'      , None],
                   ]




  def __init__( self, **kw ):
    
    Logger.__init__(self, **kw)

    self._maxPileupLinearCorrectionValue  = retrieve_kw( kw, 'maxPileupLinearCorrectionValue' , 100   )
    self._removeOutputTansigTF            = retrieve_kw( kw, 'removeOutputTansigTF'           , True  )    
    self._useEtaVar                       = retrieve_kw( kw, 'useEtaVar'                      , False )
    self._useLumiVar                      = retrieve_kw( kw, 'useLumiVar'                     , False )
    self._toPython                        = retrieve_kw( kw, 'toPython'                       , True  )
    self._doPileupCorrection              = retrieve_kw( kw, 'doPileupCorrection'             , True  )
    self._toPickle                        = retrieve_kw( kw, 'toPickle'                       , False )


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
    modelDict['tuning']			 = []
    
    def tolist(a):
      if isinstance(a,list): return a
      else: return a.tolist()
    
    for model in discrList:
      #etBinIdx = model['etBinIdx']
      #etaBinIdx = model['etaBinIdx']
      ## Discriminator configuration
      discrData={}
      discrData['etBin']     = model['etBin'].tolist()
      if discrData['etBin'][0]==0 and discrData['etBin'][1]==20.0: discrData['etBin']=[15.0, 20.0]
      discrData['etaBin']    = model['etaBin'].tolist()

      discrData['nodes']     = tolist( model['discriminator']['nodes']   )
      discrData['bias']      = tolist( model['discriminator']['bias']    )
      discrData['weights']   = tolist( model['discriminator']['weights'] )
      modelDict['tuning'].append( {'discriminator':discrData} )


    if self._toPickle:
      self._logger.info('Export weights to pickle format...')
      modelDict['__version__'] = self._version
      modelDict['__core__'] = TuningToolCores.keras
      from RingerCore import save
      save( modelDict, filename )

    
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
    
    for t in modelDict['tuning']:
      for idx, b in enumerate(self._discrBranches):
        self.__attachToVector( t['discriminator'][b[1]],b[2])
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
    
    modelDict['tuning']	 = []

    for model in discrList:
      thresData = {}
      #etBinIdx                = model['etBinIdx']
      #etaBinIdx               = model['etaBinIdx']
      thresData['etBin']      = model['etBin'].tolist()
      thresData['etaBin']     = model['etaBin'].tolist()
      thresData['thresholds'] = model['threshold']
      modelDict['tuning'].append(thresData)

    if self._toPickle:
      self._logger.info('Export Thresholds to pickle format...')
      modelDict['__version__'] = self._version
      modelDict['__core__'] = TuningToolCores.keras
      from RingerCore import save
      save( modelDict, filename )
      
    from ROOT import TFile, TTree
    from ROOT import std
    

    self._logger.info('Export Thresholds to root format...')
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



    for t in modelDict['tuning']:
      for idx, b in enumerate(self._thresBranches):
        self.__attachToVector( t[b[1]],b[2])
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

 




  def merge_thresholds( self, ifiles, filename ):
    
    import numpy as np
    from ROOT import TFile, TTree
    from ROOT import std
    from RingerCore import stdvector_to_list, list_to_stdvector

    thresList = []
    for f in ifiles:
      self._logger.info('Import Thresholds from root file (%s)...',f)
      ### Create the thresholds root object
      fthres = TFile(f, 'read')
      tree   = fthres.Get('tuning/thresholds')
      for entry in tree:        
        model = {}
        model['etBin'] = np.array(stdvector_to_list(entry.etBin))
        model['etaBin'] = np.array(stdvector_to_list(entry.etaBin))
        if model['etBin'][0]==0 and model['etBin'][1]==20.0: model['etBin']=np.array([15.0, 20.0])
        model['threshold'] = stdvector_to_list(entry.thresholds)
        print model['etBin'],' - ',model['etaBin'],' -> ',model['threshold']
        thresList.append(model)
    # export
    self.create_thresholds( thresList, filename )


  def merge_weights( self, ifiles, filename ):
    
    import numpy as np
    from ROOT import TFile, TTree
    from ROOT import std
    from RingerCore import stdvector_to_list, list_to_stdvector

    discrList = []
    for f in ifiles:
      self._logger.info('Import Weights from root file (%s)...',f)
      ### Create the thresholds root object
      fthres = TFile(f, 'read')
      tree   = fthres.Get('tuning/discriminators')
      for entry in tree:
        model = {}
        model['etBin'] = np.array(stdvector_to_list(entry.etBin))
        if model['etBin'][0]==0 and model['etBin'][1]==20.0: model['etBin']=np.array([15.0, 20.0])
        model['etaBin'] = np.array(stdvector_to_list(entry.etaBin))
        model['discriminator'] = {}
        model['discriminator']['nodes'] = np.array(stdvector_to_list(entry.nodes))
        model['discriminator']['bias'] = np.array(stdvector_to_list(entry.bias))
        model['discriminator']['weights'] = np.array(stdvector_to_list(entry.weights))
        
        print model['etBin'],' - ',model['etaBin']
        discrList.append(model)

    self._logger.info('Total number of discriminators imported are %d', len(discrList))
    # export
    self.create_weights( discrList, filename )












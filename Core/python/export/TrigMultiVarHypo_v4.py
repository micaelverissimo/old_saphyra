
__all__ = [ "TrigMultiVarHypo_v4" ]

from RingerCore import Logger
from RingerCore import ( checkForUnusedVars, calcSP, save, load, Logger
                       , LoggingLevel, expandFolders, traverse
                       , retrieve_kw, NotSet, csvStr2List, select, progressbar, getFilters
                       , apply_sort, LoggerStreamable, appendToFileName, ensureExtension
                       , measureLoopTime, checkExtension, MatlabLoopingBounds, mkdir_p
                       , LockFile, EnumStringification )



class TrigMultiVarHypo_v4( Logger ):

  # the athena version
  _version = 4

  # root branches used by the discriminator file
  _discrBranches = [
                   ['unsigned int', 'dense_nodes'  , None],
                   ['double'      , 'dense_weights', None],
                   ['double'      , 'dense_bias'   , None],
                   ['string'      , 'dense_tfnames', None],

                   ['bool'        , 'useConvLayer'    , None],
                   ['unsigned int', 'conv_nodes'      , None],
                   ['unsigned int', 'conv_kernel_i'   , None],
                   ['unsigned int', 'conv_kernel_j'   , None],
                   ['double'      , 'conv_kernel'     , None],
                   ['double'      , 'conv_bias'       , None],
                   ['unsigned int', 'conv_input_i'    , None],
                   ['unsigned int', 'conv_input_j'    , None],
                   ['string'      , 'conv_tfnames'    , None],


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
                                  'UseCaloRings':True,
                                  'UseTrack':False,
                                  'UseShowerShape':False,
                                  'RemoveOutputTansigTF': self._removeOutputTansigTF,
                               }
    
    modelDict['tuning']			 = []
    
    def tolist(a):
      if isinstance(a,list): return a
      elif isinstance(a,tuple): return a
      else: return a.tolist()
   

    from keras.models import model_from_json
    from keras.layers import Conv2D, Dense, Activation
    import json
    from copy import deepcopy

    for model in discrList:

      etBinIdx = model['etBinIdx']
      etaBinIdx = model['etaBinIdx']
      ## Discriminator configuration
      discrData={}
      discrData['etBin']     = tolist(model['etBin'])
      discrData['etaBin']    = tolist(model['etaBin'])
      discrData['muBin']     = tolist(model['muBin'])
      
      if self._toPickle:    
        discrData['model'] = deepcopy(model['discriminator']['model'])
        discrData['weights'] = deepcopy(model['discriminator']['weights'])

      else:
        keras_model = model_from_json( json.dumps(model['discriminator']['model'], separators=(',', ':'))  )
        keras_model.set_weights( model['discriminator']['weights'] )

        ### Extract and reshape Keras weights
        dense_weights = []; dense_bias = []; dense_nodes = []; dense_tfnames = []
        conv_kernel = [];  conv_kernel_i = []; conv_kernel_j = []; conv_bias = []; conv_tfnames = []; conv_nodes = []


        useConvLayer = False
        ### Loop over layers
        for idx, obj in enumerate(keras_model.layers):
          
          dobj = model['discriminator']['model']['config'][idx]['config']
          
          if type(obj) is Conv2D:
            useConvLayer=True
            conv_nodes.append( dobj['filters'] )
            conv_tfnames.append( str(dobj['activation']) )
            w, b = obj.get_weights()
           
            for wn in w.T:
              for wu in wn:
                conv_kernel.extend( wu.T.reshape( (dobj['kernel_size'][0]*dobj['kernel_size'][1],) ).tolist() )

            conv_bias.extend( b.tolist() )
            conv_kernel_i.append( dobj['kernel_size'][0] )
            conv_kernel_j.append( dobj['kernel_size'][1] )

          elif type(obj) is Dense:
            dense_nodes.append( dobj['units'] )
            dense_tfnames.append( str(dobj['activation']) )
            w, b = obj.get_weights()
            dense_weights.extend( w.reshape(-1,order='F') )
            dense_bias.extend( b.reshape(-1,order='F') )

          # TODO: Need to implement something smart to tread this case
          elif type(obj) is Activation:
            dense_tfnames.pop(); dense_tfnames.append( str(dobj['activation']) )

          else:
            continue


        
        discrData['dense_nodes']     = tolist( dense_nodes   )
        discrData['dense_bias']      = tolist( dense_bias    )
        discrData['dense_weights']   = tolist( dense_weights )
        discrData['dense_tfnames']   = tolist( dense_tfnames )

        discrData['useConvLayer']    = [useConvLayer]
        # Convolutional neural network
        if useConvLayer:
          discrData['conv_nodes']       = tolist( conv_nodes      )
          discrData['conv_tfnames']     = tolist( conv_tfnames    )
          discrData['conv_kernel_i']    = tolist( conv_kernel_i   )
          discrData['conv_kernel_j']    = tolist( conv_kernel_j   )
          discrData['conv_kernel']      = tolist( conv_kernel     )
          discrData['conv_bias']        = tolist( conv_bias       )
          discrData['conv_input_i']     = [model['discriminator']['model']['config'][0]['config']['batch_input_shape'][1]]
          discrData['conv_input_j']     = [model['discriminator']['model']['config'][0]['config']['batch_input_shape'][2]]
          
          i = discrData['conv_input_i'][0] - (sum(conv_kernel_i)-len(conv_kernel_i))
          j = discrData['conv_input_j'][0] - (sum(conv_kernel_j)-len(conv_kernel_j))
          input_layer = i*j*discrData['conv_nodes'][-1]
          discrData['dense_nodes']    = [input_layer]+discrData['dense_nodes']



      ### Attach
      modelDict['tuning'].append(  {'discriminator':discrData}  )



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
    
    def tolist(a):
      if isinstance(a,list): return a
      elif isinstance(a,tuple): return a
      else: return a.tolist()
 
    from TuningTools import TuningToolCores
    modelDict = {}
    modelDict['__version__'] = self._version
    modelDict['__type__']	   = 'Hypo'
    modelDict['__core__']	   = TuningToolCores.FastNet
    modelDict['metadata'] 	 = {
                                'RemoveOutputTansigTF'                  : self._removeOutputTansigTF,
                                'DoPileupCorrection'                    : self._doPileupCorrection,
                                'LumiCut'                               : self._maxPileupLinearCorrectionValue,
                                }
    
    modelDict['tuning']	 = []

    for model in discrList:
      thresData = {}
      etBinIdx                = model['etBinIdx']
      etaBinIdx               = model['etaBinIdx']
      thresData['etBin']      = tolist(model['etBin'])
      thresData['etaBin']     = tolist(model['etaBin'])
      thresData['muBin']      = tolist(model['muBin'])
      thresData['thresholds'] = model['threshold']
      modelDict['tuning'].append(thresData)

    
    if self._toPickle:
      self._logger.info('Export Thresholds to pickle format...')
      modelDict['__version__'] = self._version
      modelDict['__core__'] = TuningToolCores.keras
      from RingerCore import save
      save( modelDict, filename )


    self._logger.info('Export Thresholds to root format...')
    from ROOT import TFile, TTree
    from ROOT import std

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

 



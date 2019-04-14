__all__ = ['CreateSelectorFiles']

from RingerCore import ( checkForUnusedVars, calcSP, save, load, Logger
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
from copy import deepcopy, copy
import numpy as np



class CreateSelectorFiles( Logger ):

  def __init__(self, **kw):

    Logger.__init__(self,**kw)
    from TuningTools.export import TrigMultiVarHypo_v2
    # hold the export tool used to transform the dict data to some format
    self._exportModel = retrieve_kw( kw, 'model', TrigMultiVarHypo_v2() )



  def __call__( self, summaryInfoListCol, filenameWeightsList, filenameThresList,
                refBenchCol=None, configCol=None, muBins = [-999,999]):

    # treat ref benchmark collection
    if not refBenchCol:
      refBenchCol = [[refBenchCol]*len(summaryInfoListCol[0])]*len(summaryInfoListCol)
    if type(refBenchCol) is str:
      refBenchCol = [[refBenchCol]*len(summaryInfoListCol[0])]*len(summaryInfoListCol)
    if (len(refBenchCol) != len(summaryInfoListCol)) and (len(refBenchCol[0]) != len(summaryInfoListCol[0])):
      self._logger.fatal('RefBenchCol is not compatible with the definitions. See the help function')

    # treat config collections
    if not configCol:
      configCol=[[[]]*len(summaryInfoListCol[0])]*len(summaryInfoListCol)
    if type(configCol) is int:
      configCol=[[[configCol]]*len(summaryInfoListCol[0])]*len(summaryInfoListCol)
    if len(configCol) != len(summaryInfoListCol) and (len(configCol[0]) != len(summaryInfoListCol[0])):
      self._logger.fatal('ConfigCol is not compatible with the definitions. See the help function')

    # check if the numbers of paths in the line is compatible with the pileup grid
    if len(summaryInfoListCol[0]) != (len(muBins)-1):
      self._logger.fatal('The numbers of paths in the line is not compatible with the pileup bins')

    # Loop over all tuning pids
    for idx, summaryInfoList in enumerate(summaryInfoListCol):
      discrList = []
      for jdx, path in enumerate(summaryInfoList):
        files = expandFolders(path)
        crossValGrid=[]
        for f in files:
          if f.endswith('.pic.gz'):
            crossValGrid.append(f)
        # get all models
        discrList.extend( self.getModels(crossValGrid, refBenchCol = refBenchCol[idx][jdx], configCol = configCol[idx][jdx],
                          muBin = (muBins[jdx],muBins[jdx+1]) ))

      # export the configuration to root/py format
      self._exportModel.create_weights(    discrList, filenameWeightsList[idx] )
      self._exportModel.create_thresholds( discrList, filenameThresList[idx]   )
  


  def getModels(self, summaryInfoList,  **kw):
        
    refBenchCol         = kw.pop( 'refBenchCol',       None              )
    configCol           = kw.pop( 'configCol',         []                )
    muBin               = kw.pop( 'muBin',             [-999,9999]       )
    checkForUnusedVars( kw, self._logger.warning )

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

    discrList = []

    from itertools import izip, count
    for summaryInfo, refBenchmarkList, configList in zip(summaryInfoList,refBenchCol,configCol):

      if type(summaryInfo) is str:
        self._logger.info('Loading file "%s"...', summaryInfo)
        summaryInfo = load(summaryInfo)
      elif type(summaryInfo) is dict:
        pass
      else:
        logger.fatal("Cross-valid summary info is not string and not a dictionary.", ValueError)
    

      for idx, refBenchmarkName, config in izip(count(), refBenchmarkList, configList):
        
        try:
          key = filter(lambda x: refBenchmarkName in x, summaryInfo)[0]
          refDict = summaryInfo[ key ]
        except IndexError :
          self._logger.fatal("Could not find reference %s in summaryInfo. Available options are: %r", refBenchmarkName, summaryInfo.keys())
        
        self._logger.info("Using Reference key: %s", key )
        

        ppInfo = summaryInfo['infoPPChain']
        etBinIdx = refDict['etBinIdx']
        etaBinIdx = refDict['etaBinIdx']
        etBin = refDict['etBin']

        etaBin = refDict['etaBin']
        info   = refDict['infoOpBest'] if config is None else refDict['config_' + str(config).zfill(3)]['infoOpBest']
            
        # Check if user specified parameters for exporting discriminator
        # operation information:
        sort =  info['sort']
        init =  info['init']
        pyThres = info['cut']
        
        from RingerCore import retrieveRawDict
        if isinstance( pyThres, float ):
          pyThres = RawThreshold( thres = pyThres
                                , etBinIdx = etBinIdx, etaBinIdx = etaBinIdx
                                , etBin = etBin, etaBin =  etaBin)

        else:
          # Get the object from the raw dict
          pyThres = retrieveRawDict( pyThres )

        if pyThres.etBin is None:
          pyThres.etBin = etBin
        elif pyThres.etBin is '':
          pyThres.etBin = etBin
        elif isinstance( pyThres.etBin, (list,tuple)):
          pyThres.etBin = np.array( pyThres.etBin)

        if not(np.array_equal( pyThres.etBin, etBin )):
          self._logger.fatal("etBin does not match for threshold! Should be %r, is %r", pyThres.etBin, etBin )
        if pyThres.etaBin is None:
          pyThres.etaBin = etaBin
        elif pyThres.etaBin is '':
          pyThres.etaBin = etaBin
        elif isinstance( pyThres.etaBin, (list,tuple)):
          pyThres.etaBin = np.array( pyThres.etaBin)
        if not(np.array_equal( pyThres.etaBin, etaBin )):
          self._logger.fatal("etaBin does not match for threshold! Should be %r, is %r", pyThres.etaBin, etaBin )

        if type(pyThres) is RawThreshold:
          thresValues = [pyThres.thres]
        else:
          thresValues = [pyThres.slope, pyThres.intercept, pyThres.rawThres]

        pyPreProc = ppInfo['sort_'+str(sort).zfill(3)]['items'][0]
        pyPreProc = retrieveRawDict( pyPreProc )

        useCaloRings=False; useTrack=False; useShowerShape=False

        if type(pyPreProc) is Norm1:
          useCaloRings=True
        elif type(pyPreProc) is TrackSimpleNorm:
          useTrack=True
        elif type(pyPreProc) is ShowerShapesSimpleNorm:
          useShowerShape=True
        elif type(pyPreProc) is ExpertNetworksSimpleNorm:
          useCaloRings=True; useTrack=True
        elif type(pyPreProc) is ExpertNetworksShowerShapeSimpleNorm:
          useCaloRings=True; useShowerShape=True
        elif type(pyPreProc) is ExpertNetworksShowerShapeAndTrackSimpleNorm:
          useCaloRings=True; useTrack=True; useShowerShape=True
        elif type(pyPreProc) is PreProcMerge:
          for slot in pyPreProc.slots:
            if type(pyPreProc) is Norm1:
              useCaloRings=True
            elif type(pyPreProc) is TrackSimpleNorm:
              useTrack=True
            elif type(pyPreProc) is ShowerShapesSimpleNorm:
              useShowerShape=True
            elif type(pyPreProc) is ExpertNetworksSimpleNorm:
              useCaloRings=True; useTrack=True
            elif type(pyPreProc) is ExpertNetworksShowerShapeSimpleNorm:
              useCaloRings=True; useShowerShape=True
            elif type(pyPreProc) is ExpertNetworksShowerShapeAndTrackSimpleNorm:
              useCaloRings=True; useTrack=True; useShowerShape=True
        else:
          self._logger.fatal('PrepProc strategy not found...') 


        discrDict = info['discriminator']
        model   = { 
                  'discriminator' : discrDict,
                  'threshold'     : thresValues,
                  'etBin'         : etBin,
                  'etaBin'        : etaBin,
                  'muBin'         : muBin,
                  'etBinIdx'      : etBinIdx,
                  'etaBinIdx'     : etaBinIdx,
 
                  }
      
        removeOutputTansigTF = refDict.get('removeOutputTansigTF', None )
        
        model['removeOutputTansigTF'] = removeOutputTansigTF
        model['useCaloRings']         = useCaloRings
        model['useShowerShape']       = useShowerShape
        model['useTrack']             = useTrack

                 
        discrList.append( model )
  
        self._logger.info('neuron = %d, sort = %d, init = %d',
                     info['neuron'],
                     info['sort'],
                     info['init'])
        
      # for benchmark
    # for summay in list

    return discrList




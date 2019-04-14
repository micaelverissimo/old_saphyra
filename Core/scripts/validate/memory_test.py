#!/usr/bin/env python

from timeit import default_timer as timer

start = timer()

DatasetLocationInput ='/afs/cern.ch/work/w/wsfreund/public/mc14_13TeV.147406.129160.sgn.truth.bkg.truth.off.npy'

try:
  from RingerCore.Logger import Logger, LoggingLevel
  from TuningTools.TuningJob import TuningJob
  mainLogger = Logger.getModuleLogger(__name__)


  tuningJob = TuningJob()

  mainLogger.info("Entering main job.")

  tuningJob( DatasetLocationInput, 
             neuronBoundsCol = [5, 5], 
             sortBoundsCol = [1, 2],
             initBoundsCol = [1, 3], 
             epochs = 3,
             showEvo = 1, 
             doMultiStop = True,
             doPerf = True,
             seed = 0,
             crossValidSeed = 66,
             level = LoggingLevel.INFO )

  mainLogger.info("Finished.")
except ImportError,e:

  import sys
  import os
  import pickle
  import numpy as np
  from TuningTools.Preprocess import Normalize, RingerRp
  from TuningTools.CrossValid import CrossValid
  from RingerCore.util       import include, normalizeSumRow, reshape, load, getModuleLogger

  mainLogger = getModuleLogger(__name__)
  mainLogger.info('Opening data...')
  objDataFromFile                   = np.load( DatasetLocationInput )
  #Job option configuration
  Data                              = reshape( objDataFromFile[0] ) 
  Target                            = reshape( objDataFromFile[1] )
  preTool                           = Normalize( Norm='totalEnergy' )
  Data                              = preTool( Data )
  Cross                             = CrossValid( nSorts=50, nBoxes=10, nTrain=6, nValid=4, seed = 66)
  OutputName                        = 'output'
  DoMultiStop                       = True
  ShowEvo                           = 1
  Epochs                            = 3

  #job configuration
  Inits                             = [1, 2]
  minNeuron                         = 5
  maxNeuron                         = 5

  del objDataFromFile
  from TuningTools.TrainJob import TrainJob
  trainjob = TrainJob()

  for neuron in range( minNeuron, maxNeuron+1):
    trainjob( Data, Target, Cross, 
                    neuron=neuron, 
                    sort=1,
                    initBounds=Inits, 
                    epochs=Epochs,
                    showEvo=ShowEvo, 
                    doMultiStop=DoMultiStop,
                    prepTools=[],
                    doPerf=True,
                    seed=0)

end = timer()
print(end - start)      

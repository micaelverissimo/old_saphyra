#!/bin/env python

from RingerCore import *
from TuningTools import *
from itertools import product

import numpy as np

dirpath = '~guimdefreitas/RP2/root/neuralnet1'

for fpath in sorted(expandFolders(dirpath)):
  print fpath
  tdArchieve = TunedDiscrArchieve.load(fpath)
  opPerfs = []
  for neuron, sort, init in progressbar( product( tdArchieve.neuronBounds(),
                                                  tdArchieve.sortBounds(),
                                                  tdArchieve.initBounds() ),
                                                  60, 'Reading configurations: ', 60, 1, False):
    tunedDict      = tdArchieve.getTunedInfo( neuron, sort, init )
    tunedDiscr     = tunedDict['tunedDiscr']
    tunedPPChain   = tunedDict['tunedPP']
    trainEvolution = tunedDict['tuningInfo']
    perfHolder = PerfHolder( tunedDiscr[0]
                           , trainEvolution
                           #, decisionTaking = self.decisionMaker( tunedDiscr['discriminator'] ) if self.decisionMaker else None
                           )

    opPerf = perfHolder.getOperatingBenchmarks( ReferenceBenchmark( "Tuning_SP", ReferenceBenchmark.SP)
                                              , ds                   = Dataset.Operation
                                              , neuron = neuron, sort = sort, init = init
                                              )
    opPerfs.append( opPerf )
  m = np.argmax( [o.sp for o in opPerfs] )
  opPerf = opPerfs[m]
  print opPerf




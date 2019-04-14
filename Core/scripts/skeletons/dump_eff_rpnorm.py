#!/bin/env python

from RingerCore import *
from TuningTools import *
from itertools import product
import pandas as pd
import numpy as np, re

dirpath = '~guimdefreitas/RP2/root/neuralnet1'

alphas             = []
betas              = []
nalphas            = int(round((2-.1)/.1)+1)
nbetas             = int(round((4-.5)/.1)+1)
table_values_sp    = np.zeros((nalphas,nbetas))
table_values_pd    = np.zeros((nalphas,nbetas))
table_values_pf    = np.zeros((nalphas,nbetas))
table_values_mse   = np.zeros((nalphas,nbetas))
table_values_thres = np.zeros((nalphas,nbetas))

for idx, fpath in enumerate(sorted(expandFolders(dirpath))):
  print "Reading file:", fpath
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
  idx = np.argmax( [o.sp for o in opPerfs] )
  opPerf = opPerfs[idx]
  rpnorm = tdArchieve.tunedPP[0][0]
  alpha = rpnorm._alpha
  beta = rpnorm._beta
  alpha_idx = int(round(( alpha - .1 ) * 10.))
  beta_idx = int(round(( beta - .5 ) * 10.))
  print "alpha:", alpha, "beta:", beta, ", filling data in table position: (", alpha_idx, ',', beta_idx, '). Performance:'
  print opPerf
  table_values_sp[alpha_idx,beta_idx] = opPerf.sp_value * 100.
  table_values_pd[alpha_idx,beta_idx] = opPerf.pd_value * 100.
  table_values_pf[alpha_idx,beta_idx] = opPerf.pf_value * 100.
  table_values_mse[alpha_idx,beta_idx] = opPerf.mse
  table_values_thres[alpha_idx,beta_idx] = opPerf.thres_value.thres

sp_frame = pd.DataFrame(table_values_sp, columns = np.arange(.5,4.01,.1), index = np.arange(.1,2.01,.1) )
pd_frame = pd.DataFrame(table_values_pd, columns = np.arange(.5,4.01,.1), index = np.arange(.1,2.01,.1) )
pf_frame = pd.DataFrame(table_values_pf, columns = np.arange(.5,4.01,.1), index = np.arange(.1,2.01,.1) )
mse_frame = pd.DataFrame(table_values_mse, columns = np.arange(.5,4.01,.1), index = np.arange(.1,2.01,.1) )
thres_frame = pd.DataFrame(table_values_thres, columns = np.arange(.5,4.01,.1), index = np.arange(.1,2.01,.1) )
eff_frame = pd.concat([sp_frame, pd_frame, pf_frame,mse_frame],axis=0,keys=["SP-index [%]","Electron Efficiency [%]", "Background Efficiency [%]", "Mean Squared Error", "Decision Threshold"])
eff_frame.to_csv('rp_efficiency.csv')

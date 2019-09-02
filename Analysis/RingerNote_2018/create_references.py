#!/usr/bin/env python

from saphyra import PandasJob, sp, PreProcChain_v1, Norm1, Summary, PileupFit, ReshapeToConv1D
from sklearn.model_selection import KFold,StratifiedKFold
from Gaugi.messenger import LoggingLevel, Logger
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Conv1D, Flatten
from Gaugi import load
import argparse
import sys,os
import numpy as np

path = '/eos/user/j/jodafons/CERN-DATA/tuning/data17_201907XX_v10/files/data17_13TeV.AllPeriods.sgn.probes_lhmedium_EGAM1.bkg.VProbes_EGAM7.GRL_v97/*.npz'

from Gaugi import expandFolders
fileList = expandFolders(path)


ref_target = [
              ('tight_v8'       , 'T0HLTElectronRingerTight_v8'     ),
              ('medium_v8'      , 'T0HLTElectronRingerMedium_v8'    ),
              ('loose_v8'       , 'T0HLTElectronRingerLoose_v8'     ),
              ('vloose_v8'      , 'T0HLTElectronRingerVeryLoose_v8' ),
              ('tight_v6'       , 'T0HLTElectronRingerTight_v6'     ),
              ('medium_v6'      , 'T0HLTElectronRingerMedium_v6'    ),
              ('loose_v6'       , 'T0HLTElectronRingerLoose_v6'     ),
              ('vloose_v6'      , 'T0HLTElectronRingerVeryLoose_v6' ),
              ('tight_cutbased' , 'T0HLTElectronT2CaloTight'        ),
              ('medium_cutbased', 'T0HLTElectronT2CaloMedium'       ),
              ('loose_cutbased' , 'T0HLTElectronT2CaloLoose'        ),
              ('vloose_cutbased', 'T0HLTElectronT2CaloVLoose'       ),
              ]



from saphyra import Reference_v1

for f in fileList:

  ff = f.split('/')[-1].replace('.npz','')+'.ref'
  obj = Reference_v1()
  raw = load(f)
  data = raw['data'][:,1:101]
  target = raw['target']
  
  print ff 
  etBins = raw["etBins"] 
  etaBins = raw["etaBins"  ] 
  etBinIdx = raw["etBinIdx" ] 
  etaBinIdx =raw["etaBinIdx"] 

  key = 'et%d_eta%d'%(etBinIdx,etaBinIdx)
  obj.setEtBins( etBins ) 
  obj.setEtaBins( etaBins ) 
  obj.setEtBinIdx( etBinIdx ) 
  obj.setEtaBinIdx( etBinIdx ) 

  for ref in ref_target:
    d = raw['data'][:,np.where(raw['features'] == ref[1])[0][0]-1]
    d_s = d[target==1]
    d_b = d[target!=1]

    obj.addSgn( ref[0], ref[1], sum(d_s), len(d_s) )
    obj.addBkg( ref[0], ref[1], sum(d_b), len(d_b) )

  obj.save(ff)




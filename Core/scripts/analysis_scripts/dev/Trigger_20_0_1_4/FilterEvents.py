#!/usr/bin/env python
import logging
import ROOT 
import sys
import pickle
from RingerCore.FileIO import save, load
from TuningTools.ReadData import *
#from TuningTools.CrossValid import *


import numpy as np
#etaBins = [0, 0.8 , 1.37, 1.54, 2.5]
#etBins  = [0,30, 50, 20000]# in GeV

etaBins=[0.0,2.50]
etBins=[0,200000]

output   = 'mc14_13TeV.147406.129160.sgn.offLikelihood.bkg.truth.trig.e24_lhmedium_L1EM20VH'
#basepath = '/afs/cern.ch/work/j/jodafons/new/'
basepath = '/afs/cern.ch/work/j/jodafons/public/Online/PhysVal'
#bkgName='user.jodafons.mc14_13TeV.129160.Pythia8_AU2CTEQ6L1_perf_JF17.recon.RDO.rel20.1.0.4.e3084_s2044_s2008_r5988.rr0040_ph0002_PhysVal.root'
#sgnName='user.jodafons.mc14_13TeV.147406.PowhegPythia8_AZNLO_Zee.recon.RDO.rel20.1.0.4.e3059_s1982_s2008_r5993_rr0040_ph0002_PhysVal.root'
bkgName='user.jodafons.mc14_13TeV.129160.Pythia8_AU2CTEQ6L1_perf_JF17.recon.RDO.rel20.1.0.4.e3084_s2044_s2008_r5988.rr0104_a0001_PhysVal.root'
sgnName='user.jodafons.mc14_13TeV.147406.PowhegPythia8_AZNLO_Zee.recon.RDO.rel20.1.0.4.e3059_s1982_s2008_r5993_rr0104_a0001_PhysVal.root'

print 'Background:'

npBkg, bkgSummary, _  = readData(basepath+'/'+bkgName, 
                         RingerOperation.L2,
                         treePath= 'Trigger/HLT/Egamma/BackgroundNtuple/e24_lhmedium_ringer_perf_L1EM20VH', 
                         #l1EmClusCut = 20, 
                         l2EtCut = 19,
                         filterType = FilterType.Background, 
                         reference = Reference.Truth,
                         etaBins=etaBins,
                         etBins=etBins,
                         #nClusters=200,
                         #getRatesOnly=True,
                         )


print 'Signal:'

npSgn, sgnSummary, _  = readData(basepath+'/'+sgnName,
                         RingerOperation.L2,
                         treePath = 'Trigger/HLT/Egamma/ZeeNtuple/e24_lhmedium_ringer_perf_L1EM20VH',
                         #l1EmClusCut = 20,
                         l2EtCut = 19,
                         filterType = FilterType.Signal,
                         reference = Reference.Off_Likelihood,
                         etaBins=etaBins,
                         etBins=etBins,
                         #nClusters=200,
                         #getRatesOnly=True,
                         )

summary = {'sgn':sgnSummary,'bkg':bkgSummary}
save(summary, output+'_summary')


from TuningTools.CreateData import TuningDataArchieve
import scipy.io as sio
DoMatlab=True

for nEt in range(len(etBins)-1):
  for nEta in range(len(etaBins)-1):
    sufix=('_etBin_%d_etaBin_%d')%(nEt,nEta)
    print ('Saving position: [%d][%d]')%(nEt,nEta)
    print 'sgn shape is ',npSgn[nEt][nEta].shape
    print 'bkg shape is ',npBkg[nEt][nEta].shape
    savedPath = TuningDataArchieve( output+sufix,
                                   signal_rings = npSgn[nEt][nEta],
                                   background_rings = npBkg[nEt][nEta] ).save()

    if DoMatlab:
      obj = {'signal_rings':npSgn[nEt][nEta],'background_rings':npBkg[nEt][nEta]}
      sio.savemat(output+sufix+'.mat',obj)

    print ('Saved path is %s')%(savedPath)


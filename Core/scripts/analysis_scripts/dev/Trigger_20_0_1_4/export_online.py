#!/usr/bin/env python

from RingerCore.Logger import LoggingLevel
from RingerCore.FileIO import load, save
from TuningTools.CrossValidStat  import CrossValidStatAnalysis, \
                                        ReferenceBenchmark
from TuningTools.ReadData import RingerOperation, BranchEffCollector

basepath ='/tmp/jodafons/Tuning2015'

fileList = [
  ['user.wsfreund.tuned.mc14.sgn.offLH.bkg.truth.trig.l1cluscut_20.l2etcut_19.e24_medium_etBin_0_etaBin_0.t0001_tunedDiscrXYZ.tgz/',
  'user.wsfreund.tuned.mc14.sgn.offLH.bkg.truth.trig.l1cluscut_20.l2etcut_19.e24_medium_etBin_1_etaBin_0.t0001_tunedDiscrXYZ.tgz/',
  'user.wsfreund.tuned.mc14.sgn.offLH.bkg.truth.trig.l1cluscut_20.l2etcut_19.e24_medium_etBin_2_etaBin_0.t0001_tunedDiscrXYZ.tgz/'],

  ['user.jodafons.nn.mc14_13TeV.147406.sgn.Off_LH.129160.bkg.truth.l1_20.l2_19.e24_medium_etBin_0_etaBin_1.t0002_tunedDiscrXYZ.tgz/',
  'user.jodafons.nn.mc14_13TeV.147406.sgn.Off_LH.129160.bkg.truth.l1_20.l2_19.e24_medium_etBin_1_etaBin_1.t0002_tunedDiscrXYZ.tgz/',
  'user.jodafons.nn.mc14_13TeV.147406.sgn.Off_LH.129160.bkg.truth.l1_20.l2_19.e24_medium_etBin_2_etaBin_1.t0002_tunedDiscrXYZ.tgz/'],

  ['user.damazio.tuned.mc14.sgn.offLH.bkg.truth.trig.l1cluscut_20.l2etcut_19.e24_medium_etBin_0_etaBin_2.t0002_tunedDiscrXYZ.tgz/',
  'user.damazio.tuned.mc14.sgn.offLH.bkg.truth.trig.l1cluscut_20.l2etcut_19.e24_medium_etBin_1_etaBin_2.t0002_tunedDiscrXYZ.tgz/',
  'user.damazio.tuned.mc14.sgn.offLH.bkg.truth.trig.l1cluscut_20.l2etcut_19.e24_medium_etBin_2_etaBin_2.t0002_tunedDiscrXYZ.tgz/'],

  ['user.nbullacr.tuned.mc14.sgn.offLH.bkg.truth.trig.l1cluscut_20.l2etcut_19.e24_medium_etBin_0_etaBin_3.t0001_tunedDiscrXYZ.tgz/',
  'user.nbullacr.tuned.mc14.sgn.offLH.bkg.truth.trig.l1cluscut_20.l2etcut_19.e24_medium_etBin_1_etaBin_3.t0001_tunedDiscrXYZ.tgz/',
  'user.nbullacr.tuned.mc14.sgn.offLH.bkg.truth.trig.l1cluscut_20.l2etcut_19.e24_medium_etBin_2_etaBin_3.t0001_tunedDiscrXYZ.tgz/'],
  ]

config=dict()
config['Medium_LH_L2Calo_Pd'] = [ [5, 5, 5], [11,5, 5], [9, 5, 5], [9, 5, 5] ]
config['Medium_LH_EFCalo_Pd'] = [ [5, 5, 5], [5 ,5, 5], [5, 5, 5], [14,5, 5] ]
config['Medium_LH_L2Calo_Pf'] = [ [5, 5, 5], [5 ,5, 5], [5, 5, 5], [5, 5, 5] ]
config['Medium_LH_EFCalo_Pf'] = [ [5, 5, 5], [14,5, 5], [5, 5, 5], [5, 5, 5] ]
config['Medium_LH_MaxSP']     = [ [9, 5, 5], [11,11,5], [5,15, 5], [12,5, 5] ]
config['Tight_LH_L2Calo_Pd']  = [ [5, 5, 5], [5 ,5, 5], [5, 5, 5], [5, 5, 5] ]
config['Tight_LH_EFCalo_Pd']  = [ [5, 5, 5], [5 ,5, 5], [5, 5, 5], [5, 5, 5] ]
config['Tight_LH_L2Calo_Pf']  = [ [5, 5, 5], [5 ,5, 5], [5, 5, 5], [5, 5, 5] ]
config['Tight_LH_EFCalo_Pf']  = [ [5, 5, 5], [5 ,5, 5], [5, 5, 5], [5, 5, 5] ]


#crossValBasepath = '/afs/cern.ch/work/j/jodafons/public/Online/CrossValStat'
crossValBasepath = '.'
crossValName     = 'crossValStat_mc14_13TeV.147406.129160.sgn.offCutID.bkg.truth.trig.e24.etaBin_%d_etBin_%d.pic' 

etaBins = [0.0, 0.8, 1.37, 1.54, 2.50]
etBins  = [0.0, 30.0, 50.0, 9999.99]

output = open('TrigL2CaloRingerConstants.py','w')
output.write('def RingerMap():\n')
output.write('  signatures = dict()\n')

triggerList=[
              'e24_lhmedium_L1EM20VH_L2EFCalo_ringer_pd',
              'e24_lhmedium_L1EM20VH_L2Calo_ringer_pd',
              'e24_lhmedium_L1EM20VH_ringer_sp',
              'e24_lhtight_L1EM20VH_L2EFCalo_ringer_pd',
              'e24_lhtight_L1EM20VH_L2Calo_ringer_pd',
            ]
tc=0

for key in ['Medium_LH_EFCalo_Pd', 'Medium_LH_L2Calo_Pd','Medium_LH_MaxSP','Tight_LH_EFCalo_Pd','Tight_LH_L2Calo_Pd']:

  netBins=dict()
  for nEta in [0,1,2,3]:  
    for nEt in [0,1,2]:

      crossValSummary = load((crossValBasepath+'/'+crossValName)%(nEta,nEt))
      stat = CrossValidStatAnalysis( basepath+'/'+fileList[nEta][nEt], level = LoggingLevel.DEBUG )
      # Add them to a list:
      data  = CrossValidStatAnalysis.exportDiscrFiles(crossValSummary, RingerOperation.L2,
                                                      refBenchmarkNameList=[key],
                                                      configList=[config[key][nEta][nEt]])

      network = data['tunedDiscr']
      network['etaBin']=[etaBins[nEta],etaBins[nEta+1]] 
      network['etBin'] =[etBins[nEt]  ,etBins[nEt+1]  ] 
      netBins[('eta%d_et%d')%(nEta,nEt)]=network

  output.write(('  signatures["%s"]=%s\n')%(triggerList[tc],str(netBins)))
  tc+=1

output.write('  return signatures')
output.close()

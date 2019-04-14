
from RingerCore import masterLevel, LoggingLevel, keyboard
from TuningTools import *
import ROOT
ROOT.TH1.AddDirectory(ROOT.kFALSE)
ROOT.gROOT.SetBatch(ROOT.kTRUE)
masterLevel.set( LoggingLevel.VERBOSE )

# FIXME Go to data curator and force multiStop if needed
dCurator = DataCurator( kw, dataLocation = dataLocation )
sort = 0
#dCurator.crossValid._sort_boxes_list[sort] = [3, 4, 5, 7, 8, 9, 0, 1, 2, 6]
dCurator.prepareForBin( etBinIdx = 2, etaBinIdx = 0
                      , loadEfficiencies = True, loadCrossEfficiencies = False )
dCurator.toTunableSubsets( sort, PreProcChain( RingerEtaMu() ) )
td = TunedDiscrArchieve.load('/home/wsfreund/junk/tuningDataTest/networks2/nn.tuned.pp-ExNREM.hn0010.s0000.il0000.iu0002.et0002.eta0000.pic.gz')

decisionMaker = DecisionMaker( dCurator, {}, removeOutputTansigTF = True, pileupRef = 'nvtx' )

tunedDict  = td.getTunedInfo( 10, 0, 2 )
tunedDiscrSP = tunedDict['tunedDiscr'][0]
sInfoSP      = tunedDiscrSP['summaryInfo']
trnOutSP = [npCurrent.fp_array( a ) for a in sInfoSP['trnOutput']]
valOutSP = [npCurrent.fp_array( a ) for a in sInfoSP['valOutput']]
tunedDiscrPd = tunedDict['tunedDiscr'][1]
sInfoPd      = tunedDiscrPd['summaryInfo']
trnOutPd = [npCurrent.fp_array( a ) for a in sInfoPd['trnOutput']]
valOutPd = [npCurrent.fp_array( a ) for a in sInfoPd['valOutput']]
tunedDiscrPf = tunedDict['tunedDiscr'][2]
sInfoPf      = tunedDiscrPf['summaryInfo']
trnOutPf = [npCurrent.fp_array( a ) for a in sInfoPf['trnOutput']]
valOutPf = [npCurrent.fp_array( a ) for a in sInfoPf['valOutput']]

decisionTaking = decisionMaker( tunedDiscrPf['discriminator'] )
a = ROOT.TFile("pf.root","recreate")
a.cd()
decisionTaking( dCurator.references[2], CuratedSubset.trnData, neuron = 10, sort = 0, init = 0 )
s = CuratedSubset.fromdataset(Dataset.Test)
tstPointCorr = decisionTaking.getEffPoint( dCurator.references[2].name + '_Test' , subset = [s, s], makeCorr = True )
decisionTaking.saveGraphs()
a.Write()
del a
print tstPointCorr
print dCurator.crossValid.getTrnBoxIdxs( sort )
print dCurator.crossValid.getValBoxIdxs( sort )
try:
  print trnOutPf[0] - decisionTaking.sgnOut
  print trnOutPf[1] - decisionTaking.bkgOut
  print valOutPf[0] - decisionTaking._effOutput[0]
  print valOutPf[1] - decisionTaking._effOutput[1]
except ValueError: pass


keyboard()

b = ROOT.TFile("sp.root",'recreate')
b.cd()
decisionTaking = decisionMaker( tunedDiscrSP['discriminator'] )
decisionTaking( dCurator.references[0], CuratedSubset.trnData, neuron = 10, sort = 0, init = 0 )
s = CuratedSubset.fromdataset(Dataset.Test)
tstPointCorr = decisionTaking.getEffPoint( dCurator.references[0].name + '_Test' , subset = [s, s], makeCorr = True )
decisionTaking.saveGraphs()
b.Write()
print tstPointCorr
try:
  print trnOutSP[0] - decisionTaking.sgnOut
  print trnOutSP[1] - decisionTaking.bkgOut
  print valOutSP[0] - decisionTaking._effOutput[0]
  print valOutSP[1] - decisionTaking._effOutput[1]
except ValueError: pass



basePath     = '/afs/cern.ch/work/j/jodafons/public/Tuning2016/Physval'
sgnInputFile = 'user.jodafons.mc14_13TeV.147406.PowhegPythia8_AZNLO_Zee.recon.RDO.rel20.7.3.6.e3059_s1982_s2008_r5993_reco01_01_PhysVal/'
bkgInputFile = 'user.jodafons.mc14_13TeV.129160.Pythia8_AU2CTEQ6L1_perf_JF17.recon.RDO.rel20.7.3.6.e3084_s2044_s2008_r5988.reco01_01_PhysVal/'
outputFile   = 'data.pic'
treePath     = 'HLT/Egamma/Ntuple/Ntuple/HLT_e24_lhmedium_nod0_iloose'
crossValPath = 'crossValid_5sorts.pic.gz'

#etBins       = [0, 30, 40, 50, 100000 ]
#etaBins      = [0, 0.8 , 1.37, 1.54, 2.5]
etBins       = [0, 30]
etaBins      = [0, 0.8]

from TuningTools  import CrossValidArchieve
with CrossValidArchieve( crossValPath ) as CVArchieve:
  crossVal = CVArchieve
  del CVArchieve

from TuningTools import createData
from TuningTools import Reference, RingerOperation
from RingerCore  import expandFolders


createData( sgnFileList     = expandFolders( basePath+'/'+sgnInputFile ), 
            bkgFileList     = expandFolders( basePath+'/'+bkgInputFile ),
            ringerOperation = RingerOperation.EFCalo,
            referenceSgn    = Reference.Off_Likelihood,
            referenceBkg    = Reference.Truth,
            treePath        = treePath,
            output          = outputFile,
            l1EmClusCut     = 20,
            l2EtCut         = 19,
            efEtCut         = 24,
            #offEtCut        = 24,
            #nClusters       = 50,
            #getRatesOnly    = args.getRatesOnly,
            etBins          = etBins,
            etaBins         = etaBins,
            #ringConfig      = args.ringConfig
            crossVal        = crossVal,
            toMatlab        = True,
            )

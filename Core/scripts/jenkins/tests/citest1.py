
basePath     = 'samples'
sgnInputFile = 'sample.sgn.root'
bkgInputFile = 'sample.bkg.root'
outputFile   = 'tuningData_citest1'
treePath     = 'HLT/Egamma/Ntuple/Ntuple/HLT_e24_lhmedium_nod0_iloose'
crossValPath = 'data/crossValid_citest0.pic.gz'
etBins       = [0, 100000 ]
etaBins      = [0, 2.5]

from TuningTools.CrossValid import CrossValidArchieve
with CrossValidArchieve( crossValPath ) as CVArchieve:
  crossVal = CVArchieve
  del CVArchieve

from TuningTools import createData
from TuningTools import Reference, RingerOperation
from RingerCore  import expandFolders

createData( basePath+'/'+sgnInputFile , 
            basePath+'/'+bkgInputFile ,
            RingerOperation.EFCalo,
            referenceSgn    = Reference.Off_Likelihood,
            referenceBkg    = Reference.Truth,
            treePath        = treePath,
            pattern_oFile   = outputFile,
            l1EmClusCut     = 1,
            l2EtCut         = 1,
            efEtCut         = 1,
            etBins          = etBins,
            etaBins         = etaBins,
            crossVal        = crossVal,
            toMatlab        = False)

import sys,os
sys.exit(os.EX_OK) # code 0, all ok

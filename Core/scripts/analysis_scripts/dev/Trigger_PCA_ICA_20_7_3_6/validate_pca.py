#!/usr/bin/env python

from TuningTools.CreateData import TuningDataArchieve
filePath = '/afs/cern.ch/work/j/jodafons/public/Tuning2016/TuningConfig/mc14_13TeV.147406.129160.sgn.offLikelihood.bkg.truth.trig.e24_lhmedium_nod0_l1etcut20_l2etcut19_efetcut24_binned.pic.npz'
TDArchieve = TuningDataArchieve(filePath)
nEtBins = TDArchieve.nEtBins()
nEtaBins = TDArchieve.nEtaBins()

from TuningTools.PreProc import PreProcArchieve
with PreProcArchieve('/afs/cern.ch/work/w/wsfreund/public/Online/Trigger_PCA_ICA_20_7_3_6/pre_proc_pca_T.pic') as ppCol:
  pass
from TuningTools.CrossValid import CrossValid, CrossValidArchieve
crossValidFile = '/afs/cern.ch/work/j/jodafons/public/Tuning2016/TuningConfig/crossVal_50sorts_20160324.pic.gz'
with CrossValidArchieve( crossValidFile ) as CVArchieve:
  crossValid = CVArchieve
del CVArchieve

import numpy as np
#np.set_printoptions(threshold=np.nan)

from itertools import product
for etBinIdx, etaBinIdx in product( range( nEtBins if nEtBins is not None else 1 ), 
                                    range( nEtaBins if nEtaBins is not None else 1 )):
  with TuningDataArchieve(filePath, et_bin = etBinIdx if nEtBins is not None else None
                                  , eta_bin = etaBinIdx if nEtaBins is not None else None
                         ) as data:
    for sort in range(50):
      filePathPCA = '/afs/cern.ch/work/w/wsfreund/private/PCA-Validated/pca-%02d.npz' % (sort + 1)
      with TuningDataArchieve(filePathPCA, et_bin = etBinIdx if nEtBins is not None else None
                                         , eta_bin = etaBinIdx if nEtaBins is not None else None
                             ) as dataPCA:
        # Obtain data applying pre-processings:
        sigRings = data['signal_rings']
        bkgRings = data['background_rings']
        trnData, valData, tstData = crossValid( (sigRings, bkgRings), sort )
        ppChain = ppCol[etBinIdx][etaBinIdx][sort]
        ppChain.takeParams( trnData )
        sigPPAplied = ppChain( sigRings )
        # Obtain data with pre-processings applied on matlab:
        sigCmp = dataPCA['signal_rings'].T
        bkgCmp = dataPCA['background_rings'].T
        #trnDataCmp, valDataCmp, tstDataCmp = crossValid( (sigCmp, bkgRings), sort )
        #print "------------------------"
        #print np.mean( np.concatenate( trnDataCmp ), axis=0 )
        sigCmp = sigCmp[:,:sigPPAplied.shape[1]]
        deltaSig = np.abs( ( sigCmp - sigPPAplied ) / sigCmp * 100. )
        if np.any( deltaSig > 1e-2 ):
          print "WARNING: some delta sig is greater than threshold! eta: %d, et: %d, sort: %d" % (etaBinIdx, etBinIdx, sort)
          print "deltaSig[deltaSig > 1e-2]"
          print deltaSig[deltaSig > 1e-2]
        else:
          print "All OK sig. eta: %d, et: %d, sort: %d" % (etaBinIdx, etBinIdx, sort)
        #print "meanDeltaSig"
        #print np.mean( deltaSig, axis=0 )
        bkgPPAplied = ppChain( bkgRings )
        bkgCmp = bkgCmp[:,:bkgPPAplied.shape[1]]
        deltaBkg = np.abs( ( bkgCmp - bkgPPAplied ) / bkgCmp * 100. )
        if np.any(deltaBkg > 1e-2):
          print "WARNING: some delta bkg is greater than threshold! eta: %d, et: %d, sort: %d" % (etaBinIdx, etBinIdx, sort)
          print "deltaBkg[deltaBkg > 1e-2]"
          print deltaBkg[deltaBkg > 1e-2]
        else:
          print "All OK bkg. eta: %d, et: %d, sort: %d" % (etaBinIdx, etBinIdx, sort)
        #print "meanDeltaBkg"
        #print np.mean( deltaBkg, axis=0 )

            

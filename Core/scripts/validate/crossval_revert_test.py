#!/usr/bin/env python

import sys

from RingerCore import Logger, LoggingLevel
mainLogger = Logger.getModuleLogger(__name__)
mainLogger.info("Entering main job.")

crossValidFile = '/afs/cern.ch/work/w/wsfreund/private/crossValid.pic.gz'
dataLocation = '/afs/cern.ch/work/w/wsfreund/public/RingerTrainingSamples/mc14_13TeV.147406.129160.sgn.truth.bkg.truth.env.off.test-sample.npy'

from TuningTools import CrossValidArchieve, TuningDataArchieve
with CrossValidArchieve( crossValidFile ) as CVArchieve:
  crossValid = CVArchieve
del CVArchieve
mainLogger.info('CrossValid is: \n%s',crossValid)

mainLogger.info('Opening data...')
with TuningDataArchieve(dataLocation) as TDArchieve:
  data = TDArchieve
del TDArchieve

import numpy as np

for sort in range( crossValid.nSorts() ):
  mainLogger.info('Checking sort (%d)...', sort)
  trnData, valData, tstData = crossValid( data, sort ) 
  revertedData = crossValid.revert( trnData, valData, tstData, sort = sort )
  try:
    for idx, cData, cRevertedData in zip(range(len(data)), data, revertedData):
      np.testing.assert_equal(cData,cRevertedData,
          err_msg='Found differencies when reverting cross-val')
      mainLogger.info( 'Class (%d) is ok.', idx)
  except Exception, e:
    mainLogger.fatal( 'There were an issue when trying to compare reverted crossVal. Reason:\n%r', e )
    sys.exit(1)

sys.exit(0)

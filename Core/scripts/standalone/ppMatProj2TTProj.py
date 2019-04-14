#!/usr/bin/env python
#
# Convert matlab matrix projection to Tuning Tool PreProcesing objec.
# In matlab you can do this:
# 
# nEtBin = 5
# nEtaBin = 4
# nSort = 10
# projCollection = cell(nEtBin,nEtaBin,nSort)
# for et = 1:nEtBin
#   for eta = 1:nEtaBin
#     for sort = 1:nSort
#        projCollection{et,eta,sort} = A % your matrix projection here!
#     end
#   end
# end
# save('your pp file name', 'nEtaBin', 'nEtBin', 'projCollection')
#

from RingerCore import Logger, LoggingLevel, save, load, ArgumentParser, emptyArgumentsPrintHelp
from TuningTools import fixPPCol
import numpy as np
import sys, os

mainParser = ArgumentParser()

mainParser.add_argument('-i','--input', action='store',  required = True,
                        help = "The input files [.mat] that will be used to generate a extract the preproc proj matrix.\
                            Your matlab file must be inside:  projCollection = [[[]]], nEtaBin = int, nEtBin = int, \
                            nSort = int")
mainParser.add_argument('-o','--output', action='store',  required = False, default = 'ppCol',
                        help = "The output file")

emptyArgumentsPrintHelp( mainParser )

mainLogger = Logger.getModuleLogger( __name__, LoggingLevel.INFO )
args=mainParser.parse_args()


import scipy.io
mainLogger.info(('Loading matlab file: %s')%(args.input))
rawData = scipy.io.loadmat(args.input)
collections = rawData['projCollection']
nEta = rawData['nEtaBin'][0][0]
nEt = rawData['nEtBin'][0][0]
nSort= rawData['nSort'][0][0]

#initialize ppcol as none matrix
ppCol = [[[None for i in range(nSort)] for j in range(nEta)] for k in range(nEt)]


from TuningTools import npCurrent, fixPPCol
from copy import deepcopy

for etBin in range(nEt):
  for etaBin in range(nEta):
    mainLogger.info(('(Et = %d, Eta = %d) Parser information to PreProcChain')%(etBin,etaBin))
    for sort in range(nSort):

      obj = npCurrent.fp_array(collections[etBin][etaBin][sort])
      from TuningTools.PreProc import *
      mainLogger.debug('Projection matrix with shape: <%d, %d>', obj.shape[0], obj.shape[1])
      ppCol[etBin][etaBin][sort] = PreProcChain( Norm1(), Projection(matrix = obj) )

ppCol = fixPPCol( ppCol, len(ppCol[0][0]),len(ppCol[0]),len(ppCol))
mainLogger.info('Saving file...')
place = PreProcArchieve( args.output,  ppCol = ppCol ).save( compress = True )



nEt   = 2
nEta  = 2
nSorts= 2

from TuningTools.CreateTuningJobFiles import createTuningJobFiles
createTuningJobFiles( outputFolder   = 'config_citest0',
                      neuronBounds   = [2,2],
                      sortBounds     = 2,
                      nInits         = 1,
                      nNeuronsPerJob = 1,
                      nInitsPerJob   = 1,
                      nSortsPerJob   = 2,
                      compress       = True )

from TuningTools.CrossValid import CrossValid, CrossValidArchieve
crossValid = CrossValid(nSorts = nSorts,
                        nBoxes = 5,
                        nTrain = 3, 
                        nValid = 2,
                        #nTest=args.nTest,
                        #seed=args.seed,
                        #level=args.output_level
                        )
place = CrossValidArchieve( 'crossValid_citest0', 
                            crossValid = crossValid,
                            ).save( True )


from TuningTools.PreProc import *
#ppCol = PreProcCollection( PreProcChain( MapStd() ) )
ppCol = PreProcChain( Norm1() )
from TuningTools import fixPPCol
ppCol = fixPPCol(ppCol)
place = PreProcArchieve( 'ppFile_citest0', ppCol = ppCol ).save()



from TuningTools import SubsetGeneratorArchieve, fixSubsetCol, SubsetGeneratorPatterns, Cluster, GMMCluster
from TuningTools import Norm1 , PreProcChain, Projection


ppCross = [[[None for k in range(nSorts)] for j in range(nEta)] for i in range(nEt) ]
import numpy as np
def genMat(m,c,f):
  return np.random.normal(m,1,(c,f))

for etBin in range(nEt):
  for etaBin in range(nEta):
    for sort in range(nSorts):
      ppCross[etBin][etaBin][sort] = SubsetGeneratorPatterns(
        Cluster(code_book = genMat(0,3,100), ppChain = PreProcChain(Norm1())) , 
        Cluster(code_book = genMat(1,3,100), ppChain = PreProcChain(Norm1())) , 
        #GMMCluster(code_book = gen(0,3,20),sigma = gen(0,3,20) , ppChain = PreProcChain(Projection(matrix = gen(0,100,20))) ), 
        #GMMCluster(code_book = gen(1,3,20),sigma = gen(0,3,20) , ppChain = PreProcChain(Projection(matrix = gen(0,100,20))) ), 
      )

ppCross = fixSubsetCol( ppCross, len(ppCross[0][0]),len(ppCross[0]),len(ppCross))

place = SubsetGeneratorArchieve( 'crossValidSubset_citest0', 
                                  subsetCol = ppCross,
                                ).save( True )

print 'opening'




import sys,os
sys.exit(os.EX_OK) # code 0, all ok


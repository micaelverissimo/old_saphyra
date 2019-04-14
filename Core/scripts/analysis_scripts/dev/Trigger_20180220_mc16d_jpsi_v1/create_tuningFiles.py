

#from TuningTools.CreateTuningJobFiles import createTuningJobFiles
#createTuningJobFiles( outputFolder   = 'config.n5to10.JK.inits_10by10',
#                      neuronBounds   = [5,10],
#                      sortBounds     = 10,
#                      nInits         = 100,
#                      nNeuronsPerJob = 1,
#                      nInitsPerJob   = 10,
#                      nSortsPerJob   = 1,
#                      prefix         = 'job_slim',
#                      compress       = True )
#
#
#
#from TuningTools.CrossValid import CrossValid, CrossValidArchieve
#crossValid = CrossValid(nSorts = 10,
#                        nBoxes = 10,
#                        nTrain = 9, 
#                        nValid = 1,
#                        )
#place = CrossValidArchieve( 'crossValid', 
#                            crossValid = crossValid,
#                            ).save( True )

nsorts=10; neta=5; net=4
from TuningTools.PreProc import *
ppCol = [[[PreProcChain( Norm1() ) for _ in range(nsorts)] for __ in range(neta)] for ___ in range(net)]
ppCol = PreProcChain( Norm1() ) 


from TuningTools.TuningJob import fixPPCol

ppCol = fixPPCol(ppCol)
place = PreProcArchieve( 'ppFile', ppCol = ppCol ).save()




from TuningTools.CreateTuningJobFiles import createTuningJobFiles
createTuningJobFiles( outputFolder   = 'configs.n5to10.jk.inits_20by20',
                      neuronBounds   = [5,10],
                      sortBounds     = 10,
                      nInits         = 100,
                      nNeuronsPerJob = 1,
                      nInitsPerJob   = 20,
                      nSortsPerJob   = 1,
                      prefix         = 'job_configs',
                      compress       = True )



from TuningTools.CrossValid import CrossValid, CrossValidArchieve
crossValid = CrossValid(nSorts = 10,
                        nBoxes = 10,
                        nTrain = 9, 
                        nValid = 1,
                        )
place = CrossValidArchieve( 'crossValid', 
                            crossValid = crossValid,
                            ).save( True )


from TuningTools.PreProc import *
ppCol = PreProcChain( Norm1() ) 


from TuningTools.TuningJob import fixPPCol
ppCol = fixPPCol(ppCol)
place = PreProcArchieve( 'ppFile', ppCol = ppCol ).save()


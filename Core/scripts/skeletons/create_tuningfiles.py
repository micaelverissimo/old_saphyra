#!/usr/bin/env python

from TuningTools.CreateTuningJobFiles import createTuningJobFiles
createTuningJobFiles( outputFolder   = 'config.nn5to6_sorts5_5by5_inits5_5by5',
                      neuronBounds   = [5, 6],
                      sortBounds     = 5,
                      nInits         = 5,
                      nNeuronsPerJob = 2,
                      nInitsPerJob   = 5,
                      nSortsPerJob   = 5,
                      compress       = True )

from TuningTools.CrossValid import CrossValid, CrossValidArchieve
crossValid = CrossValid(nSorts = 5,
                        nBoxes = 10,
                        nTrain = 6, 
                        nValid = 4,
                        #nTest=args.nTest,
                        #seed=args.seed,
                        #level=args.output_level
                        )

place = CrossValidArchieve( 'crossValid_5sorts', 
                            crossValid = crossValid,
                            ).save( True )

from TuningTools.PreProc import *
ppCol = PreProcCollection( PreProcChain( MapStd() ) )
place = PreProcArchieve( 'ppMapStd', ppCol = ppCol ).save()




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


from TuningTools.PreProc import *
#ppCol = PreProcChain( Norm1() ) 
#ppCol = PreProcChain([TrackSimpleNorm()])
#ppCol = PreProcChain([ShowerShapesSimpleNorm()])
#ppCol = PreProcChain([ExpertNetworksSimpleNorm()])
#ppCol = PreProcChain([ExpertNetworksShowerShapeSimpleNorm()])
#ppCol = PreProcChain([ExpertNetworksShowerShapeAndTrackSimpleNorm()])



from TuningTools.TuningJob import fixPPCol
#ppCol = fixPPCol(ppCol)
#place = PreProcArchieve( 'ppFile', ppCol = ppCol ).save()



### Implement the segmentation preproc
layers = [RingerLayer.PS,RingerLayer.EM1,RingerLayer.EM2,RingerLayer.EM3,RingerLayer.HAD1,RingerLayer.HAD2,RingerLayer.HAD3]
for l in layers:
  #ppCol = PreProcChain( [RingerLayerSegmentation(layer=l), Norm1()] )
  ppCol = PreProcChain( [Norm1(), RingerLayerSegmentation(layer=l)] )
  ppCol = fixPPCol(ppCol)
  #place = PreProcArchieve( 'ppFile.Seg%s_Norm1'%RingerLayer.tostring(l), ppCol = ppCol ).save()
  place = PreProcArchieve( 'ppFile.Norm1_Seg%s'%RingerLayer.tostring(l), ppCol = ppCol ).save()









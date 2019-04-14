
__all__ = [ "LinearPileupCorrectionDrawer", "TuningDrawer" ]

from plots.PlotFunctions import *
from plots.TAxisFunctions import *
from RingerCore import Logger, LoggingLevel, retrieve_kw, checkForUnusedVars, expandFolders, csvStr2List
import ROOT
from ROOT import kBlue, kBlack, kRed, kMagenta, kGreen 
from ROOT import TH1,TH1F, TH2F, TProfile,TCanvas,TFile,TColor
import numpy as np
from plots.AtlasStyle import ATLASLabel, ATLASLumiLabel, SetAtlasStyle
import argparse
#from rDev.drawers.AtlasStyle import *
SetupStyle()

from ROOT import kBlack,kBlue,kRed,kAzure,kGreen,kMagenta,kCyan,kOrange,kGray,kYellow,kWhite

local_these_colors = [kGray+2,kBlue-4,kRed-2,kAzure+2,kGreen+1,kMagenta+1,kCyan+1,kOrange+1
                ,kBlack+2,kRed+3,kBlue+3,kGreen+3,kMagenta+3,kCyan+3,kOrange+3
                ,kGray,kRed-7,kBlue-7,kGreen-7,kMagenta-7,kCyan-7,kOrange-7
                ,kYellow+2,kRed-5,kBlue-5,kGreen-5,kMagenta-5,kCyan-5,kOrange-5
                ,21,22,23,24,25,26,27,28,29,30
                ,21,22,23,24,25,26,27,28,29,30
                ,21,22,23,24,25,26,27,28,29,30
                ]

local_these_transcolors=[ROOT.TColor.GetColorTransparent(c,.5) for c in local_these_colors]
local_these_marker = (23, 24, 22, 26, 32 ,23, 20,25)


xlabel = {'nvtx':'N_{vtx}','mu':'<#mu>'}

eps=0.001
# sort frame function
def SortFrames( frames, best=0, worst=0, attribute='sort' ):
  """
    Use this function to sort all frames. The first position
    will be the best sort and the last position will be the
    worst case.
  """
  l=list()
  bestObj = None; worstObj=None
  for f in frames:
    ### Hold the best frame
    if getattr(f,attribute) == best:  bestObj=f
    ### Hold the worst frame
    if getattr(f,attribute) == worst: worstObj=f
    if getattr(f,attribute) != best or getattr(f,attribute) != worst: l.append(f)
  # Add the best in the first position and the worst
  # frame in the end
  l.insert(0,bestObj)
  l.append(worstObj)
  return l



def TuningDrawer( basepath, neuron, oDict, csummary, logger=None ):


  neuronStr = 'config_'+str(neuron).zfill(3)
  objects = SortFrames( oDict['allBestOpSorts'], 
                        best  = csummary[neuronStr]['infoTstBest']['sort'],
                        worst = csummary[neuronStr]['infoTstWorst']['sort'],
                        attribute = 'sort')
   ### Get Et bin
  etlist = csummary['etBin'].tolist()
  ### Get eta bin
  etalist = csummary['etaBin'].tolist()
 
  ### Initialize all frames
  for frames in objects: frames.initialize()

  ### Make the legend MSE plot, the order here matter!
  legends = [None for _ in range(len(objects))]
  legends[0] = 'MSE curves (Tst)' 
  legends.append("Worst MSE sort (Tst)")
  legends.append("Best MSE sort (Tst)")
  legends.append("Best MSE sort (Trn)")

  outname=basepath+'/mse_val.pdf'
  if logger:  logger.debug("Save as  %s"%outname)
  PlotMeanSquareError(objects, outname=outname, etlist=etlist, etalist=etalist,
                      legends = legends)

  hists = [frame['roc_tst'] for frame in objects]
  legends = [None for _ in range(len(objects))]
  legends[0] = 'ROC (tst)' 
  legends.append("Best ROC sort (tst)")
  legends.append("Worst ROC sort (tst)")
  outname = basepath+'/roc_tst.pdf'
  if logger:  logger.debug("Save as  %s"%outname)
  PlotRoc( hists, etlist=etlist, etalist=etalist , outname=outname, legends=legends)

  for frames in objects: frames.finalize()


  objects = SortFrames( oDict['allBestOpSorts'], 
                        best  = csummary[neuronStr]['infoOpBest']['sort'],
                        worst = csummary[neuronStr]['infoOpWorst']['sort'],
                        attribute = 'sort')
 
  for frames in objects: frames.initialize()
  hists = [frame['roc_operation'] for frame in objects]
  legends = [None for _ in range(len(objects))]
  legends[0] = 'ROC (Op)' 
  legends.append("Best ROC sort (Op)")
  legends.append("Worst ROC sort (Op)")
  outname = basepath+'/roc_operation.pdf'
  if logger:  logger.debug("Save as  %s"%outname)
  PlotRoc( hists, etlist=etlist, etalist=etalist , outname=outname, legends=legends)

  for frames in objects: frames.finalize()




def LinearPileupCorrectionDrawer( basepath, neuron, oDict, csummary, logger=None ):

  neuronStr = 'config_'+str(neuron).zfill(3)
  ### Get the pileup limits
  limits = csummary[neuronStr]['summaryInfoOp']['limits']
  ### Get Et bin
  etlist = csummary['etBin'].tolist()
  ### Get eta bin
  etalist = csummary['etaBin'].tolist()
  ### Get min and max points
  pileup_min = limits[0]
  pileup_max = limits[2]+5
  pileup_nbins= pileup_max-pileup_min

  ### Pileup variable
  pileupVar = csummary[neuronStr]['summaryInfoOp']['pileupStr']

  objects = SortFrames( oDict['allBestOpSorts'], 
                        best  = csummary[neuronStr]['infoTstBest']['sort'],
                        worst = csummary[neuronStr]['infoTstWorst']['sort'],
                        attribute = 'sort')
  
  thesecolors = [GetTransparent(kGray+1) for _ in range(len(objects))]
  thesecolors[0] = kBlue+2
  thesecolors[-1]= kRed+2
  thesemarkers = [23]*len(objects)

  ### helper function to fix the x axis
  def FixXaxis(hists, nbins, xmin, xmax):
    for idx, h in enumerate(hists):
  	  hists[idx] = GetXAxisWorkAround( h, nbins, xmin, xmax )


  for frames in objects: frames.initialize()
  ### Get Signal Eff Corrected for all sorts in tst
  hists = [frame['signalCorr_tstData_eff'] for frame in objects]
  outname = basepath+'/signalCorr_tstData_eff.pdf'
  FixXaxis(hists,pileup_nbins,pileup_min,pileup_max)
  
  if logger:  logger.debug("Save as  %s"%outname)
  PlotProfiles( hists, theseColors=thesecolors, theseMarker=thesemarkers,
                xlabel=xlabel[pileupVar], outname=outname, etlist=etlist, 
                etalist=etalist)


  ### Get Background Eff Corrected for all sorts in tst
  hists = [frame['backgroundCorr_tstData_eff'] for frame in objects]
  FixXaxis(hists,pileup_nbins,pileup_min,pileup_max)
  outname = basepath+'/backgroundCorr_tstData_eff.pdf'
  if logger:  logger.debug("Save as  %s"%outname)
  PlotProfiles( hists, theseColors=thesecolors, theseMarker=thesemarkers ,
                xlabel=xlabel[pileupVar], outname=outname, etlist=etlist, etalist=etalist) 
  for frames in objects: frames.finalize()


  objects = SortFrames( oDict['allBestOpSorts'], 
                      best  = csummary[neuronStr]['infoOpBest']['sort'],
                      worst = csummary[neuronStr]['infoOpWorst']['sort'],
                      attribute = 'sort')

  for frames in objects: frames.initialize()
  ### Get Signal Eff for all sorts in operation
  hists = [frame['signalCorr_opData_histEff'] for frame in objects]
  FixXaxis(hists,pileup_nbins,pileup_min,pileup_max)
  outname = basepath+'/signalCorr_opData_eff.pdf'
  if logger:  logger.debug("Save as  %s"%outname)
  PlotProfiles( hists, theseColors=thesecolors, theseMarker=thesemarkers,
                xlabel=xlabel[pileupVar], outname=outname, etlist=etlist, etalist=etalist) 
  

  ### Make before and after correction
  frameTst = oDict['allBestTstNeurons'][-1]
  frameOp = oDict['allBestOpNeurons'][-1]
  frameTst.initialize(); frameOp.initialize()

  hists = [ # NOTE: the best sort in the tst 
            frameTst['signalCorr_tstData_eff'],
            # NOTE: the best sort in the op
            frameOp['signalCorr_opData_histEff'],
            frameTst['signalUncorr_tstData_eff'],
            frameOp['signalUncorr_opData_eff'],
          ]
  legends = ['tstData corrected', 'opData corrected', 'tstData uncorrected', 'opData uncorrected']
  thesecolors = [kBlack, kBlack, kGray+1, kGray+1]
  thesemarkers = [20, 23, 4, 32]
  outname = basepath+'/signalComparison_opData_eff.pdf'
  FixXaxis(hists,pileup_nbins,pileup_min,pileup_max)
  if logger:  logger.debug("Save as  %s"%outname)
  PlotProfiles( hists, theseColors=thesecolors, theseMarker=thesemarkers, legends=legends, 
                outname=outname, etlist=etlist, etalist=etalist)
  frameTst.finalize()


  ### Make 2D Signal Operation Plot
  outname = basepath+'/signalCorr2D_opData.pdf' 
  hist2D = frameOp['signal2DCorr_opData']
  if logger:  logger.debug("Save as  %s"%outname)
  Plot2DCorrection( Copy2DRegion(hist2D, hist2D.GetNbinsX(), hist2D.GetXaxis().GetXmin(), 
                   hist2D.GetXaxis().GetXmax(), pileup_nbins, pileup_min, pileup_max),
									 frameOp['signalCorr_opData_graph'], frameOp['signalCorr_opData_f1'], 
                   xlabel = xlabel[pileupVar], etlist=etlist, etalist=etalist, outname=outname)

  
  ### Make 2D Background Operation Plot
  outname = basepath+'/backgroundCorr2D_opData.pdf'
  hist2D = frameOp['background2DCorr_opData']
  f1 = [frameOp['signalCorr_opData_f1']] + [frameOp['backgroundCorr_%d_opData_f1'%n] for n in range(7)]
  if logger:  logger.debug("Save as  %s"%outname)
  Plot2DCorrection( Copy2DRegion(hist2D, hist2D.GetNbinsX(), hist2D.GetXaxis().GetXmin(), 
                   hist2D.GetXaxis().GetXmax(), pileup_nbins, pileup_min, pileup_max),
									 frameOp['signalCorr_opData_graph'], f1,
                   xlabel = xlabel[pileupVar], etlist=etlist, etalist=etalist, outname=outname)


  frameOp.finalize()




######################################################################################################


def AddTopLabels(can,legend, legOpt = 'p', quantity_text = '', etlist = None
                     , etalist = None, etidx = None, etaidx = None, legTextSize=10
                     , runLabel = '', extraText1 = None, legendY1=.68, legendY2=.93
                     , maxLegLength = 19, logger=None):
    text_lines = []
    #text_lines += [GetAtlasInternalText()]
    #text_lines.append( GetSqrtsText(13) )
    if runLabel: text_lines.append( runLabel )
    if extraText1: text_lines.append( extraText1 )
    DrawText(can,text_lines,.40,.68,.70,.93,totalentries=4)
    if legend:
        MakeLegend( can,.53,legendY1,.89,legendY2,textsize=legTextSize
                  , names=legend, option = legOpt, squarebox=False
                  , totalentries=0, maxlength=maxLegLength )
    try:
        extraText = []
        if etlist and etidx is not None:
            # add infinity in case of last et value too large
            #for idx, v in enumerate(etlist):  etlist[idx] = round(v,2)
            if etlist[-1]>9999:  etlist[-1]='#infty'
            binEt = (str(etlist[etidx]) + ' < E_{T} [GeV] < ' + str(etlist[etidx+1]) if etidx+1 < len(etlist) else
                                     'E_{T} > ' + str(etlist[etidx]) + ' GeV')
            extraText.append(binEt)
        if quantity_text: 
            if not isinstance(quantity_text,(tuple,list)): quantity_text = [quantity_text]
            extraText += quantity_text
        if etalist and etaidx is not None:
            for idx, v in enumerate(etalist):  etalist[idx] = round(v,2)
            binEta = (str(etalist[etaidx]) + ' < #eta < ' + str(etalist[etaidx+1]) if etaidx+1 < len(etalist) else
                                        str(etalist[etaidx]) + ' < #eta < 2.47')
            extraText.append(binEta)
        DrawText(can,extraText,.14,.68,.35,.93,totalentries=4)
    except NameError, e:
        if logger:
          logger.warning("Couldn't print test due to error: %s", e)
        pass



def PlotProfiles( hists, legends=None, title=None, drawopt='pE1', runLabel=None, outname=None, 
                  theseColors=None,theseTransColors=None,theseMarker=None,
                  extraText1=None,legendX1=.5, xlabel='nvtx',ylabel='Efficiency',
                  etlist=None, etalist=None, etidx=0, etaidx=0):

  these_colors = theseColors if theseColors else local_these_colors
  these_transcolors = theseTransColors if theseTransColors else local_these_transcolors
  these_marker = theseMarker if theseMarker else local_these_marker
  outcan = TCanvas( 'canvas', "", 500, 500)  

  collect=[]
  for idx, hist in enumerate(hists): 
    AddHistogram(outcan, hist, drawopt = drawopt)
    SetColors(outcan,these_colors=these_colors)
    SetMarkerStyles(outcan, these_styles=these_marker)
    SetColors(outcan,these_colors=these_transcolors, lineColor=False,markerColor=False,fillColor=True)
  
  AddTopLabels(outcan, legends, runLabel=runLabel, legOpt='p',
               etlist=etlist,etalist=etalist,etidx=etidx,etaidx=etaidx)

  FormatCanvasAxes(outcan, XLabelSize=18, YLabelSize=18, XTitleOffset=0.87, YTitleOffset=1.5)
  SetAxisLabels(outcan,xlabel,ylabel)
  AutoFixAxes(outcan,ignoreErrors=False)
  #FixYaxisRanges(outcan, ignoreErrors=True, yminc=-eps )
  #AddBinLines(outcan,hists[0],useHistMax=True,horizotalLine=0.)
  #AddBinLines(outcan,hists[0],useHistMax=True,horizotalLine=0.)
  outcan.SaveAs( outname ) 


  

def Plot2DCorrection( hist2D, graph, f1,etBin = None, etaBin = None, outname=None, 
                     xlabel='N_{vtx}',runLabel=None, legends=None, extraText1=None,
                     legendX1=.5,etidx=None,etaidx=None,etlist=None, etalist=None):

  import array as ar
  from ROOT import TCanvas, gStyle, TLegend, kRed, kBlue, kBlack, TLine, kBird, kOrange
  from ROOT import TGraphErrors, TF1, TColor
  pileup_max = hist2D.GetYaxis().GetXmax()
  pileup_min = hist2D.GetYaxis().GetXmin()
  # Retrieve some usefull information
  gStyle.SetPalette(kBird)
  canvas = TCanvas('canvas','canvas', 500, 500)
  #FormatCanvasAxes(canvas, XLabelSize=18, YLabelSize=18, XTitleOffset=0.87, YTitleOffset=1.5)
  canvas.SetRightMargin(0.12)
  canvas.SetLeftMargin(0.10)
  hist2D.Draw('colz')
  hist2D.GetZaxis().SetTitle("Entries")
  canvas.SetLogz()
  AddTopLabels(canvas, legends, runLabel=runLabel, legOpt='p',
               etlist=etlist,etalist=etalist,etidx=etidx,etaidx=etaidx)
  FormatCanvasAxes(canvas, XLabelSize=12, YLabelSize=12, XTitleOffset=0.87, ZLabelSize=12, 
                   ZTitleSize=14, YTitleOffset=0.87, ZTitleOffset=0.67) 
  SetAxisLabels(canvas,'Neural Network output (Discriminant)',xlabel)
  # Invert graph
  import array
  x=graph.GetX(); x.SetSize(graph.GetN())
  ex=graph.GetEX(); ex.SetSize(graph.GetN())
  y=graph.GetY(); y.SetSize(graph.GetN())
  ey=graph.GetEY(); ey.SetSize(graph.GetN())
  nvtx_points        = array.array( 'd', x )
  nvtx_error_points  = array.array( 'd', ex )
  discr_points       = array.array('d', y  )
  discr_error_points = array.array( 'd', ey )
  g1 = TGraphErrors(len(discr_points), discr_points, nvtx_points, discr_error_points, nvtx_error_points)
  g1.SetLineWidth(1)
  #g1.SetLineColor(kBlack)
  g1.SetMarkerColor(kBlue+1)
  g1.SetMarkerSize(.6)
  g1.Draw("P same")
  tobject_collector.append(g1)
  #l2 = TLine(eff_uncorr.thres,miny,eff_uncorr.thres,maxy)
  #l2.SetLineColor(kRed)
  #l2.SetLineWidth(2)
  #l2.Draw("l,same")
  #tobject_collector.append(l2)
  #f1 = eff.f1
  if type(f1) is not list:  f1=[f1]
  
  for idx, f in enumerate(f1):
    l3 = TLine(f.Eval(pileup_min), pileup_min, f.Eval(pileup_max), pileup_max)
    if idx>0:  l3.SetLineColor(GetTransparent(kRed))
    else:
      l3.SetLineColor(kBlack)
    l3.SetLineWidth(2)
    l3.Draw("l,same")
    tobject_collector.append(l3)
  
  if outname:  canvas.SaveAs(outname)






def PlotMeanSquareError( frames, outname=None, drawtrn=True, runLabel=None, etlist=None, etalist=None,
                         etidx=0, etaidx=0, legends=None):

  canvas = TCanvas('canvas', 'canvas', 1500, 800)
  FormatCanvasAxes(canvas)
  drawopt='l'
  
  for idx in range(len(frames)):
    graph = frames[idx]['mse_val']
    graph.SetLineColor(GetTransparent(kGray))
    graph.SetMarkerColor(GetTransparent(kGray))
    AddHistogram(canvas,graph,drawopt)
    #graph.Draw('same')

  ### Plor the worst curve
  wgraph = frames[-1]['mse_val']
  wgraph.SetLineColor(kRed+2)
  wgraph.SetMarkerColor(kRed+2)
  AddHistogram(canvas,wgraph,drawopt)
  #wgraph.Draw('AL')
  ### Plot the best curve
  bgraph = frames[0]['mse_val']
  bgraph.SetLineColor(kBlue+2)
  bgraph.SetMarkerColor(kBlue+2)
  AddHistogram(canvas,bgraph,drawopt)
  #bgraph.Draw('same')

  ### Plot the train best curve
  if drawtrn:
    tgraph = frames[0]['mse_trn']
    tgraph.SetLineColor(kBlack)
    tgraph.SetMarkerColor(kBlack)
    tgraph.SetLineStyle(2)
    AddHistogram(canvas,tgraph,drawopt)
    #tgraph.Draw('same')

  AddTopLabels(canvas, legends, runLabel=runLabel, legOpt='p',
               etlist=etlist,etalist=etalist,etidx=etidx,etaidx=etaidx)
  SetAxisLabels(canvas, 'Epoch', 'MSE')
  FixYaxisRanges(canvas, ignoreErrors=True, yminc=-eps)
  AutoFixAxes(canvas, ignoreErrors=True)
  if outname:  canvas.SaveAs(outname)




def PlotRoc(hists ,outname=None, runLabel=None, etlist=None, etalist=None, etidx=0, etaidx=0,
            drawopt='l', legends=None, yminValue=0.7, ymaxValue=0.99):

  canvas = TCanvas('canvas', 'canvas', 500, 500)
  for hist in hists:
    hist.SetLineColor(GetTransparent(kGray+3))
    hist.SetMarkerColor(GetTransparent(kGray+3))
    AddHistogram(canvas,hist,drawopt)
  
  bgraph = hists[0]
  bgraph.SetLineColor(kBlue+2)
  bgraph.SetMarkerColor(kBlue+2)
  AddHistogram(canvas,bgraph,drawopt)
  wgraph = hists[-1]
  wgraph.SetLineColor(kRed+2)
  wgraph.SetMarkerColor(kRed+2)
  AddHistogram(canvas,wgraph,drawopt)

  FormatCanvasAxes(canvas, XLabelSize=12, YLabelSize=18, XTitleOffset=0.87, YTitleOffset=1.5)
  AddTopLabels(canvas, legends, runLabel=runLabel, legOpt='p',
               etlist=etlist,etalist=etalist,etidx=etidx,etaidx=etaidx)
  SetAxisLabels(canvas, 'False Alarm', 'Detection')

  ### Make the Zoon
  import array
  graph = hists[0]
  ### Retrieve the X,Y coordinates from TGraph object
  x=graph.GetX(); x.SetSize(graph.GetN())
  y=graph.GetY(); y.SetSize(graph.GetN())
  x = array.array( 'd', x )
  y = array.array( 'd', y )
  ### Make the Zoon
  xmin=0; xmax=1; ymin=0; ymax=1
  for idx in range(len(x)):
    if y[idx]> yminValue:  xmin=x[idx]; ymin=y[idx]
    if y[idx]> ymaxValue: xmax=x[idx]; ymax=y[idx]

  SetXaxisRanges(canvas,xmin,xmax)
  SetYaxisRanges(canvas,ymin,ymax) 
  #AutoFixAxes(canvas, ignoreErrors=True)
  if outname:  canvas.SaveAs(outname)




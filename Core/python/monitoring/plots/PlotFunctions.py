
try:
  from TagAndProbeFrame.PlotFunctions import *
  __TP_PlotFunctions = True
except ImportError:
  __TP_PlotFunctions = False

if not __TP_PlotFunctions:
  from TAxisFunctions import *
  from ROOT import TColor, kGray

  ##
  ## New plotting functions :
  ##
  ## FullFormatCanvasDefault(can,...)
  ## ConvertToDifferential()
  ## AddHistogram(can,hist)
  ## SetAxisLabels(can,xlabel,ylabel)
  ## SetColors(can,[color1,color2,color3...])
  ## GetLuminosityText(lumi)
  ## GetSqrtsText(sqrts)
  ## GetAtlasInternalText(status='Internal')
  ## DrawText(can,text,x1,y1,x2,y2,...)
  ## MakeLegend(can,x1,x2,y1,y2,...)
  ## FormatCanvasAxes(can,options...) - must be run AFTER the first histograms are added!
  ## SetupStyle()
  ## RatioCanvas(name,title,canw,canh,ratio_size_as_fraction)
  ## SetLeftMargin(can,margin)
  ## GetTopPad(can)
  ## GetBotPad(can)
  ## AddHistogramTop(can,hist)
  ## AddHistogramBot(can,hist)
  ## AddRatio(can,hist,ref_hist)
  ##
  ## # SetMarkerStyles() Coming soon!
  ## # SetFillStyles() Coming soon!
  ##

  ##
  ## This global list called "tobject_collector" collects TObjects (TH1, TGraph, TLegend, TLatex...)
  ## that are created in these functions. It is a way of preventing these objects from going out of 
  ## scope (and thus being deleted) while requiring very little from the user.
  ##
  ## IMPORTANT NOTE! If you are using too much memory because of the proliferation of TObjects in this
  ## list, you can periodically delete them (after you have printed the canvas to pdf) by calling
  ## del tobject_collector[:]
  ## in your script. (tobject_collector is a global variable, so this single line is sufficient.)
  ##
  global tobject_collector;
  tobject_collector = []

  def clear_objects():
    global tobject_collector;
    tobject_collector = []


  tGray = TColor.GetColorTransparent( kGray+2, .3 )

  ##
  ## FullFormatCanvasDefault is a collection of functions for easy "1-step" plotting.
  ##
  def FullFormatCanvasDefault(can,lumi=3.2,sqrts=13,additionaltext1='',additionaltext2='',
                              preliminary=False,ignoreErrors=False, addLegend=True, setColors=True) :
      FormatCanvasAxes(can)
      if setColors: SetColors(can)
      text_lines = []
      #text_lines += [GetAtlasInternalText()]

      if sqrts and lumi : text_lines += [GetSqrtsText(sqrts)+', '+ GetLuminosityText(lumi)]
      elif sqrts : text_lines += [GetSqrtsText(sqrts)]
      elif lumi : text_lines += [GetLuminosityText(lumi)]

      if additionaltext1 : 
          additionaltext1 = FixLength(additionaltext1)
          text_lines += [additionaltext1]
      if additionaltext2 : 
          additionaltext2 = FixLength(additionaltext2)
          text_lines += [additionaltext2]
      if can.GetPrimitive('pad_top') :
          DrawText(can,text_lines,.35,.68,.65,.93,totalentries=4)
          #DrawText(can,text_lines,.30,.68,.65,.93,totalentries=4)
          #DrawText(can,text_lines,.20,.68,.45,.93,totalentries=4)
          if addLegend:
              #MakeLegend(can,.65,.73,.85,.93,totalentries=2,textsize=12)
              MakeLegend(can,.55,.68,.80,.93,totalentries=2,textsize=12)
      else :
          #DrawText(can,text_lines,.40,.73,.70,.94,totalentries=4)
          DrawText(can,text_lines,.40,.73,.70,.94,totalentries=4)
          if addLegend:
              MakeLegend(can,.6,.78,.8,.94,totalentries=2,textsize=12)
      AutoFixAxes(can,ignoreErrors)
      return

  def AddXAxisWorkaround(can, hists):
      if can.GetPrimitive('pad_bot'): AddXAxisWorkaround(can.GetPrimitive('pad_bot'),hists)
      if can.GetPrimitive('pad_top'): AddXAxisWorkaround(can.GetPrimitive('pad_top'),hists)
      if can.GetPrimitive('pad_bot') or can.GetPrimitive('pad_bot'): return
      if not isinstance(hists,(tuple,list)): hists = [hists]
      axesLimits = [(hist.GetXaxis().GetBinLowEdge(1),hist.GetXaxis().GetBinUpEdge(hist.GetXaxis().GetNbins())) for hist in hists if hist]
      if len(hists) == 1 or not all(map(lambda x,y: x == y, axesLimits[1:], axesLimits[:-1])):
          from ROOT import TH1F, kWhite
          from operator import itemgetter
          limits = (min(axesLimits, key=itemgetter(0))[0], max(axesLimits, key=itemgetter(1))[1])
          hist = TH1F("__xaxis","",1,limits[0], limits[1])
          hist.SetStats(0)
          # Make it invisible
          hist.SetLineColorAlpha( kWhite, 0. )
          AddHistogram(can, hist, drawopt="hist")


  ##
  ## Convert a histogram to a differential histogram. Remember to change your y-axis label accordingly
  ## (e.g. events/GeV)
  ##
  def ConvertToDifferential(hist) :
      hist.Scale(1,'width')
      return

  ##
  ## Add a TH1 or a TGraph to a canvas.
  ## If a RatioCanvas is specified as the canvas, then the histogram will be added to the top pad
  ## by default. (To specifically add a canvas to the bottom, do AddHistogram(GetBotPad(can),hist)
  ## This will *make a copy* of the histogram or graph, so that when you further manipulate the histogram
  ## in its canvas it will only affect the appearance in this one canvas. This way you
  ## can add the same histogram to multiple canvases and be able to manipulate the appearance of each
  ## instance separately.
  ##
  def AddHistogram(can,hist,drawopt='pE1',inStack=False,markerSize=1, markerStyle = 20) :
      if can.GetPrimitive('pad_top') :
          AddHistogram(can.GetPrimitive('pad_top'),hist,drawopt,inStack,markerSize,markerStyle)
          return
      from ROOT import TH1,TGraph,THStack
      tmp = hist.Clone()
      is_graph = issubclass(type(hist),TGraph)
      is_stack = issubclass(type(hist),THStack)

      plot_exists = list(issubclass(type(a),TH1) for a in can.GetListOfPrimitives())
      plot_exists += list(issubclass(type(a),TGraph) for a in can.GetListOfPrimitives())
      plot_exists += list(issubclass(type(a),THStack) for a in can.GetListOfPrimitives())

      if (not is_graph) and (True in plot_exists) :
          if not "same" in drawopt: drawopt += ' sames'
      if is_graph and not (True in plot_exists) :
          drawopt += ' a'
      if is_stack :
          tobject_collector.append(tmp)
          #drawopt += ' same'
          can.cd()
          tmp.Draw(drawopt)
          return

      tobject_collector.append(tmp)
      if markerSize is not None:
          tmp.SetMarkerSize(markerSize)
      if markerStyle is not None:
          tmp.SetMarkerStyle(markerStyle)

      tmp.SetName('%s_%s'%(can.GetName(),hist.GetName()))
      if not inStack :
          can.cd()
          tmp.Draw(drawopt)
      return

  ##
  ## Set x- and y-axis labels. Do this *after* you have added your first histogram to the canvas.
  ##
  def SetAxisLabels(can,xlabel,ylabel,yratiolabel='ratio') :
      if 'pad_top' in (a.GetName() for a in can.GetListOfPrimitives()) :
          SetAxisLabels(can.GetPrimitive('pad_bot'),xlabel,yratiolabel)
          SetAxisLabels(can.GetPrimitive('pad_top'),'',ylabel)
      for i in can.GetListOfPrimitives() :
          if hasattr(i,'GetXaxis') :
              i.GetXaxis().SetTitle(xlabel)
              i.GetYaxis().SetTitle(ylabel)
              break
      can.Modified()
      can.Update()
      return


  ##
  ## Set x- and y-axis labels. Do this *after* you have added your first histogram to the canvas.
  ##
  def SetYAxisLimits(can,low,high) :
      for i in can.GetListOfPrimitives() :
          if hasattr(i,'GetYaxis') :
              i.GetYaxis().SetRangeUser(low, high)
              break
      can.Modified()
      can.Update()
      return

  def SetMarkerStyles(can,these_styles=[],these_sizes=[],alsoBottom=True) :
      if not these_styles :
          these_styles = [20 for i in xrange(30)]
                          
      if not these_sizes :
          these_sizes = [1 for i in xrange(30)]

      the_primitives = can.GetListOfPrimitives()
      if can.GetPrimitive('pad_top') :
          the_primitives = can.GetPrimitive('pad_top').GetListOfPrimitives()

      style_count = 0
      for i in the_primitives :
          if any([ignore in i.GetName() for ignore in ("ShadedProfile", "__xaxis")]): 
              continue
          if hasattr(i,'SetMarkerColor') :
              i.SetMarkerStyle(these_styles[style_count])
              i.SetMarkerSize(these_sizes[style_count])
              #
              # Check if there is a bottom pad, with ratios...
              #
              if can.GetPrimitive('pad_bot') and alsoBottom:
                  original_name = i.GetName().replace('pad_top_','')
                  j = can.GetPrimitive('pad_bot').GetPrimitive('pad_bot_%s_ratio'%(original_name))
                  if j :
                      j.SetMarkerStyle(these_styles[style_count])
                      j.SetMarkerSize(these_sizes[style_count])
                      j = can.GetPrimitive('pad_bot').GetPrimitive('pad_bot_%s_ratio_specialCases'%(original_name))
                      if j :
                          j.SetMarkerSize(these_sizes[style_count])
                      can.GetPrimitive('pad_bot').Modified()
                      can.GetPrimitive('pad_bot').Update()
              style_count += 1
          if style_count >= len(these_styles) :
              break

      can.Modified()
      can.Update()
      return







  ##
  ## Set colors. A default color list is provided, though you can provide your own list.
  ## Do this *after all of the histograms* have been added to the canvas.
  ## If you give this function a RatioCanvas, it will make histograms and their corresponding 
  ## ratio histograms the same color.
  ##
  def SetColors(can,these_colors=[], lineColor=True, markerColor=True, fillColor=False) :
      if not these_colors :
          from ROOT import kBlack,kRed,kBlue,kAzure,kGreen,kMagenta,kCyan,kOrange,kGray,kYellow
          these_colors = [kBlack+0,kRed+1,kAzure-2,kGreen+1,kMagenta+1,kCyan+1,kOrange+1
                          ,kBlack+2,kRed+3,kBlue+3,kGreen+3,kMagenta+3,kCyan+3,kOrange+3
                          ,kGray,kRed-7,kBlue-7,kGreen-7,kMagenta-7,kCyan-7,kOrange-7
                          ,kYellow+2,kRed-5,kBlue-5,kGreen-5,kMagenta-5,kCyan-5,kOrange-5
                          ,21,22,23,24,25,26,27,28,29,30
                          ,21,22,23,24,25,26,27,28,29,30
                          ,21,22,23,24,25,26,27,28,29,30
                          ]
          
      the_primitives = can.GetListOfPrimitives()
      if can.GetPrimitive('pad_top') :
          the_primitives = can.GetPrimitive('pad_top').GetListOfPrimitives()

      color_count = 0
      for i in the_primitives :
          if any([ignore in i.GetName() for ignore in ("ShadedProfile", "__xaxis")]):  continue
          if hasattr(i,'SetLineColor') and hasattr(i,'SetMarkerColor') :
              if lineColor: i.SetLineColor(these_colors[color_count])
              if markerColor: i.SetMarkerColor(these_colors[color_count])
              if fillColor: i.SetFillColor(these_colors[color_count])
              #
              # Check if there is a bottom pad, with ratios...
              #
              if can.GetPrimitive('pad_bot') :
                  original_name = i.GetName().replace('pad_top_','')
                  j = can.GetPrimitive('pad_bot').GetPrimitive('pad_bot_%s_ratio'%(original_name))
                  if j :
                      if lineColor: j.SetLineColor(these_colors[color_count])
                      if markerColor: j.SetMarkerColor(these_colors[color_count])
                      if fillColor: j.SetFillColor(these_colors[color_count])
                      can.GetPrimitive('pad_bot').Modified()
                      can.GetPrimitive('pad_bot').Update()
              color_count += 1
          if color_count >= len(these_colors) :
              break

      can.Modified()
      can.Update()
      return




  ##
  ## Draw luminosity on your plot. Give it the lumi and sqrts.
  ## The x and y coordinates are the fractional distances, with the origin at the bottom left.
  ##
  def GetLuminosityText(lumi=3.2) :
      #return '#lower[-0.2]{#scale[0.60]{#int}}Ldt = %1.1f fb^{-1}'%(lumi)
      return '%1.1f fb^{-1}'%(lumi)

  def GetSqrtsText(sqrts=13) :
      return '#sqrt{s} = %d TeV'%(sqrts)

  def GetAtlasInternalText(status='Internal') :
      return '#font[72]{ATLAS} #font[42]{%s}'%(status)
      
  ##
  ## Draw some additional text on your plot, in the form of a TLegend (easier to manage)
  ## The x and y coordinates are the fractional distances, with the origin at the bottom left.
  ## Specify multi-lines by specifing a list ['line1','line2','line3'] instead of a string 'single line'.
  ##
  def DrawText(can,text='text',x1=.2,y1=.84,x2=.5,y2=.9,angle=0,align='',textsize=12,totalentries=0) :
      can.cd()
      if can.GetPrimitive('pad_top') :
          can.GetPrimitive('pad_top').cd()
      from ROOT import TLegend
      leg = TLegend(x1,y1,x2,y2)
      leg.SetName('text')
      tobject_collector.append(leg)
      leg.SetTextSize(textsize)
      leg.SetTextFont(43)
      leg.SetBorderSize(0)
      leg.SetFillStyle(0)
      if type(text) == type('') :
          text = [text]
      total = 0
      for i in text :
          leg.AddEntry(0,i,'')
          total += 1
      #for i in range(100) :
      #    if totalentries == 0 : break
      #    if total >= totalentries : break
      #    leg.AddEntry(None,'','')
      #    total += 1
      leg.Draw()
      can.Modified()
      can.Update()
      return

  ##
  ## The MakeLegend function looks for any TH1 or TGraph you added to your canvas, and puts them
  ## in a legend in the order that you added them to a canvas.
  ## The entry label is taken from the title of the TH1 or TGraph. *Be sure to set the title
  ## of your TH1 or TGraph *before* you add it to the canvas.*
  ## The x and y coordinates are the fractional distances, with the origin at the bottom left.
  ##
  def MakeLegend( can,x1=.8,y1=.8,x2=.9,y2=.9,textsize=18,ncolumns=1
                , totalentries=0,option='f', names=None, squarebox=True
                , doFixLength=True, title='', maxlength=22) :
      from ROOT import TLegend,TH1,gStyle,TGraph,THStack
      if can.GetPrimitive('pad_top') :
          MakeLegend( can.GetPrimitive('pad_top')
                    , x1=x1,y1=y1,x2=x2,y2=y2,textsize=textsize
                    , ncolumns=ncolumns,totalentries=totalentries
                    , option=option, names=names, squarebox=squarebox
                    , doFixLength=doFixLength, title=title
                    , maxlength=maxlength )
          return
      is_th1 = list(issubclass(type(i),TH1) for i in can.GetListOfPrimitives())
      is_tgr = list(issubclass(type(i),TGraph) for i in can.GetListOfPrimitives())
      is_ths = list(issubclass(type(i),THStack) for i in can.GetListOfPrimitives())
      if True in is_ths : return # currently skip the legend for THStacks!
      if not (True in is_th1+is_tgr+is_ths) :
          print 'Error: trying to make legend from canvas with 0 plots. Will do nothing.'
          return
      #
      # if a previous version exists from this function, delete it
      #
      if can.GetPrimitive('legend' + ("_" + title if title else "")) :
          can.GetPrimitive('legend' + ("_" + title if title else "")).Delete()
      leg = TLegend(x1,y1,x2,y2,title)
      leg.SetName('legend' + ("_" + title if title else ""))
      tobject_collector.append(leg)
      leg.SetTextFont(43)
      leg.SetTextSize(textsize)
      leg.SetTextFont(43)
      leg.SetBorderSize(0)
      leg.SetFillStyle(0)
      if ncolumns > 1:
          leg.SetNColumns(ncolumns)
      #leg.SetTextAlign(12)

      #
      # Add by TH1 GetTitle()
      #
      the_primitives = can.GetListOfPrimitives()
      if can.GetPrimitive('pad_top') :
          the_primitives = can.GetPrimitive('pad_top').GetListOfPrimitives()

      if isinstance(names, basestring): names = names.split(',')
      isOptionsStr = isinstance(option,basestring)
      # TODO: we may consider a better algorithm to handle multiple splitlines
      lNames = 0
      if names is not None:
          if doFixLength: names = FixLength(names, maxlength)
          lNames = len(names)
      total = idx = 0
      for i in the_primitives:
          if lNames and total == lNames: break
          drawopt = i.GetDrawOption()
          if any([ignore in i.GetName() for ignore in ("ShadedProfile", "__xaxis")]):  continue
          if issubclass(type(i),TH1) or issubclass(type(i),TGraph) :
              if i.GetName() not in ('TFrame','text'):
                  if names is not None: 
                      if names[idx] is None: 
                          idx += 1
                          continue
                      if not names[idx]: 
                          leg.AddEntry(None, '', '') # plef
                      else:
                          leg.AddEntry(i, names[idx],option[idx] if not isOptionsStr else option) # plef
                  idx += 1
              else:
                  leg.AddEntry(i,i.GetName().replace(can.GetName()+'_',''),option[idx] if not isOptionsStr else option ) # plef
                  idx += 1
              total += 1
          elif issubclass(type(i),THStack) :
              for stackedHists in i.GetHists() :
                  leg.AddEntry(stackedHists,stackedHists.GetName().replace(can.GetName()+'_',''),option[idx] if not isOptionsStr else option) # plef
                  total += 1


      #
      # Add empty entries to ensure a standard layout
      #            
      for i in range(100) :
          if totalentries == 0 : break
          if total >= totalentries : break
          leg.AddEntry(None,'','')
          total += 1

      # recipe for making roughly square boxes
      if squarebox:
          h = leg.GetY2()-leg.GetY1()
          w = leg.GetX2()-leg.GetX1()
          if leg.GetNRows():
              leg.SetMargin(leg.GetNColumns()*h/float(leg.GetNRows()*w))
      can.cd()
      if can.GetPrimitive('pad_top') :
          can.GetPrimitive('pad_top').cd()
      leg.SetHeader("#font[63]{" + title + "}")
      leg.Draw()
      can.Modified()
      can.Update()
      return

  ##
  ## Format the axes of your canvas or RatioCanvas, including axis labels, sizes, offsets. 
  ## Call this *after* one or more histograms have been added to the canvas.
  ##
  def FormatCanvasAxes(can
                       ,XTitleSize   = 22
                       ,XTitleOffset = 0.98
                       ,XTitleFont   = 43
                       ,XLabelSize   = 22
                       ,XLabelOffset = 0.002
                       ,XLabelFont   = 43
                       
                       ,YTitleSize   = 22
                       ,YTitleOffset = 1.75
                       ,YTitleFont   = 43
                       ,YLabelSize   = 22
                       ,YLabelOffset = 0.006
                       ,YLabelFont   = 43
                       ,YNDiv = [10,5,0]
                       
                       ,ZTitleSize   = 22
                       ,ZTitleOffset = 0.85
                       ,ZTitleFont   = 43
                       ,ZLabelSize   = 22
                       ,ZLabelOffset = 0.002
                       ,ZLabelFont   = 43
                       ) :

      if can.GetPrimitive('pad_top') :
          FormatCanvasAxes(can.GetPrimitive('pad_top'),XLabelOffset=0.1
                           ,XTitleSize=XTitleSize,XTitleOffset=XTitleOffset,XTitleFont=XTitleFont
                           ,XLabelSize=XLabelSize,XLabelFont=XLabelFont
                           ,YTitleSize=YTitleSize,YTitleOffset=YTitleOffset,YTitleFont=YTitleFont
                           ,YLabelSize=YLabelSize,YLabelOffset=YLabelOffset,YLabelFont=YLabelFont
                           ,YNDiv=YNDiv
                           ,ZTitleSize=ZTitleSize,ZTitleOffset=ZTitleOffset,ZTitleFont=ZTitleFont
                           ,ZLabelSize=ZLabelSize,ZLabelOffset=ZLabelOffset,ZLabelFont=ZLabelFont
                           )
      if can.GetPrimitive('pad_bot') :
          FormatCanvasAxes(can.GetPrimitive('pad_bot'),YLabelOffset=0.009
                           ,XTitleSize=XTitleSize,XTitleOffset=XTitleOffset,XTitleFont=XTitleFont
                           ,XLabelSize=XLabelSize,XLabelOffset=XLabelOffset,XLabelFont=XLabelFont
                           ,YTitleSize=YTitleSize,YTitleOffset=YTitleOffset,YTitleFont=YTitleFont
                           ,YLabelSize=YLabelSize,YLabelFont=YLabelFont
                           ,YNDiv = [5,5,0]
                           ,ZTitleSize=ZTitleSize,ZTitleOffset=ZTitleOffset,ZTitleFont=ZTitleFont
                           ,ZLabelSize=ZLabelSize,ZLabelOffset=ZLabelOffset,ZLabelFont=ZLabelFont
                           )

      for i in can.GetListOfPrimitives() :
          if not hasattr(i,'GetXaxis') :
              continue
          i.GetXaxis().SetTitleSize  (XTitleSize  )
          i.GetXaxis().SetTitleOffset(XTitleOffset/float(can.GetHNDC()))
          i.GetXaxis().SetTitleFont  (XTitleFont  )
          i.GetXaxis().SetLabelSize  (XLabelSize  )
          i.GetXaxis().SetLabelOffset(XLabelOffset/float(can.GetHNDC()))
          i.GetXaxis().SetLabelFont  (XLabelFont  )

          i.GetXaxis().SetTickLength(0.02/float(can.GetHNDC()))
          
          i.GetYaxis().SetTitleSize  (YTitleSize  )
          i.GetYaxis().SetTitleOffset(YTitleOffset)
          i.GetYaxis().SetTitleFont  (YTitleFont  )
          i.GetYaxis().SetLabelSize  (YLabelSize  )
          i.GetYaxis().SetLabelOffset(YLabelOffset)
          i.GetYaxis().SetLabelFont  (YLabelFont  )
          i.GetYaxis().SetNdivisions (YNDiv[0],YNDiv[1],YNDiv[2])

          if not hasattr(i,'GetZaxis') :
              continue
          i.GetZaxis().SetTitleSize  (ZTitleSize  )
          i.GetZaxis().SetTitleOffset(ZTitleOffset)
          i.GetZaxis().SetTitleFont  (ZTitleFont  )
          i.GetZaxis().SetLabelSize  (ZLabelSize  )
          i.GetZaxis().SetLabelOffset(ZLabelOffset)
          i.GetZaxis().SetLabelFont  (ZLabelFont  )

          break

      can.Modified()
      can.Update()
      return

  ##
  ## Setup general style.
  ##
  def SetupStyle() :
      from ROOT import gROOT,TStyle, kBird
      mystyle = TStyle("mystyle","mystyle")
      mystyle.SetStatColor(0)
      mystyle.SetTitleColor(0)
      mystyle.SetCanvasColor(0)
      mystyle.SetPadColor(0)
      mystyle.SetPadBorderMode(0)
      mystyle.SetCanvasBorderMode(0)
      mystyle.SetFrameBorderMode(0)
      #mystyle.SetOptStat(111111)
      mystyle.SetOptStat(0)
      #mystyle.SetStatH(0.3)
      #mystyle.SetStatW(0.3)
      mystyle.SetTitleColor(1)
      mystyle.SetTitleFillColor(0)
      mystyle.SetTitleBorderSize(0)
      mystyle.SetHistLineWidth(2)
      #mystyle.SetLineWidth(2) # no
      mystyle.SetFrameFillColor(0)
      mystyle.SetOptTitle(0)
      mystyle.SetPaintTextFormat('4.1f ')
      mystyle.SetEndErrorSize(3)
      mystyle.SetPalette(kBird)
      #mystyle.SetPalette(1)

      mystyle.SetPadTickX(1)
      mystyle.SetPadTickY(1)

      mystyle.SetPadTopMargin(0.05)
      mystyle.SetPadRightMargin(0.05)
      mystyle.SetPadBottomMargin(0.11)
      mystyle.SetPadLeftMargin(0.16)

      mystyle.SetMarkerStyle(20)
      mystyle.SetMarkerSize(1.2)

      #
      # NOTE that in ROOT rendering the font size is slightly smaller than in pdf viewers!
      # The effect is about 2 points (i.e. 18 vs 20 font)
      #
      # all axes
      mystyle.SetTitleSize  (22   ,'xyz')
      mystyle.SetTitleFont  (43   ,'xyz')
      mystyle.SetLabelSize  (22   ,'xyz')
      mystyle.SetLabelFont  (43   ,'xyz')

      # x axis
      mystyle.SetTitleXOffset(1.0)
      mystyle.SetLabelOffset(0.002,'x')

      # y axis
      mystyle.SetTitleOffset(1.75 ,'y')
      mystyle.SetLabelOffset(0.002,'y')

      # y axis
      mystyle.SetTitleOffset(1.75 ,'z')
      mystyle.SetLabelOffset(0.002,'z')

      # printing plots
      
      gROOT.SetStyle("mystyle")

      return mystyle

  ##
  ## Call this if you want a TCanvas especially prepared for ratio plots. It creates two
  ## sub-pads, "pad_top" and "pad_bot", and the rest of the functions in this file will
  ## specifically look for this type of configuration and act accordingly. See also the special
  ## functions GetTopPad(can) and GetBotPad(can) if you want to manipulate the sub-pads yourself.
  ## To add histograms to the top pad, do AddHistogram(can,hist) or AddHistogramTop(can,hist)
  ## To add histograms to the bot pad, do AddHistogramBot(can,hist).
  ## To add a histogram to the top pad, and its ratio with a reference histogram to the bottom pad,
  ## do AddRatio(can,hist,ref_hist,'B') (the B is for binomial errors).
  ##
  def RatioCanvas(canvas_name,canvas_title,canw=500,canh=600,ratio_size_as_fraction=0.35,drawopt='pE1') :
      from ROOT import TCanvas,TPad, TColor
      c = TCanvas(canvas_name,canvas_title,canw,canh)
      c.SetFillStyle(4050)
      c.cd()
      top = TPad("pad_top", "This is the top pad",0.0,ratio_size_as_fraction,1.0,1.0)
      top.SetBottomMargin(0.02/float(top.GetHNDC()))
      top.SetTopMargin   (0.04/float(top.GetHNDC()))
      top.SetRightMargin (0.05 )
      top.SetLeftMargin  (0.16 )
      #top.SetFillColor(TColor.GetColorTransparent(0,0.))
      top.SetFillColor(0)
      #top.SetFillStyle(4050)
      top.Draw(drawopt)
      tobject_collector.append(top)

      c.cd()
      bot = TPad("pad_bot", "This is the bottom pad",0.0,0.0,1.0,ratio_size_as_fraction)
      bot.SetBottomMargin(0.10/float(bot.GetHNDC()))
      bot.SetTopMargin   (0.02/float(bot.GetHNDC()))
      bot.SetRightMargin (0.05)
      bot.SetLeftMargin  (0.16)
      #bot.SetFillColor(TColor.GetColorTransparent(0,0.))
      bot.SetFillColor(0)
      bot.Draw(drawopt)
      tobject_collector.append(bot)
      
      return c

  ##
  ## Set the left margin - useful for the RatioCanvas in particular (since it will handle sub-pads)
  ##
  def SetLeftMargin(can,margin) :
      if can.GetPrimitive('pad_top') :
          SetLeftMargin(can.GetPrimitive('pad_top'),margin)
      if can.GetPrimitive('pad_bot') :
          SetLeftMargin(can.GetPrimitive('pad_bot'),margin)
      can.SetLeftMargin(margin)
      can.Modified()
      can.Update()
      return

  ##
  ## Set the right margin - useful for the RatioCanvas in particular (since it will handle sub-pads)
  ##
  def SetRightMargin(can,margin) :
      if can.GetPrimitive('pad_top') :
          SetRightMargin(can.GetPrimitive('pad_top'),margin)
      if can.GetPrimitive('pad_bot') :
          SetRightMargin(can.GetPrimitive('pad_bot'),margin)
      can.SetRightMargin(margin)
      can.Modified()
      can.Update()
      return

  ##
  ## Return a pointer to the top pad of a RatioCanvas
  ##
  def GetTopPad(can) :
      return can.GetPrimitive('pad_top')

  ##
  ## Return a pointer to the bottom pad of a RatioCanvas
  ##
  def GetBotPad(can) :
      return can.GetPrimitive('pad_bot')

  ##
  ## Add a TH1 or TGraph to the top pad of a RatioCanvas
  ##
  def AddHistogramTop(can,hist,drawopt='pE1') :
      AddHistogram(can.GetPrimitive('pad_top'),hist,drawopt)
      return

  ##
  ## Add a TH1 or TGraph to the bottom pad of a RatioCanvas
  ##
  def AddHistogramBot(can,hist,drawopt='pE1') :
      AddHistogram(can.GetPrimitive('pad_bot'),hist,drawopt)
      return

  ##
  ## Adds a histogram to the top pad of a RatioCanvas, and a ratio (dividing by some reference
  ## histogram ref_hist) to the bottom pad of the RatioCanvas. Specify the division type
  ## by the "divide" option ("B" for binomial, "" for uncorrelated histograms)
  ##
  def AddRatio(can,hist,ref_hist,divide='',drawopt='pE1', ratiodrawopt='pE1', dist = None
              , drawSpecialCases=True, markerSize=1, markerStyle = 20) :
      yref = 1. if divide != 'poll' else 0.
      from ROOT import TH1, kRed, TGraph, TGraphErrors, TGraphAsymmErrors, kGray, kDashed
      TH1.SetDefaultSumw2(True)
      ratioplot = hist.Clone()
      ratioplot.SetName(hist.GetName()+'_ratio')
      specialCase = [] 
      removeIdxs = []
      if divide.startswith("poll"):
          ratioplot.SetMarkerSize( .5 )
          ratioplot.Add(hist,ref_hist,1.,-1.)
          notNorm = divide.endswith("_notnorm")
          divN = divide.endswith("_divn")
          for xi in range( ratioplot.GetNbinsX() + 2 ):
              xv = ratioplot.GetBinContent(xi)
              yv = ref_hist.GetBinError( xi )
              # division operation
              Nx = hist.GetBinContent( xi )
              Ny = ref_hist.GetBinContent( xi )
              if Ny:
                  if notNorm:
                      mu = xv
                  elif divN:
                      mu = xv / ref_hist.GetBinContent( xi )
                  else:
                      mu = xv / yv
                  ratioplot.SetBinContent( xi, mu )
                  #ratioplot.SetBinError( xi, ( (Nx**2+Ny**2)/Ny**2 + Nx**2/(2*(Ny**(4.5))) ) ** 0.5)
                  ratioplot.SetBinError( xi, 0.)
              elif Nx:
                  ratioplot.SetBinContent( xi, 0. )
                  ratioplot.SetBinError( xi, 0. )
                  specialCase.append( ref_hist.GetBinCenter(xi) )
              #else:
              #    ratioplot.SetBinContent( xi, mu )
      else:
          ratioplot.Divide(hist,ref_hist,1.,1.,divide)
          for x in range(1, ref_hist.GetNbinsX() + 1):
              hContent = hist.GetBinContent( x )
              refContent = ref_hist.GetBinContent( x )
              if dist and not dist.GetBinContent( x ):
                  removeIdxs.append( x )
              elif not refContent and hContent:
                  ratioplot.SetBinContent(x, yref) # Sign that ref did not miss but hist did
                  specialCase.append(ref_hist.GetBinCenter(x))
              elif not refContent and not hContent:
                  ratioplot.SetBinContent(x, 1); ratioplot.SetBinError(x, 0) # Both ok
      if removeIdxs:
          import numpy as np
          x = np.array( [ratioplot.GetBinCenter(idx) for idx in range(1,ratioplot.GetNbinsX()+1) if not (idx) in removeIdxs ] )
          y = np.array( [ratioplot.GetBinContent(idx) for idx in range(1,ratioplot.GetNbinsX()+1) if not (idx) in removeIdxs ] )
          yel = np.array( [ratioplot.GetBinErrorLow(idx) for idx in range(1,ratioplot.GetNbinsX()+1) if not (idx) in removeIdxs ] )
          yeh = np.array( [ratioplot.GetBinErrorUp(idx) for idx in range(1,ratioplot.GetNbinsX()+1) if not (idx) in removeIdxs ] )
          hw = np.array( [ratioplot.GetBinWidth(idx) for idx in range(1,ratioplot.GetNbinsX()+1) if not (idx) in removeIdxs ] ) * .5
          if len(x):
              graph = TGraphAsymmErrors( len(x), x, y, hw, hw, yel, yeh )
              graph.SetLineWidth(2)
              name = ratioplot.GetName()
              ratioplot = graph
              graph.SetName( name )
      ratioplot.SetFillColor(kGray)
      #temp.SetFillColorAlpha(kGray, 0.15);
      ratioplot.SetLineColor(kGray)
      ratioplot.SetFillStyle(0)
      ratioplot.SetMarkerColor(1)
      ratioplot.SetMarkerStyle(24)
      #ratioplot.SetMarkerStyle(7)
      #ratioplot.SetMarkerSize(1.2)
      AddHistogram(can.GetPrimitive('pad_top'),hist,drawopt, markerSize=markerSize, markerStyle=markerStyle )
      #AddHistogram(can.GetPrimitive('pad_bot'),ratioplot,drawopt,False, None, None)
      AddHistogram(can.GetPrimitive('pad_bot'),ratioplot,ratiodrawopt,False, None, None)
      #AddHistogram(can.GetPrimitive('pad_bot'),ratioplot,'hist p',False, None, None)
      if specialCase and drawSpecialCases:
          import numpy as np
          a, b = np.array(specialCase, dtype='float'), np.array([yref]*len(specialCase))
          specialCase = TGraph( a.shape[0], a, b )
          specialCase.SetName( ratioplot.GetName() + '_specialCases')
          #x = np.frombuffer( specialCase.GetX(), dtype=np.float64 ,count=specialCase.GetN() )
          #y = np.frombuffer( specialCase.GetY(), dtype=np.float64 ,count=specialCase.GetN() )
          specialCase.SetFillColor(0)
          specialCase.SetFillStyle(0)
          specialCase.SetMarkerSize( ratioplot.GetMarkerSize() )
          specialCase.SetMarkerColor(2)
          specialCase.SetMarkerStyle(20)
          AddHistogram(can.GetPrimitive('pad_bot'),specialCase,'p', markerSize=ratioplot.GetMarkerSize(), markerStyle=20)
          tobject_collector.append(specialCase)
      if removeIdxs:
          (xmin,xmax) = GetXaxisRanges(GetTopPad(can),check_all=True)
          SetXaxisRanges(GetBotPad(can),xmin,xmax)
      return

  def GetHistogramsMinMax(hists, check_all=False,ignorezeros=False,ignoreErrors=False):
      from ROOT import TGraph,TH1,TH2,THStack,TMath
      import itertools
      ymin = 999999999
      ymax = -999999999
      #from ROOT import TH1,TGraph,THStack,TColor, kGray, kBlue, TGaxis, TText
      #listOfPlottedObjects = [o for o in can.GetListOfPrimitives() if isinstance(o,(TH1, THStack))]
      #listOfPlottedObjects += [o.GetHistogram() for o in can.GetListOfPrimitives() if isinstance(o,TGraph)]
      #if listOfPlottedObjects:
      #    #maxValue = max([o.GetBinContent(o.GetMaximumBin()) for o in listOfPlottedObjects])
      #    #minValue = min([o.GetBinContent(o.GetMinimumBin()) for o in listOfPlottedObjects])
      #    maxValue = max([o.GetBinContent(o.GetMaximumBin()) + o.GetBinError(o.GetMaximumBin()) for o in listOfPlottedObjects])
      #    minValue = min([o.GetBinContent(o.GetMinimumBin()) - o.GetBinError(o.GetMinimumBin()) for o in listOfPlottedObjects])
      if hists:
          for i in hists:
              if isinstance(i, TH2):
                  x = i.GetXaxis()
                  y = i.GetYaxis()
                  nx = i.GetNbinsY(); ny = i.GetNbinsY()
                  # This is just a workaround for candles/violins
                  for rxc, ryc in itertools.product( range(1,nx+1), range(1,ny+1)):
                      z = i.GetBinContent(rxc,ryc)
                      if ignorezeros and z == 0 :
                          continue
                      ymin = min(ymin,y.GetBinCenter(ryc))
                      ymax = max(ymax,y.GetBinCenter(ryc))
              if issubclass(type(i),TGraph) :
                  ymin = min(ymin,TMath.MinElement(i.GetN(),i.GetY()))
                  ymax = max(ymax,TMath.MaxElement(i.GetN(),i.GetY()))
                  if not check_all :
                      return ymin,ymax
              elif issubclass(type(i),TH1) :
                  ysum = 0 
                  for bin in range(i.GetNbinsX()) :
                      ysum = ysum+i.GetBinContent(bin+1)
                  if ysum == 0: ignorezeros = 0
                  for bin in range(i.GetNbinsX()) :
                      y = i.GetBinContent(bin+1)
                      if ignoreErrors :
                          ye = 0
                      else :
                          ye = i.GetBinError(bin+1)
                      if ignorezeros and y == 0 :
                          continue
                      ymin = min(ymin,y-ye)
                      ymax = max(ymax,y+ye)
                  if not check_all :
                      return ymin,ymax
                  if not check_all :
                      return ymin,ymax

              elif issubclass(type(i),THStack) :
                  ymin = i.GetMinimum()
                  ymax = i.GetMaximum()
      return ymin, ymax

  def AddHorizontalLine(can, pos = 1., color = None, style = None):
      from ROOT import TH1, THStack, TGraph, TLine, kRed, kDashed
      if color is None: color = kRed
      if style is None: style = kDashed
      if can.GetPrimitive('pad_bot') :
          AddHorizontalLine(GetBotPad(can), pos, color, style)
          return
      can.cd()
      listOfPlottedObjects = [o for o in can.GetListOfPrimitives() if isinstance(o,(TH1, THStack))]
      if not listOfPlottedObjects:
          listOfPlottedObjects += [o.GetHistogram() for o in can.GetListOfPrimitives() if isinstance(o,TGraph)]
      if not listOfPlottedObjects:
          return
      o = listOfPlottedObjects[0]
      l = TLine( o.GetXaxis().GetXmin(), pos, o.GetXaxis().GetXmax(), pos )
      l.SetLineColor( color )
      l.SetLineStyle( style )
      l.Draw()
      tobject_collector.append(l)

  def AddRightAxisObj(can, hists, drawopt="pE1", equate=None
                     , drawAxis=True, axisColor=None, ignorezeros=False
                     , ignoreErrors=False, label = None, dist = .035):
      if not isinstance(hists,(list,tuple)): hists = [hists]
      hists = [h.Clone(h.GetName() + "_local") for h in hists]
      if not equate:
          #origMax = max([h.GetBinContent(h.GetMaximumBin()) for h in hists])
          #origMin = min([h.GetBinContent(h.GetMinimumBin()) for h in hists])
          origMax = max([h.GetMaximum() for h in hists])
          origMin = min([h.GetMinimum() for h in hists])
      else:
          from ROOT import TH1
          if all([isinstance(e,TH1) for e in equate]):
              origMax = max([h.GetMaximum() for h in equate])
              origMin = min([h.GetMinimum() for h in equate])
          else:
              origMax = max(equate)
              origMin = min(equate)
      if origMax > 0:
          from ROOT import TGaxis, TLatex
          minValue, maxValue = GetHistogramsMinMax( can.GetListOfPrimitives(), check_all=True
                                                  , ignorezeros=ignorezeros, ignoreErrors=ignoreErrors)
          k = (maxValue - minValue) / (origMax - origMin)
          can.cd()
          for i, h in enumerate(hists):
              #for x in range(1,h.GetNbinsX()+1):
              #    h.AddBinContent(x, ( minValue/k - origMin  ) )
              h.Scale(k)
              # Get new min value
              #AddHistogram(can, hist, markerSize=None, markerStyle=None )
              #AddHistogram(can, hist, drawopt=drawopt, markerSize=None, markerStyle=None )
              h.Draw(drawopt)
              tobject_collector.append(h)
          h = hists[0]
          oldDigits = TGaxis.GetMaxDigits()
          TGaxis.SetMaxDigits(3)
          #if not drawAxis: return
          axis = TGaxis( can.GetUxmax(), can.GetUymin()
                       , can.GetUxmax(), can.GetUymax()
                       , origMin, origMax
                       , 510, "+L")
          #axis.SetLineColor( h.GetMarkerColor() if axisColor is None else axisColor )
          #axis.SetLabelColor( h.GetMarkerColor() if axisColor is None else axisColor )
          #axis.SetTitle("count")
          axis.Draw()
          tobject_collector.append(axis)
          can.SetTicks( can.GetTickx(), 0 )
          can.Modified()
          can.Update()
          if label:
              text = TLatex(can.GetUxmax()+dist*(can.GetUxmax()-can.GetUxmin()),maxValue, label);
              text.SetTextAlign(33)
              text.SetTextAngle(90)
              text.SetTextColor(axis.GetLabelColor() )
              text.Draw()
              tobject_collector.append(text)
          TGaxis.SetMaxDigits(oldDigits)

  def AddShadedProfile(can,hist):
      if can.GetPrimitive('pad_top') :
          GetTopPad(can).SetRightMargin (0.08)
          GetBotPad(can).SetRightMargin (0.08)
          AddShadedProfile(can.GetPrimitive('pad_top'), hist)
          GetBotPad(can).Modified()
          GetBotPad(can).Update()
          return
      #    #print [o.GetMaximum() for o in listOfPlottedObjects]
      #maxValue = can.GetUymax()
      #minValue = can.GetUymin()
      #print maxValue, minValue
      from ROOT import kGray,kAzure
      temp = hist.Clone()
      temp.SetName("ShadedProfile")
      temp.SetFillStyle(1001)
      lightgray = 1001
      #color = TColor(lightgray, 0.956, 0.956, 0.956)
      temp.SetFillColorAlpha(kGray, 0.20);
      temp.SetLineColor( kGray )
      temp.SetStats(0)
      AddRightAxisObj(can, temp, "hist same", axisColor=kGray)

  def AddBinLines(can,hist,useCanvasHistsMax=True,useHistMax=False, horizotalLine=1.,lineStyle=2, maxvalue=None):
      from ROOT import TH1,TGraph,THStack,TColor, kGray, kBlue, TLine, kRed
      if can.GetPrimitive('pad_top'):
          AddBinLines( can.GetPrimitive('pad_top'), hist
                     , useCanvasHistsMax=useCanvasHistsMax
                     , useHistMax=useHistMax, horizotalLine=horizotalLine
                     , lineStyle=lineStyle )
          if can.GetPrimitive('pad_bot'):
              # TODO Move this to another function
              pad = GetBotPad(can)
              AddBinLines(pad, hist,useCanvasHistsMax=False,useHistMax=False,horizotalLine=horizotalLine, lineStyle=lineStyle)
              if horizotalLine is not None and pad.GetUymax() > horizotalLine > pad.GetUymin():
                  pad.cd()
                  maxValue = pad.GetUxmax()
                  minValue = pad.GetUxmin()
                  l = TLine( minValue, horizotalLine, maxValue, horizotalLine )
                  l.SetLineColor(kRed)
                  l.SetLineStyle(2)
                  l.Draw()
                  tobject_collector.append(l)
          return
      can.cd()
      #listOfPlottedObjects = [o for o in can.GetListOfPrimitives() if isinstance(o,(TH1, THStack))]
      #listOfPlottedObjects += [o.GetHistogram() for o in can.GetListOfPrimitives() if isinstance(o,TGraph)]
      #if listOfPlottedObjects:
          #maxValue = max([o.GetBinContent(o.GetMaximumBin()) + o.GetBinError(o.GetMaximumBin()) for o in listOfPlottedObjects])
          #minValue = min([o.GetBinContent(o.GetMinimumBin()) - o.GetBinError(o.GetMinimumBin()) for o in listOfPlottedObjects])
      
      if useCanvasHistsMax:
          from TagAndProbeFrame.TAxisFunctions import GetYaxisRanges
          _, maxValue = GetYaxisRanges(can,check_all=True,ignorezeros=False,ignoreErrors=False)
      elif useHistMax:
          maxValue = hist.GetBinContent(hist.GetMaximumBin()) 
      elif maxvalue:
          maxValue=maxvalue
      else:
          maxValue = can.GetUymax()
      minValue = can.GetUymin()
      for x in range(2, hist.GetXaxis().GetNbins()+1):
          xv = hist.GetBinLowEdge(x)
          line = TLine(xv, minValue, xv, maxValue)
          line.SetLineColor( tGray )
          line.SetLineStyle(lineStyle)
          line.Draw()
          tobject_collector.append(line)
          
  def GetNDC(x):
      from  ROOT import gPad
      gPad.Update()
      return (x - gPad.GetX1())/(gPad.GetX2()-gPad.GetX1())

  #def DistributeXHists(hists):
      # Should be done via BinWidth and OffSet, but it doesn't work on marker
      # only histograms

  def FixLength(names, nchar = 22):
      """
      Return root latex characters trunc'd at 'nchar' char
      """
      from copy import copy
      names = copy(names)
      pop = False
      if isinstance(names, basestring): 
          names = [names]
          pop = True
      if isinstance(names, (list, tuple)):
          for idx, name in enumerate(names):
              if name is None: continue
              lName = len(name)
              breakVec = [0]; cBreakVecIdx=0
              from RingerCore import keyboard
              while True:
                  prevIdx = breakVec[cBreakVecIdx]
                  maxIdx = nchar + prevIdx
                  if maxIdx >= lName: break
                  if 'rightarrow' in name: break # TODO handle latex symbols
                  bfield = prevIdx + name[prevIdx:maxIdx].rfind('_') + 1
                  if bfield == prevIdx: 
                      bfield = maxIdx
                      bfield = prevIdx + name[prevIdx:maxIdx].rfind(' ') + 1
                      if bfield == prevIdx: bfield = maxIdx
                  breakVec.append( bfield )
                  cBreakVecIdx += 1
              for cBreakVecIdx, bfield in enumerate(reversed(breakVec[1:])):
                  prevIdx = breakVec[-(cBreakVecIdx+2)]
                  name = names[idx]
                  #+np.sum(breakVec[:cBreakVecIdx]
                  #names[idx] = '#splitline{' + name[:bfield+11*cBreakVecIdx] + '}{' + name[bfield+11*cBreakVecIdx:] + '}'
                  names[idx] = name[:prevIdx] + '#splitline{' + name[prevIdx:bfield] + '}{' + name[bfield:] + '}'
      if pop: names = names[0]
      return names

  def ReducePowerOf10Str(s, doPrint = False):
      import re
      if not isinstance(s,basestring): return s
      thousand = re.compile(r"""
          (?<!\S)       
          # Ensures that we are at the begin of a word
          ###############################################
          (?=(\d+|\d*,?(\d{3},)*\d+)k*|(k*\.^)) 
          # Guarantees that what come next is a sequence of digits or commas ending
          # with possible 'k's added from previous substitutions
          ###############################################
          (?P<BEFORE>(\d+|\d*,?(\d{3},)*\d+)) 
          # What may come before the matching pattern that we want to substitute
          # (000). It is basically the string the we have guaranteed before, except
          # for the 'k*' that we will use later on
          ###############################################
          (,?0{3})(?!(\d|,)+) 
          # This is the match that we will change by k. It must not be followed by a
          # digit or a comma to ensure that we are substituting the last three zeros
          # available. We also consume a left comma if available
          ###############################################
          (?:\.?(?!\d+))
          # And finally, we also consume an ending dot if it hasn't following
          # digits. It will also consume end of sentence punctuation
          ###############################################
          (?P<AFTER>(k*)|(k*\.^))
          # To ensure that the string will keep any already available 'k's
          """
          , re.X)
      s2 = thousand.sub(r'\g<BEFORE>k\g<AFTER>',s)
      while s2 != s:
          s = s2
          s2 = thousand.sub(r'\g<BEFORE>k\g<AFTER>',s)
      s = re.sub(r'k\.?k|kk','M',s2)
      s = re.sub(r'Mk|kM|kkk','B',s)
      s = re.sub(r'MM|kB|Bk|kkkk','T',s)
      s = re.sub(r'kT|Tk|kkkkk','P',s)
      return s
      

  def MergeLowCount(hist, minCounts = [30]):
      if not isinstance( minCounts, (tuple,list)): minCounts = [minCounts]
      nBins=hist.GetNbinsX()
      import numpy as np
      content = [hist.GetBinContent(idx) for idx in range(1,nBins+1)]
      edges = [hist.GetBinLowEdge(idx) for idx in range(1,nBins+2)]
      binIdxs = range(len(content)-1)
      prevSum = sum(content)
      for minCount in minCounts:
          popIdx = []
          flagSum = False
          for idx in binIdxs:
              if content[idx] < minCount and content[idx+1] < minCount:
                  content[idx+1] += content[idx]
                  popIdx.append(idx)
          for idx in reversed(popIdx): 
              content.pop(idx) 
              edges.pop(idx+1)
          binIdxs = range(1,len(content))
          popIdx = []
          flagSum = False
          for idx in reversed(binIdxs):
              if content[idx-1] < minCount and content[idx] < minCount:
                  content[idx-1] += content[idx]
                  popIdx.append(idx)
          lB = len(binIdxs)
          for idx in popIdx: 
              content.pop(idx) 
              edges.pop(idx-1)
          binIdxs = range(len(content)-1)
      edges = np.array(edges)
      #print 'new content(edges):', [(c,e) for c, e in zip(content, edges)]
      #print 'total content:', sum(content)
      #print 'new len:', len(content)
      if prevSum != sum(content):
          print "ERROR: Sum algorithm failed"
      newHist = hist.Rebin(len(edges)-1, hist.GetName() + "_rebin", edges)
      return newHist, edges


  def AddOutOfBoundArrows(can, useFill=True, useMarkerColor=True, colors=None, lengthDiv=40.,arrowLenghtDiv=8., textLengthDiv=60., textPerc=2, addNumbers=True):
      import numpy as np
      from ROOT import TH1, THStack, TGraph, TArrow, TLatex
      maxY = can.GetUymax()
      minY = can.GetUymin()
      listOfPlottedObjects = [o for o in can.GetListOfPrimitives() if isinstance(o,(TH1, THStack, TGraph))]
      can.cd()
      def drawAr(i,ar, cColor=None):
         ar.SetAngle(40)
         ar.SetLineWidth(1)
         ar.SetLineColor(cColor if cColor is not None else i.GetLineColor())
         if useFill:
             ar.SetFillStyle(cColor if cColor is not None else i.GetFillStyle())
             ar.SetFillColor(cColor if cColor is not None else i.GetFillColor())
         if useMarkerColor:
             ar.SetFillColor(cColor if cColor is not None else i.GetMarkerColor())
         ar.Draw()
         tobject_collector.append(ar)
      for v, i in enumerate(listOfPlottedObjects) :
          try:
              cColor = colors[v]
          except:
              cColor = None
          if any([ignore in i.GetName() for ignore in ("ShadedProfile", )]):  continue
          if isinstance(i, TGraph):
              x = np.frombuffer( i.GetX(), dtype=np.float64 ,count=i.GetN() )
              y = np.frombuffer( i.GetY(), dtype=np.float64 ,count=i.GetN() )
          else:
              x = np.array( [i.GetBinCenter(idx) for idx in range(1,i.GetNbinsX()+1)] )
              if addNumbers: xedges = np.array( [i.GetBinLowEdge(idx) for idx in range(0,i.GetNbinsX()+2)] )
              y = np.array( [i.GetBinContent(idx) for idx in range(1,i.GetNbinsX()+1)] )
          higherThanUpperBound = np.nonzero( y > maxY )[0]
          lowerThanUpperBound = np.nonzero( y < minY )[0]
          for k, idx in enumerate(higherThanUpperBound):
             ar = TArrow(x[idx],maxY-(maxY-minY)/lengthDiv,x[idx],maxY,(maxY-minY)/(lengthDiv*arrowLenghtDiv),"|>");
             drawAr(i,ar, cColor)
          for k, idx in enumerate(lowerThanUpperBound):
             ar = TArrow(x[idx],minY,x[idx],minY+(maxY-minY)/lengthDiv,(maxY-minY)/(lengthDiv*arrowLenghtDiv),"<|");
             drawAr(i,ar, cColor)
          if addNumbers:
              for k, idx in enumerate(higherThanUpperBound):
                 if k != 0 and higherThanUpperBound[k-1] == idx-1: continue
                 upperLimit=None
                 k2=k+1
                 while k2 < len(higherThanUpperBound):
                      if higherThanUpperBound[k2]==idx+(k2-k): upperLimit=higherThanUpperBound[k2]
                      else: break
                      k2 += 1
                 centerx = (xedges[idx+1] + xedges[upperLimit+2])/2. if upperLimit else x[idx]
                 text = TLatex(centerx, maxY-(maxY-minY)/(lengthDiv), '%d' % round(xedges[idx+1]) if not upperLimit else '%d-%d' % (round(xedges[idx+1]),round(xedges[upperLimit+1])) )
                 text.Draw()
                 text.SetTextFont(43)
                 text.SetTextSizePixels(textPerc)
                 text.SetTextAlign(22)
                 text.SetTextAngle(90)
                 tobject_collector.append(text)
              for k, idx in enumerate(lowerThanUpperBound):
                 if k != 0 and lowerThanUpperBound[k-1] == idx-1: continue
                 upperLimit=None
                 k2=k+1
                 while k2 < len(lowerThanUpperBound):
                      if lowerThanUpperBound[k2]==idx+(k2-k): upperLimit=lowerThanUpperBound[k2]
                      else: break
                      k2 += 1
                 centerx = (xedges[idx+1] + xedges[upperLimit+2])/2. if upperLimit else x[idx]
                 text = TLatex(centerx, minY+(maxY-minY)/(lengthDiv), '%d' % round(xedges[idx+1]) if not upperLimit else '%d-%d' % (round(xedges[idx+1]),round(xedges[upperLimit+1])))
                 text.Draw()
                 text.SetTextFont(43)
                 text.SetTextAlign(22)
                 text.SetTextAngle(90)
                 text.SetTextSizePixels(textPerc)
                 tobject_collector.append(text)


del __TP_PlotFunctions






def GetXAxisWorkAround( hist, nbins, xmin, xmax ):
  from ROOT import TH1F
  h=TH1F(hist.GetName()+'_resize', hist.GetTitle(), nbins,xmin,xmax)
  for bin in range(h.GetNbinsX()):
    x = h.GetBinCenter(bin+1)
    m_bin = hist.FindBin(x)
    y = hist.GetBinContent(m_bin)
    error = hist.GetBinError(m_bin)
    h.SetBinContent(bin+1,y)
    h.SetBinError(bin+1,error)
  return h


def Copy2DRegion(hist, xbins, xmin, xmax, ybins, ymin, ymax):
  from ROOT import TH2F
  h = TH2F(hist.GetName()+'_region',hist.GetTitle(),xbins,xmin,xmax,ybins,ymin,ymax)
  yhigh = hist.GetYaxis().FindBin(ymax) - 1
  ylow = hist.GetYaxis().FindBin(ymin) - 1
  yhigh = min(hist.GetNbinsY(),yhigh)

  xhigh = hist.GetXaxis().FindBin(xmax) - 1
  xlow = hist.GetXaxis().FindBin(xmin) - 1
  xhigh = min(hist.GetNbinsX(),xhigh)
  V=0
  x=0; y=0
  for bx in xrange(int(xlow),int(xhigh)+1) :
    x+=1
    for by in xrange(int(ylow),int(yhigh)+1) :
      y+=1
      value = hist.GetBinContent(bx+1,by+1)
      V+=value
      h.SetBinContent(x-1,y-1,value)
    y=0
  return h


def GetTransparent(color,factor=.5):
  return TColor.GetColorTransparent(color,factor)
 



__all__ = ['PileUpDiscFit', 'CalculateEfficiencyWithSlope']

import time,os,math,sys,pprint,glob
from array import array


def PileUpDiscFit(hist,effref, getGraph = False, getf1=False):
  import ROOT
  NBINSY = hist.GetNbinsY()
  NBINSX = hist.GetNbinsX()
  g = ROOT.TGraphErrors()
  counter = 0
  for k in xrange(NBINSY) :
    n_sig = hist.Integral(0,-1,k,k)
    if n_sig == 0 : continue
    cut = -4.0
    pileupVal = 0
    for m in xrange(NBINSX) :
      #Below is where the efficiency is computed
      if (1 - hist.Integral(0,m,k,k)/n_sig) < effref :
        if abs((1 - hist.Integral(0,m-1,k,k)/n_sig) - effref) < abs((1 - hist.Integral(0,m,k,k)/n_sig) - effref) :
          cut = hist.GetXaxis().GetBinLowEdge(m)
        else:
          cut = hist.GetXaxis().GetBinLowEdge(m+1)
        pileupVal = hist.GetYaxis().GetBinLowEdge(k+1)
        counter = counter + 1
        #print "effref is: %3.15f" % effref
        #print "calc eff is is: %3.15f" % (1 - hist.Integral(0,m,k,k)/n_sig)
        break
    if cut == -4.0 : continue
    #inverting plot to do fit
    ex = 0
    ey = 1/math.sqrt(hist.Integral(0,-1,k,k))
    g.SetPoint(counter - 1 ,pileupVal, cut)
    g.SetPointError(counter - 1 ,ex, ey)
  FirstBinVal = hist.GetYaxis().GetBinLowEdge(hist.GetYaxis().GetFirst())
  LastBinVal = hist.GetYaxis().GetBinLowEdge(hist.GetYaxis().GetLast()+1)
  #print "First bin val is %3.15f" % FirstBinVal
  #print "Last bin val is %3.15f" % LastBinVal
  f1 = ROOT.TF1('f1','pol1',FirstBinVal, LastBinVal)
  g.Fit(f1,"FR")
  #canvas = ROOT.TCanvas('Offline')
  #g.SetMarkerStyle(20)
  #g.Draw()
  #canvas.SaveAs('Tgraph'+hist.GetName()+'.pdf')
  a = f1.GetParameter(0)
  b = f1.GetParameter(1)

  ret = [a,b]

  if getGraph: ret += [g]
  if getf1: ret += [f1]
  return ret

#Calculate efficiency and errors
def CalculateEfficiencyWithSlope(hist2D, effref, a_1, limits
    , nvtxFixFraction, getGraph = False, getf1 = False):
  #print nvtxFixFraction

  # Get the intercept and slope in disc vs. pileup plane
  o = PileUpDiscFit(hist2D, effref, getGraph = getGraph, getf1 = getf1 )
  theIntercept, theSlope = o[0:2]

  # Now do some correction to give the efficiency a small slope
  # (so backgrounds do not explode)
  pivotPoint = limits[1]
  theIntercept = theIntercept + pivotPoint*theSlope*(1-nvtxFixFraction)
  #print "theSlope (in calcEff): %3.15f" % theSlope
  theSlope = theSlope*nvtxFixFraction
  #print "theSlope (in calcEff): %3.15f" % theSlope
  # Put into histograms
  histNum = GetParameterizedDiscrNumeratorProfile(hist2D,theIntercept,theSlope)
  histDen = hist2D.ProjectionY()
  histEff = histNum.Clone()
  #histEff.Divide(histDen)
  histEff.Divide(histNum,histDen,1.,1.,'B')
  for bin in xrange(histEff.GetNbinsX()):
    if histDen.GetBinContent(bin+1) != 0 :
      Eff = histEff.GetBinContent(bin+1)
      dEff = math.sqrt(Eff*(1-Eff)/histDen.GetBinContent(bin+1))
      histEff.SetBinError(bin+1,dEff)
    else:
      histEff.SetBinError(bin+1,0)
  ret = [histNum, histDen, histEff, theIntercept, theSlope]
  if getGraph: ret += [o[2]]
  if getf1: ret += [o[2 + int(getGraph)]]
  return ret


def GetParameterizedDiscrNumeratorProfile(hist,a,b) :
    err_on_higher_eff = False
    #self.mh.DEBUG('GetParameterizedDiscrNumeratorProfile start',5)
    nbinsy = hist.GetNbinsY()
    h1 = hist.ProjectionY(hist.GetName()+'_proj'+str(time.time()),1,1)
    h1.Reset("ICESM")
    for by in xrange(nbinsy) :
        xproj = hist.ProjectionX('xproj'+str(time.time()),by+1,by+1)
        discr = a + b*by
        dbin = xproj.FindBin(discr)
        num = xproj.Integral(dbin+(0 if err_on_higher_eff else 1),xproj.GetNbinsX()+1)
        h1.SetBinContent(by+1,num)
    #self.mh.DEBUG('GetParameterizedDiscrNumeratorProfile end',5)
    return h1


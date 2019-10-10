

__all__ = ["PileupFit"]

try:
  xrange
except NameError:
  xrange = range

from saphyra import isTensorFlowTwo
from saphyra import Algorithm
from Gaugi.messenger.macros import *
from Gaugi import StatusCode, progressbar
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from sklearn.metrics import roc_auc_score
from sklearn.metrics import mean_squared_error
from sklearn.metrics import roc_curve
from monet.PlotFunctions import *
from monet.TAxisFunctions import *
from monet.AtlasStyle import *
from ROOT import TCanvas, gStyle, TLegend, kRed, kBlue, kBlack,TLine,kBird, kOrange,kGray
from ROOT import TGraphErrors,TF1,TColor
from ROOT import TH2F , TH2D
if isTensorFlowTwo():
  from tensorflow.keras import Model
else:
  from keras import Model

import ROOT
import numpy as np
import time
import math

def sp(pd, fa):
  return np.sqrt(  np.sqrt(pd*(1-fa)) * (0.5*(pd+(1-fa)))  )


class PileupFit( Algorithm ):

  def __init__( self, name, pileup, **kw ):
    Algorithm.__init__(self, name, **kw)
    self._pileup = pileup
    import collections
    self._reference = collections.OrderedDict()
    # Set ATLAS style
    from monet.AtlasStyle import SetAtlasStyle
    SetAtlasStyle()


  def add( self, key, reference, pd, fa ):
    pd = (pd[0]/float(pd[1]), pd[0],pd[1])
    fa = (fa[0]/float(fa[1]), fa[0],fa[1])
    print(pd)
    print(fa)
    MSG_INFO( self, '%s | %s(pd=%1.2f, fa=%1.2f, sp=%1.2f)', key, reference, pd[0]*100, fa[0]*100, sp(pd[0],fa[0])*100 )
    self._reference[key] = {'pd':pd, 'fa':fa, 'sp':sp(pd[0],fa[0]), 'reference' : reference}


  def execute( self, context ):

    model  = context.getHandler("model")
    # remove the last activation and recreate the mode
    model  = Model(model.inputs, model.layers[-2].output)
    imodel = context.getHandler("imodel")
    index  = context.getHandler("index")
    sort   = context.getHandler("sort" )
    init   = context.getHandler("init" )
    #store = self.getStoreGateSvc()
    #store.mkdir( "model_%s_sort_%d_init_%d" % (imodel,sort,init) )

    history          = context.getHandler("history" )
    x_train, y_train = context.getHandler("trnData")
    x_val , y_val    = context.getHandler("valData")

    # Get all outputs before the last activation function
    y_pred = model.predict( x_train, batch_size = 1024*6, verbose=1 )
    y_pred_val = model.predict( x_val, batch_size = 1024*6, verbose=1 )

    # Get the pileup value for each event using the
    # external information
    pileup = self._pileup[index[sort][0]]
    pileup_val = self._pileup[index[sort][1]]
    pileup_s = pileup[y_train==1]
    y_pred_s = y_pred[y_train==1]
    pileup_val_s = pileup_val[y_val==1]
    y_pred_val_s = y_pred_val[y_val==1]
    pileup_b = pileup[y_train!=1]
    y_pred_b = y_pred[y_train!=1]
    pileup_val_b = pileup_val[y_val!=1]
    y_pred_val_b = y_pred_val[y_val!=1]

    xmin =  1.5*np.percentile( y_pred_s, 0.01  )
    xmax =  1.1*np.percentile( y_pred_s, 97 )
    xbins= int( (xmax-xmin) / 0.005 ) # 0.001
    ymin = int( 1.2*np.percentile( pileup_s, 2.3  ) )
    ymax = int( 1.2*np.percentile( pileup_s, 97 ) )
    ybins= int( (ymax-ymin) / 0.5 )
    # Get the correction for train dataset for signal
    #print xbins, ' - ', xmin, ' - ', xmax
    #print ybins, ' - ', ymin, ' - ', ymax
    hist  = TH2D('','', xbins, xmin, xmax, ybins, ymin, ymax )

    history['fitting'] = {}

    for key, ref in self._reference.items():

      d = self.calculate( history, hist, ref, y_pred_s, y_pred_b, y_pred_val_s, y_pred_val_b, pileup_s, pileup_b, pileup_val_s, pileup_val_b )
      MSG_INFO(self, "          : %s", key )
      MSG_INFO(self, "Reference : [Pd: %1.4f] , Fa: %1.4f and SP: %1.4f ", ref['pd'][0]*100, ref['fa'][0]*100, ref['sp']*100 )
      MSG_INFO(self, "Train     : [Pd: %1.4f] , Fa: %1.4f and SP: %1.4f ", d['pd'][0]*100, d['fa'][0]*100, d['sp']*100 )
      MSG_INFO(self, "Validation: [Pd: %1.4f] , Fa: %1.4f and SP: %1.4f ", d['pd_val'][0]*100, d['fa_val'][0]*100, d['sp_val']*100 )
      MSG_INFO(self, "Operation : [Pd: %1.4f] , Fa: %1.4f and SP: %1.4f ", d['pd_op'][0]*100, d['fa_op'][0]*100, d['sp_op']*100 )

      history['fitting'][key] = d

    return StatusCode.SUCCESS





  def calculate( self, history, hist, ref, y_pred_s, y_pred_b, y_pred_val_s, y_pred_val_b, pileup_s, pileup_b, pileup_val_s, pileup_val_b ):

    d = {}
    d['pd_ref'] = ref['pd']
    d['fa_ref'] = ref['fa']
    d['sp_ref'] = ref['sp']


    d['reference'] = ref['reference']

    # Fitting
    self.Fill( hist, y_pred_s, pileup_s)
    slope, offset, discr_points, pileup_points, error_points = self.fit( hist, ref['pd'][0] )
    d['slope'] = slope
    d['offset'] = offset
    #self.plot( store, 'signal',hist_s, slope, offset, discr_points, pileup_points, error_points, xmin, xmax, ymin, ymax )

    # Get the efficiencies for train dataset
    eff, passed, total = self.efficiency(y_pred_s, pileup_s, slope, offset )
    d['pd'] = (eff,passed,total)
    eff, passed, total = self.efficiency( y_pred_b, pileup_b, slope, offset )
    d['fa'] = (eff,passed,total)
    d['sp'] = sp(d['pd'][0], d['fa'][0])

    # Validation values
    eff, passed, total = self.efficiency( y_pred_val_s, pileup_val_s, slope, offset )
    d['pd_val'] = (eff,passed,total)
    eff, passed, total = self.efficiency( y_pred_val_b, pileup_val_b, slope, offset )
    d['fa_val'] = (eff,passed,total)
    d['sp_val'] = sp(d['pd_val'][0], d['fa_val'][0])

    # Fit for operation (train+val)
    # Here, we just need to fill the train values since the val set was filled before
    self.Fill( hist, y_pred_val_s, pileup_val_s)
    slope, offset, discr_points, pileup_points, error_points = self.fit( hist, ref['pd'][0] )
    d['slope_op'] = slope
    d['offset_op'] = offset
    y_pred_op_s = np.concatenate((y_pred_s, y_pred_val_s))
    y_pred_op_b = np.concatenate((y_pred_b, y_pred_val_b))
    pileup_op_s = np.concatenate( (pileup_s, pileup_val_s))
    pileup_op_b = np.concatenate( (pileup_b, pileup_val_b))
    eff, passed, total = self.efficiency( y_pred_op_s, pileup_op_s, slope, offset )
    d['pd_op'] = (eff,passed,total)
    eff, passed, total = self.efficiency( y_pred_op_b, pileup_op_b, slope, offset )
    d['fa_op'] = (eff,passed,total)
    d['sp_op'] = sp(d['pd_op'][0], d['fa_op'][0])
    return d


  def Fill( self, hist, pred, pileup ):
    import array
    hist.FillN( len(pred), array.array('d', pred), array.array('d', pileup), array.array('d', [1]*len(pred) ) )


  # Calculate the slope and offset give an 2D histogram and a reference (target value)
  def fit(self, hist, effref):

    NBINSY = hist.GetNbinsY()
    NBINSX = hist.GetNbinsX()
    # get the threshold used to hold the requested target
    def get_thresholds(h, effref):
      nbins = h.GetNbinsX()
      fullArea = h.Integral(0,nbins+1)
      if fullArea == 0:
        return 0,1
      notDetected = 0.0; i = 0
      while 1. - notDetected > effref:
        cutArea = h.Integral(0,i)
        i+=1
        prevNotDetected = notDetected
        notDetected = cutArea/fullArea
      eff = 1. - notDetected
      prevEff = 1. -prevNotDetected
      deltaEff = (eff - prevEff)
      threshold = h.GetBinCenter(i-1)+(effref-prevEff)/deltaEff*(h.GetBinCenter(i)-h.GetBinCenter(i-1))
      error = 1./math.sqrt(fullArea)
      return threshold, error

    # Get the list of points
    def calculate(h , effref):
      nbinsy = h.GetNbinsY()
      x = list(); y = list(); errors = list()
      for by in xrange(nbinsy):
        xproj = h.ProjectionX('xproj'+str(time.time()),by+1,by+1)
        discr, error = get_thresholds(xproj,effref)
        dbin = xproj.FindBin(discr)
        x.append(discr); y.append(h.GetYaxis().GetBinCenter(by+1))
        errors.append( error )
      return x,y,errors
    # Get requested points for each range of pileup and efficiency (target)
    discr_points, pileup_points, error_points = calculate(hist, effref )
    import array
    g = ROOT.TGraphErrors( len(discr_points)
                         , array.array('d',pileup_points) # x
                         , array.array('d',discr_points) # y
                         , array.array('d',[0.]*len(discr_points))
                         , array.array('d',error_points) )

    FirstBinVal = hist.GetYaxis().GetBinLowEdge(hist.GetYaxis().GetFirst())
    LastBinVal = hist.GetYaxis().GetBinLowEdge(hist.GetYaxis().GetLast()+1)
    f1 = ROOT.TF1('f1','pol1',FirstBinVal, LastBinVal)
    # Linear fit using pol1
    g.Fit(f1,"FRq")
    slope = f1.GetParameter(1)
    offset = f1.GetParameter(0)
    return slope,offset, discr_points, pileup_points, error_points


  def efficiency(self, predict, pileup, slope, offset ):

    predict = predict.reshape((len(pileup),))
    thresholds = slope*pileup + offset
    answer  = np.greater(predict,thresholds)
    
    passed = len(answer[answer==True])
    total = len(answer)
    eff = passed / float(total)
    return eff, passed, total


  def plot( self, store, cname, hist, slope, offset, discr_points,
                  pileup_points, error_points, xmin, xmax, ymin, ymax ):

    gStyle.SetPalette(kBird)
    drawopt='lpE2'
    canvas = TCanvas(cname,cname,500, 500)
    canvas.SetRightMargin(0.15)
    hist.GetXaxis().SetTitle('Neural Network output (Discriminant)')
    hist.GetYaxis().SetTitle("Pileup")
    hist.GetZaxis().SetTitle('Count')
    hist.Draw('colz')
    canvas.SetLogz()
    import array
    g = TGraphErrors(len(discr_points), array.array('d',discr_points), array.array('d',pileup_points),
                          array.array('d',error_points) , array.array('d',[0]*len(discr_points)))
    g.SetLineWidth(1)
    g.SetLineColor(kBlue)
    g.SetMarkerColor(kBlue)
    g.Draw("P same")
    # discr = slope*pileup + offset
    l = TLine(offset+slope*ymin,ymin, slope*ymax+offset, ymax)
    l.SetLineColor(kBlack)
    l.SetLineWidth(2)
    l.Draw()
    FormatCanvasAxes(canvas, XLabelSize=16, YLabelSize=16, XTitleOffset=0.87, ZLabelSize=14,ZTitleSize=14, YTitleOffset=0.87, ZTitleOffset=1.1)
    SetAxisLabels(canvas,'Neural Network output (Discriminant)',"Pileup")
    store.addObject( canvas )





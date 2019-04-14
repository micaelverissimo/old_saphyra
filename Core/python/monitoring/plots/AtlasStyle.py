__all__ = ["AtlasStyle","SetAtlasStyle","ATLASLabel","ATLASLumiLabel","AtlasTemplate1","setLegend1"]

from ROOT import gROOT, TStyle

def SetAtlasStyle ():
  print "\nApplying ATLAS style settings..."
  atlasStyle = AtlasStyle()
  gROOT.SetStyle("mystyle")
  gROOT.ForceStyle()

try:
  from TagAndProbeFrame import SetupStyle as AtlasStyle
except ImportError:
  def AtlasStyle():
    atlasStyle = TStyle("mystyle","mystyle")
    # use plain black on white colors
    icol=0 # WHITE
    atlasStyle.SetFrameBorderMode(icol)
    atlasStyle.SetFrameFillColor(icol)
    atlasStyle.SetCanvasBorderMode(icol)
    atlasStyle.SetCanvasColor(icol)
    atlasStyle.SetPadBorderMode(icol)
    atlasStyle.SetPadColor(icol)
    atlasStyle.SetStatColor(icol)
    #atlasStyle.SetFillColor(icol) # don't use: white fill color for *all* objects
    # set the paper & margin sizes
    atlasStyle.SetPaperSize(20,26)

    # set margin sizes
    atlasStyle.SetPadTopMargin(0.05)
    atlasStyle.SetPadRightMargin(0.05)
    atlasStyle.SetPadBottomMargin(0.16)
    atlasStyle.SetPadLeftMargin(0.16)

    # set title offsets (for axis label)
    atlasStyle.SetTitleXOffset(1.4)
    atlasStyle.SetTitleYOffset(1.4)

    # use large fonts
    #Int_t font=72 # Helvetica italics
    font=42 # Helvetica
    tsize=0.05
    atlasStyle.SetTextFont(font)

    atlasStyle.SetTextSize(tsize)
    atlasStyle.SetLabelFont(font,"x")
    atlasStyle.SetTitleFont(font,"x")
    atlasStyle.SetLabelFont(font,"y")
    atlasStyle.SetTitleFont(font,"y")
    atlasStyle.SetLabelFont(font,"z")
    atlasStyle.SetTitleFont(font,"z")
    
    atlasStyle.SetLabelSize(tsize,"x")
    atlasStyle.SetTitleSize(tsize,"x")
    atlasStyle.SetLabelSize(tsize,"y")
    atlasStyle.SetTitleSize(tsize,"y")
    atlasStyle.SetLabelSize(tsize,"z")
    atlasStyle.SetTitleSize(tsize,"z")

    # use bold lines and markers
    atlasStyle.SetMarkerStyle(20)
    atlasStyle.SetMarkerSize(1.2)
    atlasStyle.SetHistLineWidth(2)
    atlasStyle.SetLineStyleString(2,"[12 12]") # postscript dashes

    # get rid of X error bars 
    #atlasStyle.SetErrorX(0.001)
    # get rid of error bar caps
    atlasStyle.SetEndErrorSize(0.)

    # do not display any of the standard histogram decorations
    atlasStyle.SetOptTitle(0)
    #atlasStyle.SetOptStat(1111)
    atlasStyle.SetOptStat(0)
    #atlasStyle.SetOptFit(1111)
    atlasStyle.SetOptFit(0)

    # put tick marks on top and RHS of plots
    atlasStyle.SetPadTickX(1)
    atlasStyle.SetPadTickY(1)
    atlasStyle.SetPalette(1)
    return atlasStyle

from ROOT import TLatex, gPad

def ATLASLabel(x,y,text,color=1):
  l = TLatex()
  l.SetNDC();
  l.SetTextFont(72);
  l.SetTextColor(color);
  delx = 0.115*696*gPad.GetWh()/(472*gPad.GetWw());
  l.DrawLatex(x,y,"ATLAS");
  if True:
    p = TLatex(); 
    p.SetNDC();
    p.SetTextFont(42);
    p.SetTextColor(color);
    p.DrawLatex(x+delx,y,text);
    #p.DrawLatex(x,y,"#sqrt{s}=900GeV");

def ATLASLumiLabel(x,y,lumi=None,color=1):   
    l = TLatex()
    l.SetNDC();
    l.SetTextFont(42);
    l.SetTextSize(0.045);
    l.SetTextColor(color);
    dely = 0.115*472*gPad.GetWh()/(506*gPad.GetWw());
    label="#sqrt{s}=13 TeV"
    if lumi is not None: label += ", #intL dt = " + lumi + " fb^{-1}"
    l.DrawLatex(x,y-dely,label);


def setLegend1(leg):
    leg.SetBorderSize(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.032)
    leg.SetLineColor(1)
    leg.SetLineStyle(1)
    leg.SetLineWidth(1)
    leg.SetFillColor(0)
    leg.SetFillStyle(0)
    leg.Draw()


def AtlasTemplate1( canvas, **kw ):
  
  atlaslabel = kw.pop('atlaslabel', 'Internal')
  dolumi = kw.pop('dolumi',False)
  #ATLASLabel(0.2,0.85,'Preliminary')
  #ATLASLabel(0.2,0.85,'Internal')
  if atlaslabel: 
    ATLASLabel(0.2,0.85, atlaslabel)
  if dolumi:
    ATLASLumiLabel(0.2,0.845,'33.5')
  #ATLASLumiLabel(0.2,0.845)
  canvas.Modified()
  canvas.Update()



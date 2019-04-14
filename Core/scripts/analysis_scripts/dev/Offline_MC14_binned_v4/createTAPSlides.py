#!/usr/bin/env python

import os, re, itertools

from RingerCore import ( emptyArgumentsPrintHelp, ArgumentParser, getFiles, traverse
                       , BooleanStr )
from RingerCore.tex.TexAPI import *
from RingerCore.tex.BeamerAPI import *
from TuningTools.parsers import loggerParser

parentParser = ArgumentParser(add_help = False)
parentParser.add_argument_group( "" )
mainGroup = parentParser.add_argument_group( "Required arguments", "")
mainGroup.add_argument('-s','--sgnBaseFolder',
    required = True, help = "The base folder containing signal folders created by runRinger_plot.sh")
mainGroup.add_argument('-sp','--sgnPattern', 
    required = True, help = "Base pattern used to flag the signal type")
mainGroup.add_argument('-b','--bkgBaseFolder',
    required = True, help = "The base folder containing background folders created by runRinger_plot.sh")
mainGroup.add_argument('-bp','--bkgPattern', 
    required = True, help = "Base pattern used to flag the background type")
mainGroup.add_argument('--doOverall', type=BooleanStr, default = True, help = "Whether to do overall performance comparison.")
mainGroup.add_argument('--doEtaPerformance', type=BooleanStr, default = True, help = "Whether to do eta performance comparison.")
mainGroup.add_argument('--doNNOutput', type=BooleanStr, default = True, help = "Whether to do NN output.")
mainGroup.add_argument('--doRingerComparison', type=BooleanStr, default = True, help = "Whether to compare ringer performances.")
mainGroup.add_argument('--pdf', type=BooleanStr, default = True, help = "Whether to create pdf files or not.")


parser = ArgumentParser(description = 'Create TuningTool data from PhysVal.',
                        parents = [parentParser, loggerParser])
parser.make_adjustments()
emptyArgumentsPrintHelp(parser)

# Retrieve parser args:
args = parser.parse_args()

def update( d, **kw):
  """
  Wrapper to update d and return d
  """
  d.update( d, **kw )
  return d

# Make one slide group for each comparison, e.g. v1_versus_v3 one pdf, v2_versus_v3 another pdf
if False: #with TexSessionStream( 'beamer' ):
  with BeamerTexReport( theme = 'Berlin', _toPDF = True ):
    with BeamerSection( name = 'Section1' ):
      BeamerSlide( title = "Slide1" )
      BeamerSlide( title = "Slide2" )
    with BeamerSection( name = 'Section2' ):
      BeamerSlide( title = "Slide3" )
      BeamerSlide( title = "Slide4" )
      basePathSgn = '~/Documents/Doutorado/CERN/Offline/v3_binned_vs_unbinned/electrons/electrons_rNN_LooseAndBLayerL_LH_Pd_v1_comp_LH/'
      basePathBkg = '~/Documents/Doutorado/CERN/Offline/v3_binned_vs_unbinned/JF17/JF17_rNN_LooseAndBLayerL_LH_Pd_v1_comp_LH/'
      BeamerFigureSlide( title = 'Slide5'
                       , path = os.path.join( basePathSgn, 'electrons_rNN_LooseAndBLayerL_LH_Pd_v1_comp_LH_ET.pdf')
                       )
    with BeamerSection( name = 'Section3' ):
      BeamerMultiFigureSlide( title = 'Slide6'
                            , paths = [ os.path.join( basePathSgn, 'electrons_rNN_LooseAndBLayerL_LH_Pd_v1_comp_LH_ET.pdf'  )
                                      , os.path.join( basePathSgn, 'electrons_rNN_LooseAndBLayerL_LH_Pd_v1_comp_LH_eta.pdf' )
                                      , os.path.join( basePathSgn, 'electrons_rNN_LooseAndBLayerL_LH_Pd_v1_comp_LH_mu.pdf'  )
                                      , os.path.join( basePathBkg, 'JF17_rNN_LooseAndBLayerL_LH_Pd_v1_comp_LH_ET.pdf'       )
                                      , os.path.join( basePathBkg, 'JF17_rNN_LooseAndBLayerL_LH_Pd_v1_comp_LH_eta.pdf'      )
                                      , os.path.join( basePathBkg, 'JF17_rNN_LooseAndBLayerL_LH_Pd_v1_comp_LH_mu.pdf'       )
                                      ]
                            , nDivWidth = 3
                            , nDivHeight = 2
                            )

#sgnFolders = getFiles( args.sgnBaseFolder, ftype=os.path.isdir )
#bkgFolders = getFiles( args.sgnBaseFolder, ftype=os.path.isdir )

et_bins = [(15,20),(20,25),(25,30),(30,35),(35,40),(40,45),(45,50),(50,60),(60,80),(80,150)]

ringer_cutbased_decode = { "" : " "
                         , "L" : " and Track CutID Loose"
                         , "M" : " and Track CutID Medium"
                         , "T" : " and Track CutID Tight"
                         }

lh_req_v11 = { 'Tight':     'TightLLH_Smooth_v11'
             , 'Medium':    'MediumLLH_Smooth_v11'
             , 'Loose':     'LooseAndBLayerLLH_Smooth_v11'
             , 'VeryLoose': 'VeryLooseLLH_Smooth_v11' 
             }
lh_req_v8 = { 'Tight':      'TightLLHMC15_v8'
            , 'Medium':     'MediumLLHMC15_v8'
            , 'Loose':      'LooseAndBLayerLLHMC15_v8'
            , 'VeryLoose':  'VeryLooseLLHMC15_v8' 
            }
cutid_2015 = { 'Tight' : 'TightIsEMMC15'
             , 'Medium' : 'MediumIsEMMC15'
             , 'Loose' : 'LooseIsEMMC15'
             }
refDict = { 'LH' : lh_req_v11
          , 'LH_MC15' : lh_req_v8
          , 'CutID' : cutid_2015 }

#latex_ref_decode = { 'Pd' : 'set to have similar P_D to the baseline method'
#                   , 'MaxSP' : 'set via SP-index maximization'
#                   , 'Pf' : 'set to have similar P_F to the baseline method'
#                   }

latex_ref_decode = { 'Pd' : 'P_D'
                   , 'MaxSP' : 'MaxSP'
                   , 'Pf' : 'P_F'
                   }

#'electrons_rNN_TightL_LH_Pf_v2_comp_LH_MC15'
#"${label}_rNN_${lreq}${trackCut}_LH_${lref}_${r_version}_comp_${comp_name}"

baseName = '%(dataset)s_rNN_%(req)s%(trackCut)s_LH_%(ringer_ref)s_%(r_version)s_comp_%(ref)s'
baseRingerNN = 'RingerMC14_%(ringer_req)s_LH_%(ringer_ref)s_%(r_version)s_%(dataset)s_rNN_%(req)s%(trackCut)s_LH_%(ringer_ref)s_%(r_version)s_comp_%(ref)s_RNN'

latex_code = { 'ET' : r'$\text{E}_{\rm \text{T}}$'
             , 'eta' : r'$\eta$'
             , 'mu' : r'$\left<\mu\right>$'
             }

track_operation = { '' : "No Track CutID"
                  , "L" : "Track CutID Loose"
                  , "M" : "Track CutID Medium"
                  , "T" : "Track CutID Tight"
                  }
if args.doOverall:
  for r_version in ["v1", "v2", "v3_unbinned", "v3_binned"]:
    with BeamerTexReportTemplate1( theme = 'Berlin'
                                 , _toPDF = args.pdf
                                 , title = 'Offline Ringer ' + r_version + " Performance w.r.t Baseline Electron ID Algorithms."
                                 , outputFile = "OfflineRinger_" + r_version + "_performance" 
                                 , font = 'structurebold'):
      for ref in ["CutID", "LH", "LH_MC15"]:
        with BeamerSection( name = escape_latex( ref ) ):
          for req in ["Loose", "Medium", "Tight"]:
            with BeamerSubSection( name = escape_latex( req ) ):
              for ringer_ref in ["Pd", "MaxSP", "Pf"]:
                searchFolder_ringer_ref = ringer_ref
                if "v3" in r_version and ringer_ref == "MaxSP":
                  searchFolder_ringer_ref = "SP"
                if ringer_ref == "MaxSP" and req is not "Medium": continue
                with BeamerSubSubSection( name = ringer_ref ):
                  for trackCut in ["", "L", "M", "T"]:
                    baseline_req = req
                    if ref == "LH" and req == "Loose":
                      baseline_req = "LooseAndBLayer"
                    d = { 'req' : baseline_req
                        , 'trackCut' : trackCut
                        , 'ringer_ref' : searchFolder_ringer_ref
                        , 'r_version' : r_version
                        , 'ref' : ref }
                    d.update( { 'dataset' : args.sgnPattern } )
                    baseSgn = baseName % d
                    d.update( { 'dataset' : args.bkgPattern } )
                    baseBkg = baseName % d
                    title = escape_latex( 'Ringer{ringer_requirement}{ringer_ref}_{r_version}{track_version} w.r.t {reference}'.format(
                                                                    r_version = r_version
                                                                  , ringer_requirement = req
                                                                  , ringer_ref = ringer_ref
                                                                  , track_version = ringer_cutbased_decode[trackCut]
                                                                  , reference = refDict[ref][req]
                                                                  )
                                        )
                    BeamerMultiFigureSlide( title = title
                                          , paths = [ os.path.join( baseFolder, basePath, basePath + '_%s.pdf' % var  )
                                                    for var in ['ET', 'eta', 'mu']
                                                    for baseFolder, basePath in zip([args.sgnBaseFolder, args.bkgBaseFolder], [baseSgn, baseBkg])
                                                    ]
                                          , nDivHeight = 2
                                          , nDivWidth = 3
                                          )
                  # end of trackCut
                  title = escape_latex( 'Ringer{ringer_requirement}{ringer_ref}_{r_version} w.r.t {reference} '.format(
                                                                    r_version = r_version
                                                                  , ringer_requirement = req
                                                                  , ringer_ref = ringer_ref
                                                                  , reference = refDict[ref][req]
                                                                  )
                                      )
                  BeamerMultiFigureSlide( title = title + ' | All CutBased Operation Cases'
                      , paths = [ os.path.join( baseFolder, baseName % update( d , trackCut = trackCut
                                                                                 , dataset = dataset )
                                              , (baseName % d) + ( '_%s.pdf' % var ) )
                                for var in ['ET', 'eta', 'mu']
                                for dataset, baseFolder in zip([args.sgnPattern, args.bkgPattern], [args.sgnBaseFolder, args.bkgBaseFolder] )
                                for trackCut in ['', 'L', 'M', 'T'] 
                                ]
                      , texts = [ [ (100, 110, latex_code[var]), 
                                    (10, 100, r'\fontsize{0}{2}{' + dataset_name + '}'),
                                    (-10, 10, r'\rotatebox{90}{' + track_operation[track_version] + '}') ] 
                                      if track_version is '' and baseFolder == args.sgnBaseFolder and var == 'ET' else 
                                  [ (100, 110, latex_code[var]), 
                                    (10, 100, r'\fontsize{0}{2}{' + dataset_name + '}') ] 
                                      if track_version is '' and baseFolder == args.sgnBaseFolder else 
                                  [ (10, 100, r'\fontsize{0}{2}{' + dataset_name + '}') ] if track_version is '' else 
                                  [ (-12, 10, r'\rotatebox{90}{' + track_operation[track_version] + '}') if var == "ET" and dataset == args.sgnPattern else None ]
                                for var in ['ET', 'eta', 'mu']
                                for dataset, baseFolder, dataset_name in zip([args.sgnPattern, args.bkgPattern], 
                                                                             [args.sgnBaseFolder, args.bkgBaseFolder],
                                                                             ["  Signal Selected Events", "Background Selected Events"])
                                for track_version in ['', 'L', 'M', 'T']
                                ]
                      , nDivHeight = 4
                      , nDivWidth = 6
                      , fontsize = 4
                      , fortran = True
                      , verticalStartAt = .05
                      )
                # end of BeamerSubSubSection context
              # end of ringer_ref 
            # end of BeamerSubSection context
          # end of req
        # end of BeamerSection context
      # end of ref
    # end of BeamerTexReport
  # end of r_version

if args.doEtaPerformance:
  for r_version in ["v1", "v2", "v3_unbinned", "v3_binned"]:
    with BeamerTexReportTemplate1( theme = 'Berlin'
                                 , _toPDF = args.pdf
                                 , title = 'Offline Ringer ' + r_version + " Eta Projection Performances w.r.t. Baseline Electron ID Algorithms"
                                 , outputFile = "OfflineRinger_" + r_version + "_eta_projections_performance"
                                 , font = 'structurebold' ):
      for ref in ["CutID", "LH", "LH_MC15"]:
        with BeamerSection( name = escape_latex( ref ) ):
          for req in ["Loose", "Medium", "Tight"]:
            with BeamerSubSection( name = escape_latex( req ) ):
              for ringer_ref in ["Pd", "MaxSP", "Pf"]:
                searchFolder_ringer_ref = ringer_ref
                if "v3" in r_version and ringer_ref == "MaxSP":
                  searchFolder_ringer_ref = "SP"
                if ringer_ref == "MaxSP" and req is not "Medium": continue
                with BeamerSubSubSection( name = escape_latex( ringer_ref ) ):
                  for trackCut in ["", "L", "M", "T"]:
                    baseline_req = req
                    if ref == "LH" and req == "Loose":
                      baseline_req = "LooseAndBLayer"
                    d = { 'req' : baseline_req
                        , 'trackCut' : trackCut
                        , 'ringer_ref' : searchFolder_ringer_ref
                        , 'r_version' : r_version
                        , 'ref' : ref }
                    d.update( { 'dataset' : args.sgnPattern } )
                    baseSgn = baseName % d
                    d.update( { 'dataset' : args.bkgPattern } )
                    baseBkg = baseName % d
                    title = escape_latex( 'Ringer{ringer_requirement}{ringer_ref}_{r_version}{track_version} w.r.t {reference}'.format(
                                                                    r_version = r_version
                                                                  , ringer_requirement = req
                                                                  , ringer_ref = ringer_ref
                                                                  , track_version = ringer_cutbased_decode[trackCut]
                                                                  , reference = refDict[ref][req]
                                                                  )
                                       )
                    BeamerMultiFigureSlide( title = title + ' | Signal/Background Performances'
                                          , paths = list(
                                                      traverse(
                                                        [ ( os.path.join( args.sgnBaseFolder, baseSgn, baseSgn + '_ET_%d.pdf' % i )
                                                          , os.path.join( args.bkgBaseFolder, baseBkg, baseBkg + '_ET_%d.pdf' % i )
                                                          )
                                                        for i in range(3,13) ] + [
                                                          os.path.join( args.sgnBaseFolder, baseSgn, baseSgn + '_eta.pdf' )
                                                        , os.path.join( args.bkgBaseFolder, baseBkg, baseBkg + '_eta.pdf' )
                                                        , os.path.join( args.sgnBaseFolder, baseSgn, baseSgn + '_ET.pdf' )
                                                        , os.path.join( args.bkgBaseFolder, baseBkg, baseBkg + '_ET.pdf' )
                                                        ], simple_ret=True ) )
                                          , texts =  list( traverse (       
                                                [ ( ( (20,79,r'$%.0f < \text{E}_{\rm T} [\text{GeV}] < %.0f$' % ( etMin, etMax ) )
                                                    , (20,87,r'Signal selected events' ) 
                                                    )
                                                  , ( (20,79,r'$%.0f < \text{E}_{\rm T} [\text{GeV}] < %.0f$' % ( etMin, etMax ) )
                                                    , (20,87,r'Background selected events' ) 
                                                    # \put(55,10){\includegraphics[scale=.07]% {golfer.ps}}
                                                    )
                                                  ) for etMin, etMax in et_bins
                                               ] +
                                               [ ( ( ( 20,79,r'Full phase space' )
                                                     , 
                                                     ( 20,87,r'Signal selected events' )
                                                   )
                                                   ,
                                                   ( ( 20,79,r'Full phase space' )
                                                     , 
                                                     ( 20,87,r'Background selected events' )
                                                   )
                                                 , ( ( 20,79,r'Full phase space' )
                                                     , 
                                                     ( 20,87,r'Signal selected events' )
                                                   )
                                                   ,
                                                 )
                                               ] , simple_ret = True, max_depth = 2
                                                                   )
                                                         ) 
                                          , nDivHeight = 4
                                          , nDivWidth = 6
                                          , fontsize = 1.2
                                          )
                    BeamerMultiFigureSlide( title = title + ' | Signal Performances'
                                          , paths = [ os.path.join( args.sgnBaseFolder, baseSgn, baseSgn + '_ET_%d.pdf' % i  ) for i in range(3,13) ] +
                                                    [ os.path.join( args.sgnBaseFolder, baseSgn, baseSgn + '_eta.pdf' ) 
                                                    , os.path.join( args.sgnBaseFolder, baseSgn, baseSgn + '_ET.pdf' )
                                                    ]
                                          , texts = [ ( ( 20,79,r'$%.0f < \text{E}_{\rm T} [\text{GeV}] < %.0f$' % ( etMin, etMax ) )
                                                      , ( 20,87,r'Signal selected events' )
                                                      ) for etMin, etMax in et_bins ] + 
                                                    [ ( ( 20,79,r'Full phase space' )
                                                      , ( 20,87,r'Signal selected events' )
                                                      )
                                                    , ( ( 20,79,r'Full phase space' )
                                                      , ( 20,87,r'Signal selected events' )
                                                      )
                                                    ]
                                          , nDivHeight = 3
                                          , nDivWidth = 4
                                          , fontsize = 1.2
                                          )
                    BeamerMultiFigureSlide( title = title + ' | Background Performances'
                                          , paths = [ os.path.join( args.bkgBaseFolder, baseBkg, baseBkg + '_ET_%d.pdf' % i ) for i in range(3,13) ] +
                                                    [ os.path.join( args.bkgBaseFolder, baseBkg, baseBkg + '_eta.pdf' ) 
                                                    , os.path.join( args.bkgBaseFolder, baseBkg, baseBkg + '_ET.pdf' )
                                                    ]
                                          , texts = [ ( ( 20,79,r'$%.0f < \text{E}_{\rm T} [\text{GeV}] < %.0f$' % ( etMin, etMax ) )
                                                      , ( 20,87,r'Background selected events' )
                                                      ) for etMin, etMax in et_bins ] + 
                                                    [ ( ( 20,79,r'Full phase space' )
                                                      , ( 20,87,r'Background selected events' )
                                                      )
                                                    , ( ( 20,79,r'Full phase space' )
                                                      , ( 20,87,r'Background selected events' )
                                                      )
                                                    ]
                                          , nDivHeight = 3
                                          , nDivWidth = 4
                                          , fontsize = 1.2
                                          )
                  # end of trackCut
                # end of BeamerSubSubSection context
              # end of ringer_ref 
            # end of BeamerSubSection context
          # end of req
        # end of BeamerSection context
      # end of ref
    # end of BeamerTexReport
  # end of r_version

if args.doNNOutput:
  for r_version in ["v1", "v2", "v3_unbinned", "v3_binned"]:
    with BeamerTexReportTemplate1( theme = 'Berlin'
                                 , _toPDF = args.pdf
                                 , title = 'Offline Ringer ' + r_version + " Neural Network Output"
                                 , outputFile = "OfflineRinger_" + r_version + "_nn_output"
                                 , font = 'structurebold' ):
      for req in ["Loose", "Medium", "Tight"]:
        with BeamerSection( name = escape_latex( req ) ):
          for ringer_ref in ["Pd", "MaxSP", "Pf"]:
            searchFolder_ringer_ref = ringer_ref
            if "v3" in r_version and ringer_ref == "MaxSP":
              searchFolder_ringer_ref = "SP"
            if ringer_ref == "MaxSP" and req is not "Medium": continue
            with BeamerSubSection( name = escape_latex( ringer_ref ) ):
              specialBaseRingerNN = baseRingerNN
              if ringer_ref == "MaxSP" and not "v3" in r_version:
                specialBaseRingerNN = specialBaseRingerNN.replace( "_LH", "", 1 )
              baseline_req = req
              if req == "Loose":
                baseline_req = "LooseAndBLayer"
              d = { 'req' : baseline_req
                  , 'ringer_req' : req
                  , 'trackCut' : ''
                  , 'ringer_ref' : searchFolder_ringer_ref
                  , 'r_version' : r_version
                  , 'ref' : "LH" }
              d.update( { 'dataset' : args.sgnPattern } )
              baseSgn = baseName % d
              baseSgnNN = specialBaseRingerNN % d
              d.update( { 'dataset' : args.bkgPattern } )
              baseBkg = baseName % d
              baseBkgNN = specialBaseRingerNN % d
              title = escape_latex( 'Ringer{ringer_requirement}{ringer_ref}_{r_version}{track_version}'.format(
                                                              r_version = r_version
                                                            , ringer_requirement = req
                                                            , ringer_ref = ringer_ref
                                                            , track_version = ""
                                                            , reference = refDict["LH"][req]
                                                            )
                                 )
              BeamerMultiFigureSlide( title = title + ' | NN Output Transverse Energy Projections'
                                    , paths = list(
                                                traverse(
                                                  [ ( os.path.join( args.sgnBaseFolder, baseSgn, baseSgnNN + '_ET_%d.pdf' % i )
                                                    , os.path.join( args.bkgBaseFolder, baseBkg, baseBkgNN + '_ET_%d.pdf' % i )
                                                    )
                                                  for i in range(3,13) ] + [
                                                    os.path.join( args.sgnBaseFolder, baseSgn, baseSgn + '_ET.pdf' )
                                                  , os.path.join( args.bkgBaseFolder, baseBkg, baseBkg + '_ET.pdf' )
                                                  ], simple_ret=True ) )
                                    , texts =  list( traverse (       
                                          [ ( ( (20,79,r'$%.0f < \text{E}_{\rm T} [\text{GeV}] < %.0f$' % ( etMin, etMax ) )
                                              , (20,87,r'Signal selected events' ) 
                                              )
                                            , ( (20,79,r'$%.0f < \text{E}_{\rm T} [\text{GeV}] < %.0f$' % ( etMin, etMax ) )
                                              , (20,87,r'Background selected events' ) 
                                              # \put(55,10){\includegraphics[scale=.07]% {golfer.ps}}
                                              )
                                            ) for etMin, etMax in et_bins
                                         ] +
                                         [ ( ( ( 20,79,r'Full phase space' )
                                               , 
                                               ( 20,87,r'Signal selected events' )
                                             )
                                             ,
                                             ( ( 20,79,r'Full phase space' )
                                               , 
                                               ( 20,87,r'Background selected events' )
                                             )
                                           )
                                         ] , simple_ret = True, max_depth = 2
                                                             )
                                                   )      
                                    , nDivHeight = 4
                                    , nDivWidth = 6
                                    , fontsize = 1.2
                                    )
              BeamerMultiFigureSlide( title = title + ' |  NN Output x Transverse Energy'
                                    , paths = [ os.path.join( args.sgnBaseFolder, baseSgn, baseSgnNN + '2D.pdf' ) 
                                              , os.path.join( args.bkgBaseFolder, baseBkg, baseBkgNN + '2D.pdf' )
                                              ]
                                    , texts = [ ( ( 20,100,r'Signal selected events' ) )
                                              , ( ( 20,100,r'Background selected events' ) )
                                              ]
                                    , nDivHeight = 1
                                    , nDivWidth = 2
                                    , usedHeight = .7
                                    , startAt = -.2
                                    )
            # end of BeamerSubSection context
          # end of ringer_ref 
        # end of BeamerSection context
      # end of req
    # end of BeamerTexReport
  # end of r_version

#rNN_TightM_LH_Pf_v1_vs_v3_unbinned
#rNN_MediumL_LH_SP_v1_vs_v3_unbinned
#rNN_MediumT_LH_SP_v3_binned_vs_v3_unbinned
ringer_cutbased_decode_with = { "" : " "
                         , "L" : " with Track CutID Loose"
                         , "M" : " with Track CutID Medium"
                         , "T" : " with Track CutID Tight"
                         }
baseRingerCmpName = 'rNN_%(req)s%(trackCut)s_LH_%(ringer_ref)s_%(r_comp)s'
if args.doRingerComparison:
  for r_comp in ["v1_vs_v3_unbinned", "v2_vs_v3_binned", "v3_binned_vs_v3_unbinned"]:
    f_version, s_version = r_comp.split('_vs_')
    with BeamerTexReportTemplate1( theme = 'Berlin'
                                 , _toPDF = args.pdf
                                 , title = 'Offline Ringer ' + f_version + ' and ' + s_version + ' comparison'
                                 , outputFile = "OfflineRinger_" + r_comp + "_comparison"
                                 , font = 'structurebold' ):
      for req in ["Loose", "Medium", "Tight"]:
        with BeamerSection( name = escape_latex( req ) ):
          for ringer_ref in ["Pd", "MaxSP", "Pf"]:
            searchFolder_ringer_ref = ringer_ref
            if ringer_ref == "MaxSP":
              searchFolder_ringer_ref = "SP"
            if ringer_ref == "MaxSP" and req is not "Medium": continue
            with BeamerSubSection( name = escape_latex( ringer_ref ) ):
              for trackCut in ["", "L", "M", "T"]:
                with BeamerSubSubSection( name = escape_latex( ringer_ref + ringer_cutbased_decode[trackCut] ) ):
                  specialBaseRingerNN = baseRingerNN
                  d = { 'req' : req
                      , 'trackCut' : trackCut
                      , 'ringer_ref' : searchFolder_ringer_ref
                      , 'r_comp' : r_comp }
                  base = baseRingerCmpName % d
                  title = escape_latex( 'Ringer {f_version} and {s_version} comparison operating at {ringer_requirement}_{ringer_ref}{track_version}'.format(
                                                                  f_version = f_version
                                                                , s_version = s_version
                                                                , ringer_requirement = req
                                                                , ringer_ref = ringer_ref
                                                                , track_version = ringer_cutbased_decode_with[trackCut]
                                                                )
                                    )
                  BeamerMultiFigureSlide( title = title + ' | Overall performances'
                                        , paths = [ os.path.join( args.sgnBaseFolder, base, base + '_ET.pdf'  )
                                                  , os.path.join( args.sgnBaseFolder, base, base + '_eta.pdf' )
                                                  , os.path.join( args.sgnBaseFolder, base, base + '_mu.pdf'  )
                                                  , os.path.join( args.bkgBaseFolder, base, base + '_ET.pdf'  )
                                                  , os.path.join( args.bkgBaseFolder, base, base + '_eta.pdf' )
                                                  , os.path.join( args.bkgBaseFolder, base, base + '_mu.pdf'  )
                                                  ]
                                        , nDivHeight = 2
                                        , nDivWidth = 3
                                        )
                  BeamerMultiFigureSlide( title = title + ' | Signal/Background eta Performances'
                                        , paths = list(
                                                    traverse(
                                                      [ ( os.path.join( args.sgnBaseFolder, base, base + '_ET_%d.pdf' % i )
                                                        , os.path.join( args.bkgBaseFolder, base, base + '_ET_%d.pdf' % i )
                                                        )
                                                      for i in range(3,13) ] + [
                                                        os.path.join( args.sgnBaseFolder, base, base + '_eta.pdf' )
                                                      , os.path.join( args.bkgBaseFolder, base, base + '_eta.pdf' )
                                                      , os.path.join( args.sgnBaseFolder, base, base + '_ET.pdf' )
                                                      , os.path.join( args.bkgBaseFolder, base, base + '_ET.pdf' )
                                                      ], simple_ret=True ) )
                                        , texts =  list( traverse (       
                                              [ ( ( (20,79,r'$%.0f < \text{E}_{\rm T} [\text{GeV}] < %.0f$' % ( etMin, etMax ) )
                                                  , (20,87,r'Signal selected events' ) 
                                                  )
                                                , ( (20,79,r'$%.0f < \text{E}_{\rm T} [\text{GeV}] < %.0f$' % ( etMin, etMax ) )
                                                  , (20,87,r'Background selected events' ) 
                                                  )
                                                ) for etMin, etMax in et_bins
                                             ] +
                                             [ ( ( ( 20,79,r'Full phase space' )
                                                   , 
                                                   ( 20,87,r'Signal selected events' )
                                                 )
                                                 ,
                                                 ( ( 20,79,r'Full phase space' )
                                                   , 
                                                   ( 20,87,r'Background selected events' )
                                                 )
                                               , ( ( 20,79,r'Full phase space' )
                                                   , 
                                                   ( 20,87,r'Signal selected events' )
                                                 )
                                                 ,
                                                 ( ( 20,79,r'Full phase space' )
                                                   , 
                                                   ( 20,87,r'Background selected events' )
                                                 )
                                               )
                                             ] , simple_ret = True, max_depth = 2
                                                                 )
                                                       ) 
                                        , nDivHeight = 4
                                        , nDivWidth = 6
                                        , fontsize = 1.2
                                        )
                  BeamerMultiFigureSlide( title = title + ' | Signal Performances'
                                        , paths = [ os.path.join( args.sgnBaseFolder, base, base + '_ET_%d.pdf' % i  ) for i in range(3,13) ] +
                                                  [ os.path.join( args.sgnBaseFolder, base, base + '_eta.pdf' ) 
                                                  , os.path.join( args.sgnBaseFolder, base, base + '_ET.pdf' )
                                                  ]
                                        , texts = [ ( ( 20,79,r'$%.0f < \text{E}_{\rm T} [\text{GeV}] < %.0f$' % ( etMin, etMax ) )
                                                    , ( 20,87,r'Signal selected events' )
                                                    ) for etMin, etMax in et_bins ] + 
                                                  [ ( ( 20,79,r'Full phase space' )
                                                    , ( 20,87,r'Signal selected events' )
                                                    )
                                                  , ( ( 20,79,r'Full phase space' )
                                                    , ( 20,87,r'Signal selected events' )
                                                    )
                                                  ]
                                        , nDivHeight = 3
                                        , nDivWidth = 4
                                        , fontsize = 1.2
                                        )
                  BeamerMultiFigureSlide( title = title + ' | Background Performances'
                                        , paths = [ os.path.join( args.bkgBaseFolder, base, base + '_ET_%d.pdf' % i ) for i in range(3,13) ] +
                                                  [ os.path.join( args.bkgBaseFolder, base, base + '_eta.pdf' ) 
                                                  , os.path.join( args.bkgBaseFolder, base, base + '_ET.pdf' )
                                                  ]
                                        , texts = [ ( ( 20,79,r'$%.0f < \text{E}_{\rm T} [\text{GeV}] < %.0f$' % ( etMin, etMax ) )
                                                    , ( 20,87,r'Background selected events' )
                                                    ) for etMin, etMax in et_bins ] + 
                                                  [ ( ( 20,79,r'Full phase space' )
                                                    , ( 20,87,r'Background selected events' )
                                                    )
                                                  , ( ( 20,79,r'Full phase space' )
                                                    , ( 20,87,r'Background selected events' )
                                                    )
                                                  ]
                                        , nDivHeight = 3
                                        , nDivWidth = 4
                                        , fontsize = 1.2
                                        )
                # End of BeamerSubSubSection context
              # end of trackCut
              title = escape_latex( 'Ringer {f_version} and {s_version} comparison operating at {ringer_requirement}_{ringer_ref}'.format(
                                                              f_version = f_version
                                                            , s_version = s_version
                                                            , ringer_requirement = req
                                                            , ringer_ref = ringer_ref
                                                            )
                                  )

              with BeamerSubSubSection( name = escape_latex( ringer_ref + " All Track CutID Cases" ) ):
                BeamerMultiFigureSlide( title = title + ' | All CutBased Operation Cases'
                    , paths = [ os.path.join( baseFolder, baseRingerCmpName % update( d, trackCut = trackCut )
                                                        , ( baseRingerCmpName % d ) + ( '_%s.pdf' % var ) )
                              for var in ['ET', 'eta', 'mu']
                              for baseFolder in [args.sgnBaseFolder, args.bkgBaseFolder]
                              for trackCut in ['', 'L', 'M', 'T'] 
                              ]
                    , texts = [ [ (100, 110, latex_code[var]), 
                                  (10, 100, r'\fontsize{0}{2}{' + dataset_name + '}'),
                                  (-10, 10, r'\rotatebox{90}{' + track_operation[track_version] + '}') ] 
                                    if track_version is '' and baseFolder == args.sgnBaseFolder and var == 'ET' else 
                                [ (100, 110, latex_code[var]), 
                                  (10, 100, r'\fontsize{0}{2}{' + dataset_name + '}') ] 
                                    if track_version is '' and baseFolder == args.sgnBaseFolder else 
                                [ (10, 100, r'\fontsize{0}{2}{' + dataset_name + '}') ] if track_version is '' else 
                                [ (-12, 10, r'\rotatebox{90}{' + track_operation[track_version] + '}') if var == "ET" and dataset == args.sgnPattern else None ]
                              for var in ['ET', 'eta', 'mu']
                              for dataset, baseFolder, dataset_name in zip([args.sgnPattern, args.bkgPattern], 
                                                                           [args.sgnBaseFolder, args.bkgBaseFolder],
                                                                           ["  Signal Selected Events", "Background Selected Events"])
                              for track_version in ['', 'L', 'M', 'T']
                              ]
                    , nDivHeight = 4
                    , nDivWidth = 6
                    , fontsize = 4
                    , fortran = True
                    , verticalStartAt = .05
                    )
              # End of All Track Cases subsubsection
              f_searchFolder_ringer_ref = ringer_ref
              if "v3" in f_version and ringer_ref == "MaxSP":
                f_searchFolder_ringer_ref = "SP"
              s_searchFolder_ringer_ref = ringer_ref
              if "v3" in s_version and ringer_ref == "MaxSP":
                s_searchFolder_ringer_ref = "SP"
              f_specialBaseRingerNN = baseRingerNN
              if ringer_ref == "MaxSP" and not "v3" in f_version:
                f_specialBaseRingerNN = f_specialBaseRingerNN.replace( "_LH", "", 1 )
              s_specialBaseRingerNN = baseRingerNN
              if ringer_ref == "MaxSP" and not "v3" in s_version:
                s_specialBaseRingerNN = s_specialBaseRingerNN.replace( "_LH", "", 1 )
              baseline_req = req
              if req == "Loose":
                baseline_req = "LooseAndBLayer"
              fd = { 'req' : baseline_req
                   , 'ringer_req' : req
                   , 'trackCut' : ''
                   , 'ringer_ref' : f_searchFolder_ringer_ref
                   , 'r_version' : f_version
                   , 'ref' : "LH" }
              fd.update( { 'dataset' : args.sgnPattern } )
              baseSgnFst = baseName % fd
              baseSgnFstNN = f_specialBaseRingerNN % fd
              fd.update( { 'dataset' : args.bkgPattern } )
              baseBkgFst = baseName % fd
              baseBkgFstNN = f_specialBaseRingerNN % fd
              sd = { 'req' : baseline_req
                   , 'ringer_req' : req
                   , 'trackCut' : ''
                   , 'ringer_ref' : s_searchFolder_ringer_ref
                   , 'r_version' : s_version
                   , 'ref' : "LH" }
              sd.update( { 'dataset' : args.sgnPattern } )
              baseSgnSnd = baseName % sd
              baseSgnSndNN = s_specialBaseRingerNN % sd
              sd.update( { 'dataset' : args.bkgPattern } )
              baseBkgSnd = baseName % sd
              baseBkgSndNN = s_specialBaseRingerNN % sd
              with BeamerSubSubSection( name = escape_latex( ringer_ref + " NN Output comparison" ) ):
                BeamerMultiFigureSlide( title = title + ' |  NN Output x Transverse Energy'
                                      , paths = [ os.path.join( args.sgnBaseFolder, baseSgnFst, baseSgnFstNN + '2D.pdf' ) 
                                                , os.path.join( args.bkgBaseFolder, baseBkgFst, baseBkgFstNN + '2D.pdf' )
                                                , os.path.join( args.sgnBaseFolder, baseSgnSnd, baseSgnSndNN + '2D.pdf' ) 
                                                , os.path.join( args.bkgBaseFolder, baseBkgSnd, baseBkgSndNN + '2D.pdf' )
                                                ]
                                      , texts = [ ( ( 5,95,r'Signal events '+ ' - ' + escape_latex(f_version) ), )
                                                , ( ( 5,95,r'Background events' + ' - ' + escape_latex(f_version) ), )
                                                , ( ( 5,95,r'Signal events' + ' - ' + escape_latex(s_version) ), )
                                                , ( ( 5,95,r'Background events' + ' - ' + escape_latex(s_version) ), )
                                                ]
                                      , nDivHeight = 2
                                      , nDivWidth = 2
                                      , usedHeight = .7
                                      , fontsize = 6
                                      )
                for i in range(3,13):
                  etMin, etMax = et_bins[i - 3]
                  BeamerMultiFigureSlide( title = title + ' | NN Output Transverse Energy Projections Bin ' + str(i)
                                        , paths = [ os.path.join( args.sgnBaseFolder, baseSgnFst, baseSgnFstNN + '_ET_%d.pdf' % i )
                                                  , os.path.join( args.bkgBaseFolder, baseBkgFst, baseBkgFstNN + '_ET_%d.pdf' % i )
                                                  , os.path.join( args.sgnBaseFolder, baseSgnSnd, baseSgnSndNN + '_ET_%d.pdf' % i )
                                                  , os.path.join( args.bkgBaseFolder, baseBkgSnd, baseBkgSndNN + '_ET_%d.pdf' % i )
                                                  ]
                                        , texts =  [ ( (45,79,r'$%.0f < \text{E}_{\rm T} [\text{GeV}] < %.0f$' % ( etMin, etMax ) )
                                                     , (45,87,r'Signal selected events' ) 
                                                     , (48,95,r'\fontsize{6}{0}{\selectfont ' + escape_latex(f_version) + '}' ) 
                                                     )
                                                   , ( (48,79,r'$%.0f < \text{E}_{\rm T} [\text{GeV}] < %.0f$' % ( etMin, etMax ) )
                                                     , (48,87,r'Background selected events' ) 
                                                     , (48,95,r'\fontsize{6}{0}{\selectfont ' + escape_latex(f_version) + '}' ) 
                                                     )
                                                   , ( (42,79,r'$%.0f < \text{E}_{\rm T} [\text{GeV}] < %.0f$' % ( etMin, etMax ) )
                                                     , (45,87,r'Signal selected events' ) 
                                                     , (42,95,r'\fontsize{6}{0}{\selectfont ' + escape_latex(s_version) + '}' ) 
                                                     )
                                                   , ( (42,79,r'$%.0f < \text{E}_{\rm T} [\text{GeV}] < %.0f$' % ( etMin, etMax ) )
                                                     , (42,87,r'Background selected events' ) 
                                                     , (42,95,r'\fontsize{6}{0}{\selectfont ' + escape_latex(s_version) + '}' ) 
                                                     )
                                                   ]
                                        , nDivHeight = 2
                                        , nDivWidth = 2
                                        , fontsize = 2
                                        )
                # end of Et bins
              # end of BeamerSubSubSection context
            # end of BeamerSubSection context
          # end of ringer_ref
        # end of BeamerSection
      # end of req
    # end of beamer tex report context
  # end of r_comp

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, re, itertools, sys

from RingerCore import ( emptyArgumentsPrintHelp, ArgumentParser, getFiles, traverse
                       , BooleanStr )
from RingerCore.tex.TexAPI import *
from RingerCore.tex.BeamerAPI import *
from TuningTools.parsers import loggerParser

parentParser = ArgumentParser(add_help = False)
parentParser.add_argument_group( "" )
mainGroup = parentParser.add_argument_group( "Required arguments", "")
mainGroup.add_argument('-smc','--sgnBaseMCFolder',
    required = True, help = "The base folder containing signal folders created by runRinger_plot.sh using MC Truth event selection")
mainGroup.add_argument('-stp','--sgnBaseTAPFolder',
    required = True, help = "The base folder containing signal folders created by runRinger_plot.sh using TAP event selection")
mainGroup.add_argument('-scmp','--sgnEvtSelCompFolder', 
    required = True, help = "The base folder containing signal comparison folders created by runPlot_Truth_TAP_Comp.sh")
mainGroup.add_argument('-spmc','--sgnMCPattern', 
    required = True, help = "Base pattern used to flag the signal type when using MC Truth event selection")
mainGroup.add_argument('-sptp','--sgnTAPPattern', 
    required = True, help = "Base pattern used to flag the signal type when using TAP event selection")
mainGroup.add_argument('-b','--bkgBaseFolder',
    required = True, help = "The base folder containing background folders created by runRinger_plot.sh")
mainGroup.add_argument('-bp','--bkgPattern', 
    required = True, help = "Base pattern used to flag the background type")
mainGroup.add_argument('--doOverall', type=BooleanStr, default = True, help = "Whether to do overall performance comparison.")
mainGroup.add_argument('--doEtaPerformance', type=BooleanStr, default = True, help = "Whether to do eta performance comparison.")
mainGroup.add_argument('--doNNOutput', type=BooleanStr, default = True, help = "Whether to do NN output.")
mainGroup.add_argument('--doRingerComparison', type=BooleanStr, default = True, help = "Whether to compare ringer performances.")
mainGroup.add_argument('--doEventSelectionComparison', type=BooleanStr, default = True, help = "Whether to compare event-selection performances.")
mainGroup.add_argument('--doBaselineComparison', type=BooleanStr, default = True, help = "Whether to compare baseline performances.")
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

lh_req_v11 = { 'Tight':     'TightLLH_v11'
             , 'Medium':    'MediumLLH_v11'
             , 'Loose':     'LooseAndBLayerLLH_v11'
             , 'VeryLoose': 'VeryLooseLLH_v11' 
             }
lh_req_v11Calo = { 'Tight':     'TightLLHCalo_v11'
                 , 'Medium':    'MediumLLHCalo_v11'
                 , 'Loose':     'LooseLLHCalo_v11'
                 , 'VeryLoose': 'VeryLooseLLHCalo_v11' 
                 }
lh_req_v11_Smooth = { 'Tight':     'TightLLH_Smooth_v11'
                    , 'Medium':    'MediumLLH_Smooth_v11'
                    , 'Loose':     'LooseAndBLayerLLH_Smooth_v11'
                    , 'VeryLoose': 'VeryLooseLLH_Smooth_v11' 
                    }
lh_req_v11Calo_Smooth = { 'Tight':     'TightLLHCalo_Smooth_v11'
                        , 'Medium':    'MediumLLHCalo_Smooth_v11'
                        , 'Loose':     'LooseLLHCalo_Smooth_v11'
                        , 'VeryLoose': 'VeryLooseLLHCalo_Smooth_v11' 
                        }
lh_req_v8 = { 'Tight':      'TightLLHMC15_v8'
            , 'Medium':     'MediumLLHMC15_v8'
            , 'Loose':      'LooseLLHMC15_v8'
            , 'VeryLoose':  'VeryLooseLLHMC15_v8' 
            }
lh_req_v8Calo = { 'Tight':      'TightLLHMC15Calo_v8'
                , 'Medium':     'MediumLLHMC15Calo_v8'
                , 'Loose':      'LooseLLHMC15Calo_v8'
                , 'VeryLoose':  'VeryLooseLLHMC15Calo_v8' 
                }
lh_req_mc14_truth_calo = { 'Tight':      'TightLLHMC14Calo'
                         , 'Medium':     'MediumLLHMC14Calo'
                         , 'Loose':      'LooseLLHMC14Calo'
                         , 'VeryLoose':  'VeryLooseLLHMC14Calo' 
                         }
cutid_2015 = { 'Tight' : 'TightIsEMMC15'
             , 'Medium' : 'MediumIsEMMC15'
             , 'Loose' : 'LooseIsEMMC15'
             , 'VeryLoose' : 'VeryLooseIsEMMC15'
             }
cutid_2015_Track = { 'Tight' : 'TightIsEMMC15_TrackOnly'
                   , 'Medium' : 'MediumIsEMMC15_TrackOnly'
                   , 'Loose' : 'LooseIsEMMC15_TrackOnly'
                   , 'VeryLoose' : 'VeryLooseIsEMMC15_TrackOnly'
                   }
refDict = { 'LH_MC15' : lh_req_v11
          , 'LH_MC15Calo' : lh_req_v11Calo
          , 'LH_MC15_Smooth' : lh_req_v11_Smooth
          , 'LH_MC15Calo_Smooth' : lh_req_v11Calo_Smooth
          , 'LH_MC15_50ns' : lh_req_v8
          , 'LH_MC15Calo_50ns' : lh_req_v8Calo
          , 'LH_MC14TruthCalo' : lh_req_mc14_truth_calo
          , 'CutID' : cutid_2015 
          , 'CutIDTrack' : cutid_2015_Track }

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

evtSelection_decode = { 'MCTruth' : r' MCTruth Event Selection'
                      , 'MCTap'   : r' Zee T&P Event Selection'
                      }
#evtSelection_decode = { 'MCTruth' : r' Sele\'{c}\~{a}o de Eventos atrav\'{e}s da Verdade de Monte Carlo'
#                      , 'MCTap'   : r' Sele\'{c}\~{a}o de Eventos com o m\'{e}todo Z$\rightarrow$ee T\&P'
#                      }

if args.doOverall:
  for r_version in [ "v3_unbinned", "v3_binned", "v1", "v2",]:
    for evtSelection in ['MCTruth', 'MCTap']:
      sgnPattern = args.sgnMCPattern if evtSelection == 'MCTruth' else args.sgnTAPPattern
      sgnBaseFolder = args.sgnBaseMCFolder if evtSelection == 'MCTruth' else args.sgnBaseTAPFolder
      if r_version in ['v1', 'v2'] and evtSelection == 'MCTap':
        continue
      with BeamerTexReportTemplate1( theme = 'Berlin'
                                   , _toPDF = args.pdf
                                   , title = ( 'Offline Ringer ' + r_version 
                                             + " Performance w.r.t. Baseline Electron ID Algorithms using " 
                                             + evtSelection_decode[evtSelection]
                                             + '.' )
                                   #, title = ( 'Performance do Offline Ringer ' + r_version 
                                   #          + r" em rela\'{c}\~{a}o aos Algoritmos de ID de El\'{e}trons usando " 
                                   #          + evtSelection_decode[evtSelection]
                                   #          + '.' )
                                   , outputFile = "OfflineRinger_" + r_version + "_performance_" + evtSelection
                                   , font = 'structurebold'):
        for ref in [  "CutID", "CutIDTrack", "LH_MC15", "LH_MC15Calo", "LH_MC15_Smooth"
                   , "LH_MC15Calo_Smooth", "LH_MC15_50ns", "LH_MC15Calo_50ns"
                   , "LH_MC14TruthCalo" ]:
          if evtSelection == 'MCTap' and ref == "LH_MC15Calo_Smooth": continue
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
                      if ref in ("LH_MC15_Smooth",) and req == "Loose":
                        baseline_req = "LooseAndBLayer"
                      d = { 'req' : baseline_req
                          , 'trackCut' : trackCut
                          , 'ringer_ref' : searchFolder_ringer_ref
                          , 'r_version' : r_version
                          , 'ref' : ref }
                      d.update( { 'dataset' : sgnPattern } )
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
                                                      for baseFolder, basePath in zip([sgnBaseFolder, args.bkgBaseFolder], [baseSgn, baseBkg])
                                                      ]
                                            , nDivHeight = 2
                                            , nDivWidth = 3
                                            , fortran = True
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
                                  for dataset, baseFolder in zip([sgnPattern, args.bkgPattern], [sgnBaseFolder, args.bkgBaseFolder] )
                                  for trackCut in ['', 'L', 'M', 'T'] 
                                  ]
                        , texts = [ [ (100, 110, latex_code[var]), 
                                      (30, 100, r'\fontsize{0}{2}{' + dataset_name + '}'),
                                      (-10, 10, r'\rotatebox{90}{' + track_operation[track_version] + '}') ] 
                                        if track_version is '' and baseFolder == sgnBaseFolder and var == 'ET' else 
                                    [ (100, 110, latex_code[var]), 
                                      (30, 100, r'\fontsize{0}{2}{' + dataset_name + '}') ] 
                                        if track_version is '' and baseFolder == sgnBaseFolder else 
                                    [ (30, 100, r'\fontsize{0}{2}{' + dataset_name + '}') ] if track_version is '' else 
                                    [ (-12, 10, r'\rotatebox{90}{' + track_operation[track_version] + '}') if var == "ET" and dataset == sgnPattern else None ]
                                  for var in ['ET', 'eta', 'mu']
                                  for dataset, baseFolder, dataset_name in zip([sgnPattern, args.bkgPattern], 
                                                                               [sgnBaseFolder, args.bkgBaseFolder],
                                                                               [r"Sinal", r"Ru\'ido"])
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
  for r_version in ["v3_unbinned", "v3_binned", "v1", "v2",]:
    for evtSelection in ['MCTruth', 'MCTap']:
      sgnPattern = args.sgnMCPattern if evtSelection == 'MCTruth' else args.sgnTAPPattern
      sgnBaseFolder = args.sgnBaseMCFolder if evtSelection == 'MCTruth' else args.sgnBaseTAPFolder
      if r_version in ['v1', 'v2'] and evtSelection == 'MCTap':
        continue
      with BeamerTexReportTemplate1( theme = 'Berlin'
                                   , _toPDF = args.pdf
                                   , title = ( 'Offline Ringer ' + r_version 
                                             + " Eta Detailed Performances w.r.t. Electron ID Algorithms using"
                                             + evtSelection_decode[evtSelection]
                                             + '.'
                                             )
                                   , outputFile = "OfflineRinger_" + r_version + "_eta_projections_performance_" + evtSelection
                                   , font = 'structurebold' ):
        for ref in [  "CutID", "CutIDTrack", "LH_MC15", "LH_MC15Calo", "LH_MC15_Smooth"
                   , "LH_MC15Calo_Smooth", "LH_MC15_50ns", "LH_MC15Calo_50ns"
                   , "LH_MC14TruthCalo" ]:
          if evtSelection == 'MCTap' and ref == "LH_MC15Calo_Smooth": continue
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
                      if ref in ("LH_MC15_Smooth",) and req == "Loose":
                        baseline_req = "LooseAndBLayer"
                      d = { 'req' : baseline_req
                          , 'trackCut' : trackCut
                          , 'ringer_ref' : searchFolder_ringer_ref
                          , 'r_version' : r_version
                          , 'ref' : ref }
                      d.update( { 'dataset' : sgnPattern } )
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
                                                          [ ( os.path.join( sgnBaseFolder, baseSgn, baseSgn + '_ET_%d.pdf' % i )
                                                            , os.path.join( args.bkgBaseFolder, baseBkg, baseBkg + '_ET_%d.pdf' % i )
                                                            )
                                                          for i in range(0,10) ] + [
                                                            os.path.join( sgnBaseFolder, baseSgn, baseSgn + '_eta.pdf' )
                                                          , os.path.join( args.bkgBaseFolder, baseBkg, baseBkg + '_eta.pdf' )
                                                          , os.path.join( sgnBaseFolder, baseSgn, baseSgn + '_ET.pdf' )
                                                          , os.path.join( args.bkgBaseFolder, baseBkg, baseBkg + '_ET.pdf' )
                                                          ], simple_ret=True ) )
                                            , texts =  list( traverse (       
                                                  [ ( ( (20,79.5,r'$%.0f < \text{E}_{\rm T} [\text{GeV}] < %.0f$' % ( etMin, etMax ) )
                                                      , (20,85.2,r'Eventos selecionados como sinal' ) 
                                                      )
                                                    , ( (20,79.5,r'$%.0f < \text{E}_{\rm T} [\text{GeV}] < %.0f$' % ( etMin, etMax ) )
                                                      , (17,85.2,r'Eventos selecionados como ru\'ido' ) 
                                                      # \put(55,10){\includegraphics[scale=.07]% {golfer.ps}}
                                                      )
                                                    ) for etMin, etMax in et_bins
                                                 ] +
                                                 [ ( ( ( 20,79.5,r'Todo espa\c{c}o de fase avaliado' )
                                                       , 
                                                       ( 20,85.2,r'Eventos selecionados como sinal' )
                                                     )
                                                     ,
                                                     ( ( 20,79.5,r'Todo espa\c{c}o de fase avaliado' )
                                                       , 
                                                       ( 20,85.2,r'Eventos selecionados como ru\'ido' )
                                                     )
                                                   , ( ( 20,79.5,r'Todo espa\c{c}o de fase avaliado' )
                                                       , 
                                                       ( 20,85.2,r'Eventos selecionados como sinal' )
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
                                            , paths = [ os.path.join( sgnBaseFolder, baseSgn, baseSgn + '_ET_%d.pdf' % i  ) for i in range(0,10) ] +
                                                      [ os.path.join( sgnBaseFolder, baseSgn, baseSgn + '_eta.pdf' ) 
                                                      , os.path.join( sgnBaseFolder, baseSgn, baseSgn + '_ET.pdf' )
                                                      ]
                                            , texts = [ ( ( 20,79.5,r'$%.0f < \text{E}_{\rm T} [\text{GeV}] < %.0f$' % ( etMin, etMax ) )
                                                        , ( 20,85.2,r'Eventos selecionados como sinal' )
                                                        ) for etMin, etMax in et_bins ] + 
                                                      [ ( ( 20,79.5,r'Todo espa\c{c}o de fase avaliado' )
                                                        , ( 20,85.2,r'Eventos selecionados como sinal' )
                                                        )
                                                      , ( ( 20,79.5,r'Todo espa\c{c}o de fase avaliado' )
                                                        , ( 20,85.2,r'Eventos selecionados como sinal' )
                                                        )
                                                      ]
                                            , nDivHeight = 3
                                            , nDivWidth = 4
                                            , fontsize = 1.2
                                            )
                      BeamerMultiFigureSlide( title = title + ' | Background Performances'
                                            , paths = [ os.path.join( args.bkgBaseFolder, baseBkg, baseBkg + '_ET_%d.pdf' % i ) for i in range(0,10) ] +
                                                      [ os.path.join( args.bkgBaseFolder, baseBkg, baseBkg + '_eta.pdf' ) 
                                                      , os.path.join( args.bkgBaseFolder, baseBkg, baseBkg + '_ET.pdf' )
                                                      ]
                                            , texts = [ ( ( 20,79.5,r'$%.0f < \text{E}_{\rm T} [\text{GeV}] < %.0f$' % ( etMin, etMax ) )
                                                        , ( 20,85.2,r'Eventos selecionados como ru\'ido' )
                                                        ) for etMin, etMax in et_bins ] + 
                                                      [ ( ( 20,79.5,r'Todo espa\c{c}o de fase avaliado' )
                                                        , ( 20,85.2,r'Eventos selecionados como ru\'ido' )
                                                        )
                                                      , ( ( 20,79.5,r'Todo espa\c{c}o de fase avaliado' )
                                                        , ( 20,85.2,r'Eventos selecionados como ru\'ido' )
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
    # end of event selection
  # end of r_version

if args.doNNOutput:
  for r_version in ["v3_unbinned", "v3_binned", "v1", "v2",]:
    sgnPattern = args.sgnMCPattern
    sgnBaseFolder = args.sgnBaseMCFolder
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
              #if req == "Loose":
              #  baseline_req = "LooseAndBLayer"
              d = { 'req' : baseline_req
                  , 'ringer_req' : req
                  , 'trackCut' : ''
                  , 'ringer_ref' : searchFolder_ringer_ref
                  , 'r_version' : r_version
                  , 'ref' : "LH_MC14TruthCalo" }
              d.update( { 'dataset' : sgnPattern } )
              baseSgn = baseName % d
              baseSgnNN = specialBaseRingerNN % d
              d.update( { 'dataset' : args.bkgPattern } )
              baseBkg = baseName % d
              baseBkgNN = specialBaseRingerNN % d
              title = escape_latex( 'Ringer{ringer_requirement}{ringer_ref}_{r_version}'.format(
                                                              r_version = r_version
                                                            , ringer_requirement = req
                                                            , ringer_ref = ringer_ref
                                                            , reference = refDict["LH_MC14TruthCalo"][req]
                                                            )
                                 )
              BeamerMultiFigureSlide( title = title + ' | NN Output Transverse Energy Projections'
                                    , paths = list(
                                                traverse(
                                                  [ ( os.path.join( sgnBaseFolder, baseSgn, baseSgnNN + '_ET_%d.pdf' % i )
                                                    , os.path.join( args.bkgBaseFolder, baseBkg, baseBkgNN + '_ET_%d.pdf' % i )
                                                    )
                                                  for i in range(0,10) ] + [
                                                    os.path.join( sgnBaseFolder, baseSgn, baseSgn + '_ET.pdf' )
                                                  , os.path.join( args.bkgBaseFolder, baseBkg, baseBkg + '_ET.pdf' )
                                                  ], simple_ret=True ) )
                                    , texts =  list( traverse (       
                                          [ ( ( (20,79.5,r'$%.0f < \text{E}_{\rm T} [\text{GeV}] < %.0f$' % ( etMin, etMax ) )
                                              , (20,85.2,r'Eventos selecionados como sinal' ) 
                                              )
                                            , ( (20,79.5,r'$%.0f < \text{E}_{\rm T} [\text{GeV}] < %.0f$' % ( etMin, etMax ) )
                                              , (20,85.2,r'Eventos selecionados como ru\'ido' ) 
                                              # \put(55,10){\includegraphics[scale=.07]% {golfer.ps}}
                                              )
                                            ) for etMin, etMax in et_bins
                                         ] +
                                         [ ( ( ( 20,79.5,r'Todo espa\c{c}o de fase avaliado' )
                                               , 
                                               ( 20,85.2,r'Eventos selecionados como sinal' )
                                             )
                                             ,
                                             ( ( 20,79.5,r'Todo espa\c{c}o de fase avaliado' )
                                               , 
                                               ( 20,85.2,r'Eventos selecionados como ru\'ido' )
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
                                    , paths = [ os.path.join( sgnBaseFolder, baseSgn, baseSgnNN + '2D.pdf' ) 
                                              , os.path.join( args.bkgBaseFolder, baseBkg, baseBkgNN + '2D.pdf' )
                                              ]
                                    , texts = [ ( ( 10,100,r'Eventos selecionados como sinal' ), )
                                              , ( ( 10,100,r'Eventos selecionados como ru\'ido' ), )
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
  for r_comp in ["v3_binned_vs_v3_unbinned", "v1_vs_v3_unbinned", "v2_vs_v3_binned", ]:
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
                for evtSelection in ['MCTruth', 'MCTap']:
                  sgnPattern = args.sgnMCPattern if evtSelection == 'MCTruth' else args.sgnTAPPattern
                  sgnBaseFolder = args.sgnBaseMCFolder if evtSelection == 'MCTruth' else args.sgnBaseTAPFolder
                  if ( 'v1' in r_comp or 'v2' in r_comp) and evtSelection == 'MCTap':
                    continue
                  with BeamerSubSubSection( name = escape_latex( ringer_ref + ringer_cutbased_decode[trackCut] + " using " + evtSelection_decode[evtSelection]) ):
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
                                          , paths = [ os.path.join( sgnBaseFolder, base, base + '_ET.pdf'  )
                                                    , os.path.join( sgnBaseFolder, base, base + '_eta.pdf' )
                                                    , os.path.join( sgnBaseFolder, base, base + '_mu.pdf'  )
                                                    , os.path.join( args.bkgBaseFolder, base, base + '_ET.pdf'  )
                                                    , os.path.join( args.bkgBaseFolder, base, base + '_eta.pdf' )
                                                    , os.path.join( args.bkgBaseFolder, base, base + '_mu.pdf'  )
                                                    ]
                                          , nDivHeight = 2
                                          , nDivWidth = 3
                                          )
                    BeamerMultiFigureSlide( title = title + ' | Signal/Background Detailed Eta Performances'
                                          , paths = list(
                                                      traverse(
                                                        [ ( os.path.join( sgnBaseFolder, base, base + '_ET_%d.pdf' % i )
                                                          , os.path.join( args.bkgBaseFolder, base, base + '_ET_%d.pdf' % i )
                                                          )
                                                        for i in range(0,10) ] + [
                                                          os.path.join( sgnBaseFolder, base, base + '_eta.pdf' )
                                                        , os.path.join( args.bkgBaseFolder, base, base + '_eta.pdf' )
                                                        , os.path.join( sgnBaseFolder, base, base + '_ET.pdf' )
                                                        , os.path.join( args.bkgBaseFolder, base, base + '_ET.pdf' )
                                                        ], simple_ret=True ) )
                                          , texts =  list( traverse (       
                                                [ ( ( (20,79.5,r'$%.0f < \text{E}_{\rm T} [\text{GeV}] < %.0f$' % ( etMin, etMax ) )
                                                    , (20,85.2,r'Eventos selecionados como sinal' ) 
                                                    )
                                                  , ( (20,79.5,r'$%.0f < \text{E}_{\rm T} [\text{GeV}] < %.0f$' % ( etMin, etMax ) )
                                                    , (20,85.2,r'Eventos selecionados como ru\'ido' ) 
                                                    )
                                                  ) for etMin, etMax in et_bins
                                               ] +
                                               [ ( ( ( 20,79.5,r'Todo espa\c{c}o de fase avaliado' )
                                                     , 
                                                     ( 20,85.2,r'Eventos selecionados como sinal' )
                                                   )
                                                   ,
                                                   ( ( 20,79.5,r'Todo espa\c{c}o de fase avaliado' )
                                                     , 
                                                     ( 20,85.2,r'Eventos selecionados como ru\'ido' )
                                                   )
                                                 , ( ( 20,79.5,r'Todo espa\c{c}o de fase avaliado' )
                                                     , 
                                                     ( 20,85.2,r'Eventos selecionados como sinal' )
                                                   )
                                                   ,
                                                   ( ( 20,79.5,r'Todo espa\c{c}o de fase avaliado' )
                                                     , 
                                                     ( 20,85.2,r'Eventos selecionados como ru\'ido' )
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
                                          , paths = [ os.path.join( sgnBaseFolder, base, base + '_ET_%d.pdf' % i  ) for i in range(0,10) ] +
                                                    [ os.path.join( sgnBaseFolder, base, base + '_eta.pdf' ) 
                                                    , os.path.join( sgnBaseFolder, base, base + '_ET.pdf' )
                                                    ]
                                          , texts = [ ( ( 20,79.5,r'$%.0f < \text{E}_{\rm T} [\text{GeV}] < %.0f$' % ( etMin, etMax ) )
                                                      , ( 20,85.2,r'Eventos selecionados como sinal' )
                                                      ) for etMin, etMax in et_bins ] + 
                                                    [ ( ( 20,79.5,r'Todo espa\c{c}o de fase avaliado' )
                                                      , ( 20,85.2,r'Eventos selecionados como sinal' )
                                                      )
                                                    , ( ( 20,79.5,r'Todo espa\c{c}o de fase avaliado' )
                                                      , ( 20,85.2,r'Eventos selecionados como sinal' )
                                                      )
                                                    ]
                                          , nDivHeight = 3
                                          , nDivWidth = 4
                                          , fontsize = 1.2
                                          )
                    BeamerMultiFigureSlide( title = title + ' | Background Performances'
                                          , paths = [ os.path.join( args.bkgBaseFolder, base, base + '_ET_%d.pdf' % i ) for i in range(0,10) ] +
                                                    [ os.path.join( args.bkgBaseFolder, base, base + '_eta.pdf' ) 
                                                    , os.path.join( args.bkgBaseFolder, base, base + '_ET.pdf' )
                                                    ]
                                          , texts = [ ( ( 20,79.5,r'$%.0f < \text{E}_{\rm T} [\text{GeV}] < %.0f$' % ( etMin, etMax ) )
                                                      , ( 20,85.2,r'Eventos selecionados como ru\'ido' )
                                                      ) for etMin, etMax in et_bins ] + 
                                                    [ ( ( 20,79.5,r'Todo espa\c{c}o de fase avaliado' )
                                                      , ( 20,85.2,r'Eventos selecionados como ru\'ido' )
                                                      )
                                                    , ( ( 20,79.5,r'Todo espa\c{c}o de fase avaliado' )
                                                      , ( 20,85.2,r'Eventos selecionados como ru\'ido' )
                                                      )
                                                    ]
                                          , nDivHeight = 3
                                          , nDivWidth = 4
                                          , fontsize = 1.2
                                          )
                  # End of BeamerSubSubSection context
                # end of evtSelection
              # end of trackCut
              title = escape_latex( 'Ringer {f_version} and {s_version} comparison operating at {ringer_requirement}_{ringer_ref}'.format(
                                                              f_version = f_version
                                                            , s_version = s_version
                                                            , ringer_requirement = req
                                                            , ringer_ref = ringer_ref
                                                            )
                                  )
              sgnPattern = args.sgnMCPattern
              sgnBaseFolder = args.sgnBaseMCFolder

              with BeamerSubSubSection( name = escape_latex( ringer_ref + " All Track CutID Cases" ) ):
                BeamerMultiFigureSlide( title = title + ' | All CutBased Operation Cases'
                    , paths = [ os.path.join( baseFolder, baseRingerCmpName % update( d, trackCut = trackCut )
                                                        , ( baseRingerCmpName % d ) + ( '_%s.pdf' % var ) )
                              for var in ['ET', 'eta', 'mu']
                              for baseFolder in [sgnBaseFolder, args.bkgBaseFolder]
                              for trackCut in ['', 'L', 'M', 'T'] 
                              ]
                    , texts = [ [ (100, 110, latex_code[var]), 
                                  (30, 100, r'\fontsize{0}{2}{' + dataset_name + '}'),
                                  (-10, 10, r'\rotatebox{90}{' + track_operation[track_version] + '}') ] 
                                    if track_version is '' and baseFolder == sgnBaseFolder and var == 'ET' else 
                                [ (100, 110, latex_code[var]), 
                                  (30, 100, r'\fontsize{0}{2}{' + dataset_name + '}') ] 
                                    if track_version is '' and baseFolder == sgnBaseFolder else 
                                [ (30, 100, r'\fontsize{0}{2}{' + dataset_name + '}') ] if track_version is '' else 
                                [ (-12, 10, r'\rotatebox{90}{' + track_operation[track_version] + '}') if var == "ET" and dataset == sgnPattern else None ]
                              for var in ['ET', 'eta', 'mu']
                              for dataset, baseFolder, dataset_name in zip([sgnPattern, args.bkgPattern], 
                                                                           [sgnBaseFolder, args.bkgBaseFolder],
                                                                           ["Sinal", r"Ru\'ido"])
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
              #if req == "Loose":
              #  baseline_req = "LooseAndBLayer"
              fd = { 'req' : baseline_req
                   , 'ringer_req' : req
                   , 'trackCut' : ''
                   , 'ringer_ref' : f_searchFolder_ringer_ref
                   , 'r_version' : f_version
                   , 'ref' : "LH_MC14TruthCalo" }
              fd.update( { 'dataset' : sgnPattern } )
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
                   , 'ref' : "LH_MC14TruthCalo" }
              sd.update( { 'dataset' : sgnPattern } )
              baseSgnSnd = baseName % sd
              baseSgnSndNN = s_specialBaseRingerNN % sd
              sd.update( { 'dataset' : args.bkgPattern } )
              baseBkgSnd = baseName % sd
              baseBkgSndNN = s_specialBaseRingerNN % sd
              with BeamerSubSubSection( name = escape_latex( ringer_ref + " NN Output comparison" ) ):
                BeamerMultiFigureSlide( title = title + ' |  NN Output x Transverse Energy'
                                      , paths = [ os.path.join( sgnBaseFolder, baseSgnFst, baseSgnFstNN + '2D.pdf' ) 
                                                , os.path.join( args.bkgBaseFolder, baseBkgFst, baseBkgFstNN + '2D.pdf' )
                                                , os.path.join( sgnBaseFolder, baseSgnSnd, baseSgnSndNN + '2D.pdf' ) 
                                                , os.path.join( args.bkgBaseFolder, baseBkgSnd, baseBkgSndNN + '2D.pdf' )
                                                ]
                                      , texts = [ ( ( 5,95,r'Sinal '+ ' - ' + escape_latex(f_version) ), )
                                                , ( ( 5,95,r'Ru\'ido' + ' - ' + escape_latex(f_version) ), )
                                                , ( ( 5,95,r'Sinal' + ' - ' + escape_latex(s_version) ), )
                                                , ( ( 5,95,r'Ru\'ido' + ' - ' + escape_latex(s_version) ), )
                                                ]
                                      , nDivHeight = 2
                                      , nDivWidth = 2
                                      , usedHeight = .7
                                      , fontsize = 6
                                      )
                for i in range(0,10):
                  etMin, etMax = et_bins[i]
                  BeamerMultiFigureSlide( title = title + ' | NN Output Transverse Energy Projections Bin ' + str(i)
                                        , paths = [ os.path.join( sgnBaseFolder, baseSgnFst, baseSgnFstNN + '_ET_%d.pdf' % i )
                                                  , os.path.join( args.bkgBaseFolder, baseBkgFst, baseBkgFstNN + '_ET_%d.pdf' % i )
                                                  , os.path.join( sgnBaseFolder, baseSgnSnd, baseSgnSndNN + '_ET_%d.pdf' % i )
                                                  , os.path.join( args.bkgBaseFolder, baseBkgSnd, baseBkgSndNN + '_ET_%d.pdf' % i )
                                                  ]
                                        , texts =  [ ( (45,79.5,r'$%.0f < \text{E}_{\rm T} [\text{GeV}] < %.0f$' % ( etMin, etMax ) )
                                                     , (45,85.2,r'Eventos selecionados como sinal' ) 
                                                     , (48,95,r'\fontsize{6}{0}{\selectfont ' + escape_latex(f_version) + '}' ) 
                                                     )
                                                   , ( (48,79.5,r'$%.0f < \text{E}_{\rm T} [\text{GeV}] < %.0f$' % ( etMin, etMax ) )
                                                     , (48,85.2,r'Eventos selecionados como ru\'ido' ) 
                                                     , (48,95,r'\fontsize{6}{0}{\selectfont ' + escape_latex(f_version) + '}' ) 
                                                     )
                                                   , ( (42,79.5,r'$%.0f < \text{E}_{\rm T} [\text{GeV}] < %.0f$' % ( etMin, etMax ) )
                                                     , (45,85.2,r'Eventos selecionados como sinal' ) 
                                                     , (42,95,r'\fontsize{6}{0}{\selectfont ' + escape_latex(s_version) + '}' ) 
                                                     )
                                                   , ( (42,79.5,r'$%.0f < \text{E}_{\rm T} [\text{GeV}] < %.0f$' % ( etMin, etMax ) )
                                                     , (42,85.2,r'Eventos selecionados como ru\'ido' ) 
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

array=("CutID",            "CutIDTrack",
       "LH_MC15_Smooth",   "LH_MC15",
       "LH_MC15",          "LH_MC15Calo",
       "LH_MC15",          "LH_MC15_uncorr",
       "LH_MC15_50ns",     "LH_MC15Calo_50ns",
       "LH_MC15_50ns",     "LH_MC14TruthCalo",
       "LH_MC15_50ns",     "LH_MC15Calo",
       "LH_MC15_50ns",     "LH_MC15",
       "LH_MC15Calo_50ns", "LH_MC14TruthCalo",
       "LH_MC15Calo_50ns", "LH_MC15Calo")

# comp_LooseAndBLayer_LH_MC15_Smooth_LooseAndBLayer_LH_MC15_Smooth_uncorr
# comp_LooseAndBLayer_LH_MC15_Smooth_Loose_LH_MC15
baseName = 'comp_%(f_req)s_%(f_version)s_%(s_req)s_%(s_version)s'
if args.doBaselineComparison:
  with BeamerTexReportTemplate1( theme = 'Berlin'
                               , _toPDF = args.pdf
                               , title = 'Comparison of ATLAS Collaboration Standard Electron ID methods'
                               , outputFile = "ATLAS_ElectronID_comparison"
                               , font = 'structurebold' ):
    for f_version, s_version in zip(array[slice(0,None,2)], array[slice(1,None,2)]): # this can be improved using itertools pick 0 and pick 1
      with BeamerSection( name = escape_latex( f_version + " w.r.t. " + s_version ) ):
        for req in ["Loose", "Medium", "Tight"]: # VeryLoose
          f_reference = refDict[f_version.replace('_uncorr','')][req]
          s_reference = refDict[s_version.replace('_uncorr','')][req]
          f_req = req
          if f_version in ("LH_MC15_Smooth",) and f_req == "Loose":
            f_req = "LooseAndBLayer"
          s_req = req
          if s_version in ("LH_MC15_Smooth",) and s_req == "Loose":
            s_req = "LooseAndBLayer"
          with BeamerSubSection( name = req ):
            for evtSelection in ['MCTruth', 'MCTap']:
              if evtSelection == 'MCTap' and f_version == "LH_MC15Calo_Smooth": continue
              if evtSelection == 'MCTap' and s_version == "LH_MC15Calo_Smooth": continue
              sgnPattern = args.sgnMCPattern if evtSelection == 'MCTruth' else args.sgnTAPPattern
              sgnBaseFolder = args.sgnBaseMCFolder if evtSelection == 'MCTruth' else args.sgnBaseTAPFolder
              with BeamerSubSubSection( name = escape_latex( f_reference + ' w.r.t. ' + s_reference + ' using ' + evtSelection_decode[evtSelection] ) ):
                d = { 'f_req' : f_req
                    , 'f_version' : f_version
                    , 's_req' : s_req
                    , 's_version' : s_version }
                basePath = baseName % d
                title = escape_latex( f_reference + ' w.r.t. ' + s_reference + ' using ' + evtSelection_decode[evtSelection] )

                # Summary Slide
                BeamerMultiFigureSlide( title = title + ' | Overall performance'
                                      , paths = [ os.path.join( baseFolder, basePath, basePath + '_%s.pdf' % var  )
                                                for var in ['ET', 'eta', 'mu']
                                                for baseFolder in [sgnBaseFolder, args.bkgBaseFolder]
                                                ]
                                      , nDivHeight = 2
                                      , nDivWidth = 3
                                      , fortran = True
                                      )

                BeamerMultiFigureSlide( title = title + ' | Signal/Background Detailed Eta Performances'
                                      , paths = list(
                                                  traverse(
                                                    [ ( os.path.join( sgnBaseFolder, basePath, basePath + '_ET_%d.pdf' % i )
                                                      , os.path.join( args.bkgBaseFolder, basePath, basePath + '_ET_%d.pdf' % i )
                                                      )
                                                    for i in range(0,10) ] + [
                                                      os.path.join( sgnBaseFolder, basePath, basePath + '_eta.pdf' )
                                                    , os.path.join( args.bkgBaseFolder, basePath, basePath + '_eta.pdf' )
                                                    , os.path.join( sgnBaseFolder, basePath, basePath + '_ET.pdf' )
                                                    , os.path.join( args.bkgBaseFolder, basePath, basePath + '_ET.pdf' )
                                                    ], simple_ret=True ) )
                                      , texts =  list( traverse (       
                                            [ ( ( (20,79.5,r'$%.0f < \text{E}_{\rm T} [\text{GeV}] < %.0f$' % ( etMin, etMax ) )
                                                , (20,85.2,r'Eventos selecionados como sinal' ) 
                                                )
                                              , ( (20,79.5,r'$%.0f < \text{E}_{\rm T} [\text{GeV}] < %.0f$' % ( etMin, etMax ) )
                                                , (17,85.2,r'Eventos selecionados como ru\'ido' ) 
                                                # \put(55,10){\includegraphics[scale=.07]% {golfer.ps}}
                                                )
                                              ) for etMin, etMax in et_bins
                                           ] +
                                           [ ( ( ( 20,79.5,r'Todo espa\c{c}o de fase avaliado' )
                                                 , 
                                                 ( 20,85.2,r'Eventos selecionados como sinal' )
                                               )
                                               ,
                                               ( ( 20,79.5,r'Todo espa\c{c}o de fase avaliado' )
                                                 , 
                                                 ( 20,85.2,r'Eventos selecionados como ru\'ido' )
                                               )
                                             , ( ( 20,79.5,r'Todo espa\c{c}o de fase avaliado' )
                                                 , 
                                                 ( 20,85.2,r'Eventos selecionados como sinal' )
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
                BeamerMultiFigureSlide( title = title + ' | Signal Detailed Eta Performances'
                                      , paths = [ os.path.join( sgnBaseFolder, basePath, basePath + '_ET_%d.pdf' % i  ) for i in range(0,10) ] +
                                                [ os.path.join( sgnBaseFolder, basePath, basePath + '_eta.pdf' ) 
                                                , os.path.join( sgnBaseFolder, basePath, basePath + '_ET.pdf' )
                                                ]
                                      , texts = [ ( ( 20,79.5,r'$%.0f < \text{E}_{\rm T} [\text{GeV}] < %.0f$' % ( etMin, etMax ) )
                                                  , ( 20,85.2,r'Eventos selecionados como sinal' )
                                                  ) for etMin, etMax in et_bins ] + 
                                                [ ( ( 20,79.5,r'Todo espa\c{c}o de fase avaliado' )
                                                  , ( 20,85.2,r'Eventos selecionados como sinal' )
                                                  )
                                                , ( ( 20,79.5,r'Todo espa\c{c}o de fase avaliado' )
                                                  , ( 20,85.2,r'Eventos selecionados como sinal' )
                                                  )
                                                ]
                                      , nDivHeight = 3
                                      , nDivWidth = 4
                                      , fontsize = 1.2
                                      )
                BeamerMultiFigureSlide( title = title + ' | Background Detailed Eta Performances'
                                      , paths = [ os.path.join( args.bkgBaseFolder, basePath, basePath + '_ET_%d.pdf' % i ) for i in range(0,10) ] +
                                                [ os.path.join( args.bkgBaseFolder, basePath, basePath + '_eta.pdf' ) 
                                                , os.path.join( args.bkgBaseFolder, basePath, basePath + '_ET.pdf' )
                                                ]
                                      , texts = [ ( ( 20,79.5,r'$%.0f < \text{E}_{\rm T} [\text{GeV}] < %.0f$' % ( etMin, etMax ) )
                                                  , ( 20,85.2,r'Eventos selecionados como ru\'ido' )
                                                  ) for etMin, etMax in et_bins ] + 
                                                [ ( ( 20,79.5,r'Todo espa\c{c}o de fase avaliado' )
                                                  , ( 20,85.2,r'Eventos selecionados como ru\'ido' )
                                                  )
                                                , ( ( 20,79.5,r'Todo espa\c{c}o de fase avaliado' )
                                                  , ( 20,85.2,r'Eventos selecionados como ru\'ido' )
                                                  )
                                                ]
                                      , nDivHeight = 3
                                      , nDivWidth = 4
                                      , fontsize = 1.2
                                      )
              # end of eta projections
            # end of evtSelection
          # end of req section
        # end of req loop
      # end of section
    # end of array loop
  # end of beamer file

array = ( "v3_binned"
        , "v3_unbinned"
        , "CutID"
        , "CutIDTrack" 
        #, "LH_MC15_Smooth" 
        , "LH_MC15" 
        , "LH_MC15Calo" 
        , "LH_MC15_50ns" 
        , "LH_MC15Calo_50ns" 
        , "LH_MC14TruthCalo" )

# Zee_MCTP_Comp_rNN_v3_binned_Loose_LH_Pd
# Zee_MCTP_Comp_MediumLH_MC14TruthCalo

baseRingerPath = 'Zee_MCTP_Comp_rNN_%(id_version)s_%(req)s%(trackCut)s_LH_%(ringer_ref)s'
baseStandardPath = 'Zee_MCTP_Comp_%(req)s%(id_version)s'
if args.doEventSelectionComparison:
  with BeamerTexReportTemplate1( theme = 'Berlin'
                               , _toPDF = args.pdf
                               , title = 'Comparison of Electron ID Performance over Different Event Selection Methods.'
                               , outputFile = "evt_selection_comparison"
                               , font = 'structurebold' ):
    for id_version in array:
      with BeamerSection( name = escape_latex( id_version ) ):
        for req in ["Loose", "Medium", "Tight"]: # VeryLoose
          with BeamerSubSection( name = req ):
            if 'v3' in id_version:
              for ringer_ref in ["Pd", "SP", "Pf"]:
                if ringer_ref == "SP" and req is not "Medium": continue
                with BeamerSubSubSection( name = ringer_ref ):
                  for trackCut in ["", "L", "M", "T"]:
                    basePath = baseRingerPath % { 'id_version' : id_version
                                                , 'req' : req
                                                , 'trackCut' : trackCut
                                                , 'ringer_ref' : ringer_ref
                                                }
                    title = escape_latex( 'Ringer{ringer_requirement}{ringer_ref}_{r_version}{track_version} Zee MC Event Selection Comparison'.format(
                                                                    r_version = id_version
                                                                  , ringer_requirement = req
                                                                  , ringer_ref = ringer_ref
                                                                  , track_version = ringer_cutbased_decode[trackCut]
                                                                  )
                                        )
                    BeamerMultiFigureSlide( title = title + ' | Overall Performances'
                                          , paths = [ os.path.join( args.sgnEvtSelCompFolder, basePath, basePath + '_%s.pdf' % var  )
                                                    for var in ['ET', 'eta', 'mu']
                                                    ]
                                          , nDivHeight = 1
                                          , nDivWidth = 3
                                          , usedHeight = .45
                                          , fortran = True
                                          )
                    BeamerMultiFigureSlide( title = title + ' | Eta Detailed Performances'
                                          , paths = [ os.path.join( args.sgnEvtSelCompFolder, basePath, basePath + '_ET_%d.pdf' % i  ) for i in range(0,10) ] +
                                                    [ os.path.join( args.sgnEvtSelCompFolder, basePath, basePath + '_eta.pdf' ) 
                                                    , os.path.join( args.sgnEvtSelCompFolder, basePath, basePath + '_ET.pdf' )
                                                    ]
                                        , texts = [ ( ( 20,79.5,r'$%.0f < \text{E}_{\rm T} [\text{GeV}] < %.0f$' % ( etMin, etMax ) ),
                                                    ) for etMin, etMax in et_bins ] + 
                                                  [ ( ( 20,79.5,r'Todo espa\c{c}o de fase avaliado' ),
                                                    )
                                                  , ( ( 20,79.5,r'Todo espa\c{c}o de fase avaliado' ),
                                                    )
                                                  ]
                                          , nDivHeight = 3
                                          , nDivWidth = 4
                                          , fontsize = 1.2
                                          )
                  # end of trackCut
                # end of BeamerSubSubSection context
              # end of ringer reference
            else:
              reference = refDict[id_version.replace('_uncorr','')][req]
              basePath = baseStandardPath % { 'id_version' : id_version
                                            , 'req' : req
                                            }
              title = escape_latex( reference + ' Zee MC Event Selection Comparison' )
              BeamerMultiFigureSlide( title = title + ' | Overall Performances'
                                    , paths = [ os.path.join( args.sgnEvtSelCompFolder, basePath, basePath + '_%s.pdf' % var  )
                                              for var in ['ET', 'eta', 'mu']
                                              ]
                                    , nDivHeight = 1
                                    , nDivWidth = 3
                                    , usedHeight = .45
                                    , fortran = True
                                    )
              BeamerMultiFigureSlide( title = title + ' | Eta Detailed Performances'
                                    , paths = [ os.path.join( args.sgnEvtSelCompFolder, basePath, basePath + '_ET_%d.pdf' % i  ) for i in range(0,10) ] +
                                              [ os.path.join( args.sgnEvtSelCompFolder, basePath, basePath + '_eta.pdf' ) 
                                              , os.path.join( args.sgnEvtSelCompFolder, basePath, basePath + '_ET.pdf' )
                                              ]
                                  , texts = [ ( ( 20,79.5,r'$%.0f < \text{E}_{\rm T} [\text{GeV}] < %.0f$' % ( etMin, etMax ) ),
                                              ) for etMin, etMax in et_bins ] + 
                                            [ ( ( 20,79.5,r'Todo espa\c{c}o de fase avaliado' ),
                                              )
                                            , ( ( 20,79.5,r'Todo espa\c{c}o de fase avaliado' ),
                                              )
                                            ]
                                    , nDivHeight = 3
                                    , nDivWidth = 4
                                    , fontsize = 1.2
                                    )
          # end of beamer subsection context
        # end of req loop
      # end of BeamerSection context
    # end of id_version loop
  # end of BeamerTexReport context

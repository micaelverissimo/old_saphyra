#!/usr/bin/env python

from RingerCore.Logger import LoggingLevel
from TuningTools.CrossValidStat import CrossValidStatAnalysis, GridJobFilter


basepath = 'files'

stat = CrossValidStatAnalysis( 
    basepath+'/tuned/',
    #binFilters = GridJobFilter,
    level = LoggingLevel.DEBUG,
    )

from TuningTools.CreateData import TuningDataArchieve
TDArchieve = TuningDataArchieve(basepath+'/data.pic.npz')

nEtBins = TDArchieve.nEtBins()
nEtaBins = TDArchieve.nEtaBins()
refBenchmarkList = []

from itertools import product
from TuningTools.TuningJob import ReferenceBenchmark
with TDArchieve as data:
  for etBin, etaBin in product( range( nEtBins if nEtBins is not None else 1 ),
                                range( nEtaBins if nEtaBins is not None else 1 )):
    benchmarks = (data['signal_efficiencies'], data['background_efficiencies'])
    #cross_benchmarks = (TDArchieve['signal_cross_efficiencies'], TDArchieve['background_cross_efficiencies'])
    sigEff = data['signal_efficiencies']['EFCaloAccept'][etBin][etaBin]
    bkgEff = data['background_efficiencies']['EFCaloAccept'][etBin][etaBin]
    try:
      sigCrossEff = data['signal_cross_efficiencies']['EFCaloAccept'][etBin][etaBin]
      bkgCrossEff = data['background_cross_efficiencies']['EFCaloAccept'][etBin][etaBin]
    except KeyError:
      sigCrossEff = None; bkgCrossEff = None
    args = (sigEff, bkgEff, sigCrossEff, bkgCrossEff)
    Medium_LH_EFCalo_Pd = ReferenceBenchmark( "Medium_LH_L2Calo_Pd", "Pd", *args )
    Medium_MaxSP        = ReferenceBenchmark( "Medium_MaxSP",        "SP", *args )
    Medium_LH_EFCalo_Pf = ReferenceBenchmark( "Medium_LH_L2Calo_Pf", "Pf", *args )
    references =  [ Medium_LH_EFCalo_Pd,
                    Medium_MaxSP,
                    Medium_LH_EFCalo_Pf ] 
    print ('Et:',etBin, 'eta:', etaBin), [ref.refVal for ref in references]
    refBenchmarkList.append( references )
del data

stat( refBenchmarkList , outputName = 'crossval' )

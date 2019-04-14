__all__ = [ 'FilterType',  'Reference', 'RingerOperation', 'Target',
    'BaseInfo','PileupReference', 'Dataset', 'Detector', 'Dataframe']

from Gaugi import EnumStringification

class Dataframe(EnumStringification):
  """
    Select the input data frame type.
    - PhysVal: TriggerEgammaTool
    - SkimmedNtuple: TagAndProbeFrame
    - MuonPhysVal: TriggerMuonFrame
  """
  PhysVal = 0
  SkimmedNtuple  = 1
  MuonPhysVal = 2
  PhysVal_v2 = 3
  SkimmedNtuple_v2  = 4

class RingerOperation(EnumStringification):
  """
    Select which framework ringer will operate
    - Positive values for Online operation; and
    - Negative values for Offline operation.
  """
  _ignoreCase = True
  Offline_LH_DataDriven2016_Rel20pt7_VeryLoose = -53
  Offline_LH_DataDriven2016_Rel20pt7_Loose     = -52
  Offline_LH_DataDriven2016_Rel20pt7_Medium    = -51
  Offline_LH_DataDriven2016_Rel20pt7_Tight     = -50
  Offline_LH_DataDriven2016_Rel21_VeryLoose    = -49
  Offline_LH_DataDriven2016_Rel21_Loose        = -48
  Offline_LH_DataDriven2016_Rel21_Medium       = -47
  Offline_LH_DataDriven2016_Rel21_Tight        = -46
  Offline                                      = -44
  Offline_LHCalo_MC14_Truth_VeryLoose          = -43
  Offline_LHCalo_MC14_Truth_Loose              = -42
  Offline_LHCalo_MC14_Truth_Medium             = -41
  Offline_LHCalo_MC14_Truth_Tight              = -40
  Offline_LHCalo_MC14_TaP_VeryLoose            = -39
  Offline_LHCalo_MC14_TaP_Loose                = -38
  Offline_LHCalo_MC14_TaP_Medium               = -37
  Offline_LHCalo_MC14_TaP_Tight                = -36
  Offline_LHCalo_v8_VeryLoose                  = -35
  Offline_LHCalo_v8_Loose                      = -34
  Offline_LHCalo_v8_Medium                     = -33
  Offline_LHCalo_v8_Tight                      = -32
  Offline_LH_v8_VeryLoose                      = -31
  Offline_LH_v8_Loose                          = -30
  Offline_LH_v8_Medium                         = -29
  Offline_LH_v8_Tight                          = -28
  Offline_LHCalo_v11_VeryLoose                 = -27
  Offline_LHCalo_v11_Loose                     = -26
  Offline_LHCalo_v11_Medium                    = -25
  Offline_LHCalo_v11_Tight                     = -24
  Offline_LH_v11_VeryLoose                     = -23
  Offline_LH_v11_Loose                         = -22
  Offline_LH_v11_Medium                        = -21
  Offline_LH_v11_Tight                         = -20
  Offline_LHCalo_v11_Smooth_Tight              = -19
  Offline_LHCalo_v11_Smooth_Medium             = -18
  Offline_LHCalo_v11_Smooth_Loose              = -17
  Offline_LHCalo_v11_Smooth_VeryLoose          = -16
  Offline_LH_v11_Smooth_Tight                  = -15
  Offline_LH_v11_Smooth_Medium                 = -14
  Offline_LH_v11_Smooth_Loose                  = -13
  Offline_LH_v11_Smooth_LooseAndBLayer         = -44
  Offline_LH_v11_Smooth_VeryLoose              = -12
  Offline_All                                  = -9
  Offline_CutBased_Tight                       = -8
  Offline_CutBased_Medium                      = -7
  Offline_CutBased_Loose                       = -6
  Offline_CutBased_VeryLoose                   = -11
  Offline_CutBased                             = -5
  Offline_LH_Tight                             = -4
  Offline_LH_Medium                            = -3
  Offline_LH_Loose                             = -2
  Offline_LH_VeryLoose                         = -10
  Offline_LH                                   = -1
  Offline                                      = -1
  L2                                           = 1
  EF                                           = 2
  L2Calo                                       = 3
  EFCalo                                       = 4
  HLT                                          = 5
  EFCalo_LH_Tight                              = 6
  EFCalo_LH_Medium                             = 7
  EFCalo_LH_Loose                              = 8
  EFCalo_LH_VLoose                             = 9
  HLT_LH_Tight                                 = 10
  HLT_LH_Medium                                = 11
  HLT_LH_Loose                                 = 12
  HLT_LH_VLoose                                = 13
  L2Calo_CutBased_Tight                        = 14
  L2Calo_CutBased_Medium                       = 15
  L2Calo_CutBased_Loose                        = 16
  L2Calo_CutBased_VLoose                       = 17
  Trigger                                      = 18

  @classmethod
  def branchName(cls, val):
    val = cls.retrieve( val )
    from TuningTools.coreDef import dataframeConf
    if dataframeConf.configured() or dataframeConf.can_autoconfigure():
      if not dataframeConf.configured() and dataframeConf.can_autoconfigure(): dataframeConf.auto()
      return cls.efficiencyBranches()[val]
    else:
      self._warning("Attempting to guess the branch name as dataframe is not configured.")
      branchDict = efficiencyBranches(cls, frameConf = Dataframe.PhysVal)
      if val in branchDict: return branchDict[val]
      branchDict = efficiencyBranches(cls, frameConf = Dataframe.SkimmedNtuple)
      if val in branchDict: return branchDict[val]
      self._fatal("Couldn't guess what is the branch name")

  @classmethod
  def efficiencyBranches(cls, frameConf = None):
    from TuningTools.coreDef import dataframeConf
    if frameConf is None: frameConf = dataframeConf()
    if frameConf is Dataframe.PhysVal:
      return { cls.L2Calo                      : 'L2CaloAccept'
             , cls.L2                          : 'L2ElAccept'
             , cls.EFCalo                      : 'EFCaloAccept'
             , cls.HLT                         : 'HLTAccept'
             , cls.Offline_LH_VeryLoose        : None
             , cls.Offline_LH_Loose            : 'LHLoose'
             , cls.Offline_LH_Medium           : 'LHMedium'
             , cls.Offline_LH_Tight            : 'LHTight'
             , cls.Offline_LH                  : ['LHLoose','LHMedium','LHTight']
             , cls.Offline_CutBased_Loose      : 'CutBasedLoose'
             , cls.Offline_CutBased_Medium     : 'CutBasedMedium'
             , cls.Offline_CutBased_Tight      : 'CutBasedTight'
             , cls.Offline_CutBased            : ['CutBasedLoose','CutBasedMedium','CutBasedTight'],

             }
    elif frameConf is Dataframe.PhysVal_v2:
      return { cls.L2Calo                      : 'L2CaloAccept'
             , cls.L2                          : 'L2ElAccept'
             , cls.EFCalo                      : 'EFCaloAccept'
             , cls.HLT                         : 'HLTAccept'
             , cls.EFCalo_LH_Tight             : 'EFCalo_LH_Tight'
             , cls.EFCalo_LH_Medium            : 'EFCalo_LH_Medium'
             , cls.EFCalo_LH_Loose             : 'EFCalo_LH_Loose'
             , cls.EFCalo_LH_VLoose            : 'EFCalo_LH_VLoose'
             , cls.HLT_LH_Tight                : 'HLT_LH_Tight'
             , cls.HLT_LH_Medium               : 'HLT_LH_Medium'
             , cls.HLT_LH_Loose                : 'HLT_LH_Loose'
             , cls.HLT_LH_VLoose               : 'HLT_LH_VLoose'
             , cls.Offline_LH_VeryLoose        : 'LHVLoose'
             , cls.Offline_LH_Loose            : 'LHLoose'
             , cls.Offline_LH_Medium           : 'LHMedium'
             , cls.Offline_LH_Tight            : 'LHTight'
             , cls.Offline_LH                  : ['LHLoose','LHMedium','LHTight']
             , cls.Offline_CutBased_Loose      : 'CutBasedLoose'
             , cls.Offline_CutBased_Medium     : 'CutBasedMedium'
             , cls.Offline_CutBased_Tight      : 'CutBasedTight'
             , cls.Offline_CutBased            : ['CutBasedLoose','CutBasedMedium','CutBasedTight']
             , cls.Trigger                     : 'Trigger'
             , cls.Offline                     : 'Offline'
             }

    elif frameConf is Dataframe.SkimmedNtuple:
      return { cls.L2Calo:                                     None
             , cls.L2:                                         None
             , cls.EFCalo:                                     None
             , cls.HLT:                                        None
             , cls.Offline_LH_DataDriven2016_Rel21_VeryLoose:    'elCand2_VeryLooseLLH_DataDriven_Rel21_Smooth_vTest'
             , cls.Offline_LH_DataDriven2016_Rel21_Loose:        'elCand2_LooseLLH_DataDriven_Rel21_Smooth_vTest'
             , cls.Offline_LH_DataDriven2016_Rel21_Medium:       'elCand2_MediumLLH_DataDriven_Rel21_Smooth_vTest'
             , cls.Offline_LH_DataDriven2016_Rel21_Tight:        'elCand2_TightLLH_DataDriven_Rel21_Smooth_vTest'
             , cls.Offline_LH_DataDriven2016_Rel20pt7_VeryLoose: 'elCand2_VeryLooseLLH_DataDriven_Rel20pt7_Smooth_vTest'
             , cls.Offline_LH_DataDriven2016_Rel20pt7_Loose:     'elCand2_LooseLLH_DataDriven_Rel20pt7_Smooth_vTest'
             , cls.Offline_LH_DataDriven2016_Rel20pt7_Medium:    'elCand2_MediumLLH_DataDriven_Rel20pt7_Smooth_vTest'
             , cls.Offline_LH_DataDriven2016_Rel20pt7_Tight:     'elCand2_TightLLH_DataDriven_Rel20pt7_Smooth_vTest'
             , cls.Offline_LH_v11_Smooth_VeryLoose:              'elCand2_isVeryLooseLLH_Smooth_v11'
             , cls.Offline_LH_v11_Smooth_Loose:                  'elCand2_isLooseLLH_Smooth_v11'
             , cls.Offline_LH_v11_Smooth_LooseAndBLayer:         'elCand2_isLooseAndBLayerLLH_Smooth_v11'
             , cls.Offline_LH_v11_Smooth_Medium:                 'elCand2_isMediumLLH_Smooth_v11'
             , cls.Offline_LH_v11_Smooth_Tight:                  'elCand2_isTightLLH_Smooth_v11'
             , cls.Offline_LHCalo_v11_Smooth_VeryLoose:          'elCand2_isVeryLooseLLHCalo_Smooth_v11'
             , cls.Offline_LHCalo_v11_Smooth_Loose:              'elCand2_isLooseLLHCalo_Smooth_v11'
             , cls.Offline_LHCalo_v11_Smooth_Medium:             'elCand2_isMediumLLHCalo_Smooth_v11'
             , cls.Offline_LHCalo_v11_Smooth_Tight:              'elCand2_isTightLLHCalo_Smooth_v11'
             , cls.Offline_LH_VeryLoose:                         'elCand2_isVeryLooseLL2016_v11'
             , cls.Offline_LH_Loose:                             'elCand2_isLooseAndBLayerLL2016_v11'
             #, cls.Offline_LH_LooseAndBLayer:                  'elCand2_isLooseAndBLayerLL2016_v11'
             , cls.Offline_LH_Medium:                            'elCand2_isMediumLL2016_v11'
             , cls.Offline_LH_Tight:                             'elCand2_isTightLL2016_v11'
             , cls.Offline_LH_v11_VeryLoose:                     'elCand2_isVeryLooseLLHCalo_v11'
             , cls.Offline_LH_v11_Loose:                         'elCand2_isLooseLLHCalo_v11'
             , cls.Offline_LH_v11_Medium:                        'elCand2_isMediumLLHCalo_v11'
             , cls.Offline_LH_v11_Tight:                         'elCand2_isTightLLHCalo_v11'
             , cls.Offline_LH_v8_VeryLoose:                      'elCand2_isVeryLooseLLHMC15_v8'
             , cls.Offline_LH_v8_Loose:                          'elCand2_isLooseLLHMC15_v8'
             , cls.Offline_LH_v8_Medium:                         'elCand2_isMediumLLHMC15_v8'
             , cls.Offline_LH_v8_Tight:                          'elCand2_isTightLLHMC15_v8'
             , cls.Offline_LHCalo_v8_VeryLoose:                  'elCand2_isVeryLooseLLHMC15Calo_v8'
             , cls.Offline_LHCalo_v8_Loose:                      'elCand2_isLooseLLHMC15Calo_v8'
             , cls.Offline_LHCalo_v8_Medium:                     'elCand2_isMediumLLHMC15Calo_v8'
             , cls.Offline_LHCalo_v8_Tight:                      'elCand2_isTightLLHMC15Calo_v8'
             , cls.Offline_LHCalo_MC14_TaP_VeryLoose:            'elCand2_isVeryLooseLLHCaloMC14'
             , cls.Offline_LHCalo_MC14_TaP_Loose:                'elCand2_isLooseLLHCaloMC14'
             , cls.Offline_LHCalo_MC14_TaP_Medium:               'elCand2_isMediumLLHCaloMC14'
             , cls.Offline_LHCalo_MC14_TaP_Tight:                'elCand2_isTightLLHCaloMC14'
             , cls.Offline_LHCalo_MC14_Truth_VeryLoose:          'elCand2_isVeryLooseLLHCaloMC14Truth'
             , cls.Offline_LHCalo_MC14_Truth_Loose:              'elCand2_isLooseLLHCaloMC14Truth'
             , cls.Offline_LHCalo_MC14_Truth_Medium:             'elCand2_isMediumLLHCaloMC14Truth'
             , cls.Offline_LHCalo_MC14_Truth_Tight:              'elCand2_isTightLLHCaloMC14Truth'
             , cls.Offline_LH:                                   ['elCand2_isVeryLooseLLH_Smooth_v11'
                                                                 ,'elCand2_isLooseLLH_Smooth_v11'
                                                                 ,'elCand2_isMediumLLH_Smooth_v11'
                                                                 ,'elCand2_isTightLLH_Smooth_v11']
             #, cls.Offline_CutBased_VeryLoose:                  'elCand2_isEMVeryLoose2015'
             , cls.Offline_CutBased_Loose:                       'elCand2_isEMLoose2015'
             , cls.Offline_CutBased_Medium:                      'elCand2_isEMMedium2015'
             , cls.Offline_CutBased_Tight:                       'elCand2_isEMTight2015'
             , cls.Offline_CutBased:                             [#'elCand2_isEMVeryLoose2015',
                                                                  'elCand2_isEMLoose2015'
                                                                 ,'elCand2_isEMMedium2015'
                                                                 ,'elCand2_isEMTight2015']
             }

class Reference(EnumStringification):
  """
    Reference for training algorithm
  """
  _ignoreCase = True

  Truth = -1
  AcceptAll = 0
  Off_CutID = 1
  Off_Likelihood = 2
  elCand2_trig_EF_VeryLooseLLH_z0offlineMatch_Smooth_Probe = 3
  elCand2_passTrackQuality = 4

class FilterType(EnumStringification):
  """
    Enumeration if selection event type w.r.t reference
  """
  _ignoreCase = True

  DoNotFilter = 0
  Background = 1
  Signal = 2

class Target(EnumStringification):
  """
    Holds the target value for the discrimination method
  """
  _ignoreCase = True

  Signal = 1
  Background = -1
  Unknown = -999

class Dataset(EnumStringification):
  """
  The possible datasets to use
  """
  _ignoreCase = True

  Unspecified = 0
  Train = 1
  Validation = 2
  Test = 3
  Operation = 4

class Detector(EnumStringification):
  """
  The ATLAS Detector systems.
  """
  Tracking = 1
  Calorimetry = 2
  MuonSpectometer = 3
  CaloAndTrack = 4
  All = 5

class BaseInfo( EnumStringification ):
  Et = 0
  Eta = 1
  PileUp = 2
  Phi = 3
  nInfo = 4 # This must always be the last base info

  def __init__(self, baseInfoBranches, dtypes):
    self._baseInfoBranches = baseInfoBranches
    self._dtypes = dtypes

  def retrieveBranch(self, idx):
    idx = self.retrieve(idx)
    return self._baseInfoBranches[idx]

  def dtype(self, idx):
    idx = self.retrieve(idx)
    return self._dtypes[idx]

  def __iter__(self):
    return self.loop()

  def loop(self):
    for baseEnum in range(BaseInfo.nInfo):
      yield baseEnum

class PileupReference(EnumStringification):
  """
    Reference branch type for luminosity
  """
  _ignoreCase = True

  avgmu = 0
  AverageLuminosity = 0
  nvtx = 1
  NumberOfVertices = 1

  @classmethod
  def label( cls, val ):
    val = cls.retrieve( val )
    if val is PileupReference.avgmu:
      return '#mu'
    elif val is PileupReference.nvtx:
      return 'Number of Primary Vertices'

  @classmethod
  def shortlabel( cls, val ):
    val = cls.retrieve( val )
    if val is PileupReference.avgmu:
      return '#mu'
    elif val is PileupReference.nvtx:
      return 'nvtx'






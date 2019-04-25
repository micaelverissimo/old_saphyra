__all__ = ['ReadData','readData']

from Gaugi import ( EnumStringification, Logger, LoggingLevel, traverse
                       , stdvector_to_list, checkForUnusedVars, expandFolders
                       , RawDictStreamer, RawDictStreamable, RawDictCnv, retrieve_kw
                       , csvStr2List, NotSet, progressbar )
from TuningTools.coreDef import npCurrent
from collections import OrderedDict
import numpy as np
from copy import deepcopy
from TuningTools.dataframe import *


class ReadData(Logger):
  """
    Retrieve from TTree the training information. Use readData object.
  """

  def __setBranchAddress( self, tree, varname, holder ):
    " Set tree branch varname to holder "
    if not tree.GetBranchStatus(varname):
      tree.SetBranchStatus( varname, True )
      from ROOT import AddressOf
      tree.SetBranchAddress( varname, AddressOf(holder, varname) )
      self._debug("Set %s branch address on %s", varname, tree )
    else:
      self._debug("Already set %s branch address on %s", varname, tree)


  def __retrieveBinIdx( self, bins, value ):
    return npCurrent.scounter_dtype.type(np.digitize(npCurrent.fp_array([value]), bins)[0]-1)

  def __init__( self, logger = None ):
    """
      Load TuningTools C++ library and set logger
    """
    # Retrieve python logger
    Logger.__init__( self, logger = logger)
    self._store = None


  def __call__( self, fList, ringerOperation, **kw):
    """
      Read ntuple and return patterns and efficiencies.
      Arguments:
        - fList: The file path or file list path. It can be an argument list of
        two types:
          o List: each element is a string path to the file;
          o Comma separated string: each path is separated via a comma
          o Folders: Expand folders recursively adding also files within them to analysis
        - ringerOperation: Set Operation type. It can be both a string or the
          RingerOperation
      Optional arguments:
        - filterType [None]: whether to filter. Use FilterType enumeration
        - reference [Truth]: set reference for targets. Use Reference enumeration
        - treePath [Set using operation]: set tree name on file, this may be set to
          use different sources then the default.
            Default for:
              o Offline: Offline/Egamma/Ntuple/electron
              o L2: Trigger/HLT/Egamma/TPNtuple/e24_medium_L1EM18VH
        - l1EmClusCut [None]: Set L1 cluster energy cut if operating on the trigger
        - l2EtCut [None]: Set L2 cluster energy cut value if operating on the trigger
        - offEtCut [None]: Set Offline cluster energy cut value
        - nClusters [None]: Read up to nClusters. Use None to run for all clusters.
        - getRatesOnly [False]: Read up to nClusters. Use None to run for all clusters.
        - etBins [None]: E_T bins (GeV) where the data should be segmented
        - etaBins [None]: eta bins where the data should be segmented
        - ringConfig [100]: A list containing the number of rings available in the data
          for each eta bin.
        - crossVal [None]: Whether to measure benchmark efficiency splitting it
          by the crossVal-validation datasets
        - extractDet [None]: Which detector to export (use Detector enumeration).
          Defaults are:
            o L2Calo: Calorimetry
            o L2: Tracking
            o Offline: Calorimetry
            o Others: CaloAndTrack
        - standardCaloVariables [False]: Whether to extract standard track variables.
        - useTRT [False]: Whether to export TRT information when dumping track
          variables.
        - supportTriggers [True]: Whether reading data comes from support triggers
    """

    __eventBranches = [ 'EventNumber',
                        'RunNumber',
                        'RandomRunNumber',
                        'MCChannelNumber',
                        'RandomLumiBlockNumber',
                        'MCPileupWeight',
                        'VertexZPosition',
                        'Zcand_M',
                        'Zcand_pt',
                        'Zcand_eta',
                        'Zcand_phi',
                        'Zcand_y',
                        'isTagTag']

    __trackBranches = [ '%s%d_deltaeta1',
                        '%s%d_DeltaPOverP',
                        '%s%d_deltaphiRescaled',
                        '%s%d_d0significance',
                        '%s%d_trackd0pvunbiased',
                        '%s%d_eProbabilityHT']

    __stdCaloBranches = [ '%s%d_eratio',
                          '%s%d_reta',
                          '%s%d_rphi',
                          '%s%d_rhad',
                          '%s%d_weta2',
                          '%s%d_f1',
                          '%s%d_f3']

    __monteCarloBranches = [
                        'type',
                        'origin',
                        'originbkg',
                        'typebkg',
                        'isTruthElectronFromZ',
                        'TruthParticlePdgId',
                        'firstEgMotherPdgId',
                        'TruthParticleBarcode',
                        'firstEgMotherBarcode',
                        'MotherPdgId',
                        'MotherBarcode',
                        'FirstEgMotherTyp',
                        'FirstEgMotherOrigin',
                        'dRPdgId',
                       ]

    __onlineBranches = ['fcCand%d_et',
                        'fcCand%d_eta',
                        'fcCand%d_phi',
                        'fcCand%d_ringerMatch']

    __ignoreEffValues = [
        'elCand2_isVeryLooseLLHCaloMC14Truth',
        'elCand2_isLooseLLHCaloMC14Truth',
        'elCand2_isMediumLLHCaloMC14Truth',
        'elCand2_isTightLLHCaloMC14Truth',
        'elCand2_isVeryLooseLLHCaloMC14',
        'elCand2_isLooseLLHCaloMC14',
        'elCand2_isMediumLLHCaloMC14',
        'elCand2_isTightLLHCaloMC14',
        'elCand2_isVeryLooseLLHMC15Calo_v8',
        'elCand2_isLooseLLHMC15Calo_v8',
        'elCand2_isMediumLLHMC15Calo_v8',
        'elCand2_isTightLLHMC15Calo_v8',
        'elCand2_isVeryLooseLLHMC15_v8',
        'elCand2_isLooseLLHMC15_v8',
        'elCand2_isMediumLLHMC15_v8',
        'elCand2_isTightLLHMC15_v8',
				'elCand2_isLooseLLHCalo_v11',
				'elCand2_isMediumLLHCalo_v11',
				'elCand2_isTightLLHCalo_v11',
        'elCand2_isVeryLooseLLHCalo_v11',
				'elCand2_isTightLLHCalo_Smooth_v11',
				'elCand2_isMediumLLHCalo_Smooth_v11',
				'elCand2_isLooseLLHCalo_Smooth_v11',
				'elCand2_isVeryLooseLLHCalo_Smooth_v11',
        ]

    offlineBranches = ['et', 'eta', 'phi']

    # The current pid map used as offline reference
    pidConfigs  = {key : value for key, value in RingerOperation.efficiencyBranches().iteritems() if key in (
          RingerOperation.Offline_LH_DataDriven2016_Rel21_VeryLoose
        , RingerOperation.Offline_LH_DataDriven2016_Rel21_Loose
        , RingerOperation.Offline_LH_DataDriven2016_Rel21_Medium
        , RingerOperation.Offline_LH_DataDriven2016_Rel21_Tight
        )         }

    # Retrieve information from keyword arguments
    filterType            = retrieve_kw(kw, 'filterType',            FilterType.DoNotFilter )
    reference             = retrieve_kw(kw, 'reference',             Reference.AcceptAll    )
    offEtCut              = retrieve_kw(kw, 'offEtCut',              None                   )
    l2EtCut               = retrieve_kw(kw, 'l2EtCut',               None                   )
    treePath              = retrieve_kw(kw, 'treePath',              'ZeeCandidate'         )
    nClusters             = retrieve_kw(kw, 'nClusters',             None                   )
    etBins                = retrieve_kw(kw, 'etBins',                None                   )
    etaBins               = retrieve_kw(kw, 'etaBins',               None                   )
    crossVal              = retrieve_kw(kw, 'crossVal',              None                   )
    ringConfig            = retrieve_kw(kw, 'ringConfig',            100                    )
    monitoring            = retrieve_kw(kw, 'monitoring',            None                   )
    pileupRef             = retrieve_kw(kw, 'pileupRef',             NotSet                 )
    getRates              = retrieve_kw(kw, 'getRates',              True                   )
    getRatesOnly          = retrieve_kw(kw, 'getRatesOnly',          False                  )
    getTagsOnly           = retrieve_kw(kw, 'getTagsOnly',           False                  )
    extractDet            = retrieve_kw(kw, 'extractDet',            None                   )
    standardCaloVariables = retrieve_kw(kw, 'standardCaloVariables', False                  )

    import ROOT, pkgutil
    #gROOT.ProcessLine (".x $ROOTCOREDIR/scripts/load_packages.C");
    #ROOT.gROOT.Macro('$ROOTCOREDIR/scripts/load_packages.C')
    if not( bool( pkgutil.find_loader( 'libTuningTools' ) ) and ROOT.gSystem.Load('libTuningTools') >= 0 ) and \
       not( bool( pkgutil.find_loader( 'libTuningToolsLib' ) ) and ROOT.gSystem.Load('libTuningToolsLib') >= 0 ):
      self._fatal("Could not load TuningTools library", ImportError)

    if 'level' in kw: self.level = kw.pop('level')
    # and delete it to avoid mistakes:
    checkForUnusedVars( kw, self._warning )
    del kw

    ### Parse arguments
    # Also parse operation, check if its type is string and if we can
    # transform it to the known operation enum:
    fList = csvStr2List ( fList )
    fList = expandFolders( fList )
    ringerOperation = RingerOperation.retrieve(ringerOperation)
    self._branchRef = 'elCand' if ringerOperation < 0 else 'fcCand'

    reference = Reference.retrieve(reference)

    self._info("Using reference %s for filtering events of type %s", Reference.tostring( reference )
              , FilterType.tostring( filterType ) )

    # Offline E_T cut
    if offEtCut:
      offEtCut = 1000.*offEtCut # Put energy in MeV
    if l2EtCut:
      l2EtCut = 1000.*l2EtCut # Put energy in MeV


    # Check whether using bins
    useBins=False; useEtBins=False; useEtaBins=False
    nEtaBins = 1; nEtBins = 1

    if etaBins is None: etaBins = npCurrent.fp_array([])
    if type(etaBins) is list: etaBins=npCurrent.fp_array(etaBins)
    if etBins is None: etBins = npCurrent.fp_array([])
    if type(etBins) is list: etBins=npCurrent.fp_array(etBins)

    if etBins.size:
      etBins = etBins * 1000. # Put energy in MeV
      nEtBins  = len(etBins)-1
      if nEtBins >= np.iinfo(npCurrent.scounter_dtype).max:
        self._fatal(('Number of et bins (%d) is larger or equal than maximum '
            'integer precision can hold (%d). Increase '
            'TuningTools.coreDef.npCurrent scounter_dtype number of bytes.'), nEtBins,
            np.iinfo(npCurrent.scounter_dtype).max)
      # Flag that we are separating data through bins
      useBins=True
      useEtBins=True
      self._debug('E_T bins enabled.')

    if not type(ringConfig) is list and not type(ringConfig) is np.ndarray:
      ringConfig = [ringConfig] * (len(etaBins) - 1) if etaBins.size else 1
    if type(ringConfig) is list: ringConfig=npCurrent.int_array(ringConfig)
    if not len(ringConfig):
      self._fatal('Rings size must be specified.');

    if etaBins.size:
      nEtaBins = len(etaBins)-1
      if nEtaBins >= np.iinfo(npCurrent.scounter_dtype).max:
        self._fatal(('Number of eta bins (%d) is larger or equal than maximum '
            'integer precision can hold (%d). Increase '
            'TuningTools.coreDef.npCurrent scounter_dtype number of bytes.'), nEtaBins,
            np.iinfo(npCurrent.scounter_dtype).max)
      if len(ringConfig) != nEtaBins:
        self._fatal(('The number of rings configurations (%r) must be equal than '
                            'eta bins (%r) region config'),ringConfig, etaBins)
      useBins=True
      useEtaBins=True
      self._debug('eta bins enabled.')
    else:
      self._debug('eta/et bins disabled.')

    # The base information holder, such as et, eta and pile-up
    if pileupRef is NotSet:
      if ringerOperation > 0:
        pileupRef = PileupReference.avgmu
      else:
        pileupRef = PileupReference.nvtx

    pileupRef = PileupReference.retrieve( pileupRef )
    self._info("Using '%s' as pile-up reference.", PileupReference.tostring( pileupRef ) )

    # Candidates: (1) is tags and (2) is probes. Default is probes
    self._candIdx = 1 if getTagsOnly else 2

    # Mutual exclusive arguments:
    if not getRates and getRatesOnly:
      self._logger.error("Cannot run with getRates set to False and getRatesOnly set to True. Setting getRates to True.")
      getRates = True


    ### Prepare to loop:
    t = ROOT.TChain(treePath)
    for inputFile in progressbar(fList, len(fList),
                                 logger = self._logger,
                                 prefix = "Creating collection tree "):
      # Check if file exists
      f  = ROOT.TFile.Open(inputFile, 'read')
      if not f or f.IsZombie():
        self._warning('Couldn''t open file: %s', inputFile)
        continue
      # Inform user whether TTree exists, and which options are available:
      self._debug("Adding file: %s", inputFile)
      obj = f.Get(treePath)
      if not obj:
        self._warning("Couldn't retrieve TTree (%s)!", treePath)
        self._info("File available info:")
        f.ReadAll()
        f.ReadKeys()
        f.ls()
        continue
      elif not isinstance(obj, ROOT.TTree):
        self._fatal("%s is not an instance of TTree!", treePath, ValueError)
      t.Add( inputFile )
    # Turn all branches off.
    t.SetBranchStatus("*", False)
    # RingerPhysVal hold the address of required branches
    event = ROOT.SkimmedNtuple()
    # Ready to retrieve the total number of events
    t.GetEntry(0)
    ## Allocating memory for the number of entries
    entries = t.GetEntries()
    nobs = entries if (nClusters is None or nClusters > entries or nClusters < 1) \
                                                                else nClusters
    ## Retrieve the dependent operation variables:
    if useEtBins:
      etBranch = ('%s%d_et')%(self._branchRef,self._candIdx)
      self.__setBranchAddress(t,etBranch,event)
      self._debug("Added branch: %s", etBranch)
      npEt    = npCurrent.scounter_zeros(shape=npCurrent.shape(npat = 1, nobs = nobs))
      self._debug("Allocated npEt    with size %r", npEt.shape)

    if useEtaBins:
      etaBranch = ('%s%d_eta')%(self._branchRef,self._candIdx)
      self.__setBranchAddress(t,etaBranch,event)
      self._debug("Added branch: %s", etaBranch)
      npEta    = npCurrent.scounter_zeros(shape=npCurrent.shape(npat = 1, nobs = nobs))
      self._debug("Allocated npEta   with size %r", npEta.shape)

    phiBranch = ('%s%d_phi')%(self._branchRef,self._candIdx)

    if reference is Reference.Truth:
      self.__setBranchAddress(t,('elCand%d_isTruthElectronFromZ') % (self._candIdx),event)

    for var in offlineBranches:
      self.__setBranchAddress(t,('elCand%d_%s')%(self._candIdx,var),event)

    if reference is Reference.elCand2_trig_EF_VeryLooseLLH_z0offlineMatch_Smooth_Probe:
      self.__setBranchAddress(t,"elCand2_trig_EF_VeryLooseLLH_z0offlineMatch_Smooth_Probe",event)
    elif reference is Reference.elCand2_passTrackQuality:
      self.__setBranchAddress(t,"elCand2_passTrackQuality",event)

    for var in pidConfigs.values():
      self.__setBranchAddress(t,var,event)

    self.__setBranchAddress(t,('%s%d_%s')%(self._branchRef,self._candIdx,'ringer_rings'),event)

    if extractDet in (Detector.Tracking,
                      Detector.CaloAndTrack,
                      Detector.All):
      for i, var in enumerate(__trackBranches):
        var = var % (self._branchRef,self._candIdx)
        __trackBranches[i] = var
        self.__setBranchAddress(t, var, event)

    if extractDet in (Detector.Calorimetry,
                      Detector.CaloAndTrack,
                      Detector.All):
      if standardCaloVariables:
        for i, var in enumerate(__stdCaloBranches):
          var = var % (self._branchRef,self._candIdx)
          __stdCaloBranches[i] = var
          self.__setBranchAddress(t, var, event)


    # Add online branches if using Trigger
    if ringerOperation > 0:
      for i, var in enumerate(__onlineBranches):
        var = var % self._candIdx
        __onlineBranches[i] = var
        self.__setBranchAddress(t, var, event)

    if pileupRef is PileupReference.nvtx:
      pileupBranch = 'Nvtx'
      pileupDataType = np.uint16
    elif pileupRef is PileupReference.avgmu:
      pileupBranch = 'averageIntPerXing'
      pileupDataType = np.float32
    else:
      raise NotImplementedError("Pile-up reference %r is not implemented." % pileupRef)

    #for var in __eventBranches +
    for var in [pileupBranch]:
      self.__setBranchAddress(t,var,event)

    ### Allocate memory
    npat=0
    if extractDet == (Detector.Calorimetry):
      if standardCaloVariables:
        npat = len(__stdCaloBranches)
      else:
        npat = ringConfig.max()
    elif extractDet == (Detector.Tracking):
      npat = len(__trackBranches)
    # NOTE: Check if pat is correct for both Calo and track data
    elif extractDet in (Detector.CaloAndTrack,
                        Detector.All):
      if standardCaloVariables:
        npat = len(__stdCaloBranches) + len(__trackBranches)
      else:
        npat = ringConfig.max() + len(__trackBranches)

    npPatterns = npCurrent.fp_zeros( shape=npCurrent.shape(npat=npat, #getattr(event, ringerBranch).size()
                                                 nobs=nobs)
                                   )
    self._debug("Allocated npPatterns with size %r", npPatterns.shape)

    baseInfoBranch = BaseInfo((etBranch, etaBranch, pileupBranch, phiBranch ),
                              (npCurrent.fp_dtype, npCurrent.fp_dtype, pileupDataType, npCurrent.fp_dtype) )

    baseInfo = [None, ] * baseInfoBranch.nInfo
    # Add E_T, eta and luminosity information
    npBaseInfo = [npCurrent.zeros( shape=npCurrent.shape(npat=1, nobs=nobs ), dtype=baseInfoBranch.dtype(idx) )
                                  for idx in baseInfoBranch]

    from TuningTools.CreateData import BranchEffCollector, BranchCrossEffCollector
    branchEffCollectors = OrderedDict()
    branchCrossEffCollectors = OrderedDict()

    if ringerOperation < 0:
      from operator import itemgetter
      benchmarkDict  = OrderedDict(sorted([(key, value)
                                           for key, value in RingerOperation.efficiencyBranches().iteritems()
                                           if key < 0 and not(isinstance(value,(list,tuple))) and value not in __ignoreEffValues ]
                                         , key = itemgetter(0) ) )
    else:
      benchmarkDict = OrderedDict()

    for key, val in benchmarkDict.iteritems():
      branchEffCollectors[key] = list()
      branchCrossEffCollectors[key] = list()
      # Add efficincy branch:
      if ringerOperation < 0:
       self.__setBranchAddress(t,val,event)

      for etBin in range(nEtBins):
        if useBins:
          branchEffCollectors[key].append(list())
          branchCrossEffCollectors[key].append(list())
        for etaBin in range(nEtaBins):
          etBinArg = etBin if useBins else -1
          etaBinArg = etaBin if useBins else -1
          argList = [ RingerOperation.tostring(key), val, etBinArg, etaBinArg ]
          branchEffCollectors[key][etBin].append(BranchEffCollector( *argList ) )
          if crossVal:
            branchCrossEffCollectors[key][etBin].append(BranchCrossEffCollector( entries, crossVal, *argList ) )
        # etBin
      # etaBin
    # benchmark dict

    if self._logger.isEnabledFor( LoggingLevel.DEBUG ):
      self._debug( 'Retrieved following branch efficiency collectors: %r',
          [collector[0].printName for collector in traverse(branchEffCollectors.values())])

    etaBin = 0; etBin = 0
    step = int(entries/100) if int(entries/100) > 0 else 1

    ## Start loop!
    self._info("There is available a total of %d entries.", entries)
    cPos=0

    ### Loop over entries
    for entry in progressbar(range(entries), entries,
                             step = step, logger = self._logger,
                             prefix = "Looping over entries "):

      self._verbose('Processing eventNumber: %d/%d', entry, entries)
      t.GetEntry(entry)

      if event.elCand2_et < offEtCut:
        self._debug("Ignoring entry due to offline E_T cut. E_T = %1.3f < %1.3f MeV",event.elCand2_et, offEtCut )
        continue
      # Add et distribution for all events

      if ringerOperation > 0:
        if event.fcCand2_et < l2EtCut:
          self._debug("Ignoring entry due Fast Calo E_T cut.")
          continue
        # Add et distribution for all events

      # Set discriminator target:
      target = Target.Unknown
      # Monte Carlo cuts
      if reference is Reference.Truth:
        if getattr(event, ('elCand%d_isTruthElectronFromZ') % (self._candIdx)):
          target = Target.Signal
        elif not getattr(event, ('elCand%d_isTruthElectronFromZ') % (self._candIdx)):
          target = Target.Background
      # Offline Likelihood cuts
      elif reference is Reference.Off_Likelihood:
        #if getattr(event, pidConfigs[RingerOperation.Offline_LH_DataDriven2016_Rel20pt7_Tight]):
        if getattr(event, pidConfigs[RingerOperation.Offline_LH_DataDriven2016_Rel21_Medium]):
          target = Target.Signal
        #elif not getattr(event, pidConfigs[RingerOperation.Offline_LH_DataDriven2016_Rel20pt7_VeryLoose]):
        elif not getattr(event, pidConfigs[RingerOperation.Offline_LH_DataDriven2016_Rel21_VeryLoose]):
          target = Target.Background
      # By pass everything (Default)
      elif reference is Reference.AcceptAll:
        target = Target.Signal if filterType is FilterType.Signal else Target.Background
      elif reference is Reference.elCand2_trig_EF_VeryLooseLLH_z0offlineMatch_Smooth_Probe:
        target = Target.Signal if event.elCand2_trig_EF_VeryLooseLLH_z0offlineMatch_Smooth_Probe else Target.Background
      elif reference is Reference.elCand2_passTrackQuality:
        if event.elCand2_passTrackQuality and filterType:
          target = Target.Signal if filterType is FilterType.Signal else Target.Background

      # Run filter if it is defined
      if filterType and \
         ( (filterType is FilterType.Signal and target != Target.Signal) or \
           (filterType is FilterType.Background and target != Target.Background) or \
           (target == Target.Unknown) ):
        self._verbose("Ignoring entry due to filter cut.")
        continue

      ## Retrieve base information and rings:
      for idx in baseInfoBranch:
        lInfo = getattr(event, baseInfoBranch.retrieveBranch(idx))
        baseInfo[idx] = lInfo
        if not getRatesOnly: npBaseInfo[idx][cPos] = lInfo
      # Retrieve dependent operation region
      if useEtBins:
        etBin  = self.__retrieveBinIdx( etBins, baseInfo[0] )
      if useEtaBins:
        etaBin = self.__retrieveBinIdx( etaBins, np.fabs( baseInfo[1]) )

      # Check if bin is within range (when not using bins, this will always be true):
      if (etBin < nEtBins and etaBin < nEtaBins):

        if useEtBins:  npEt[cPos] = etBin
        if useEtaBins: npEta[cPos] = etaBin
        # Online operation
        cPat=0

        #if not standardCaloVariables:
        caloAvailable=True
        rings = self.__get_rings_energy(event)
        if rings.empty():
          self._warning('No rings available in this event. Skipping...')
          continue

        # Retrieve rings:
        if extractDet in (Detector.Calorimetry,
                          Detector.CaloAndTrack,
                          Detector.All):

          if standardCaloVariables:
            for var in __stdCaloBranches:
              npPatterns[npCurrent.access( pidx=cPat,oidx=cPos )] = getattr(event,var)
              cPat += 1
          else:
            caloAvailable=True
            try:
              patterns = stdvector_to_list( rings )
              lPat = len(patterns)
              if lPat == ringConfig[etaBin]:
                npPatterns[npCurrent.access(pidx=slice(cPat,ringConfig[etaBin]),oidx=cPos)] = patterns
              else:
                oldEtaBin = etaBin
                if etaBin > 0 and ringConfig[etaBin - 1] == lPat:
                  etaBin -= 1
                elif etaBin + 1 < len(ringConfig) and ringConfig[etaBin + 1] == lPat:
                  etaBin += 1
                npPatterns[npCurrent.access(pidx=slice(cPat, ringConfig[etaBin]),oidx=cPos)] = patterns
                self._warning(("Recovered event which should be within eta bin (%d: %r) "
                               "but was found to be within eta bin (%d: %r). "
                               "Its read eta value was of %f."),
                               oldEtaBin, etaBins[oldEtaBin:oldEtaBin+2],
                               etaBin, etaBins[etaBin:etaBin+2],
                               np.fabs( getattr(event,etaBranch)))
            except ValueError:
              self._logger.error(("Patterns size (%d) do not match expected "
                                "value (%d). This event eta value is: %f, and ringConfig is %r."),
                                lPat, ringConfig[etaBin], np.fabs( getattr(event,etaBranch)), ringConfig
                                )
              continue
            cPat += ringConfig[etaBin]
        if extractDet in (Detector.Tracking,
                          Detector.CaloAndTrack,
                          Detector.All):
          for var in __trackBranches:
            npPatterns[npCurrent.access( pidx=cPat,oidx=cPos )] = getattr(event,var)
            if var == 'elCand2_eProbabilityHT':
              from math import log
              TRT_PID = npPatterns[npCurrent.access( pidx=cPat,oidx=cPos )]
              epsilon = 1e-99
              if TRT_PID >= 1.0: TRT_PID = 1.0-1.e-15
              elif TRT_PID <= 0.0: TRT_PID = epsilon
              tau = 15.0
              TRT_PID = -(1/tau)*log( (1.0/TRT_PID) - 1.0 )
              npPatterns[npCurrent.access( pidx=cPat,oidx=cPos )] = TRT_PID
            cPat += 1

        ## Retrieve rates information:
        if getRates and ringerOperation < 0:
          event.elCand2_isEMLoose2015 = not( event.elCand2_isEMLoose2015 & 34896 )
          event.elCand2_isEMMedium2015 = not( event.elCand2_isEMMedium2015 & 276858960 )
          event.elCand2_isEMTight2015 = not( event.elCand2_isEMTight2015 & 281053264 )

          for branch in branchEffCollectors.itervalues():
            if not useBins:
              branch.update(event)
            else:
              branch[etBin][etaBin].update(event)
          if crossVal:
            for branchCross in branchCrossEffCollectors.itervalues():
              if not useBins:
                branchCross.update(event)
              else:
                branchCross[etBin][etaBin].update(event)
        # end of (getRates)

        if not monitoring is None:
          self.__fillHistograms(monitoring, filterType, pileupRef, pidConfigs, event)

        # We only increment if this cluster will be computed
        cPos += 1
      # end of (et/eta bins)

      # Limit the number of entries to nClusters if desired and possible:
      if not nClusters is None and cPos >= nClusters:
        break
    # for end


    ## Treat the rings information
    ## Remove not filled reserved memory space:
    if npPatterns.shape[npCurrent.odim] > cPos:
      npPatterns = np.delete( npPatterns, slice(cPos,None), axis = npCurrent.odim)

    ## Segment data over bins regions:
    # Also remove not filled reserved memory space:
    if useEtBins:
      npEt  = npCurrent.delete( npEt, slice(cPos,None))
    if useEtaBins:
      npEta = npCurrent.delete( npEta, slice(cPos,None))

    # Treat
    npObject = self.treatNpInfo(cPos, npEt, npEta, useEtBins, useEtaBins,
                                nEtBins, nEtaBins, standardCaloVariables, ringConfig,
                                npPatterns, )

    data = [self.treatNpInfo(cPos, npEt, npEta, useEtBins, useEtaBins,
                             nEtBins, nEtaBins, standardCaloVariables, ringConfig,
                             npData) for npData in npBaseInfo]
    npBaseInfo = npCurrent.array( data, dtype=np.object )

    if getRates:
      if crossVal:
        for etBin in range(nEtBins):
          for etaBin in range(nEtaBins):
            for branchCross in branchCrossEffCollectors.itervalues():
              if not useBins:
                branchCross.finished()
              else:
                branchCross[etBin][etaBin].finished()

      # Print efficiency for each one for the efficiency branches analysed:
      for etBin in range(nEtBins) if useBins else range(1):
        for etaBin in range(nEtaBins) if useBins else range(1):
          for branch in branchEffCollectors.itervalues():
            lBranch = branch if not useBins else branch[etBin][etaBin]
            self._info('%s',lBranch)
          if crossVal:
            for branchCross in branchCrossEffCollectors.itervalues():
              lBranchCross = branchCross if not useBins else branchCross[etBin][etaBin]
              lBranchCross.dump(self._debug, printSort = True,
                                 sortFcn = self._verbose)
          # for branch
        # for eta
      # for et
    else:
      branchEffCollectors = None
      branchCrossEffCollectors = None
    # end of (getRates)

    outputs = []
    outputs.extend((npObject, npBaseInfo))
    if getRates:
      outputs.extend((branchEffCollectors, branchCrossEffCollectors))

    return outputs
  # end __call__


  ####################################################################################

  def treatNpInfo(self, cPos, npEt, npEta, useEtBins,
                  useEtaBins, nEtBins, nEtaBins, standardCaloVariables,
                  ringConfig, npInput, ):

    ## Remove not filled reserved memory space:
    if npInput.shape[npCurrent.odim] > cPos:
      npInput = np.delete( npInput, slice(cPos,None), axis = npCurrent.odim)

    # Separation for each bin found
    if useEtBins or useEtaBins:
      npObject = np.empty((nEtBins,nEtaBins),dtype=object)
      npObject.fill((npCurrent.array([[]]),))
      for etBin in range(nEtBins):
        for etaBin in range(nEtaBins):
          if useEtBins and useEtaBins:
            # Retrieve all in current eta et bin
            idx = np.all([npEt==etBin,npEta==etaBin],axis=0).nonzero()[0]
            if len(idx):
              npObject[etBin][etaBin]=npInput[npCurrent.access(oidx=idx)]
              # Remove extra features in this eta bin
              if not standardCaloVariables:
                npObject[etBin][etaBin]=npCurrent.delete(npObject[etBin][etaBin],slice(ringConfig[etaBin],ringConfig.max()),
                                                         axis=npCurrent.pdim)
            else:
              npObject[etBin][etaBin] = npCurrent.array([[]])
          elif useEtBins:
            # Retrieve all in current et bin
            idx = (npEt==etBin).nonzero()[0]
            if len(idx):
              npObject[etBin][etaBin]=npInput[npCurrent.access(oidx=idx)]
            else:
              npObject[etBin][etaBin] = npCurrent.array([[]])
          else:# useEtaBins
            # Retrieve all in current eta bin
            idx = (npEta==etaBin).nonzero()[0]
            if len(idx):
              npObject[etBin][etaBin]=npInput[npCurrent.access(oidx=idx)]
              # Remove extra rings:
              if not standardCaloVariables:
                npObject[etBin][etaBin]=npCurrent.delete(npObject[etBin][etaBin],slice(ringConfig[etaBin],ringConfig.max()),
                                                         axis=npCurrent.pdim)
            else:
              npObject[etBin][etaBin] = npCurrent.array([[]])
        # for etaBin
      # for etBin
    else:
      npObject = npInput
    # useBins
    return npObject
  # end of (ReadData.treatNpInfo)


  ####################################################################################

  def bookHistograms(self, monTool):
    """
      Booking all histograms to monitoring signal and backgorund samples
    """
    from ROOT import TH1F, TH2F
    etabins = [-2.47,-2.37,-2.01,-1.81,-1.52,-1.37,-1.15,-0.80,-0.60,-0.10,0.00,
               0.10, 0.60, 0.80, 1.15, 1.37, 1.52, 1.81, 2.01, 2.37, 2.47]

    pidnames   = ['Entries', 'VLoose','Loose','Medium','Tight','LHVLoose','LHLoose','LHMedium','LHTight']
    dirnames   = ['Distributions/Signal','Distributions/Background']

    for dirname in dirnames:
      monTool.mkdir(dirname)
      monTool.addHistogram(TH1F('et'       ,'E_{T}; E_{T}   ; Count'  , 200,0,200))
      monTool.addHistogram(TH1F('eta'      ,'#eta; #eta     ; Count'  , len(etabins)-1, np.array(etabins)))
      monTool.addHistogram(TH1F('phi'      ,'#phi; #phi     ; Count'  , 20, -3.2, 3.2))
      monTool.addHistogram(TH1F('mu'       ,'<#mu>; <#mu>   ; Count'  , 80,0,80))
      monTool.addHistogram(TH1F('Offline'  , 'Event Counter; Cuts; Count', len(pidnames), 0.  , len(pidnames))  )
      monTool.setLabels(dirname+'/Offline', pidnames   )



  def __fillHistograms(self, monTool, filterType, pileupRef, pidConfigs, event):

    # Select the correct directory to Fill the histograns
    if filterType == FilterType.Signal:
      dirname = 'Distributions/Signal'
    elif filterType == FilterType.Background:
      dirname = 'Distributions/Background'
    else:
      return

    if pileupRef is PileupReference.avgmu:
      avgmu = self.__getAvgmu(event)
    elif pileupRef is PileupReference.nvtx:
      avgmu = self.__getNvtx(event)
    else:
      avgmu = 0.0

    #for idx, val in enumerate(patterns):
    #  monTool.histogram(dirname+'/ringsVsEnergy' ).Fill(idx,val)

    # Common offline variabels monitoring
    monTool.histogram(dirname+'/et' ).Fill(self.__getEt(event)*1e-3) # To GeV
    monTool.histogram(dirname+'/eta').Fill(self.__getEta(event))
    monTool.histogram(dirname+'/mu' ).Fill(avgmu)

    monTool.histogram(dirname+'/Offline').Fill('Entries' ,1)
    if getattr(event, pidConfigs[RingerOperation.Offline_LH_Tight])  is 1:
      monTool.histogram(dirname+'/Offline').Fill('LHTight' ,1)
    if getattr(event, pidConfigs[RingerOperation.Offline_LH_Medium]) is 1:
      monTool.histogram(dirname+'/Offline').Fill('LHMedium',1)
    if getattr(event, pidConfigs[RingerOperation.Offline_LH_Loose])  is 1:
      monTool.histogram(dirname+'/Offline').Fill('LHLoose' ,1)
    if getattr(event, pidConfigs[RingerOperation.Offline_LH_VeryLoose]) is 1:
      monTool.histogram(dirname+'/Offline').Fill('LHVLoose',1)

  ####################################################################################
  ## Helper event methods

  def __getEt( self, event):
    return getattr(event, ('%s%d_et')%(self._candIdx,self._branchRef))

  def __getEta( self, event):
    return getattr(event, ('%s%d_eta')%(self._candIdx,self._branchRef))

  def __getPhi( self, event, isfc=False):
    return getattr(event, ('%s%d_phi')%(self._candIdx,self._branchRef))

  def __get_ringer_onMatch(self, event):
    return getattr(event, ('fcCand%d_ringerMatch')%(self._candIdx) )

  def __get_rings_energy(self, event):
    return getattr(event, ('%s%d_ringer_rings')%(self._branchRef,self._candIdx))

  def __getAvgmu(self, event):
    return event.averageIntPerXing

  def __getNvtx(self, event):
    return event.Nvtx

  ####################################################################################


## Instantiate object
readData = ReadData()

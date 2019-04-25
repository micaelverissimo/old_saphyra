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
    # Offline information branches:
    __offlineBranches = ['el_et',
                         'el_eta',
                         #'el_loose',
                         #'el_medium',
                         #'el_tight',
                         'el_lhvloose',
                         'el_lhloose',
                         'el_lhmedium',
                         'el_lhtight',
                         'el_nPileupPrimaryVtx',
                         'mc_hasMC',
                         'mc_isTruthElectronFromZ',
                         'mc_isTruthElectronFromW',
                         'mc_isTruthElectronFromJpsi',
                         'mc_isTruthElectronAny',
                         ]
    # Online information branches
    __onlineBranches = []
    __l2stdCaloBranches = ['trig_L2_calo_et',
                           'trig_L2_calo_eta',
                           'trig_L2_calo_phi',
                           'trig_L2_calo_e237', # rEta
                           'trig_L2_calo_e277', # rEta
                           'trig_L2_calo_fracs1', # F1: fraction sample 1
                           'trig_L2_calo_weta2', # weta2
                           'trig_L2_calo_ehad1', # energy on hadronic sample 1
                           'trig_L2_calo_emaxs1', # eratio
                           'trig_L2_calo_e2tsts1', # eratio
                           'trig_L2_calo_wstot',] # wstot
    __l2trackBranches = [ # Do not add non patter variables on this branch list
                         #'trig_L2_el_pt',
                         #'trig_L2_el_eta',
                         #'trig_L2_el_phi',
                         #'trig_L2_el_caloEta',
                         #'trig_L2_el_charge',
                         #'trig_L2_el_nTRTHits',
                         #'trig_L2_el_nTRTHiThresholdHits',
                         'trig_L2_el_etOverPt',
                         'trig_L2_el_trkClusDeta',
                         'trig_L2_el_trkClusDphi',]
    # Retrieve information from keyword arguments
    filterType            = retrieve_kw(kw, 'filterType',            FilterType.DoNotFilter )
    reference             = retrieve_kw(kw, 'reference',             Reference.Truth        )
    l1EmClusCut           = retrieve_kw(kw, 'l1EmClusCut',           None                   )
    l2EtCut               = retrieve_kw(kw, 'l2EtCut',               None                   )
    efEtCut               = retrieve_kw(kw, 'efEtCut',               None                   )
    offEtCut              = retrieve_kw(kw, 'offEtCut',              None                   )
    treePath              = retrieve_kw(kw, 'treePath',              None                   )
    nClusters             = retrieve_kw(kw, 'nClusters',             None                   )
    getRates              = retrieve_kw(kw, 'getRates',              True                   )
    getRatesOnly          = retrieve_kw(kw, 'getRatesOnly',          False                  )
    etBins                = retrieve_kw(kw, 'etBins',                None                   )
    etaBins               = retrieve_kw(kw, 'etaBins',               None                   )
    crossVal              = retrieve_kw(kw, 'crossVal',              None                   )
    ringConfig            = retrieve_kw(kw, 'ringConfig',            100                    )
    extractDet            = retrieve_kw(kw, 'extractDet',            None                   )
    standardCaloVariables = retrieve_kw(kw, 'standardCaloVariables', False                  )
    useTRT                = retrieve_kw(kw, 'useTRT',                False                  )
    supportTriggers       = retrieve_kw(kw, 'supportTriggers',       True                   )
    monitoring            = retrieve_kw(kw, 'monitoring',            None                   )
    pileupRef             = retrieve_kw(kw, 'pileupRef',             NotSet                 )
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
    # Mutual exclusive arguments:
    if not getRates and getRatesOnly:
      self._logger.error("Cannot run with getRates set to False and getRatesOnly set to True. Setting getRates to True.")
      getRates = True
    # Also parse operation, check if its type is string and if we can
    # transform it to the known operation enum:
    fList = csvStr2List ( fList )
    fList = expandFolders( fList )
    ringerOperation = RingerOperation.retrieve(ringerOperation)
    reference = Reference.retrieve(reference)
    if isinstance(l1EmClusCut, str):
      l1EmClusCut = float(l1EmClusCut)
    if l1EmClusCut:
      l1EmClusCut = 1000.*l1EmClusCut # Put energy in MeV
      __onlineBranches.append( 'trig_L1_emClus'  )
    if l2EtCut:
      l2EtCut = 1000.*l2EtCut # Put energy in MeV
      __onlineBranches.append( 'trig_L2_calo_et' )
    if efEtCut:
      efEtCut = 1000.*efEtCut # Put energy in MeV
      __onlineBranches.append( 'trig_EF_calo_et' )
    if offEtCut:
      offEtCut = 1000.*offEtCut # Put energy in MeV
      __offlineBranches.append( 'el_et' )
    # Check if treePath is None and try to set it automatically
    if treePath is None:
      treePath = 'Offline/Egamma/Ntuple/electron' if ringerOperation < 0 else \
                 'Trigger/HLT/Egamma/TPNtuple/e24_medium_L1EM18VH'



    # Check whether using bins
    useBins=False; useEtBins=False; useEtaBins=False
    nEtaBins = 1; nEtBins = 1
    # Set the detector which we should extract the information:
    if extractDet is None:
      extractDet = Detector.Calorimetry
    else:
      extractDet = Detector.retrieve( extractDet )

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

    ### Prepare to loop:
    # Open root file
    t = ROOT.TChain()
    for inputFile in progressbar(fList, len(fList),
                                 logger = self._logger,
                                 prefix = "Creating collection tree "):

      _treePath = treePath
      # Check if file exists
      f  = ROOT.TFile.Open(inputFile, 'read')
      if not f or f.IsZombie():
        self._warning('Couldn''t open file: %s', inputFile)
        continue
      # Inform user whether TTree exists, and which options are available:
      self._debug("Adding file: %s", inputFile)

      # Custon directory token
      try:
        if '*' in _treePath:
          dirname = f.GetListOfKeys()[0].GetName()
          _treePath = treePath.replace('*',dirname)
      except:
        continue

      obj = f.Get(_treePath)
      if not obj:
        self._warning("Couldn't retrieve TTree (%s)!", _treePath)
        self._info("File available info:")
        f.ReadAll()
        f.ReadKeys()
        f.ls()
        continue
      elif not isinstance(obj, ROOT.TTree):
        self._fatal("%s is not an instance of TTree!", _treePath, ValueError)
      t.Add( inputFile+'/'+_treePath )

    # Turn all branches off.
    t.SetBranchStatus("*", False)

    # RingerPhysVal hold the address of required branches
    event = ROOT.RingerPhysVal_v2()

    # Add offline branches, these are always needed
    cPos = 0
    for var in __offlineBranches:
      self.__setBranchAddress(t,var,event)

    # Add online branches if using Trigger
    if ringerOperation > 0:
      for var in __onlineBranches:
        self.__setBranchAddress(t,var,event)

    ## Allocating memory for the number of entries
    entries = t.GetEntries()
    nobs = entries if (nClusters is None or nClusters > entries or nClusters < 1) \
                                                                else nClusters

    ## Retrieve the dependent operation variables:
    if useEtBins:
      etBranch = 'el_et' if ringerOperation < 0 else 'trig_L2_calo_et'
      self.__setBranchAddress(t,etBranch,event)
      self._debug("Added branch: %s", etBranch)
      if not getRatesOnly:
        npEt    = npCurrent.scounter_zeros(shape=npCurrent.shape(npat = 1, nobs = nobs))
        self._debug("Allocated npEt    with size %r", npEt.shape)

    if useEtaBins:
      etaBranch    = "el_eta" if ringerOperation < 0 else "trig_L2_calo_eta"
      self.__setBranchAddress(t,etaBranch,event)
      self._debug("Added branch: %s", etaBranch)
      if not getRatesOnly:
        npEta    = npCurrent.scounter_zeros(shape=npCurrent.shape(npat = 1, nobs = nobs))
        self._debug("Allocated npEta   with size %r", npEta.shape)

    # The base information holder, such as et, eta and pile-up
    if pileupRef is NotSet:
      if ringerOperation > 0:
        pileupRef = PileupReference.avgmu
      else:
        pileupRef = PileupReference.nvtx

    pileupRef = PileupReference.retrieve( pileupRef )

    self._info("Using '%s' as pile-up reference.", PileupReference.tostring( pileupRef ) )

    if pileupRef is PileupReference.nvtx:
      pileupBranch = 'el_nPileupPrimaryVtx'
      pileupDataType = np.uint16
    elif pileupRef is PileupReference.avgmu:
      pileupBranch = 'avgmu'
      pileupDataType = np.float32
    else:
      raise NotImplementedError("Pile-up reference %r is not implemented." % pileupRef)
    baseInfoBranch = BaseInfo((etBranch, etaBranch, pileupBranch, "el_phi" if ringerOperation < 0 else "trig_L2_calo_phi" ),
                              (npCurrent.fp_dtype, npCurrent.fp_dtype, npCurrent.fp_dtype, pileupDataType) )
    baseInfo = [None, ] * baseInfoBranch.nInfo

    # Make sure all baseInfoBranch information is available:
    for idx in baseInfoBranch:
      self.__setBranchAddress(t,baseInfoBranch.retrieveBranch(idx),event)

    # Allocate numpy to hold as many entries as possible:
    if not getRatesOnly:
      # Retrieve the rings information depending on ringer operation
      ringerBranch = "el_ringsE" if ringerOperation < 0 else \
                 "trig_L2_calo_rings"
      self.__setBranchAddress(t,ringerBranch,event)
      self.__setBranchAddress(t,'trig_L2_el_trkClusDeta',event)

      t.GetEntry(0)
      npat = 0
      if extractDet in (Detector.Calorimetry,
                        Detector.CaloAndTrack,
                        Detector.All):

        if standardCaloVariables:
          if ringerOperation in (RingerOperation.L2Calo, RingerOperation.L2):
            for var in __l2stdCaloBranches:
              self.__setBranchAddress(t, var, event)
          else:
            self._warning("Unknown standard calorimeters for Operation:%s. Setting operation back to use rings variables.",
                                 RingerOperation.tostring(ringerOperation))
          npat= 6
        else:
          npat = ringConfig.max()


      if extractDet in (Detector.Tracking,
                       Detector.CaloAndTrack,
                       Detector.All):
        if ringerOperation is RingerOperation.L2:
          if useTRT:
            self._info("Using TRT information!")
            npat = 2
            __l2trackBranches.append('trig_L2_el_nTRTHits')
            __l2trackBranches.append('trig_L2_el_nTRTHiThresholdHits')
          npat += 3

          for var in __l2trackBranches:
            self.__setBranchAddress(t,var,event)
          self.__setBranchAddress(t,"trig_L2_el_pt",event)

        elif ringerOperation < 0: # Offline
          self._warning("Still need to implement tracking for the ringer offline.")



      npPatterns = npCurrent.fp_zeros( shape=npCurrent.shape(npat=npat, #getattr(event, ringerBranch).size()
                                                   nobs=nobs)
                                     )
      self._debug("Allocated npPatterns with size %r", npPatterns.shape)

      # Add E_T, eta and luminosity information
      npBaseInfo = [npCurrent.zeros( shape=npCurrent.shape(npat=1, nobs=nobs ), dtype=baseInfoBranch.dtype(idx) )
                                    for idx in baseInfoBranch]
    else:
      npPatterns = npCurrent.fp_array([])
      npBaseInfo = [deepcopy(npCurrent.fp_array([])) for _ in baseInfoBranch]

    ## Allocate the branch efficiency collectors:
    if getRates:
      if ringerOperation < 0:
        benchmarkDict = OrderedDict(
          [( RingerOperation.Offline_CutBased_Loose  , 'el_loose'            ),
           ( RingerOperation.Offline_CutBased_Medium , 'el_medium'           ),
           ( RingerOperation.Offline_CutBased_Tight  , 'el_tight'            ),
           ( RingerOperation.Offline_LH_Loose        , 'el_lhloose'          ),
           ( RingerOperation.Offline_LH_Medium       , 'el_lhmedium'         ),
           ( RingerOperation.Offline_LH_Tight        , 'el_lhtight'          ),
          ])
      else:
        benchmarkDict = OrderedDict(
          # Only the Asg selector decisions for each trigger level
          [
           #TODO: Dummy branch used to attach external efficiencies
           (RingerOperation.L2Calo                 , 'trig_EF_calo_lhtight'  ),
           (RingerOperation.L2                     , 'trig_EF_calo_lhtight'  ),
           (RingerOperation.EFCalo                 , 'trig_EF_calo_lhtight'  ),
           (RingerOperation.HLT                    , 'trig_EF_calo_lhtight'  ),
           #( RingerOperation.branchName( RingerOperation.EFCalo_LH_Tight         ), 'trig_EF_calo_lhtight'  ),
           #( RingerOperation.branchName( RingerOperation.EFCalo_LH_Medium        ), 'trig_EF_calo_lhmedium' ),
           #( RingerOperation.branchName( RingerOperation.EFCalo_LH_Loose         ), 'trig_EF_calo_lhloose'  ),
           #( RingerOperation.branchName( RingerOperation.EFCalo_LH_VLoose        ), 'trig_EF_calo_lhvloose' ),
           #( RingerOperation.branchName( RingerOperation.HLT_LH_Tight            ), 'trig_EF_el_lhtight'    ),
           #( RingerOperation.branchName( RingerOperation.HLT_LH_Medium           ), 'trig_EF_el_lhmedium'   ),
           #( RingerOperation.branchName( RingerOperation.HLT_LH_Loose            ), 'trig_EF_el_lhloose'    ),
           #( RingerOperation.branchName( RingerOperation.HLT_LH_VLoose           ), 'trig_EF_el_lhvloose'   ),
          ])


      from TuningTools.CreateData import BranchEffCollector, BranchCrossEffCollector
      branchEffCollectors = OrderedDict()
      branchCrossEffCollectors = OrderedDict()
      for key, val in benchmarkDict.iteritems():
        branchEffCollectors[key] = list()
        branchCrossEffCollectors[key] = list()
        # Add efficincy branch:
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
    # end of (getRates)

    etaBin = 0; etBin = 0
    step = int(entries/100) if int(entries/100) > 0 else 1
    ## Start loop!
    self._info("There is available a total of %d entries.", entries)

    for entry in progressbar(range(entries), entries,
                             step = step, logger = self._logger,
                             prefix = "Looping over entries "):

      #self._verbose('Processing eventNumber: %d/%d', entry, entries)
      t.GetEntry(entry)

      # Check if it is needed to remove energy regions (this means that if not
      # within this range, it will be ignored as well for efficiency measuremnet)
      if event.el_et < offEtCut:
        self._verbose("Ignoring entry due to offline E_T cut.")
        continue

      # Only for trigger
      if ringerOperation > 0:
        if event.trig_L2_calo_et < l2EtCut:
          self._verbose("Ignoring entry due to L2Calo E_T cut.")
          continue

      # remove events without rings from the main loop
      if getattr(event,ringerBranch).empty():
        self._verbose("Ignoring entry without rings")
        continue

      if ringerOperation is RingerOperation.L2  and not event.trig_L2_el_trkClusDeta.size():
        continue

      # Set discriminator target:
      target = Target.Unknown
      if reference is Reference.Truth:
        if event.mc_isTruthElectronFromZ or event.mc_isTruthElectronFromJpsi:
          target = Target.Signal
        elif not event.mc_isTruthElectronAny:
          target = Target.Background
      elif reference is Reference.Off_Likelihood:
        #if event.el_lhtight: target = Target.Signal
        if event.el_lhmedium: target = Target.Signal
        elif not event.el_lhvloose: target = Target.Background
      elif reference is Reference.AcceptAll:
        target = Target.Signal if filterType is FilterType.Signal else Target.Background

      # Run filter if it is defined
      if filterType and \
         ( (filterType is FilterType.Signal and target != Target.Signal) or \
           (filterType is FilterType.Background and target != Target.Background) or \
           (target == Target.Unknown) ):
        #self._verbose("Ignoring entry due to filter cut.")
        continue

      # Retrieve base information:
      for idx in baseInfoBranch:
        lInfo = getattr(event, baseInfoBranch.retrieveBranch(idx))
        baseInfo[idx] = lInfo
        npBaseInfo[idx][cPos] = lInfo
      # Retrieve dependent operation region
      if useEtBins:
        etBin  = self.__retrieveBinIdx( etBins, baseInfo[0] )
      if useEtaBins:
        etaBin = self.__retrieveBinIdx( etaBins, np.fabs( baseInfo[1]) )


      # Check if bin is within range (when not using bins, this will always be true):
      if (etBin < nEtBins and etaBin < nEtaBins):
        # Retrieve patterns:
        if useEtBins:  npEt[cPos] = etBin
        if useEtaBins: npEta[cPos] = etaBin
        ## Retrieve calorimeter information:
        cPat = 0

        if extractDet in (Detector.Calorimetry,
                         Detector.CaloAndTrack,
                         Detector.All):

          if standardCaloVariables:
            patterns = []
            if ringerOperation is (RingerOperation.L2Calo, RingerOperation.L2):
              from math import cosh
              cosh_eta = cosh( event.trig_L2_calo_eta )
              # second layer ratio between 3x7 7x7
              rEta = event.trig_L2_calo_e237 / event.trig_L2_calo_e277
              base = event.trig_L2_calo_emaxs1 + event.trig_L2_calo_e2tsts1
              # Ratio between first and second highest energy cells
              eRatio = ( event.trig_L2_calo_emaxs1 - event.trig_L2_calo_e2tsts1 ) / base if base > 0 else 0
              # ratio of energy in the first layer (hadronic particles should leave low energy)
              F1 = event.trig_L2_calo_fracs1 / ( event.trig_L2_calo_et * cosh_eta )
              # weta2 is calculated over the middle layer using 3 x 5
              weta2 = event.trig_L2_calo_weta2
              # wstot is calculated over the first layer using (typically) 20 strips
              wstot = event.trig_L2_calo_wstot
              # ratio between EM cluster and first hadronic layers:
              Rhad1 = ( event.trig_L2_calo_ehad1 / cosh_eta ) / event.trig_L2_calo_et
              # allocate patterns:
              patterns = [rEta, eRatio, F1, weta2, wstot, Rhad1]
              for pat in patterns:
                npPatterns[npCurrent.access( pidx=cPat, oidx=cPos) ] = pat
                cPat += 1
            # end of ringerOperation
          else:
            # Retrieve rings:
            try:
              patterns = stdvector_to_list( getattr(event,ringerBranch) )
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

            cPat += ringConfig.max()
          # which calo variables
        # end of (extractDet needed calorimeter)

        # And track information:
        if extractDet in (Detector.Tracking,
                         Detector.CaloAndTrack,
                         Detector.All):

          if ringerOperation is (RingerOperation.L2):
            # Retrieve nearest deta/dphi only, so we need to find each one is the nearest:
            if event.trig_L2_el_trkClusDeta.size():
              clusDeta = npCurrent.fp_array( stdvector_to_list( event.trig_L2_el_trkClusDeta ) )
              clusDphi = npCurrent.fp_array( stdvector_to_list( event.trig_L2_el_trkClusDphi ) )
              bestTrackPos = int( np.argmin( clusDeta**2 + clusDphi**2 ) )
              for var in __l2trackBranches:
                npPatterns[npCurrent.access( pidx=cPat,oidx=cPos) ] = getattr(event, var)[bestTrackPos]
                cPat += 1
            else:
              self._verbose("Ignoring entry due to track information not available.")
              continue
              #for var in __l2trackBranches:
              #  npPatterns[npCurrent.access( pidx=cPat,oidx=cPos) ] = np.nan
              #  cPat += 1
          elif ringerOperation < 0: # Offline
            pass
        # end of (extractDet needs tracking)


				## Retrieve rates information:
        if getRates:
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


        # We only increment if this cluster will be computed
        cPos += 1
      # end of (et/eta bins)

      # Limit the number of entries to nClusters if desired and possible:
      if not nClusters is None and cPos >= nClusters:
        break
    # for end

    ## Treat the rings information
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
    if not getRatesOnly:
      outputs.extend((npObject, npBaseInfo))
    if getRates:
      outputs.extend((branchEffCollectors, branchCrossEffCollectors))
    #outputs = tuple(outputs)

    return outputs
  # end __call__


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


  #def bookHistograms(self, monTool):
  #  """
  #    Booking all histograms to monitoring signal and backgorund samples
  #  """
  #  from ROOT import TH1F
  #  etabins = [-2.47,-2.37,-2.01,-1.81,-1.52,-1.37,-1.15,-0.80,-0.60,-0.10,0.00,\
  #             0.10, 0.60, 0.80, 1.15, 1.37, 1.52, 1.81, 2.01, 2.37, 2.47]
  #  pidnames = ['VetoLHLoose','LHLoose','LHMedium','LHTight']
  #  mcnames  = ['NoFound','VetoTruth', 'Electron','Z','Unknown']
  #  dirnames = ['Signal','Background']
  #  basepath = 'Distributions'
  #  for dirname in dirnames:
  #    monTool.mkdir(basepath+'/'+dirname)
  #    monTool.addHistogram(TH1F('et'       ,'E_{T}; E_{T} ; Count'  ,200,0,200))
  #    monTool.addHistogram(TH1F('eta'      ,'eta; eta ; Count', len(etabins)-1, np.array(etabins)))
  #    monTool.addHistogram(TH1F('mu'       ,'mu; mu ; Count'  ,100,0,100))
  #    monTool.addHistogram(TH1F('et_match' ,"E_{T}; E_{T} ; Count"  ,200,0,200))
  #    monTool.addHistogram(TH1F('eta_match','eta; eta ; Count',len(etabins)-1,np.array(etabins)))
  #    monTool.addHistogram(TH1F('mu_match' ,'mu; mu ; Count'  ,100,0,100))
  #    monTool.addHistogram(TH1F('offline', 'Ofline; pidname; Count',len(pidnames),0.,len(pidnames)))
  #    monTool.addHistogram(TH1F('offline_match', 'Ofline; pidname; Count',len(pidnames),0.,len(pidnames)))
  #    monTool.addHistogram(TH1F('truth', 'Truth; ; Count',len(mcnames),0.,len(mcnames)))
  #    monTool.addHistogram(TH1F('truth_match', 'Truth; ; Count',len(mcnames),0.,len(mcnames)))
  #    monTool.setLabels(basepath+'/'+dirname+'/offline', pidnames )
  #    monTool.setLabels(basepath+'/'+dirname+'/offline_match', pidnames )

  #def __fillHistograms(self, monTool, filterType, event, match=False):
  #
  #  # Select the correct directory to Fill the histograns
  #  if filterType == FilterType.Signal:
  #    dirname = 'Signal'
  #  elif filterType == FilterType.Background:
  #    dirname = 'Background'
  #  else:
  #    return
  #  # Add a sufix "_match" when we have to fill after all selections
  #  if match is True: name = '_match'
  #  else: name = ''
  #  # Common offline variabels monitoring
  #  monTool.histogram('Distributions/'+dirname+'/et' +name).Fill(event.el_et*1e-3)
  #  monTool.histogram('Distributions/'+dirname+'/eta'+name).Fill(event.el_eta)
  #  monTool.histogram('Distributions/'+dirname+'/mu' +name).Fill(event.el_nPileupPrimaryVtx)
  #  # Offline Monitoring
  #  if not event.el_lhLoose: monTool.histogram('Distributions/'+dirname+'/offline'+name).Fill('VetoLHLoose',1)
  #  if event.el_lhLoose:     monTool.histogram('Distributions/'+dirname+'/offline'+name).Fill('LHLoose'    ,1)
  #  if event.el_lhMedium:    monTool.histogram('Distributions/'+dirname+'/offline'+name).Fill('LHMedium'   ,1)
  #  if event.el_lhTight:     monTool.histogram('Distributions/'+dirname+'/offline'+name).Fill('LHTight'    ,1)
  #
  #  # MonteCarlo Monitoring
  #  if event.mc_hasMC == False:
  #    monTool.histogram('Distributions/'+dirname+'/truth'+name).Fill('NoFound',1)
  #  else:
  #    if not (event.mc_isElectron and (event.mc_hasZMother or event.mc_hasWMother) ):
  #      monTool.histogram('Distributions/'+dirname+'/truth'+name).Fill('VetoTruth',1)
  #    elif event.mc_isElectron and event.mc_hasZMother:
  #      monTool.histogram('Distributions/'+dirname+'/truth'+name).Fill('Z',1)
  #    elif event.mc_isElectron:
  #      monTool.histogram('Distributions/'+dirname+'/truth'+name).Fill('Electron',1)
  #    else:
  #      monTool.histogram('Distributions/'+dirname+'/truth'+name).Fill('Unknown',1)


# Instantiate object
readData = ReadData()

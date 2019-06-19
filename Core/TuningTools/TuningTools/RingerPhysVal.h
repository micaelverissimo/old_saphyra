#ifndef TUNINGTOOLS_RINGERPHYSVAL_H
#define TUNINGTOOLS_RINGERPHYSVAL_H
#include <vector>
#include <string>
#include "Rtypes.h"
//#include "TObject.h"

struct RingerPhysVal /*: public TObject*/ {

  UInt_t             RunNumber;

  // Rings!
  std::vector<Float_t> *el_ringsE;
  std::vector<std::string> *trig_L1_thrNames;
  std::vector<Float_t> *trig_L2_calo_rings;
  std::vector<Float_t> *trig_L2_calo_rnnOutput;
  std::vector<Float_t> *trig_EF_calo_et;

  // Offline electron cluster
  Float_t         el_et;
  Float_t         el_eta;
  Float_t         el_phi;
  Float_t         el_ethad1;
  Float_t         el_ethad;
  Float_t         el_ehad1;
  Float_t         el_f1;
  Float_t         el_f3;
  Float_t         el_f1core;
  Float_t         el_f3core;
  Float_t         el_weta1;
  Float_t         el_weta2;
  Float_t         el_wtots1;
  Float_t         el_fracs1;
  Float_t         el_Reta;
  Float_t         el_Rphi;
  Float_t         el_Eratio;
  Float_t         el_Rhad;
  Float_t         el_Rhad1;
  // Track combined
  Float_t         el_deta1;
  Float_t         el_deta2;
  Float_t         el_dphi2;
  Float_t         el_dphiresc;

  // Pure track
  Float_t         el_pt;
  Float_t         el_d0;
  Float_t         el_eprobht;
  Float_t         el_charge;
  uint8_t         el_nblayerhits;
  uint8_t         el_nblayerolhits;
  uint8_t         el_npixhits;
  uint8_t         el_npixolhits;
  uint8_t         el_nscthits;
  uint8_t         el_nsctolhits;
  uint8_t         el_ntrthighreshits;
  uint8_t         el_ntrthits;
  uint8_t         el_ntrthighthresolhits;
  uint8_t         el_ntrtolhits;
  uint8_t         el_ntrtxenonhits;
  uint8_t         el_expectblayerhit;

  int             trk_nPileupPrimaryVtx;
  Int_t           el_nPileupPrimaryVtx;

  // BCID (Bunch cross; ID average mu luminosity
  float           avgmu;
  float           LumiBlock;

  // Selector decision
  Bool_t       el_loose;
  Bool_t       el_medium;
  Bool_t       el_tight;
  Bool_t       el_lhVLoose;
  Bool_t       el_lhLoose;
  Bool_t       el_lhMedium;
  Bool_t       el_lhTight;
  Bool_t       el_multiLepton;

  // Trigger info
  // L1
  Float_t                             trig_L1_emClus;
  // Fast Calo
  Float_t                            trig_L2_calo_et;
  Float_t                           trig_L2_calo_eta;
	Float_t                           trig_L2_calo_phi;
	Float_t                          trig_L2_calo_e237;
	Float_t                          trig_L2_calo_e277;
	Float_t                        trig_L2_calo_fracs1;
	Float_t                         trig_L2_calo_weta2;
	Float_t                         trig_L2_calo_ehad1;
	Float_t                        trig_L2_calo_emaxs1;
	Float_t                       trig_L2_calo_e2tsts1;
	Float_t                         trig_L2_calo_wstot;
	//std::vector<Float_t>*      trig_L2_calo_energySample;
  // Fast Track
	//std::vector<Int_t>*          trig_L2_el_trackAlgID;
	std::vector<Float_t>*                  trig_L2_el_pt;
	std::vector<Float_t>*                 trig_L2_el_eta;
	std::vector<Float_t>*                 trig_L2_el_phi;
	std::vector<Float_t>*             trig_L2_el_caloEta;
	std::vector<Float_t>*              trig_L2_el_charge;
	std::vector<Float_t>*            trig_L2_el_nTRTHits;
	std::vector<Float_t>* trig_L2_el_nTRTHiThresholdHits;
	std::vector<Float_t>*            trig_L2_el_etOverPt;
	std::vector<Float_t>*         trig_L2_el_trkClusDeta;
	std::vector<Float_t>*         trig_L2_el_trkClusDphi;


  Bool_t          mc_hasMC;
  Bool_t          mc_isElectron;
  Bool_t          mc_hasZMother;
  Bool_t          mc_hasWMother;


  //Bool_t          L2Calo_isEMTight;
  //Bool_t          L2Calo_isEMMedium;
  //Bool_t          L2Calo_isEMLoose;
  //Bool_t          L2_isEMTight;
  //Bool_t          L2_isEMMedium;
  //Bool_t          L2_isEMLoose;
  Bool_t          EFCalo_isLHTightCaloOnly_rel21_20170214 ;
  Bool_t          EFCalo_isLHMediumCaloOnly_rel21_20170214;
  Bool_t          EFCalo_isLHLooseCaloOnly_rel21_20170214 ;
  Bool_t          EFCalo_isLHVLooseCaloOnly_rel21_20170214;
  Bool_t          EFCalo_isLHTightCaloOnly_rel21_20170217 ;
  Bool_t          EFCalo_isLHMediumCaloOnly_rel21_20170217;
  Bool_t          EFCalo_isLHLooseCaloOnly_rel21_20170217 ;
  Bool_t          EFCalo_isLHVLooseCaloOnly_rel21_20170217;
  Bool_t          EFCalo_isLHTightCaloOnly_rel21_20170217_mc16a ;
  Bool_t          EFCalo_isLHMediumCaloOnly_rel21_20170217_mc16a;
  Bool_t          EFCalo_isLHLooseCaloOnly_rel21_20170217_mc16a ;
  Bool_t          EFCalo_isLHVLooseCaloOnly_rel21_20170217_mc16a;
  Bool_t          HLT_isLHTight_rel21_20170214 ;
  Bool_t          HLT_isLHMedium_rel21_20170214;
  Bool_t          HLT_isLHLoose_rel21_20170214 ;
  Bool_t          HLT_isLHVLoose_rel21_20170214;
  Bool_t          HLT_isLHTight_rel21_20170217 ;
  Bool_t          HLT_isLHMedium_rel21_20170217;
  Bool_t          HLT_isLHLoose_rel21_20170217 ;
  Bool_t          HLT_isLHVLoose_rel21_20170217;
  Bool_t          HLT_isLHTight_rel21_20170217_mc16a ;
  Bool_t          HLT_isLHMedium_rel21_20170217_mc16a;
  Bool_t          HLT_isLHLoose_rel21_20170217_mc16a ;
  Bool_t          HLT_isLHVLoose_rel21_20170217_mc16a;
  Bool_t          HLT_isLHTightNoD0_rel21_20170214 ;
  Bool_t          HLT_isLHMediumNoD0_rel21_20170214;
  Bool_t          HLT_isLHLooseNoD0_rel21_20170214 ;
  Bool_t          HLT_isLHVLooseNoD0_rel21_20170214;
  Bool_t          HLT_isLHTightNoD0_rel21_20170217 ;
  Bool_t          HLT_isLHMediumNoD0_rel21_20170217;
  Bool_t          HLT_isLHLooseNoD0_rel21_20170217 ;
  Bool_t          HLT_isLHVLooseNoD0_rel21_20170217;
  Bool_t          HLT_isLHTightNoD0_rel21_20170217_mc16a ;
  Bool_t          HLT_isLHMediumNoD0_rel21_20170217_mc16a;
  Bool_t          HLT_isLHLooseNoD0_rel21_20170217_mc16a ;
  Bool_t          HLT_isLHVLooseNoD0_rel21_20170217_mc16a;
  Bool_t          EFCalo_isEMTight;
  Bool_t          EFCalo_isEMMedium;
  Bool_t          EFCalo_isEMLoose;
  Bool_t          HLT_isEMTight;
  Bool_t          HLT_isEMMedium;
  Bool_t          HLT_isEMLoose;


  Bool_t          trig_L1_calo_accept;
  Bool_t          trig_L2_calo_accept;
  Bool_t          trig_L2_el_accept;
  Bool_t          trig_EF_calo_accept;
  Bool_t          trig_EF_el_accept;
  Bool_t          trig_EF_calo_isLHTightCaloOnly_rel21_20170217 ;
  Bool_t          trig_EF_calo_isLHMediumCaloOnly_rel21_20170217;
  Bool_t          trig_EF_calo_isLHLooseCaloOnly_rel21_20170217 ;
  Bool_t          trig_EF_calo_isLHVLooseCaloOnly_rel21_20170217; 
  Bool_t          trig_EF_el_isLHTight_rel21_20170217 ;
  Bool_t          trig_EF_el_isLHMedium_rel21_20170217;
  Bool_t          trig_EF_el_isLHLoose_rel21_20170217 ;
  Bool_t          trig_EF_el_isLHVLoose_rel21_20170217; 
  Bool_t          trig_EF_el_isLHTightNoD0_rel21_20170217 ;
  Bool_t          trig_EF_el_isLHMediumNoD0_rel21_20170217;
  Bool_t          trig_EF_el_isLHLooseNoD0_rel21_20170217 ;
  Bool_t          trig_EF_el_isLHVLooseNoD0_rel21_20170217;
 
  //ClassDef(RingerPhysVal,1;;
};

#endif // TUNINGTOOLS_RINGERPHYSVAL_H


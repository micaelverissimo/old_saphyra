#ifndef TUNINGTOOLS_RINGERPHYSVAL_V2_H
#define TUNINGTOOLS_RINGERPHYSVAL_V2_H
#include <vector>
#include <string>
#include "Rtypes.h"
//#include "TObject.h"

struct RingerPhysVal_v2 /*: public TObject*/ {

   

    /* Branch variables */
    uint32_t            RunNumber{};
    unsigned long long  EventNumber{};
    float               avgmu{};    
    float               LumiBlock{};    
   
    /* Egamma */
     
    bool                el_hasCalo   ;
    bool                el_hasTrack  ;
    float               el_e;
    float               el_et;
    float               el_eta;
    float               el_phi;
    float               el_ethad1;
    float               el_ehad1;
    float               el_f1;
    float               el_f3;
    float               el_f1core;
    float               el_f3core;
    float               el_weta1;
    float               el_weta2;
    float               el_wtots1;
    float               el_fracs1;
    float               el_Reta;
    float               el_Rphi;
    float               el_Eratio;
    float               el_Rhad;
    float               el_Rhad1;
    float               el_deta1;
    float               el_deta2;
    float               el_dphi2;
    float               el_dphiresc;
    float               el_deltaPhiRescaled2;
    float               el_deltaEta1;
    float               el_deltaE;
    float               el_e277;
    std::vector<float> *el_etCone;
    std::vector<float> *el_ptCone;
   
    

    float               el_trk_pt;
    float               el_trk_eta; 
    float               el_trk_charge; 
    float               el_trk_sigd0;
    float               el_trk_d0;
    float               el_trk_eProbabilityHT;
    float               el_trk_transformed_eProbabilityHT;
    float               el_trk_d0significance;
    float               el_trk_deltaPOverP;
    float               el_trk_qOverP;
    std::vector<uint8_t> *el_trk_summaryValues;

    bool                el_loose{};
    bool                el_medium{};
    bool                el_tight{};
    bool                el_lhvloose{};
    bool                el_lhloose{};
    bool                el_lhmedium{};
    bool                el_lhtight{}; 
    bool                el_multiLepton{};
    std::vector<float> *el_ringsE;
    int                 el_nGoodVtx{};
    int                 el_nPileupPrimaryVtx{};
    ///Egamma Calo
    float               el_calo_et{};
    float               el_calo_eta{};
    float               el_calo_phi{};
    float               el_calo_etaBE2{};
    float               el_calo_e{};
    // Level 1     
    float               trig_L1_eta{};
    float               trig_L1_phi{};
    float               trig_L1_emClus{};
    float               trig_L1_tauClus{};
    float               trig_L1_emIsol{};
    float               trig_L1_hadIsol{};
    float               trig_L1_hadCore{};
    std::vector<std::string> *m_trig_L1_thrNames;          

    // Level 2 Calo
    float               trig_L2_calo_et{};         
    float               trig_L2_calo_eta{};        
    float               trig_L2_calo_phi{};        
    float               trig_L2_calo_e237{};       
    float               trig_L2_calo_e277{};      
    float               trig_L2_calo_fracs1{};     
    float               trig_L2_calo_weta2{};      
    float               trig_L2_calo_ehad1{};      
    float               trig_L2_calo_emaxs1{};     
    float               trig_L2_calo_e2tsts1{};    
    float               trig_L2_calo_wstot{};      
    float               trig_L2_calo_nnOutput{};      
    std::vector<float> *trig_L2_calo_energySample;
    std::vector<float> *trig_L2_calo_rings;
    std::vector<float> *trig_L2_calo_rnnOutput;
    // level 2 id
    std::vector<int>   *trig_L2_el_trackAlgID;          
    std::vector<float> *trig_L2_el_pt;          
    std::vector<float> *trig_L2_el_caloEta;         
    std::vector<float> *trig_L2_el_eta;         
    std::vector<float> *trig_L2_el_phi;         
    std::vector<float> *trig_L2_el_charge;      
    std::vector<float> *trig_L2_el_nTRTHits;        
    std::vector<float> *trig_L2_el_nTRTHiThresholdHits;        
    std::vector<float> *trig_L2_el_etOverPt;          
    std::vector<float> *trig_L2_el_trkClusDeta; 
    std::vector<float> *trig_L2_el_trkClusDphi;
   
    // EFCalo and HLT steps
    
    std::vector<float>               *trig_EF_calo_e;
    std::vector<float>               *trig_EF_calo_et;
    std::vector<float>               *trig_EF_calo_eta;
    std::vector<float>               *trig_EF_calo_phi;
    std::vector<float>               *trig_EF_calo_etaBE2;
    
    std::vector<float>               *trig_EF_el_calo_e;
    std::vector<float>               *trig_EF_el_calo_et;
    std::vector<float>               *trig_EF_el_calo_eta;
    std::vector<float>               *trig_EF_el_calo_phi;
    std::vector<float>               *trig_EF_el_calo_etaBE2;
    
    std::vector<float>               *trig_EF_el_e;
    std::vector<float>               *trig_EF_el_et;
    std::vector<float>               *trig_EF_el_eta;
    std::vector<float>               *trig_EF_el_phi;
    std::vector<float>               *trig_EF_el_ethad1;
    std::vector<float>               *trig_EF_el_ehad1;
    std::vector<float>               *trig_EF_el_f1;
    std::vector<float>               *trig_EF_el_f3;
    std::vector<float>               *trig_EF_el_f1core;
    std::vector<float>               *trig_EF_el_f3core;
    std::vector<float>               *trig_EF_el_weta1;
    std::vector<float>               *trig_EF_el_weta2;
    std::vector<float>               *trig_EF_el_wtots1;
    std::vector<float>               *trig_EF_el_fracs1;
    std::vector<float>               *trig_EF_el_Reta;
    std::vector<float>               *trig_EF_el_Rphi;
    std::vector<float>               *trig_EF_el_Eratio;
    std::vector<float>               *trig_EF_el_Rhad;
    std::vector<float>               *trig_EF_el_Rhad1;
    std::vector<float>               *trig_EF_el_deta2;
    std::vector<float>               *trig_EF_el_dphi2;
    std::vector<float>               *trig_EF_el_dphiresc;
    std::vector<float>               *trig_EF_el_e277;
    std::vector<float>               *trig_EF_el_deltaPhiRescaled2;
    std::vector<float>               *trig_EF_el_deltaEta1;
    std::vector<float>               *trig_EF_el_deltaE;
    std::vector<float>               *trig_EF_el_etCone;
    std::vector<float>               *trig_EF_el_ptCone;
    
   
    std::vector<float>               *trig_EF_el_trk_pt;
    std::vector<float>               *trig_EF_el_trk_eta; 
    std::vector<float>               *trig_EF_el_trk_charge; 
    std::vector<float>               *trig_EF_el_trk_sigd0;
    std::vector<float>               *trig_EF_el_trk_d0;
    std::vector<float>               *trig_EF_el_trk_eProbabilityHT;
    std::vector<float>               *trig_EF_el_trk_transformed_eProbabilityHT;
    std::vector<float>               *trig_EF_el_trk_d0significance;
    std::vector<float>               *trig_EF_el_trk_deltaPOverP;
    std::vector<float>               *trig_EF_el_trk_qOverP;
    std::vector<uint8_t>             *trig_EF_el_trk_summaryValues;

   
    std::vector<bool>                *trig_EF_el_hasCalo   ;
    std::vector<bool>                *trig_EF_el_hasTrack  ;
 

    
    std::vector<bool>                *trig_EF_el_loose;
    std::vector<bool>                *trig_EF_el_medium;
    std::vector<bool>                *trig_EF_el_tight;
    std::vector<bool>                *trig_EF_el_lhvloose;
    std::vector<bool>                *trig_EF_el_lhloose;
    std::vector<bool>                *trig_EF_el_lhmedium;
    std::vector<bool>                *trig_EF_el_lhtight; 
    std::vector<bool>                *trig_EF_calo_loose;
    std::vector<bool>                *trig_EF_calo_medium;
    std::vector<bool>                *trig_EF_calo_tight;
    std::vector<bool>                *trig_EF_calo_lhvloose;
    std::vector<bool>                *trig_EF_calo_lhloose;
    std::vector<bool>                *trig_EF_calo_lhmedium;
    std::vector<bool>                *trig_EF_calo_lhtight; 
 
    std::vector<int>                 *trig_tdt_L1_calo_accept;
    std::vector<int>                 *trig_tdt_L2_calo_accept;
    std::vector<int>                 *trig_tdt_L2_el_accept  ;
    std::vector<int>                 *trig_tdt_EF_calo_accept;
    std::vector<int>                 *trig_tdt_EF_el_accept  ;
    std::vector<int>                 *trig_tdt_emu_L1_calo_accept;
    std::vector<int>                 *trig_tdt_emu_L2_calo_accept;
    std::vector<int>                 *trig_tdt_emu_L2_el_accept  ;
    std::vector<int>                 *trig_tdt_emu_EF_calo_accept;
    std::vector<int>                 *trig_tdt_emu_EF_el_accept  ;



    // Monte Carlo
    bool                mc_hasMC{}     ;
    float               mc_pt{}        ;
    float               mc_eta{}       ;
    float               mc_phi{}       ;
    bool                mc_isTop{}     ;
    bool                mc_isParton{}  ;
    bool                mc_isMeson{}   ;
    bool                mc_isQuark{}   ;
    bool                mc_isTau{}     ;
    bool                mc_isMuon{}    ;
    bool                mc_isPhoton{}  ;
    bool                mc_isElectron{};

    int                 mc_type{};
    int                 mc_origin{};
    bool                mc_isTruthElectronFromZ{};
    bool                mc_isTruthElectronFromW{};
    bool                mc_isTruthElectronFromJpsi{};
    bool                mc_isTruthElectronAny{};






  //ClassDef(RingerPhysVal,1;;
};

#endif // TUNINGTOOLS_RINGERPHYSVAL_H


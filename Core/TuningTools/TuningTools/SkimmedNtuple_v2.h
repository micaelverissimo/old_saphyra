#ifndef TUNINGTOOLS_SKIMMEDNTUPLE_V2_H
#define TUNINGTOOLS_SKIMMEDNTUPLE_V2_H

#include <TROOT.h>

// Header file for the classes stored in the TTree if any.
#include "vector"

class SkimmedNtuple_v2 {
public :

  
  int   EventNumber                           ; 
  int   RunNumber                             ; 
  int   Nvtx                                  ; 
  int   RandomRunNumber                       ; 
  int   MCChannelNumber                       ; 
  int   RandomLumiBlockNumber                 ; 
  float actualIntPerXing                      ; 
  float averageIntPerXing                     ; 
  float VertexZPosition                       ; 
  float MCPileupWeight                        ; 


	//! Probe branches 
  int   elCand2_type                          ; 
  int   elCand2_origin                        ; 
  int   elCand2_isTruthElectronFromZ          ; 
  int   elCand2_isTruthElectronAny            ; 
  int   elCand2_isTruthElectronFromW          ; 
  int   elCand2_isTruthElectronFromJpsiPrompt ;
  float elCand2_el_calo_eta                   ; 
  float elCand2_el_calo_pt                    ; 
  float elCand2_el_e                          ; 
  float elCand2_el_eta                        ; 
  float elCand2_el_etas2                      ; 
  float elCand2_el_phi                        ; 
  float elCand2_el_et                         ; 
  float elCand2_el_pt                         ; 
  float elCand2_el_charge                     ; 
  float elCand2_el_etcone20                   ; 
  float elCand2_el_etcone30                   ; 
  float elCand2_el_etcone40                   ; 
  float elCand2_el_ptcone20                   ; 
  float elCand2_el_ptcone30                   ; 
  float elCand2_el_ptcone40                   ; 
  float elCand2_el_ptvarcone20                ; 
  float elCand2_el_ptvarcone30                ; 
  float elCand2_el_ptvarcone40                ; 
  float elCand2_el_topoetcone20               ;
  float elCand2_el_topoetcone30               ;
  float elCand2_el_topoetcone40               ;
  float elCand2_el_e233                       ; 
  float elCand2_el_e237                       ; 
  float elCand2_el_e277                       ; 
  float elCand2_el_ethad                      ; 
  float elCand2_el_ethad1                     ; 
  float elCand2_el_f1                         ; 
  float elCand2_el_f3                         ; 
  float elCand2_el_weta2                      ; 
  float elCand2_el_wtots1                     ; 
  float elCand2_el_emins1                     ; 
  float elCand2_el_emaxs1                     ; 
  float elCand2_el_e2tsts1                    ; 
  float elCand2_el_fracs1                     ; 
  float elCand2_el_reta                       ; 
  float elCand2_el_rhad0                      ; 
  float elCand2_el_rhad1                      ; 
  float elCand2_el_rhad                       ; 
  float elCand2_el_rphi                       ; 
  float elCand2_el_eratio                     ; 
  float elCand2_el_deltaEta1                  ; 
  float elCand2_el_deltaEta2                  ; 
  float elCand2_el_deltaPhi1                  ; 
  float elCand2_el_deltaPhi2                  ; 
  float elCand2_el_d0                         ; 
  float elCand2_el_sigd0                      ; 
  float elCand2_el_z0                         ; 
  float elCand2_el_EOverP                     ; 
  float elCand2_el_passd0z0                   ; 
  float elCand2_el_z0sinTheta                 ; 
  float elCand2_el_d0significance             ;
  float elCand2_el_deltaPhiRescaled2          ;
  float elCand2_el_deltaPhiFromLM             ; 
  std::vector<float> *elCand2_el_calo_ringsE   ;


  int   elCand2_el_trk_numberOfInnermostPixelLayerHits          ; 
  int   elCand2_el_trk_numberOfInnermostPixelLayerOutliers      ; 
  int   elCand2_el_trk_expectInnermostPixelLayerHit             ; 
  int   elCand2_el_trk_numberOfNextToInnermostPixelLayerHits    ; 
  int   elCand2_el_trk_numberOfNextToInnermostPixelLayerOutliers; 
  int   elCand2_el_trk_expectNextToInnermostPixelLayerHit       ; 
  int   elCand2_el_trk_numberOfBLayerHits                       ; 
  int   elCand2_el_trk_numberOfBLayerOutliers                   ; 
  int   elCand2_el_trk_expectBLayerHit                          ; 
  int   elCand2_el_trk_numberOfPixelHits                        ; 
  int   elCand2_el_trk_numberOfPixelOutliers                    ; 
  int   elCand2_el_trk_numberOfPixelDeadSensors                 ; 
  int   elCand2_el_trk_numberOfSCTHits                          ; 
  int   elCand2_el_trk_numberOfSCTOutliers                      ; 
  int   elCand2_el_trk_numberOfSCTDeadSensors                   ; 
  int   elCand2_el_trk_numberOfTRTHits                          ; 
  int   elCand2_el_trk_numberOfTRTOutliers                      ; 
  int   elCand2_el_trk_numberOfTRTHighThresholdHits             ; 
  int   elCand2_el_trk_numberOfTRTHighThresholdOutliers         ; 
  int   elCand2_el_trk_numberOfTRTDeadStraws                    ; 
  int   elCand2_el_trk_numberOfTRTXenonHits                     ; 
  float elCand2_el_trk_TRTHighTOutliersRatio                    ; 
  float elCand2_el_trk_eProbabilityHT                           ; 
  float elCand2_el_trk_DeltaPOverP                              ; 
  float elCand2_el_trk_pTErr                                    ; 
  float elCand2_el_trk_deltaCurvOverErrCurv                     ; 
  float elCand2_el_trk_deltaDeltaPhiFirstAndLM                  ; 
  float elCand2_el_trk_z0significance                           ; 
  float elCand2_el_trk_qoverp                                   ; 
  float elCand2_el_trk_qoverpsignificance                       ; 
  float elCand2_el_trk_chi2oftrackmatch                         ; 
  float elCand2_el_trk_ndftrackmatch                            ; 
 
  int   elCand2_trig_EF_el_match                                ; 
  float elCand2_trig_EF_calo_eta                                ; 
  float elCand2_trig_EF_calo_pt                                 ; 
  float elCand2_trig_EF_el_e                                    ; 
  float elCand2_trig_EF_el_eta                                  ; 
  float elCand2_trig_EF_el_etas2                                ; 
  float elCand2_trig_EF_el_phi                                  ; 
  float elCand2_trig_EF_el_et                                   ; 
  float elCand2_trig_EF_el_pt                                   ; 
  float elCand2_trig_EF_el_charge                               ; 
  float elCand2_trig_EF_el_etcone20                             ; 
  float elCand2_trig_EF_el_etcone30                             ; 
  float elCand2_trig_EF_el_etcone40                             ; 
  float elCand2_trig_EF_el_ptcone20                             ; 
  float elCand2_trig_EF_el_ptcone30                             ; 
  float elCand2_trig_EF_el_ptcone40                             ; 
  float elCand2_trig_EF_el_ptvarcone20                          ; 
  float elCand2_trig_EF_el_ptvarcone30                          ; 
  float elCand2_trig_EF_el_ptvarcone40                          ; 
  float elCand2_trig_EF_el_topoetcone20                         ;
  float elCand2_trig_EF_el_topoetcone30                         ;
  float elCand2_trig_EF_el_topoetcone40                         ;

  float elCand2_trig_EF_el_e233                                 ; 
  float elCand2_trig_EF_el_e237                                 ; 
  float elCand2_trig_EF_el_e277                                 ; 
  float elCand2_trig_EF_el_ethad                                ; 
  float elCand2_trig_EF_el_ethad1                               ; 
  float elCand2_trig_EF_el_f1                                   ; 
  float elCand2_trig_EF_el_f3                                   ; 
  float elCand2_trig_EF_el_weta2                                ; 
  float elCand2_trig_EF_el_wtots1                               ; 
  float elCand2_trig_EF_el_emins1                               ; 
  float elCand2_trig_EF_el_emaxs1                               ; 
  float elCand2_trig_EF_el_e2tsts1                              ; 
  float elCand2_trig_EF_el_fracs1                               ; 
  float elCand2_trig_EF_el_reta                                 ; 
  float elCand2_trig_EF_el_rhad0                                ; 
  float elCand2_trig_EF_el_rhad1                                ; 
  float elCand2_trig_EF_el_rhad                                 ; 
  float elCand2_trig_EF_el_rphi                                 ; 
  float elCand2_trig_EF_el_eratio                               ; 
  float elCand2_trig_EF_el_deltaEta1                            ; 
  float elCand2_trig_EF_el_deltaEta2                            ; 
  float elCand2_trig_EF_el_deltaPhi1                            ; 
  float elCand2_trig_EF_el_deltaPhi2                            ; 
  float elCand2_trig_EF_el_d0                                   ; 
  float elCand2_trig_EF_el_sigd0                                ; 
  float elCand2_trig_EF_el_z0                                   ; 
  float elCand2_trig_EF_el_EOverP                               ; 
  float elCand2_trig_EF_el_passd0z0                             ; 
  float elCand2_trig_EF_el_z0sinTheta                           ; 
  float elCand2_trig_EF_el_d0significance                       ; 
  float elCand2_trig_EF_el_deltaPhiRescaled2                    ;
  float elCand2_trig_EF_el_deltaPhiFromLM                       ; 
 
  int   elCand2_trig_EF_el_trk_numberOfInnermostPixelLayerHits           ;  
  int   elCand2_trig_EF_el_trk_numberOfInnermostPixelLayerOutliers       ;  
  int   elCand2_trig_EF_el_trk_expectInnermostPixelLayerHit              ;  
  int   elCand2_trig_EF_el_trk_numberOfNextToInnermostPixelLayerHits     ;  
  int   elCand2_trig_EF_el_trk_numberOfNextToInnermostPixelLayerOutliers ;  
  int   elCand2_trig_EF_el_trk_expectNextToInnermostPixelLayerHit        ;  
  int   elCand2_trig_EF_el_trk_numberOfBLayerHits                        ;  
  int   elCand2_trig_EF_el_trk_numberOfBLayerOutliers                    ;  
  int   elCand2_trig_EF_el_trk_expectBLayerHit                           ;  
  int   elCand2_trig_EF_el_trk_numberOfPixelHits                         ;  
  int   elCand2_trig_EF_el_trk_numberOfPixelOutliers                     ;  
  int   elCand2_trig_EF_el_trk_numberOfPixelDeadSensors                  ;  
  int   elCand2_trig_EF_el_trk_numberOfSCTHits                           ;  
  int   elCand2_trig_EF_el_trk_numberOfSCTOutliers                       ;  
  int   elCand2_trig_EF_el_trk_numberOfSCTDeadSensors                    ;  
  int   elCand2_trig_EF_el_trk_numberOfTRTHits                           ;  
  int   elCand2_trig_EF_el_trk_numberOfTRTOutliers                       ;  
  int   elCand2_trig_EF_el_trk_numberOfTRTHighThresholdHits              ;  
  int   elCand2_trig_EF_el_trk_numberOfTRTHighThresholdOutliers          ;  
  int   elCand2_trig_EF_el_trk_numberOfTRTDeadStraws                     ;  
  int   elCand2_trig_EF_el_trk_numberOfTRTXenonHits                      ;  
  float elCand2_trig_EF_el_trk_TRTHighTOutliersRatio                     ;  
  float elCand2_trig_EF_el_trk_eProbabilityHT                            ;  
  float elCand2_trig_EF_el_trk_DeltaPOverP                               ;  
  float elCand2_trig_EF_el_trk_pTErr                                     ;  
  float elCand2_trig_EF_el_trk_deltaCurvOverErrCurv                      ;  
  float elCand2_trig_EF_el_trk_deltaDeltaPhiFirstAndLM                   ;  
  float elCand2_trie_EF_el_trk_z0significance                            ;  
  float elCand2_trie_EF_el_trk_qoverp                                    ;  
  float elCand2_trie_EF_el_trk_qoverpsignificance                        ;  
  float elCand2_trie_EF_el_trk_chi2oftrackmatch                          ;   
  float elCand2_trie_EF_el_trk_ndftrackmatch                             ;   
 
  int   elCand2_trig_L2_calo_match        ;
  float elCand2_trig_L2_calo_e            ; 
  float elCand2_trig_L2_calo_eta          ; 
  float elCand2_trig_L2_calo_phi          ; 
  float elCand2_trig_L2_calo_et           ; 
  float elCand2_trig_L2_calo_e237         ; 
  float elCand2_trig_L2_calo_e277         ; 
  float elCand2_trig_L2_calo_ethad        ; 
  float elCand2_trig_L2_calo_ethad1       ; 
  float elCand2_trig_L2_calo_f1           ; 
  float elCand2_trig_L2_calo_f3           ; 
  float elCand2_trig_L2_calo_weta2        ; 
  float elCand2_trig_L2_calo_wtots1       ; 
  float elCand2_trig_L2_calo_emaxs1       ; 
  float elCand2_trig_L2_calo_e2tsts1      ; 
  float elCand2_trig_L2_calo_fracs1       ; 
  float elCand2_trig_L2_calo_reta         ; 
  float elCand2_trig_L2_calo_rhad0        ; 
  float elCand2_trig_L2_calo_rhad1        ; 
  float elCand2_trig_L2_calo_rhad         ; 
  float elCand2_trig_L2_calo_eratio       ; 
  int   elCand2_trig_L2_calo_rings_match  ;
  
  int   elCand2_trig_L1_calo_match              ;
  float elCand2_trig_L1_calo_eta                ;
  float elCand2_trig_L1_calo_phi                ;
  float elCand2_trig_L1_calo_emClus             ;
  float elCand2_trig_L1_calo_tauClus            ;
  float elCand2_trig_L1_calo_emIsol             ;
  float elCand2_trig_L1_calo_hadIsol            ;
  float elCand2_trig_L1_calo_hadCore            ;
  int   elCand2_trig_L2_el_match                ;
  float elCand2_trig_L2_el_pt                   ;
  float elCand2_trig_L2_el_eta                  ;
  float elCand2_trig_L2_el_phi                  ;
  int   elCand2_trig_L2_el_nTRTHits             ;
  int   elCand2_trig_L2_el_nTRTHiThresholdHits  ;
  float elCand2_trig_L2_el_etOverPt             ;
  float elCand2_trig_L2_el_trkClusDeta          ;
  float elCand2_trig_L2_el_trkClusDphi          ;


  std::vector<float> *elCand2_trig_L2_calo_ringsE;


  int elCand1_trig_L2_TightLLH_Run2_2018_CutBased;
  int elCand1_trig_L2_MediumLLH_Run2_2018_CutBased;
  int elCand1_trig_L2_LooseLLH_Run2_2018_CutBased;
  int elCand1_trig_L2_VeryLooseLLH_Run2_2018_CutBased;
  int elCand2_trig_L2_TightLLH_Run2_2018_CutBased;
  int elCand2_trig_L2_MediumLLH_Run2_2018_CutBased;
  int elCand2_trig_L2_LooseLLH_Run2_2018_CutBased;
  int elCand2_trig_L2_VeryLooseLLH_Run2_2018_CutBased;
 

  int elCand1_TightLLH_DataDriven_Rel21_Run2_2018                 ; 
  int elCand1_MediumLLH_DataDriven_Rel21_Run2_2018                ; 
  int elCand1_LooseLLH_DataDriven_Rel21_Run2_2018                 ; 
  int elCand1_VeryLooseLLH_DataDriven_Rel21_Run2_2018             ; 
  int elCand1_trig_EF_TightLLH_DataDriven_Rel21_Run2_2018         ; 
  int elCand1_trig_EF_MediumLLH_DataDriven_Rel21_Run2_2018        ; 
  int elCand1_trig_EF_LooseLLH_DataDriven_Rel21_Run2_2018         ; 
  int elCand1_trig_EF_VeryLooseLLH_DataDriven_Rel21_Run2_2018     ; 
  int elCand1_VeryLooseLLH_DataDriven_Rel21_Smooth_vTest          ; 
  int elCand1_LooseLLH_DataDriven_Rel21_Smooth_vTest              ; 
  int elCand1_LooseAndBLayerLLH_DataDriven_Rel21_Smooth_vTest     ; 
  int elCand1_MediumLLH_DataDriven_Rel21_Smooth_vTest             ; 
  int elCand1_TightLLH_DataDriven_Rel21_Smooth_vTest              ; 
  int elCand1_VeryLooseLLH_d0z0_DataDriven_Rel21_Smooth_vTest     ; 
  int elCand1_LooseLLH_d0z0_DataDriven_Rel21_Smooth_vTest         ; 
  int elCand1_LooseAndBLayerLLH_d0z0_DataDriven_Rel21_Smooth_vTest; 
  int elCand1_MediumLLH_d0z0_DataDriven_Rel21_Smooth_vTest        ; 
  int elCand1_TightLLH_d0z0_DataDriven_Rel21_Smooth_vTest         ; 
  int elCand1_trig_EF_VeryLooseLLH_z0offlineMatch_Smooth_Probe    ;
  int elCand1_PassTrackQuality                                    ;



  int elCand2_TightLLH_DataDriven_Rel21_Run2_2018                 ; 
  int elCand2_MediumLLH_DataDriven_Rel21_Run2_2018                ; 
  int elCand2_LooseLLH_DataDriven_Rel21_Run2_2018                 ; 
  int elCand2_VeryLooseLLH_DataDriven_Rel21_Run2_2018             ; 
  int elCand2_trig_EF_TightLLH_DataDriven_Rel21_Run2_2018         ; 
  int elCand2_trig_EF_MediumLLH_DataDriven_Rel21_Run2_2018        ; 
  int elCand2_trig_EF_LooseLLH_DataDriven_Rel21_Run2_2018         ; 
  int elCand2_trig_EF_VeryLooseLLH_DataDriven_Rel21_Run2_2018     ; 
  int elCand2_VeryLooseLLH_DataDriven_Rel21_Smooth_vTest          ; 
  int elCand2_LooseLLH_DataDriven_Rel21_Smooth_vTest              ; 
  int elCand2_LooseAndBLayerLLH_DataDriven_Rel21_Smooth_vTest     ; 
  int elCand2_MediumLLH_DataDriven_Rel21_Smooth_vTest             ; 
  int elCand2_TightLLH_DataDriven_Rel21_Smooth_vTest              ; 
  int elCand2_VeryLooseLLH_d0z0_DataDriven_Rel21_Smooth_vTest     ; 
  int elCand2_LooseLLH_d0z0_DataDriven_Rel21_Smooth_vTest         ; 
  int elCand2_LooseAndBLayerLLH_d0z0_DataDriven_Rel21_Smooth_vTest; 
  int elCand2_MediumLLH_d0z0_DataDriven_Rel21_Smooth_vTest        ; 
  int elCand2_TightLLH_d0z0_DataDriven_Rel21_Smooth_vTest         ; 
  int elCand2_trig_EF_VeryLooseLLH_z0offlineMatch_Smooth_Probe    ;
  int elCand2_PassTrackQuality                                    ;
  

};

#endif // #ifdef TUNINGTOOLS_SKIMMEDNTUPLE_H




runGRIDtuning.py \
 --do-multi-stop 0 \
 -c user.jodafons.config.n5to10.JK.10sorts.inits_20by20 \
 -d user.jodafons.data17_13TeV.AllPeriods.sgn.probes_EGAM1.bkg.VProbes_EGAM7.GRL_v97.npz  \
 -p user.jodafons.ppFile_norm1.GRL_v97.pic.gz \
 -x user.jodafons.crossValid.GRL_v97.pic.gz \
 -r user.jodafons.data17_13TeV.allPeriods.tight_effs.GRL_v97.npz \
 -o user.jodafons.nn.data17_13TeV.AllPeriods.sgn_Zee_EGAM1.bkg_EGAM7.bestSP.Norm1.v8.t0001 \
 --eta-bin 0  \
 --et-bin 3  \
 --excludedSite ANALY_DESY-HH_UCORE ANALY_BNL_MCORE ANALY_MWT2_SL6 ANALY_MWT2_HIMEM  ANALY_DESY-HH ANALY_FZK_UCORE ANALY_FZU DESY-HH_UCORE FZK-LCG2_UCORE \
 --multi-files \
 #--dry-run
 
 #-mt \
 #--cloud US \

 #-cloud CERN \
 #--memory 17010 \





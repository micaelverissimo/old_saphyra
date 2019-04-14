


runGRIDtuning.py \
 --do-multi-stop 0 \
 -c user.jodafons.config.n5to10.JK.10sorts.inits_20by20 \
 -d user.jodafons.mc16d_13TeV.sgn_Jpsie3e3_truth.bkg_minbias_truth.r10210.npz  \
 -p user.jodafons.ppFile.Norm1.pic.gz \
 -x user.jodafons.crossValid.10sorts.pic.gz \
 -r user.jodafons.mc16d_13TeV.sgn_Jpsie3e3_truth.bkg_minbias_truth.r10210.tight-eff.npz \
 -o user.jodafons.nn.mc16d_14TeV.sgn_Jpsie3e_truth.bkg_minbias_truth.bestSP.Norm1.v1_jpsi.t0003 \
 --eta-bin 1 4 \
 --et-bin 0 2  \
 --excludedSite ANALY_DESY-HH_UCORE ANALY_BNL_MCORE ANALY_MWT2_SL6 ANALY_MWT2_HIMEM  ANALY_DESY-HH ANALY_FZK_UCORE ANALY_FZU DESY-HH_UCORE FZK-LCG2_UCORE \
 --cloud CERN \
 --development \
 #--dry-run
 
 #-mt \
 #--cloud US \


 #--memory 17010 \





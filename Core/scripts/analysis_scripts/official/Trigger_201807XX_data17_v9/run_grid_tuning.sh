


runGRIDtuning.py \
 --do-multi-stop 0 \
 -c user.mverissi.configs.n5to10.jk.inits_20by20_v9 \
 -d user.jodafons.data17-18_13TeV.sgn_lhmedium_probes.EGAM1.bkg.vetolhvloose.EGAM7.samples.npz  \
 -p user.mverissi.ppNorm1.v9.pic.gz \
 -x user.mverissi.crossValid.v9.pic.gz \
 -r user.jodafons.data17-18_13TeV.sgn_lhmedium_probes.EGAM1.bkg.vetolhvloose.EGAM7.samples-eff.npz \
 -o user.jodafons.nn.data17-18_13TeV.AllPeriods.sgn_Zee_EGAM1.bkg_EGAM7.Rel21.bestSP.Norm1.v9.t0002_td \
 --excludedSite ANALY_DESY-HH_UCORE ANALY_BNL_MCORE ANALY_MWT2_SL6 ANALY_MWT2_HIMEM  ANALY_DESY-HH ANALY_FZK_UCORE ANALY_FZU DESY-HH_UCORE FZK-LCG2_UCORE \
 --et-bins 4 \
 --eta-bins 0 \
 --multi-files \
 #--dry-run
 





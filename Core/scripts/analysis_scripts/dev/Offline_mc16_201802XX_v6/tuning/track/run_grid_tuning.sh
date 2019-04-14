
# et 2 eta 0

runGRIDtuning.py \
 --do-multi-stop 0 \
 -c user.jodafons.config.n5to10.JK.10sorts.inits_20by20 \
 -d user.jodafons.mc16a.zee.20M.jf17.20M.offline.binned.track.wdatadrivenlh.npz  \
 -p user.jodafons.ppFile_TrackSimpleNorm.pic.gz \
 -x user.jodafons.crossValid.10sorts.pic.gz \
 -r user.jodafons.mc16a.zee.20M.jf17.20M.offline.binned.track.wdatadrivenlh_eff.npz \
 -o user.jodafons.nn.mc16a.zee.20M.jf17.20M.offline.binned.track.wdatadrivenlh.v6.t0002 \
 --eta-bin 0 8 \
 --et-bin 0 3 \
 --excludedSite ANALY_DESY-HH_UCORE ANALY_BNL_MCORE ANALY_MWT2_SL6 ANALY_MWT2_HIMEM  ANALY_DESY-HH ANALY_FZK_UCORE ANALY_FZU DESY-HH_UCORE FZK-LCG2_UCORE \
 --multi-files \
 #--dry-run







## Rings + track
#runGRIDtuning.py \
# --do-multi-stop 0 \
# -c user.jodafons.config.n5to10.JK.10sorts.inits_20by20 \
# -d user.jodafons.mc16a.zee.20M.jf17.20M.offline.binned.calo.wdatadrivenlh.npz  \
#    user.jodafons.mc16a.zee.20M.jf17.20M.offline.binned.track.wdatadrivenlh.npz  \
# --expert-paths user.jodafons.mc16a.zee.20M.jf17.20M.offline.binned.calo.wdatadrivenlh.v6.crossValStat.pic.gz \
#                user.jodafons.mc16a.zee.20M.jf17.20M.offline.binned.track.wdatadrivenlh.v6.crossValStat.pic.gz \
# -p user.jodafons.ppFile.ExpertNetworksSimpleNorm.pic.gz \
# -x user.jodafons.crossValid.10sorts.pic.gz \
# -r user.jodafons.mc16a.zee.20M.jf17.20M.offline.binned.calo.wdatadrivenlh_eff.npz \
# -o user.jodafons.nn.mc16a.zee.20M.jf17.20M.offline.binned.caloAndTrack.wdatadrivenlh.v6.t0003 \
# -op Offline_LH_DataDriven2016_Rel21_Medium \
# --eta-bin 0 8 \
# --et-bin 0 3 \
# --excludedSite ANALY_DESY-HH_UCORE ANALY_BNL_MCORE ANALY_MWT2_SL6 ANALY_MWT2_HIMEM  ANALY_DESY-HH ANALY_FZK_UCORE ANALY_FZU DESY-HH_UCORE FZK-LCG2_UCORE \
# --multi-files \
# --development \
# #--dry-run



# Rings + Shawer
#runGRIDtuning.py \
# --do-multi-stop 0 \
# -c user.jodafons.config.n5to10.JK.10sorts.inits_20by20 \
# -d user.jodafons.mc16a.zee.20M.jf17.20M.offline.binned.calo.wdatadrivenlh.npz  \
#    user.jodafons.mc16a.zee.20M.jf17.20M.offline.binned.calostd.wdatadrivenlh.npz  \
#    user.jodafons.mc16a.zee.20M.jf17.20M.offline.binned.track.wdatadrivenlh.npz  \
# --expert-paths user.jodafons.mc16a.zee.20M.jf17.20M.offline.binned.calo.wdatadrivenlh.v6.crossValStat.pic.gz \
#                user.jodafons.mc16a.zee.20M.jf17.20M.offline.binned.calostd.wdatadrivenlh.v6.crossValStat.pic.gz \
#                user.jodafons.mc16a.zee.20M.jf17.20M.offline.binned.track.wdatadrivenlh.v6.crossValStat.pic.gz \
# -p user.jodafons.ppFile.ExpertNetworksShowerShapeAndTrackSimpleNorm.pic.gz \
# -x user.jodafons.crossValid.10sorts.pic.gz \
# -r user.jodafons.mc16a.zee.20M.jf17.20M.offline.binned.calo.wdatadrivenlh_eff.npz \
# -o user.jodafons.nn.mc16a.zee.20M.jf17.20M.offline.binned.caloAndShowerShapeAndTrack.wdatadrivenlh.v6.t0005 \
# -op Offline_LH_DataDriven2016_Rel21_Medium \
# --eta-bin 0 8 \
# --et-bin 0 3 \
# --excludedSite ANALY_DESY-HH_UCORE ANALY_BNL_MCORE ANALY_MWT2_SL6 ANALY_MWT2_HIMEM  ANALY_DESY-HH ANALY_FZK_UCORE ANALY_FZU DESY-HH_UCORE FZK-LCG2_UCORE \
# --multi-files \
# --development \
# #--dry-run





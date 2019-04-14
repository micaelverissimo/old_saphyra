


crossValStatAnalysis.py \
  -d ../data/tuning/user.jodafons.nn.mc16a.zee.20M.jf17.20M.offline.binned.calostd.wdatadrivenlh.v6.t0002_td \
  -r ../data/files/mc16calostd_lhgrid_v3/mc16a.zee.20M.jf17.20M.offline.binned.calostd.wdatadrivenlh_eff.2.npz \
  --operation Offline_LH_DataDriven2016_Rel21_Medium \
  --crossFile ../data/files/user.jodafons.crossValid.10sorts.pic.gz/crossValid.10sorts.pic.gz \
  --doMatlab 'True' \
  --doMonitoring 'True' \
  --always-use-SP-network \
  #--output-level DEBUG \
  #--pile-up-ref "nvtx" \
  #--data ../data/files/mc16calo_lhgrid_v3/mc16a.zee.20M.jf17.20M.offline.binned.calo.wdatadrivenlh.npz \
  #--tmpDir "temp.XYZ" \


#crossValStatAnalysis.py \
#  --output-level INFO \
#  -d ../data/crossval/test/user.jodafons.nn.mc16a.zee.20M.jf17.20M.offline.binned.track.wdatadrivenlh.v6.t0001_td/ \
#  -r ../data/files/mc16track_lhgrid_v3/mc16a.zee.20M.jf17.20M.offline.binned.track.wdatadrivenlh_eff.npz \
#  -rocm 0 \
#  -modelm AUC \
#  --binFilters GridJobFilter \
#  --operation Offline_LH_DataDriven2016_Rel21_Medium




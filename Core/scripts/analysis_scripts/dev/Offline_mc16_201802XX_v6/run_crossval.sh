

DATA=data/tuning/user.jodafons.nn.mc16a.zee.20M.jf17.20M.offline.binned.caloHAD3.wdatadrivenlh.v6.t0002_td/

#EM3
command="crossValStatAnalysis.py --output-level INFO -r data/files/mc16calo_lhgrid_v3/mc16a.zee.20M.jf17.20M.offline.binned.calo.wdatadrivenlh_eff.npz --crossFile data/files/user.jodafons.crossValid.10sorts.pic.gz/crossValid.10sorts.pic.gz --operation Offline_LH_DataDriven2016_Rel21_Medium --always-use-SP-network --expandOP"


python run_jobs.py -c $command -n 18 -d $DATA


#crossValStatAnalysis.py \
#  --output-level INFO \
#  -d data/tuning/user.jodafons.nn.mc16a.zee.20M.jf17.20M.offline.binned.caloEM1.wdatadrivenlh.v6.t0002_td/ \
#  -r data/files/mc16calo_lhgrid_v3/mc16a.zee.20M.jf17.20M.offline.binned.calo.wdatadrivenlh_eff.npz \
#  --crossFile data/files/user.jodafons.crossValid.10sorts.pic.gz/crossValid.10sorts.pic.gz \
#  --binFilters GridJobFilter \
#  --operation Offline_LH_DataDriven2016_Rel21_Medium \
#  --always-use-SP-network \
#  #--pile-up-ref "nvtx" \
#  #--data data/files/mc16calo_lhgrid_v3/mc16a.zee.20M.jf17.20M.offline.binned.calo.wdatadrivenlh.npz \




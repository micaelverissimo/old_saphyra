
#python run_popen_jobs.py -c "crossValStatAnalysis.py --doMatlab -r data_cern/files/data/reference-vloose.npz --expandOP --output-level INFO -rocm 0 -modelm AUC --overwrite --doMatlab 0" -d data_cern/tuning/user.jodafons.nn.data17_13TeV.AllPeriods.sgn_Zee_EGAM1.bkg_EGAM7.bestSP.Norm1.v8.t0001_td  -n 20

#python run_popen_jobs.py -c "crossValStatAnalysis.py --doMatlab -r data_cern/files/data/reference-tight.npz --expandOP --output-level INFO -rocm 0 -modelm AUC --overwrite --doMatlab 0" -d data_cern/tuning/user.jodafons.nn.data17_13TeV.AllPeriods.sgn_Zee_EGAM1.bkg_EGAM7.bestSP.Norm1.v8.t0001_td  -n 20
#mkdir tight_v8
#mv crossValStat* tight_v8


#crossValStatAnalysis.py --doMatlab -r data_cern/files/data/reference-tight.npz --expandOP --output-level INFO -d data_cern/tuning/user.jodafons.cnn.data17_13TeV.AllPeriods.sgn_Zee_EGAM1.bkg_EGAM7.bestSP.Norm1Vortex.v10.t0001_td  -rocm 0 -modelm AUC --overwrite --doMatlab 0  --binFilters StandaloneJobBinnedFilter
#mkdir tight_v10
#mv crossValStat* tight_v10


#crossValStatAnalysis.py --doMatlab -r data_cern/files/data/reference-vloose.npz --expandOP --output-level INFO -d data_cern/tuning/user.jodafons.cnn.data17_13TeV.AllPeriods.sgn_Zee_EGAM1.bkg_EGAM7.bestSP.Norm1Vortex.v10.t0001_td  -rocm 0 -modelm AUC --overwrite --doMatlab 0  --binFilters StandaloneJobBinnedFilter







crossValStatAnalysis.py --doMatlab -r data_cern/files/data/reference-tight.npz --expandOP --output-level INFO -d data_cern/tuning/user.jodafons.cnn.data17_13TeV.AllPeriods.sgn_Zee_EGAM1.bkg_EGAM7.bestSP.Norm1Conv1D.v11.t0001_td  -rocm 0 -modelm AUC --overwrite --doMatlab 0  --binFilters StandaloneJobBinnedFilter
mkdir tight_v11
mv crossValStat* tight_v11

crossValStatAnalysis.py --doMatlab -r data_cern/files/data/reference-vloose.npz --expandOP --output-level INFO -d data_cern/tuning/user.jodafons.cnn.data17_13TeV.AllPeriods.sgn_Zee_EGAM1.bkg_EGAM7.bestSP.Norm1Conv1D.v11.t0001_td  -rocm 0 -modelm AUC --overwrite --doMatlab 0  --binFilters StandaloneJobBinnedFilter
mkdir vloose_v11
mv crossValStat* vloose_v11











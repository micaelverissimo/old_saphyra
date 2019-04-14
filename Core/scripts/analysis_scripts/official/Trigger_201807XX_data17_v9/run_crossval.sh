

## v8 zee tuning extraction
#python run_popen_jobs.py -c "crossValStatAnalysis.py -r data/files/data17-18_13TeV.sgn_lhmedium_probes.EGAM1.bkg.vetolhvloose.EGAM7.samples/data17-18_13TeV.sgn_lhmedium_probes.EGAM1.bkg.vetolhvloose.EGAM7.samples-eff.npz --doMatlab --expandOP --output-level INFO -rocm 0 -modelm AUC --overwrite --doMatlab 0 -op L2Calo_CutBased_VLoose" -d data/tuning/user.jodafons.nn.data17_13TeV.AllPeriods.sgn_Zee_EGAM1.bkg_EGAM7.bestSP.Norm1.v8.t0001_td  -n 8
#
#mkdir crossval_vloose
#mv crossVal* crossval_vloose
#
#python run_popen_jobs.py -c "crossValStatAnalysis.py -r data/files/data17-18_13TeV.sgn_lhmedium_probes.EGAM1.bkg.vetolhvloose.EGAM7.samples/data17-18_13TeV.sgn_lhmedium_probes.EGAM1.bkg.vetolhvloose.EGAM7.samples-eff.npz --doMatlab --expandOP --output-level INFO -rocm 0 -modelm AUC --overwrite --doMatlab 0 -op L2Calo_CutBased_Loose" -d data/tuning/user.jodafons.nn.data17_13TeV.AllPeriods.sgn_Zee_EGAM1.bkg_EGAM7.bestSP.Norm1.v8.t0001_td  -n 8
#
#mkdir crossval_loose
#mv crossVal* crossval_loose
#
#python run_popen_jobs.py -c "crossValStatAnalysis.py -r data/files/data17-18_13TeV.sgn_lhmedium_probes.EGAM1.bkg.vetolhvloose.EGAM7.samples/data17-18_13TeV.sgn_lhmedium_probes.EGAM1.bkg.vetolhvloose.EGAM7.samples-eff.npz --doMatlab --expandOP --output-level INFO -rocm 0 -modelm AUC --overwrite --doMatlab 0 -op L2Calo_CutBased_Medium" -d data/tuning/user.jodafons.nn.data17_13TeV.AllPeriods.sgn_Zee_EGAM1.bkg_EGAM7.bestSP.Norm1.v8.t0001_td  -n 8
#
#mkdir crossval_medium
#mv crossVal* crossval_medium
#
#python run_popen_jobs.py -c "crossValStatAnalysis.py -r data/files/data17-18_13TeV.sgn_lhmedium_probes.EGAM1.bkg.vetolhvloose.EGAM7.samples/data17-18_13TeV.sgn_lhmedium_probes.EGAM1.bkg.vetolhvloose.EGAM7.samples-eff.npz --doMatlab --expandOP --output-level INFO -rocm 0 -modelm AUC --overwrite --doMatlab 0 -op L2Calo_CutBased_Tight" -d data/tuning/user.jodafons.nn.data17_13TeV.AllPeriods.sgn_Zee_EGAM1.bkg_EGAM7.bestSP.Norm1.v8.t0001_td  -n 8
#
#mkdir crossval_tight
#mv crossVal* crossval_tight
#
#
#
#
#
## v9 tuning zee extraction
#python run_popen_jobs.py -c "crossValStatAnalysis.py -r data/files/data17-18_13TeV.sgn_lhmedium_probes.EGAM1.bkg.vetolhvloose.EGAM7.samples/data17-18_13TeV.sgn_lhmedium_probes.EGAM1.bkg.vetolhvloose.EGAM7.samples-eff.npz --doMatlab --expandOP --output-level INFO -rocm 0 -modelm AUC --overwrite --doMatlab 0 -op L2Calo_CutBased_VLoose" -d data/tuning/user.jodafons.nn.data17-18_13TeV.AllPeriods.sgn_Zee_EGAM1.bkg_EGAM7.Rel21.bestSP.Norm1.v9.t0001_td_td  -n 7
#
#mkdir crossval_vloose
#mv crossVal* crossval_vloose
#
#python run_popen_jobs.py -c "crossValStatAnalysis.py -r data/files/data17-18_13TeV.sgn_lhmedium_probes.EGAM1.bkg.vetolhvloose.EGAM7.samples/data17-18_13TeV.sgn_lhmedium_probes.EGAM1.bkg.vetolhvloose.EGAM7.samples-eff.npz --doMatlab --expandOP --output-level INFO -rocm 0 -modelm AUC --overwrite --doMatlab 0 -op L2Calo_CutBased_Loose" -d data/tuning/user.jodafons.nn.data17-18_13TeV.AllPeriods.sgn_Zee_EGAM1.bkg_EGAM7.Rel21.bestSP.Norm1.v9.t0001_td_td  -n 7
#
#mkdir crossval_loose
#mv crossVal* crossval_loose
#
#python run_popen_jobs.py -c "crossValStatAnalysis.py -r data/files/data17-18_13TeV.sgn_lhmedium_probes.EGAM1.bkg.vetolhvloose.EGAM7.samples/data17-18_13TeV.sgn_lhmedium_probes.EGAM1.bkg.vetolhvloose.EGAM7.samples-eff.npz --doMatlab --expandOP --output-level INFO -rocm 0 -modelm AUC --overwrite --doMatlab 0 -op L2Calo_CutBased_Medium" -d data/tuning/user.jodafons.nn.data17-18_13TeV.AllPeriods.sgn_Zee_EGAM1.bkg_EGAM7.Rel21.bestSP.Norm1.v9.t0001_td_td  -n 7
#
#mkdir crossval_medium
#mv crossVal* crossval_medium
#
#python run_popen_jobs.py -c "crossValStatAnalysis.py -r data/files/data17-18_13TeV.sgn_lhmedium_probes.EGAM1.bkg.vetolhvloose.EGAM7.samples/data17-18_13TeV.sgn_lhmedium_probes.EGAM1.bkg.vetolhvloose.EGAM7.samples-eff.npz --doMatlab --expandOP --output-level INFO -rocm 0 -modelm AUC --overwrite --doMatlab 0 -op L2Calo_CutBased_Tight" -d data/tuning/user.jodafons.nn.data17-18_13TeV.AllPeriods.sgn_Zee_EGAM1.bkg_EGAM7.Rel21.bestSP.Norm1.v9.t0001_td_td  -n 7
#
#mkdir crossval_tight
#mv crossVal* crossval_tight


# v9 tuning jpsi extraction
python run_popen_jobs.py -c "crossValStatAnalysis.py -r data/files/data17-18_13TeV.sgn_lhmedium_probes.EGAM2.bkg.vetolhvloose.EGAM7.samples/data17-18_13TeV.sgn_lhmedium_probes.EGAM2.bkg.vetolhvloose.EGAM7.samples-eff.npz --doMatlab --expandOP --output-level INFO -rocm 0 -modelm AUC --overwrite --doMatlab 0 -op L2Calo_CutBased_VLoose" -d data/tuning/user.mverissi.nn.data17-18_13TeV.AllPeriods.sgn_Jpsi_EGAM2.bkg_EGAM7.Rel21.bestSP.Norm1.v9.t0001_td  -n 7

mkdir crossval_vloose
mv crossVal* crossval_vloose

python run_popen_jobs.py -c "crossValStatAnalysis.py -r data/files/data17-18_13TeV.sgn_lhmedium_probes.EGAM2.bkg.vetolhvloose.EGAM7.samples/data17-18_13TeV.sgn_lhmedium_probes.EGAM2.bkg.vetolhvloose.EGAM7.samples-eff.npz --doMatlab --expandOP --output-level INFO -rocm 0 -modelm AUC --overwrite --doMatlab 0 -op L2Calo_CutBased_Loose" -d data/tuning/user.mverissi.nn.data17-18_13TeV.AllPeriods.sgn_Jpsi_EGAM2.bkg_EGAM7.Rel21.bestSP.Norm1.v9.t0001_td  -n 7

mkdir crossval_loose
mv crossVal* crossval_loose

python run_popen_jobs.py -c "crossValStatAnalysis.py -r data/files/data17-18_13TeV.sgn_lhmedium_probes.EGAM2.bkg.vetolhvloose.EGAM7.samples/data17-18_13TeV.sgn_lhmedium_probes.EGAM2.bkg.vetolhvloose.EGAM7.samples-eff.npz --doMatlab --expandOP --output-level INFO -rocm 0 -modelm AUC --overwrite --doMatlab 0 -op L2Calo_CutBased_Medium" -d data/tuning/user.mverissi.nn.data17-18_13TeV.AllPeriods.sgn_Jpsi_EGAM2.bkg_EGAM7.Rel21.bestSP.Norm1.v9.t0001_td  -n 7

mkdir crossval_medium
mv crossVal* crossval_medium

python run_popen_jobs.py -c "crossValStatAnalysis.py -r data/files/data17-18_13TeV.sgn_lhmedium_probes.EGAM2.bkg.vetolhvloose.EGAM7.samples/data17-18_13TeV.sgn_lhmedium_probes.EGAM2.bkg.vetolhvloose.EGAM7.samples-eff.npz --doMatlab --expandOP --output-level INFO -rocm 0 -modelm AUC --overwrite --doMatlab 0 -op L2Calo_CutBased_Tight" -d data/tuning/user.mverissi.nn.data17-18_13TeV.AllPeriods.sgn_Jpsi_EGAM2.bkg_EGAM7.Rel21.bestSP.Norm1.v9.t0001_td -n 7

mkdir crossval_tight
mv crossVal* crossval_tight







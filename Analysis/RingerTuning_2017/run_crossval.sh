
# v9 tuning jpsi extraction

python run_popen_jobs.py -c "crossValStatAnalysis.py -r data_cern/files/mc15_13TeV.361106.423300.sgn.probes.bkg.vetotruth.trig.l2calo.vloose-eff.npz --doMatlab --expandOP --output-level INFO -rocm 0 -modelm AUC --overwrite --doMatlab 0 -op L2Calo" -d data_cern/tuning/user.jodafons.nn.mc15c_13TeV.361106.423300.sgn_Zee.bkg_JF17.Rel21.bestSP.Norm1.r0002_td -n 20
mkdir crossval_vloose
mv crossVal* crossval_vloose


python run_popen_jobs.py -c "crossValStatAnalysis.py -r data_cern/files/mc15_13TeV.361106.423300.sgn.probes.bkg.vetotruth.trig.l2calo.loose-eff.npz --doMatlab --expandOP --output-level INFO -rocm 0 -modelm AUC --overwrite --doMatlab 0 -op L2Calo" -d data_cern/tuning/user.jodafons.nn.mc15c_13TeV.361106.423300.sgn_Zee.bkg_JF17.Rel21.bestSP.Norm1.r0002_td -n 20
mkdir crossval_loose
mv crossVal* crossval_loose


python run_popen_jobs.py -c "crossValStatAnalysis.py -r data_cern/files/mc15_13TeV.361106.423300.sgn.probes.bkg.vetotruth.trig.l2calo.medium-eff.npz --doMatlab --expandOP --output-level INFO -rocm 0 -modelm AUC --overwrite --doMatlab 0 -op L2Calo" -d data_cern/tuning/user.jodafons.nn.mc15c_13TeV.361106.423300.sgn_Zee.bkg_JF17.Rel21.bestSP.Norm1.r0002_td -n 20
mkdir crossval_medium
mv crossVal* crossval_medium

python run_popen_jobs.py -c "crossValStatAnalysis.py -r data_cern/files/mc15_13TeV.361106.423300.sgn.probes.bkg.vetotruth.trig.l2calo.tight-eff.npz --doMatlab --expandOP --output-level INFO -rocm 0 -modelm AUC --overwrite --doMatlab 0 -op L2Calo" -d data_cern/tuning/user.jodafons.nn.mc15c_13TeV.361106.423300.sgn_Zee.bkg_JF17.Rel21.bestSP.Norm1.r0002_td -n 20

mkdir crossval_tight
mv crossVal* crossval_tight







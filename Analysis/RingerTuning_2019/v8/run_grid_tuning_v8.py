
command = """run_grid_tuning.py \
      -c user.jodafons.job_config_10sorts_10inits \
      -m user.jodafons.models_mlp_n5to20 \
      -x user.jodafons.StratifiedKFold.10_sorts \
      -d user.jodafons.data17_13TeV.AllPeriods.sgn.probes_lhmedium_EGAM1.bkg.VProbes_EGAM7.GRL_v97_et{et}_eta{eta}.npz \
      -pp user.jodafons.preproc.norm1 \
      --containerImage docker://jodafons/ml-base:latest  \
      -o user.jodafons.data17_13TeV.Allperiods.sgn.probes_lhmedium_EG1.bkg.VProbes_EG7.mlp.ringer_v8_et{et}_eta{eta} \
      -j /home/atlas/saphyra/Analysis/RingerTuning_2019/v8/job_tuning_v8.py \
      --site ANALY_BNL_LONG"""

import os

for etBinIdx in [0,1,2,3,4]:
  for etaBinIdx in [0,1,2,3,4]:


    os.system(command.format(et=etBinIdx, eta=etaBinIdx))

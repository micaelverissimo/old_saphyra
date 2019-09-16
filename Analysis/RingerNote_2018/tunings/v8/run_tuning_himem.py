
command = """run_grid_tuning.py \
      -c user.jodafons.job_config_standard \
      -d user.jodafons.data17_13TeV.AllPeriods.sgn.probes_lhmedium_EGAM1.bkg.VProbes_EGAM7.GRL_V97_et{et}_eta{eta}.npz \
      -r user.jodafons.data17_13TeV.AllPeriods.sgn.probes_lhmedium_EGAM1.bkg.VProbes_EGAM7.GRL_v97_et{et}_eta{eta}.ref.pic.gz \
      --containerImage docker://jodafons/gpu-base:latest  \
      -o user.jodafons.data17_13TeV.Allperiods.sgn.probes_lhmedium_EG1.bkg.VProbes_EG7.mlp.ringer_v8_et{et}_eta{eta}.himem.r01 \
      -j /code/saphyra/Analysis/RingerNote_2018/tunings/v8/job_tuning.py \
      --memory 5000 \
      --site AUTO \
      """

#--site ANALY_BNL_GPU_TEST \
#--memory 8096 \

#--site ANALY_BNL_LONG \

import os

bins = [
    #(1, 0),
    #(1, 1),
    #(1, 3),
    #(2, 0),
    #(2, 1),
    #(2, 3),
    #(3, 0),
    #(3, 1),
    #(3, 3),
    #(4, 0),
    #(4, 1),
    (4, 3),
]







for etBinIdx, etaBinIdx in bins:
    os.system(command.format(et=etBinIdx, eta=etaBinIdx))











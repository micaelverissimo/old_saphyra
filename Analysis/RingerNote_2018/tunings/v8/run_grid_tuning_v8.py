
command = """run_grid_tuning.py \
      -c user.jodafons.job_config_10sorts_10inits_v2 \
      -d user.jodafons.data17_13TeV.AllPeriods.sgn.probes_lhmedium_EGAM1.bkg.VProbes_EGAM7.GRL_v97_et{et}_eta{eta}.npz \
      -r user.jodafons.data17_13TeV.AllPeriods.sgn.probes_lhmedium_EGAM1.bkg.VProbes_EGAM7.GRL_v97_et{et}_eta{eta}.ref.pic.gz \
      --containerImage docker://jodafons/tensorflow:latest  \
      -o user.jodafons.data17_13TeV.Allperiods.sgn.probes_lhmedium_EG1.bkg.VProbes_EG7.mlp.ringer_v8_et{et}_eta{eta}.r30 \
      -j /home/atlas/saphyra/Analysis/RingerTuning_2019/v8/job_grid_tuning_v8.py \
      --site ANALY_MANC_GPU_TEST \
      """

#--site ANALY_BNL_GPU_TEST \
#--memory 8096 \

#--site ANALY_BNL_LONG \

import os

bins = [
    #(0, 0), # here: user.jodafons.data17_13TeV.Allperiods.sgn.probes_lhmedium_EG1.bkg.VProbes_EG7.mlp.ringer_v8_et0_eta0
    #(0, 1),
    #(0, 2),
    #(0, 3),
    #(0, 4),
    #(1, 0),
    ##(1, 1),
    #(1, 2),
    ##(1, 3),
    #(1, 4),
    (2, 0),
    ##(2, 1),
    ##(2, 2),
    ##(2, 3),
    #(2, 4),
    ##(3, 0),
    ##(3, 1),
    ##(3, 2),
    ##(3, 3),
    #(3, 4),
    ##(4, 0),
    ##(4, 1),
    ##(4, 2),
    ##(4, 3),
    #(4, 4),
]







for etBinIdx, etaBinIdx in bins:
    os.system(command.format(et=etBinIdx, eta=etaBinIdx))











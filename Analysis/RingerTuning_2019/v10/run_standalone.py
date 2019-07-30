


command = 'python job_standalone_tuning_v10.py -o user.jodafons.tunedDiscr_v10.et{et}_eta{eta} -d /volume/data/data17_13TeV.AllPeriods.sgn.probes_lhmedium_EGAM1.bkg.VProbes_EGAM7.GRL_v97/data17_13TeV.AllPeriods.sgn.probes_lhmedium_EGAM1.bkg.VProbes_EGAM7.GRL_v97_et{et}_eta{eta}.npz'


et_bins = [0,1,2,3,4]
eta_bins = [0,1,2,3,4]

import os
for et in et_bins:
  for eta in eta_bins:
    os.system(command.format(et=et,eta=eta))




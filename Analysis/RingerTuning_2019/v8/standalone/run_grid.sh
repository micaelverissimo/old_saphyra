prun \
     --exec \
       "sh -c 'python /home/atlas/saphyra/Analysis/RingerTuning_2019/v8/job_grid_tuning_v8.py -o tunedDiscr -d %DATA -c %IN -r %REF';" \
     --excludedSite=ANALY_DESY-HH_UCORE,ANALY_MWT2_SL6,ANALY_MWT2_HIMEM,ANALY_DESY-HH,ANALY_FZK_UCORE,ANALY_FZU,DESY-HH_UCORE,FZK-LCG2_UCORE \
     --outputs=td:tunedDiscr.pic.gz \
     --reusableSecondary=REF,DATA \
     --secondaryDSs=REF:1:user.jodafons.data17_13TeV.AllPeriods.sgn.probes_lhmedium_EGAM1.bkg.VProbes_EGAM7.GRL_v97_et2_eta0.ref.pic.gz,DATA:1:user.jodafons.data17_13TeV.AllPeriods.sgn.probes_lhmedium_EGAM1.bkg.VProbes_EGAM7.GRL_v97_et2_eta0.npz \
     --containerImage=docker://jodafons/tensorflow:latest \
     --excludeFile="*.o,*.so,*.a,*.gch,Download/*,InstallArea/*,RootCoreBin/*,RootCore/*,*new_env_file.sh," \
     --forceStaged \
     --forceStagedSecondary \
     --inDS=user.jodafons.job_config_10sorts_10inits_v2 \
     --nFilesPerJob=1 \
     --noBuild \
     --outDS=user.jodafons.data17_13TeV.Allperiods.sgn.probes_lhmedium_EG1.bkg.VProbes_EG7.mlp.ringer_v8_et0_eta0.r69\
     --site=ANALY_MANC_GPU_TEST \
     --cmtConfig nvidia-gpu \

     #--memory 4096 \
      #--site=ANALY_MANC_GPU_TEST \
#--site=ANALY_MANC_GPU_TEST \
#ANALY_BNL_GPU_TEST
#--site=ANALY_MWT2_GPU \
#--site=ANALY_BNL_MCORE \

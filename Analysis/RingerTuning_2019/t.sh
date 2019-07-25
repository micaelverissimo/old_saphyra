prun \
     --exec \
       "sh -c 'python /home/atlas/saphyra/Core/saphyra/scripts/standalone/job_tuning.py -o tunedDiscr -x %CROSSVAL -d %DATA -m %MODEL -p %PP -c %IN';" \
     --excludedSite=ANALY_DESY-HH_UCORE,ANALY_BNL_MCORE,ANALY_MWT2_SL6,ANALY_MWT2_HIMEM,ANALY_DESY-HH,ANALY_FZK_UCORE,ANALY_FZU,DESY-HH_UCORE,FZK-LCG2_UCORE \
     --outputs=td:tunedDiscr.pic.gz \
     --reusableSecondary=PP,CROSSVAL,MODEL,DATA \
     --secondaryDSs=PP:1:user.jodafons.grid_test_ppFile,CROSSVAL:1:user.jodafons.grid_test_crossValFile,MODEL:1:user.jodafons.grid_test_modelFile,DATA:1:user.jodafons.grid_test_dataFile \
     --containerImage=docker://jodafons/ml-base:latest \
     --excludeFile="*.o,*.so,*.a,*.gch,Download/*,InstallArea/*,RootCoreBin/*,RootCore/*,*new_env_file.sh," \
     --forceStaged \
     --forceStagedSecondary \
     --inDS=user.jodafons.grid_test_jobFile \
     --nFilesPerJob=1 \
     --noBuild \
     --outDS=user.jodafons.grid_test.t0012 \
     --site=AUTO \
     --debug




run_grid_tuning.py \
  -c user.jodafons.grid_test_jobFile \
  -m user.jodafons.grid_test_modelFile \
  -x user.jodafons.grid_test_crossValFile \
  -d user.jodafons.grid_test_dataFile \
  -pp user.jodafons.grid_test_ppFile \
  --containerImage docker://jodafons/ml-base:latest  \
  -o user.jodafons.grid_test.t002o \
  -j /home/atlas/saphyra/Core/saphyra/scripts/standalone/job_tuning.py \
  --site ANALY_BNL_SHORT \
  #--site AUTO \


#run_grid_tuning.py \
#  -c user.jodafons.job_container_10sorts_10inits \
#  -m user.jodafons.model_MLP_hidden_layer_n5to10 \
#  -x user.jodafons.crossval.skf_10sorts \
#  -d user.jodafons.grid_test_dataFile \
#  -pp user.jodafons.pp.norm1 \
#  --containerImage docker://jodafons/ml-base:latest  \
#  -o user.jodafons.grid_test_et4_eta4.t0001 \
#  -j /home/atlas/saphyra/Core/saphyra/scripts/standalone/job_tuning.py \
#  --site ANALY_BNL_SHORT \
#  #--site AUTO \




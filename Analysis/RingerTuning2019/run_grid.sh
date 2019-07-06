
run_grid_tuning.py \
  -c user.jodafons.grid_test_jobFile \
  -m user.jodafons.grid_test_modelFile \
  -x user.jodafons.grid_test_crossValFile \
  -d user.jodafons.grid_test_dataFile \
  -pp user.jodafons.grid_test_ppFile \
  --containerImage docker://jodafons/ml-base:latest  \
  -o user.jodafons.grid_test.t0001 \
  -j job_tuning.py




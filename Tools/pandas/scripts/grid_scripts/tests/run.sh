prun \
     --exec \
       "sh -c 'python /home/atlas/saphyra/saphyra/scripts/tests/cifar10_cnn.py -o tunedDiscr.h5" \
     --outputs=tunedDiscr.h5 \
     --containerImage=docker://jodafons/ml-base:latest \
     --forceStaged \
     --forceStagedSecondary \
     --nFilesPerJob=1 \
     --noBuild \
     --outDS=user.jodafons.job_test.429 \
     --site=AUTO \


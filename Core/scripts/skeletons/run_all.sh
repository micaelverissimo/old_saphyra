
python create_tuningfiles.py
python create_data.py  
mkdir files/
#mv summary.log files
mv  config.* files
mv *.pic.npz files
mv *.pic.gz files
mv *.mat files

python run_tuning.py
cd files
mkdir tuned
cd tuned
mv ../../nn.* .
cd ../..
python create_crossvalid.py




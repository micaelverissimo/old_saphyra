

export Athena_SETUP=off
export LC_ALL=''
export RCM_NO_COLOR=0
export RCM_GRID_ENV=0
export SAPHYRA_PATH=`pwd`



rm -rf .python_dir
mkdir .python_dir
cd .python_dir
mkdir python
cd python
ln -s ../../Gaugi/python Gaugi
ln -s ../../saphyra/python saphyra
ln -s ../../External/orchestra/python orchestra
ln -s ../../External/ringerdb/python ringerdb
ln -s ../../External/monet/python monet
ln -s ../../External/pytex/python pytex
ln -s ../../Tools/panda/python panda

export PYTHONPATH=`pwd`:$PYTHONPATH
cd ../../



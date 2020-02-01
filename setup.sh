

export LC_ALL=''
export RCM_NO_COLOR=0
export RCM_GRID_ENV=0
export SAPHYRA_PATH=`pwd`



rm -rf .pythonpaths
mkdir .pythonpaths
cd .pythonpaths


ln -s ../Gaugi/python Gaugi
ln -s ../saphyra/python saphyra
# ln -s ../External/monet/python monet
# ln -s ../External/pytex/python pytex
#ln -s ../Tools/panda/python panda

export PYTHONPATH=`pwd`:$PYTHONPATH
cd ../



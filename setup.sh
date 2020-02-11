

export LC_ALL=''
export RCM_NO_COLOR=0
export RCM_GRID_ENV=0
export SAPHYRA_PATH=`pwd`

rm -rf .__python__
mkdir .__python__
cd .__python__

ln -s ../Gaugi/python Gaugi
ln -s ../saphyra/python saphyra

export PYTHONPATH=`pwd`:$PYTHONPATH
cd ../



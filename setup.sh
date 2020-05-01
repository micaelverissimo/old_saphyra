

export LC_ALL=''
export RCM_NO_COLOR=0
export RCM_GRID_ENV=0
export SAPHYRA_PATH=`pwd`

source setup_module.sh
source setup_module.sh --head

rm -rf .__python__
mkdir .__python__
cd .__python__

ln -s ../saphyra/python saphyra
ln -s ../external/ringerdb/python ringerdb
ln -s ../external/kolmov/kolmov/python kolmov

export PYTHONPATH=`pwd`:$PYTHONPATH
cd ../



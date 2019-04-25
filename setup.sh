

export LC_ALL=''
export RCM_NO_COLOR=0
export RCM_GRID_ENV=0


cd build
CURRENT_BUILD_DIR=${PWD}
export LD_LIBRARY_PATH=`pwd`:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=`pwd`/Gaugi:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=`pwd`/Core:$LD_LIBRARY_PATH


mkdir python
cd python
ln -s ../../Gaugi/python Gaugi
ln -s ../../Core/python TuningTools



export PYTHONPATH=`pwd`:$PYTHONPATH
cd ../..



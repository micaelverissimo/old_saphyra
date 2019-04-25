

export LC_ALL=''
export RCM_NO_COLOR=0
export RCM_GRID_ENV=0

export CMAKE_PROJECT_PATH=`pwd`


cd build
export LD_LIBRARY_PATH=`pwd`:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=`pwd`/Gaugi:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=`pwd`/Core:$LD_LIBRARY_PATH


mkdir python
cd python
python ../../scripts/setup_python_modules.py
export PYTHONPATH=`pwd`:$PYTHONPATH
cd ../..



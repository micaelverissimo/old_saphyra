#!/bin/bash

export LC_ALL=''
export RCM_NO_COLOR=0
export RCM_GRID_ENV=0

if test ! -d "$PWD/.__python__" ; then
  echo "creating python dir since this does not exist yet..."
  mkdir .__python__
  cd .__python__
  ln -sf ../python saphyra
  cd ..
fi

echo "Setting saphyra envs..."
cd .__python__
export PYTHONPATH=`pwd`:$PYTHONPATH
cd ..









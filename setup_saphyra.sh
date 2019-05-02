#!/bin/bash

cd build
rm -rf lib
mkdir lib
for file in "`pwd`"/**/*.pcm
do
  #echo "$file"
  ln -sf $file lib
done 

for file in "`pwd`"/**/*.so
do
  #echo "$file"
  ln -sf $file lib
done 

export LD_LIBRARY_PATH=`pwd`/lib:$LD_LIBRARY_PATH
export PYTHONPATH=`pwd`:$LD_LIBRARY_PATH
export PYTHONPATH=`pwd`/python:$PYTHONPATH
cd ..


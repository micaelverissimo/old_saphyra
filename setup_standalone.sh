#!/bin/bash
export Athena_SETUP=off
export CPLUS_INCLUDE_PATH="$CPLUS_INCLUDE_PATH:/usr/include/python2.7/"
export LC_ALL=''
export RCM_NO_COLOR=0
export RCM_GRID_ENV=0


ln -sf standalone/CMakeLists.txt CMakeLists.txt

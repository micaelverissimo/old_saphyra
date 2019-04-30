#!/bin/bash
export Athena_SETUP=on

rm CMakeLists.txt
setupATLAS
#asetup 21.2.28,AnalysisBase,setup,here
asetup AnalysisBase,21.2.7,setup,here
#asetup none,gcc62,cmakesetup
#asetup AthAnalysis,latest,setup,here,centos
#asetup Athena,master,latest,setup,here

export LC_ALL=''
export RCM_NO_COLOR=0
export RCM_GRID_ENV=0

#for techlab
export PYTHONPATH=$PYTHONPATH:/usr/lib/python2.7/site-packages
#export PYTHONPATH=$PYTHONPATH:/afs/cern.ch/user/j/jodafons/.local/lib/python2.6/site-packages/


#/usr/lib64/python2.7/site-packages/


#!/bin/sh
filePath="/afs/cern.ch/user/w/wsfreund/public/testOffJob/"
datasetPlace="/afs/cern.ch/user/w/wsfreund/../../../work/w/wsfreund/public/mc14_13TeV.147406.129160.sgn.truth.bkg.truth.off.npy"
output="mc14_13TeV.147406.129160.sgn.truth.bkg.truth.off"
outputPlace="lxplus0010:/tmp/wsfreund/test"
queue="2nd"

# debuggin variables
debug=1
test $debug -eq 1 && set -x
count=0

scriptPlace="$(readlink -f $(dirname "$0"))"
basePlace=$(dirname $(dirname $(dirname "$scriptPlace")))
echo $basePlace
for file in `ls $filePath`
do
  let "count = count + 1"
  echo $file
  fullFilePath=$filePath/$file
  env -i bsub -q $queue -u "" -J "shellTrain" \
    $basePlace/FastNetTool/scripts/grid_submit/bsub_script.sh \
    --jobConfig $fullFilePath \
    --datasetPlace $datasetPlace \
    --output $output \
    --outputPlace $outputPlace \
    --debug
  #test $debug -eq 1 -a $count -eq 3 && break 
done

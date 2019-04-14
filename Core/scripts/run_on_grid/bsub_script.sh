#!/bin/sh

# Default args:
Inits=100
debug=0

STARTUPTIME=$(date +%s%3N)

while true
do
  echo "reading $1 $2"
  if test "$1" == "--datasetPlace"
  then
    DatasetPlace=$2
    echo "Setting DatasetPlace to $DatasetPlace"
    Dataset=`basename $DatasetPlace`
    shift 2
  elif test "$1" == "--jobConfig"
  then
    jobConfig="$2"
    jobFile=$(basename $jobConfig)
    echo "Setting jobConfig to $jobConfig"
    echo "Setting jobFile to $jobFile"
    shift 2
  elif test "$1" == "--ppFile"
  then
    ppFile=$2
    echo "Setting ppFile to $ppFile"
    shift 2
  elif test "$1" == "--crossValidFile"
  then
    crossValidFile=$2
    echo "Setting crossValidFile to $crossValidFile"
    shift 2
  elif test "$1" == "--outputPlace"
  then
    outputPlace="$2"
    outputDestination=${outputPlace%%:*}
    outputFolder=${outputPlace#*:}
    echo "Setting outputPlace to $outputPlace: destination is $outputDestination and folder is $outputFolder"
    shift 2
  elif test "$1" == "--output"
  then
    output="$2"
    echo "Setting output to $output"
    shift 2
  elif test "$1" == "--debug"
  then
    debug=1
    shift
  else
    break
  fi
done

test $debug -eq 1 && set -x

basePath=$PWD

# Check arguments
test "x$DatasetPlace" = "x" -o ! -f "$DatasetPlace" && echo "DatasetPlace \"$DatasetPlace\" doesn't exist" && exit 1;
test "x$jobConfig" = "x" -o ! -f "$jobConfig" && echo "JobConfig file \"$jobConfig\" doesn't exist" && exit 1;

# Retrieve package and compile
git clone https://github.com/joaoVictorPinto/RingerProject
rootFolder=$basePath/Ringer/root
cd $rootFolder
#git checkout `git tag | tail -n 1`
#git checkout FastNet
source ./setrootcore.sh
export OMP_NUM_THREADS=$((`cat /proc/cpuinfo | grep processor | tail -n 1 | cut -f2 -d " "`+1))

# Build and set env:
if ! source ./buildthis.sh
then
  echo "Couldn't build FastnetTool." && exit 1;
fi
source FastNetTool/cmt/new_env_file.sh
echo "Initializing and building time was $(($(date +%s%3N) - $STARTUPTIME)) ms"

# Retrieve dataset and job config
TIME=$(date +%s%3N)
if ! rsync -rvhz -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=quiet" $DatasetPlace .
then
  scp -o "StrictHostKeyChecking=no" -o "UserKnownHostsFile=/dev/null" -o "LogLevel=quiet" $DatasetPlace . \
    || { echo "Couldn't download dataset." && exit 2; }
fi
echo "Total time elapsed for copying dataset was $(($(date +%s%3N) - $TIME)) ms"

TIME=$(date +%s%3N)
if ! rsync -rvhz -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=quiet" $jobConfig .
then
  scp -o "StrictHostKeyChecking=no" -o "UserKnownHostsFile=/dev/null" -o "LogLevel=quiet" $jobConfig . \
    || { echo "Couldn't download job configuration" && exit 3; }
fi
echo "Total time elapsed for copying job configuration was $(($(date +%s%3N) - $TIME)) ms"

TIME=$(date +%s%3N)
# Job path:
gridSubFolder=$ROOTCOREBIN/user_scripts/FastNetTool/run_on_grid
# Run the job
if test -z $ppFile; then
  $gridSubFolder/BSUB_tuningJob.py $Dataset $jobFile $output || { echo "Couldn't run job!" && exit 4;}
else
  $gridSubFolder/BSUB_tuningJob.py $Dataset $jobFile $ppFile $crossValidFile $output || { echo "Couldn't run job!" && exit 4;}
fi
echo "Total time elapsed for training was $(($(date +%s%3N) - $TIME)) ms"

# Copy output to outputPlace
ssh $outputDestination mkdir -p $outputFolder

TIME=$(date +%s%3N)
if ! rsync -rvhzP -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=quiet" $output* "$outputPlace"
then
  # Try again, sometimes rsync complains about errors, but if we are persistent, it turns out to give up
  if ! rsync -rvhzP -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=quiet" $output* "$outputPlace"
  then
    # Now try with scp:
    scp -o "StrictHostKeyChecking=no" -o "UserKnownHostsFile=/dev/null" -o "LogLevel=quiet" $output* "$outputPlace"  \
      || { echo "Couldn't send file!" && exit 5; }
    echo "Used scp for sending file"
  else
    echo "rsync worked on second try."
  fi
else
  echo "rsync worked on first try."
fi
echo "Total time elapsed for copying dataset was $(($(date +%s%3N) - $TIME)) ms"


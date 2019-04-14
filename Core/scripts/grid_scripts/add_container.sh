#!/bin/sh

show_help() {
cat << EOF
Usage: ${0##*/} [-hv[verbosity_level=1]] 
                -f|--file[=] INPUTFILE | -f|--file INPUTFILES
                --dataset[=] DATASET
                [--rse[=] RSE 'CERN-PROD_SCRATCHDISK']
                [--useDQ2=1]

Create dataset on grid containing input local files at specified rse.
IMPORTANT: You need to have grid environment set.

    -h             display this help and exit
    -f INPUTFILES  files to upload to grid container. If one file is a directory,
                   it will be expanded using all non diretory files inside it.
    -v             verbose mode. Can be used multiple times for increased
                   verbosity.
    --dataset      the dataset name. It must be specified using
                   user.account.datasetname.
    --rse          The rse to upload the files and put the dataset
    --useDQ2       If set to true, then DQ2 will be used instead of rucio.
EOF
}

# Reset all variables that might be set
file=''
verbose=0 # Variables to be evaluated as shell arithmetic should be initialized to a default or validated beforehand.
dataset=''
rse='CERN-PROD_SCRATCHDISK'
useDQ2=0
user=$USER

# If no input argument, show help and exit
if [ $# -eq 0 ]; then
  show_help && exit
fi

while :; do
  case $1 in
    -h|-\?|--help)   # Call a "show_help" function to display a synopsis, then exit.
      show_help
      exit
      ;;
    -f|--file)       # Takes an option argument, ensuring it has been specified.
      shift
      if [ $# -eq 0 ]; then
        echo "ERROR: No arguments for file" >&2 && exit 1
      fi
      # Collect each file checking if it does not contain --
      while :; do
        case $1 in
          -?*|--?*)
            break
            ;;
          --)
            break
            ;;
          -)
            echo 'ERROR: Used - instead of --?' >&2
            ;;
          ?*)
            file="$file $1"
            shift
            ;;
          *)
            break
        esac
      done
      continue
      ;;
    -f=?*|--file=?*)
      file=${1#*=} # Delete everything up to "=" and assign the remainder.
      ;;
    -f=|--file=)         # Handle the case of an empty --file=
      echo 'ERROR: "--file" requires a non-empty option argument.\n' >&2
      exit 1
      ;;
    -v|--verbose)
      verbose=$((verbose + 1)) # Each -v argument adds 1 to verbosity.
      shift
      ;;
    -v?*)    # Set verbosity level
      verbose=${1#-v}
      if ! echo $verbose | egrep -q '^[0-9]+$'; then
        echo 'ERROR: use -v[number] to set verbosity level.' >&2 && exit 1
      fi
      ;;
    -v=?*|--verbose=?*)    # Set verbosity level
      verbose=${1#*=}
      ;;
    --useDQ2)
      if [ ${2#--} != $2 ]; then
        useDQ2=1
      else
        useDQ2=$2
        shift 2
        continue
      fi
      ;;
    --useDQ2=?*)
      useDQ2=${1#*=}
      ;;
    --dataset)
      if [ ${2#--} != $2 ]; then
        echo 'ERROR: Dataset value wasn''t set.' >&2 && exit 1
      else
        dataset=$2
        shift 2
        continue
      fi
      ;;
    --dataset=?*)
      dataset=${1#*=}
      ;;
    --rse)
      if [ ${2#--} != $2 ]; then
        echo 'ERROR: rse value wasn''t set.' >&2 && exit 1
      else
        rse=$2
        shift 2
        continue
      fi
      ;;
    --rse=?*)
        rse=${1#*=}
      ;;
    --)              # End of all options.
      shift
      break
      ;;
    -?*)
      echo 'WARN: Unknown option (ignored): %s\n' "$1" >&2
      ;;
    *)               # Default case: If no more options then break out of the loop.
      break
  esac
  shift
done

# Check arguments
test -z "$file" && echo "ERROR: option file was not specified." >&2 && show_help && exit 1;
test $useDQ2 -gt 1 -a $useDQ2 -lt 0 && echo "ERROR: useDQ2 was set to a value different to 0 or 1." >&2 && show_help && exit 1;
test -z $dataset && echo "ERROR: Dataset wasn't set." >&2 && show_help && exit 1;

#allFolders=1
#allFiles=1
#for f in $file
#do
#  if [ $useDQ2 -eq 0 ]; then
#    if [ -d $f ]; then
#      file="$file `find $f -maxdepth 1 -mindepth 1 -not -type d | tr \"\n\" \" \"`"
#    fi
#  else
#    if [ -f $f  ]; then
#      allFolders=0
#    fi
#    if [ -d $f  ]; then
#      allFiles=0
#    fi
#  fi
#done

test "${file## }" != "${file}" && file=${file[@]1:-1}

#if [ $useDQ2 -eq 1 -a $allFolders -eq 0 -a $allFiles -eq 0 ]; then
#  echo "ERROR: When using DQ2 add container, you should input only files or only folders." >&2 && exit 1;
#fi
#if [ $useDQ2 -eq 1 -a $allFolders -eq 1 ]; then
#  dq2Opt="-s"
#fi
#if [ $useDQ2 -eq 1 -a $allFiles -eq 1 ]; then
#  dq2Opt="-f"
#fi

if test "${dataset/:}" = "${dataset}"; then
  user=`echo $dataset | cut -d "." -f2`
else
  user=`echo $dataset | cut -d ":" -f1 | cut -d "." -f2`
fi

# Test 
test -z $user && echo "ERROR: option user was not specified or couldn't be automatically detected." >&2 && exit 1;

# Display some verbosity configuration:
#test $verbose -ge 1 && echo "Files set to: $file" >&1
test $verbose -ge 2 && echo "file is: $file" >&1
test $verbose -ge 1 && echo "verbosity is: $verbose" >&1
test $verbose -ge 1 && echo "User set to: $user" >&1
test $verbose -ge 1 && echo "useDQ2 is $useDQ2" >&1
test $verbose -ge 1 && echo "dataset is $dataset" >&1
test $verbose -ge 1 && echo "rse is $rse" >&1
test $verbose -ge 1 && test $useDQ2 -eq 1 && { echo "Using DQ2 creation method." >&1 || echo "Using rucio creation method." >&1; }

test $verbose -ge 1 && set -x

rucio_verbose=""
test $verbose -ge 0 && rucio_verbose="--verbose"

# Run command with extracted values:
if [ $useDQ2 -eq 0 ]; then
  if test "${dataset/:}" = "${dataset}"; then
    dataset="user.$user:$dataset"
  fi
  rucio add-dataset $dataset
  if ! rucio $rucio_verbose upload "$file" "$dataset" --rse $rse --scope "user.$user"; then
    echo "WARN: Could not upload using standard protocol, will retry using davs protocol!" >&2 
    if ! rucio $rucio_verbose upload "$file" "$dataset" --rse $rse --scope "user.$user" --protocol davs; then
      echo "WARN: Could not upload using davs protocol, will retry using gsiftp protocol!" >&2 
      if ! rucio $rucio_verbose upload "$file" "$dataset" --rse $rse --scope "user.$user" --protocol gsiftp; then
        echo "ERROR: Could not upload using all available protocols" >&2 
      fi
    fi
  fi
  #scoped_files=$(for f in $file; do echo "user.$user:$(basename $f)"; done)
  #rucio attach ${dataset} $scoped_files
  #rucio close user.$user:$dataset
else
  echo $file
  echo "dq2-put -d -L $rse $dq2Opt $file $dataset"
  if dq2-register-dataset $dataset; then
    if dq2-register-location $dataset $rse; then
      if dq2-put -d -L $rse -f $file $dataset; then
        test $verbose -ge 1 && echo "Finished uploading data." >&1
      else 
        echo "ERROR: Couldn't put files on dataset, but dataset is created." >&2 && exit 1;
      fi
    else 
      echo "ERROR: Couldn't register dataset at $rse." >&2 && exit 1;
    fi
  else 
    echo "ERROR: Couldn't create dataset." >&2 && exit 1;
  fi
fi
test $verbose -ge 1 && set +x

true

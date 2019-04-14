
# Taken from: http://stackoverflow.com/a/28776166/1162884
([[ -n $ZSH_EVAL_CONTEXT && $ZSH_EVAL_CONTEXT =~ :file$ ]] || 
 [[ -n $KSH_VERSION && $(cd "$(dirname -- "$0")" &&
    printf '%s' "${PWD%/}/")$(basename -- "$0") != "${.sh.file}" ]] || 
 [[ -n $BASH_VERSION && $0 != "$BASH_SOURCE" ]]) && sourced=1 || sourced=0


function citest0 {
  echo "[citest 0]: creating tuning files..."
  python citest0.py &> citest0.log
  if [ $? -eq 0 ]
  then
    echo "[citest 0]: OK"
  else
    echo "[citest 0]: X"
    test "$sourced" -eq 1 && return 1 || exit 1
  fi
}

function citest1 {
  echo "[citest 1]: creating tuning files..."
  python citest1.py &> citest1.log
  if [ $? -eq 0 ]
  then
    echo "[citest 1]: OK"
  else
    echo "[citest 1]: X"
    test "$sourced" -eq 1 && return 1 || exit 1
  fi
}

function citest2 {
  echo "[citest 2]: tuning..."
  python citest2.py &> citest2.log
  if [ $? -eq 0 ]
  then
    echo "[citest 2]: OK"
  else
    echo "[citest 2]: X"
    test "$sourced" -eq 1 && return 1 || exit 1
  fi
}

function citest3 {
  echo "[citest 3]: crossval stat!"
  source citest3.sh &> citest3.log
  if [ $? -eq 0 ]
  then
    echo "[citest 3]: OK"
  else
    echo "[citest 3]: X"
    test "$sourced" -eq 1 && return 1 || exit 1
  fi

}

function citest4 {
  echo "[citest 4]: monitoring crossval stat!"
  source citest4.sh &> citest4.log
  if [ $? -eq 0 ]
  then
    echo "[citest 4]: OK"
  else
    echo "[citest 4]: X"
    test "$sourced" -eq 1 && return 1 || exit 1
  fi

}

function citest5 {
  echo "[citest 5]: runGRIDTuning..."
  source citest5.sh &> citest5.log
  if [ $? -eq 0 ]
  then
    echo "[citest 5]: OK"
  else
    echo "[citest 5]: X"
    test "$sourced" -eq 1 && return 1 || exit 1
  fi

}

function citest6 {
  echo "[citest 6]: runGRIDCrossValidAnalysis..."
  source citest6.sh &> citest6.log
  if [ $? -eq 0 ]
  then
    echo "[citest 6]: OK"
  else
    echo "[citest 6]: X"
    test "$sourced" -eq 1 && return 1 || exit 1
  fi

}



#Start all jobs
cd samples/


echo "[samples ]: searchning for samples..."
if ls *.root > /dev/null 2>&1; then 
  echo "[samples ]: OK"
else
  echo "[samples ]: Downloading all samples from jodafons public"
  source download.sh
fi

cd ..
cp tests/* .
mkdir data
cp citest0* data/
cd data/
citest0 || { test "$sourced" -eq 1 && return 1 || exit 1; }
mv *.log ..
rm *.py
cd config_citest0/
mv *.pic.gz config_citest0.pic.gz
mv *.pic.gz ..
cd ..
rm -rf config_citest0/
cd ..
citest1 || { test "$sourced" -eq 1 && return 1 || exit 1; }
mv tuningData_citest1* data/
citest2 || { test "$sourced" -eq 1 && return 1 || exit 1; }
mkdir tuned
mv nn.tuned* tuned/
mv tuned/ data/
citest3 || { test "$sourced" -eq 1 && return 1 || exit 1; }
cd data/
mkdir crossval
mv ../crossVal* crossval
cd ..
citest4 || { test "$sourced" -eq 1 && return 1 || exit 1; }
citest5 || { test "$sourced" -eq 1 && return 1 || exit 1; }
citest6 || { test "$sourced" -eq 1 && return 1 || exit 1; }

#Clean the workspace
rm citest*.py
rm citest*.sh
rm -rf data/
rm -rf report*

#remove samples
cd samples/
rm *.root
cd ../


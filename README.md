
# Saphyra Tuning Framework

This package contains all tools used for tuning and exporting the discriminators 
into the Athena/RootCore environment. It is can be integrated with CERN grid when with 
panda access and docker. 

## Requirements:

- numpy
- python (2.7 or 3)


## Installation:

```bash
source setup.sh
```


## LCG with docker

See `docker` to build your image. You must setup ATLAS and voms first.
After setup all enviroments just use the example to launch a job using
the docker image ml-base. Saphyra must be setted.

```bash
runGRIDtuning.py \
 --do-multi-stop 0 \
 --containerImage docker://jodafons/ml-base:latest \
 -c user.jodafons.config_test2 \
 -d user.jodafons.sample.npz  \
 -p user.jodafons.ppFile.test.pic.gz \
 -x user.jodafons.crossValid.test.pic.gz \
 -o user.jodafons.job_test \
 --eta-bin 0  \
 --et-bin 0  \
 --site AUTO \
```


## Contribution:

- Dr. João Victor da Fonseca Pinto, UFRJ/COPPE, CERN/ATLAS (jodafons@cern.ch) [maintainer, developer]
- Dr. Werner Freund, UFRJ/COPPE, CERN/ATLAS (wsfreund@cern.ch) [developer]
- Msc. Micael Veríssimo de Araújo, UFRJ/COPPE, CERN/ATLAS (mverissi@cern.ch) [developer]



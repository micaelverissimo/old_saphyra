
# Ringer framework: Tuning Tools package

This package contains all tools used for tuning and exporting the discriminators into the Athena/RootCore environment. It is integrated with CERN grid when with panda access, so that the discriminators can be tuned both on the CERN grid or on standalone.

Table of Contents
=================

  * [Ringer framework: Tuning Tools package](#ringer-framework-tuning-tools-package)
  * [Installation](#installation)
    * [Tuning Cores](#tuning-cores)
    * [Other compile time flags](#other-compile-time-flags)
  * [Usage](#usage)
  * [Package Organization](#package-organization)
    * [Python files](#python-files)
    * [Script files](#script-files)
      * [Retrieving help on the python executables](#retrieving-help-on-the-python-executables)
      * [Standalone](#standalone)
      * [GRID](#grid)


# Installation

This package cannot be installed by itself. Consider installing one of the RootCore projects using this package:

 - [RingerTuning](https://github.com/wsfreund/RingerTuning) [recommended]: this project contains only the packages needed for tuning the discriminators;
 - [RingerProject](https://github.com/joaoVictorPinto/RingerProject): Use this git repository, however, if you want to install all packages related to the Ringer algorithm.

## Tuning Cores

There are two cores that can be used for tuning the discriminators. The available cores are defined during the compile time. To achieve a faster compilation (and less disk space usage), you can require installation of just one of the cores. The flags available when compiling with `buildthis.sh` are the following:

- `--with-tuningtool-fastnet` (default): Uses an adapted version of the [FastNet](https://github.com/rctorres/fastnet); 
- `--with-tuningtool-exmachina`: Install [ExMachina](https://github.com/Tiamaty/ExMachina) as its core;
- `--with-tuningtool-all`: Install both cores. The core to be used to tune can be specified during Runtime.

## Other compile time flags

Currently, it is available the following flag:

- `--with-tuningtool-dbg-level`: When specified and compiling fastnet, it will be compiled on debug mode.

# Usage

Usually, for every functionality available on this package, you will both be able to access it through shell commands (available after you set the project environment through `source setrootcore.sh`), or through a python script. For the latter, we have created skeletons on the folder [TuningTools/scripts/skeletons/](https://github.com/wsfreund/TuningTools/tree/master/scripts/skeletons/) which can be used as tutorial examples and changed to your needs.

The next steps describe the usual work flow. Steps marked with the [GRID] flag can be skipped if you are not going to run the tuning on the CERN grid, although steps concerning data configuration can still be used for tuning on standalone:

1. Transform data either in PhysVal or xAOD (in upcoming version) format to the package data format. Take a look at ["Creating Data" documentation](http://nbviewer.jupyter.org/github/wsfreund/TuningTools/tree/master/doc/CreateData.ipynb).
1. [GRID] Generate the tuning configuration data. Take a look at ["Tuning the Discriminator" documentation](http://nbviewer.jupyter.org/github/wsfreund/TuningTools/tree/master/doc/Tuning.ipynb#Create-Configuration-Data).
1. [GRID] Export datasets to the grid. Take a look at ["Tuning the Discriminator" documentation](http://nbviewer.jupyter.org/github/wsfreund/TuningTools/tree/master/doc/Tuning.ipynb#Exporting-data-to-the-GRID). 
1. Run the tuning:
    1. [GRID] Use the [runGRIDtuning.py](http://nbviewer.jupyter.org/github/wsfreund/TuningTools/tree/master/doc/Tuning.ipynb#Tuning-on-the-GRID) command;
    1. [standalone] Use the [runTuning.py](http://nbviewer.jupyter.org/github/wsfreund/TuningTools/tree/master/doc/Tuning.ipynb#Tuning-standalone) command.
1. Retrieve the Cross-Validation statistics. Take a look at ["Cross-Validation Statistics Retrieval" documentation](http://nbviewer.jupyter.org/github/wsfreund/TuningTools/tree/master/doc/CrossValStats.ipynb);
1. Dump the operational discriminator for usage on physics reconstruction/trigger environment Take a look at ["Cross-Validation Statistics Retrieval" documentation](http://nbviewer.jupyter.org/github/wsfreund/TuningTools/tree/master/doc/CrossValStats.ipynb#Dumping-operational-discriminator).

# Package Organization

The package is organized as a standard RootCore package, namely:


    Module '/afs/cern.ch/user/w/wsfreund/Ringer/xAODRingerOfflinePorting/RingerTPFrameWork/TuningTools' folders are:
    ./Root
    ./cmt
    ./python
    ./TuningTools
    ./scripts
    ./doc


The `cmt` folder only matters for the developers. On the `Root` folder we only generate the dictionary for the PhysVal ROOT TTree, which is set on the [`TuningTools/RingerPhysVal.h`](https://github.com/wsfreund/TuningTools/tree/master/TuningTools/RingerPhysVal.h).

The user interaction will happen mainly with `python` and `scripts` folders.

## Python files

When checking `python` folder, we will see the following modules:



    ./python/CreateData.py
    ./python/CreateTuningJobFiles.py
    ./python/CrossValid.py
    ./python/CrossValidStat.py
    ./python/ReadData.py
    ./python/Neural.py
    ./python/Parser.py
    ./python/PreProc.py
    ./python/TuningJob.py
    ./python/__init__.py
    ./python/TuningWrapper.py
    ./python/coreDef.py


where the main purposes are the following:

 - [`python/ReadData.py`](https://github.com/wsfreund/TuningTools/tree/master/python/ReadData.py): It can be considered as an implementation detail for the TuningTools data files creation. Its main class `ReadData` is internally used by the data creation routine which is prefered rather than directly using the ReadData. However, documentation on the `ReadData` usage is also available [here](http://nbviewer.jupyter.org/github/wsfreund/TuningTools/tree/master/doc/CreateData.ipynb#Using-ReadData). In this file you will find the `BranchEffCollector` and  `BranchCrossEffCollector` which are the classes used to store the benchmark efficiencies on the tuning data files. Many important enumerations can be found on this file, which are extensively used on other module files. The most used enumerations are:
     - Dataset: defines which Cross-Validation dataset the data is in;
     - RingerOperation: defines where the *Ringer* algorithm is operating (which Trigger level or Offline);
     - Reference: defines which benchmark (*Truth*, *Likelihood* or *CutBased*) should be used as reference for filtering the particles.
 - [`python/CreateData.py`](https://github.com/wsfreund/TuningTools/tree/master/python/CreateData.py): Its main class `CreateData` is used for creating the module used data files. The structure of this file is defined on `TuningDataArchieve` the tuning data archive, also responsible for managing these files loading and saving;
 - [`python/CreateTuningJobFiles.py`](https://github.com/wsfreund/TuningTools/tree/master/python/CreateTuningJobFiles.py): Contains the GRID configuration files which basically contains simple information such as which tuning configurations should be used and which CrossValidation sort will go on each job. Usually each file will be a job on the GRID, however the tuning job can run more than one file if you want to complicate things a little bit. On this file you will also find the `TuningJobConfigArchieve`, which is the context manager for the tuning configuration files;
 - [`python/CrossValid.py`](https://github.com/wsfreund/TuningTools/tree/master/python/CrossValid.py): The Cross-Validation manager. Its main class `CrossValid` contains all box sorts for each k-fold and can be used for applying and reverting the sort into the data. The user should not care about the implementation details as this is handled by the `TuningJob`. This file also contains the context manager `CrossValidArchieve` for saving and loading the Cross-Validation data files which are needed to run tuning jobs on the GRID; 
 - [`python/PreProc.py`](https://github.com/wsfreund/TuningTools/tree/master/python/PreProc.py): Defines the pre-processing algorithms which can be applied on the data. It is possible to apply more than one pre-processing by using the `PreProcChain`. If you want the tuning job to tune more than one pre-processing chain, you can create a pre-processing chains collection with the `PreProcCollection` class. This file also contains the `PreProcArchieve` which is the context manager for saving and loading the pre-processing data.
 - [`python/Parser.py`](https://github.com/wsfreund/TuningTools/tree/master/python/Parser.py): On this file you will find several parsers definitions which are used by the executables located on the `scripts` folder;
 - [`python/TuningJob.py`](https://github.com/wsfreund/TuningTools/tree/master/python/TuningJob.py): Its main class `TuningJob` handles all data and configuration for the user, correctly calling the core algorithm to tune the discriminators. The results are saved on `TunedDiscrArchieve` format, which are loaded using the same class as a context manager;
 - [`python/TuningTool.py`](https://github.com/wsfreund/TuningTools/tree/master/python/TuningTool.py): Contains a wrapper for the tuning core;
 - [`python/Neural.py`](https://github.com/wsfreund/TuningTools/tree/master/python/TuningTool.py): Contains a wrapper for the NeuralNetwork class returned by the tuning core;
 - [`python/coreDef.py`](https://github.com/wsfreund/TuningTools/tree/master/python/coreDef.py): Defines the cores used for tuning available and provides runtime mechanism for selecting which one of them to use;
 - [`python/CrossValidStat.py`](https://github.com/wsfreund/TuningTools/tree/master/python/CrossValidStat.py): Its main class is used to retrieve the CrossValidation statistics on the chosen operating points. This returns a summary operation dictionary (also saved in a file) which can be further used to dump the operation discriminator. The `ReferenceBenchmark` class is used to retrieve the discriminators efficiency on the operating points and the `PerfHolder` contains the discriminators tuning performance information.

## Script files

The most important content for the users are defined within the scripts folder. Instead of interacting with the `python` folder, the user can run the package functionalities by running directly shell executables defined on the `scripts/standalone` (runs the functionalities on standalone) and `scripts/grid_scripts` (on the GRID if applicable) folders. Another important folder is the `scripts/skeletons` where skeletons for interacting with the python packages can be found.

All scripts folder are:


    ./scripts/grid_scripts
    ./scripts/run_on_grid
    ./scripts/standalone
    ./scripts/validate
    ./scripts/analysis_scripts
    ./scripts/skeletons


The `scripts/validate` folder have validation scripts, and the `scripts/run_on_grid` contains scripts which are run internally inside the GRID. Finally, the `scripts/analysis_scripts` folder contain past analysis/tuning used scripts, users are encouraged to keep their scripts on this folder. 

### Retrieving help on the python executables

You might have issues when trying to retrieve help when running the executable python commands, as the -h flag is read first the python itself. To bypass python options, add first a `--` before the commands and then add `-h`. E.g.:

```
createData.py -- -h
```

### Standalone

All standalone scripts found in this package are:



    ./scripts/standalone/createData.py
    ./scripts/standalone/createTuningJobFiles.py
    ./scripts/standalone/filterTree.py


where a brief description about their utility is:

 - [`scripts/standalone/createData.py`](https://github.com/wsfreund/TuningTools/tree/master/scripts/standalone/createData.py): Execute the needed information extraction for tuning the discriminators from the xAOD/PhysVal files. For more information see the [Creating Data documentation](http://nbviewer.jupyter.org/github/wsfreund/TuningTools/tree/master/doc/CreateData.ipynb#Using-the-createData.py-executable);
 - [`scripts/standalone/createTuningJobFiles.py`](https://github.com/wsfreund/TuningTools/tree/master/scripts/standalone/createTuningJobFiles.py): generate all tuning job configuration files, as the looping bounds for each job, the pre-processing chains and the Cross-Validation file;
 - [`scripts/standalone/filterTree.py`](https://github.com/wsfreund/TuningTools/tree/master/scripts/standalone/filterTree.py): skim PhysVal files to contain only a small number of trigger chains. Use this script if you already have the PhysVal downloaded, if you still need to download it, the `scripts/grid_scripts/run_dump.py` better fits your need. 

### GRID

Now entering in details about the executables which send jobs to the GRID, the available scripts are: 


    ./scripts/grid_scripts/add_container.sh
    ./scripts/grid_scripts/createGRIDTuningJobFiles.py
    ./scripts/grid_scripts/genGRIDdata.py
    ./scripts/grid_scripts/retryBSUBtuning.py
    ./scripts/grid_scripts/runBSUBtuning.py
    ./scripts/grid_scripts/runBSUBtuning.sh
    ./scripts/grid_scripts/runGRIDtuning.py
    ./scripts/grid_scripts/run_dump.py


where a brief explanation about their utility is:
- [`scripts/grid_scripts/add_container.sh`](https://github.com/wsfreund/TuningTools/tree/master/scripts/grid_scripts/add_container.sh): A shell script used for uploading data to the GRID. It must be used to upload all locally available data and configuration data to the GRID, including the pre-processing and Cross-Validation data. The development of jobs generating those information directly on the GRID is under-development. For more information, take a look at ["Tuning the Discriminator" documentation](http://nbviewer.jupyter.org/github/wsfreund/TuningTools/tree/master/doc/Tuning.ipynb#Uploading-data-to-the-GRID);
- [`scripts/grid_scripts/createGRIDTuningJobFiles.py`](https://github.com/wsfreund/TuningTools/tree/master/scripts/grid_scripts/createGRIDTuningJobFiles.py): Under development. It will make possible to generate the configuration files directly on the GRID;
- [`scripts/grid_scripts/genGRIDdata.py`](https://github.com/wsfreund/TuningTools/tree/master/scripts/grid_scripts/genGRIDdata.py): Under development. It will make possible to generate the data file directly on the GRID;
- [`scripts/grid_scripts/retryBSUBtuning.py`](https://github.com/wsfreund/TuningTools/tree/master/scripts/grid_scripts/retryBSUBtuning.py): Retry failed jobs on LSF;
- [`scripts/grid_scripts/runBSUBtuning.py`](https://github.com/wsfreund/TuningTools/tree/master/scripts/grid_scripts/runBSUBtuning.py): Run jobs on LSF queues;
- [`scripts/grid_scripts/runGRIDtuning.py`](https://github.com/wsfreund/TuningTools/tree/master/scripts/grid_scripts/runGRIDtuning.py): Run job on the CERN grid. Take a look at ["Tuning the Discriminator" documentation](http://nbviewer.jupyter.org/github/wsfreund/TuningTools/tree/master/doc/Tuning.ipynb#Running-the-GRID-dispatch-tuning-command);
- [`scripts/grid_scripts/run_dump.py`](https://github.com/wsfreund/TuningTools/tree/master/scripts/grid_scripts/run_dump.py): Download and optimizes PhysVals from the GRID in batches so that only the desired chains to reduce disk-space usage. For more information, take a look at ["Creating Data" documentation](http://nbviewer.jupyter.org/github/wsfreund/TuningTools/tree/master/doc/CreateData.ipynb#Optimal-GRID-PhysVal-download).


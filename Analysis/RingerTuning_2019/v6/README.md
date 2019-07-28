
## Description for v8 tuning:

This tuning will be trained by keras using as sequence an MLP model with 100 inputs, n neurons in the hidden layer and only one neuron in the outputs.
All transfer functions will be tha tansig. The optimizer will be Adam. Using class weight to balance and SP stop as regularization. 
Stratified KFold with 10 splits will be user to estimate the estatistical fluctuation and best parameters. 10 inits to avoid the local
minimal.

- Using 2017 collision data (full period) as train and validation sets;
- Using cut-based fast calo as reference in the pileup fit phase;


## Data Containers:

- Cross validation: user.jodafons.StratifiedKFold.10_sorts
- Model: user.jodafons.models_mlp_n5to20
- Preproc: user.jodafons.preproc.norm1
- Job configurations: user.jodafons.job_config_10sorts_10inits
- Dataset: user.jodafons.data17_13TeV.AllPeriods.sgn.probes_lhmedium_EGAM1.bkg.VProbes_EGAM7.GRL_v97_etX_etaX.npz




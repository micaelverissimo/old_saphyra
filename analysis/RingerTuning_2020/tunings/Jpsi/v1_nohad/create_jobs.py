from saphyra import *
# ppChain
from saphyra import PreProcChain_v1, Norm1, ReshapeToConv1D
pp = PreProcChain_v1( [Norm1()] )

# tensorflow
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Activation, Conv1D, Flatten

# function to define the keras model
def get_model(neuron_min, neuron_max):
  modelCol = []
  for n in range(neuron_min,neuron_max+1):
    model = Sequential()
    model.add(Dense(n, input_shape=(88,), activation='tanh'))
    model.add(Dense(1, activation='linear'))
    model.add(Activation('tanh'))
    modelCol.append(model)
  return modelCol

# cross-validation method
n_folds = 10 # normally 10 folds
from sklearn.model_selection import StratifiedKFold, KFold
kf = StratifiedKFold(n_splits=n_folds, random_state=512, shuffle=True)

n_max_neuron = 15
n_min_neuron = 5
n_inits      = 50
createPandaJobs( 
        models       = get_model(neuron_min=n_min_neuron,
                                 neuron_max=n_max_neuron),
        ppChain       = pp,
        crossVal      = kf,
        nInits        = n_inits,
        nInitsPerJob  = 10,
        sortBounds    = n_folds,
        nSortsPerJob  = 5,
        nModelsPerJob = 2,
        outputFolder  = 'job_config.Jpsi_ringer.v1_nohad.mlp%ito%i.%isorts.%iinits' %(n_min_neuron,
                                                                                n_max_neuron, 
                                                                                n_folds, 
                                                                                n_inits)
        )
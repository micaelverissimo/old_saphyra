
__all__ = ['StandardScaler']

from saphyra.preproc import PrepObj
from Gaugi import checkForUnusedVars

import numpy as np
from sklearn.preprocessing import StandardScaler as skStdScaler


class StandardScaler(PrepObj):
    """
    Applies Standard Scaler to data. This implementation uses the sklearn StandardScaler
    implementation.
    """
    takesParamsFromData = True

    def __init__(self, d = {}, **kw):    
        self.scaler = skStdScaler()
        d.update( kw ); del kw
        PrepObj.__init__( self, d )
        checkForUnusedVars(d, self._warning )
        del d
        
    def _retrieveNorm(self, data):
        """
        Calculate pre-processing parameters.
        The parameters are extracted from the training data.
        """
        self.scaler.fit(data)
    
    def _get_params(self):
        '''
        This method will return the scaler parameters as a array that can be save.
        The arrays has ndim x 2 size, where the first collumn is the mean and
        the second is the scale.
        '''
        return np.concatenate((self.scaler.mean_[np.newaxis],
                               self.scaler.scale_[np.newaxis]), axis=0).T

    def __str__(self):
        """
        String representation of the object.
        """
        return "StandardScaler"

    def shortName(self):
        """
        Short string representation of the object.
        """
        return "StdScaler"

    def _apply(self, data):
        '''
        This method will apply the normalization to the data
        '''
        normalized_data = self.scaler.transform(data)
        return normalized_data

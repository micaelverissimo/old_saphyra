#ifndef TUNINGTOOLS_TRAINING_STANDARD_H
#define TUNINGTOOLS_TRAINING_STANDARD_H

#include "TuningTools/system/defines.h"
#include "Gaugi/MsgStream.h"
#include "TuningTools/training/Training.h"
#include "TuningTools/system/ndarray.h"

class StandardTraining : public Training
{
  protected:
    const REAL *inTrnData;
    const REAL *outTrnData;
    const REAL *inValData;
    const REAL *outValData;
    unsigned inputSize;
    unsigned outputSize;
    unsigned numValEvents;
    DataManager *dmTrn;
  
  public:
    StandardTraining( TuningTool::Backpropagation *net
        , const Ndarray<REAL,2> *inTrn  
        , const Ndarray<REAL,1> *outTrn
        , const Ndarray<REAL,2> *inVal 
        , const Ndarray<REAL,1> *outVal 
        , const unsigned bSize
        , const MSG::Level msglevel);
  
    virtual ~StandardTraining();
    
    virtual void tstNetwork(REAL &mseTst, 
                            REAL &spTst, 
                            REAL &detTst, 
                            REAL &faTst)
    {
      mseTst = spTst = detTst = faTst= 0.;
    }
  
    /**
     *
     * @brief Applies the validating set for the network's validation.
     *
     * This method takes the one or more validating events (input and targets)
     * and presents them to the network. At the end, the mean training error is
     * returned. Since it is a validating function, the network is not
     * modified, and no updating weights values are calculated. This method
     * only presents the validating sets and calculates the mean validating
     * error obtained.  of this class are not modified inside this method,
     * since it is only a network validating process.
     *
     * @return The mean validating error obtained after the entire training set
     * is presented to the network.
     **/
    virtual void valNetwork(REAL &mseVal, 
        REAL &spVal, 
        REAL &detVal, 
        REAL &faVal);
  
    /**
     * @brief Applies the training set for the network's training.
     *
     * This method takes the one or more training events (input and targets)
     * and presents them to the network, calculating the new mean (if batch
     * training is being used) update values after each input-output pair is
     * presented. At the end, the mean training error is returned.
     *
     * @return The mean training error obtained after the entire training set
     *         is presented to the network.
     **/
    virtual REAL trainNetwork();
    
    virtual void showInfo(const unsigned nEpochs) const;
};

#endif

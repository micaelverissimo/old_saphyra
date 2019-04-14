#ifndef TUNINGTOOLS_FEEDFORWARD_H
#define TUNINGTOOLS_FEEDFORWARD_H

#include "TuningTools/system/defines.h"

#include <vector>
#include <cstring>

#include "Gaugi/MsgStream.h"
#include "TuningTools/neuralnetwork/NeuralNetwork.h"
#include "TuningTools/neuralnetwork/NetConfHolder.h"

namespace TuningTool
{

/** 
 * This class should be used for network production, when no training is
 * necessary, just feedforward the incoming events, fot output collection.
 **/
class FeedForward : public NeuralNetwork 
{
  private:

    /**
     * @brief Returns if space needed is already allocated
     *
     * Override NeuralNetwork version, with same behavior, but for space needed
     * by FeedForward.
     **/
    bool isAllocated() const;
  public:

    /**
     * @brief Copy constructor
     *
     * This constructor should be used to create a new network which is an
     * exactly copy of another network.
     *
     * @param[in] net The network that we will copy the parameters from.
     **/
    FeedForward(const FeedForward &net);

    /**
     * @brief Constructor taking the parameters for a matlab net structure.
     *
     * This constructor should be called when the network parameters are
     * stored in a matlab network structure.
     *
     * @param[in] netStr The Matlab network structure as returned by newff.
     **/
    FeedForward(const NetConfHolder &net, 
                const MSG::Level msglevel, 
                const std::string& name);

    /**
     * @brief Returns a clone of the object.
     *
     * Returns a clone of the calling object. The clone is dynamically
     * allocated, so it must be released with delete at the end of its use.
     *
     * @return A dynamically allocated clone of the calling object.
     **/
    virtual NeuralNetwork *clone();

    /**
     * @brief Class destructor.
     * Releases all the dynamically allocated memory used by the class.
     **/
    virtual ~FeedForward();

};

}

#endif

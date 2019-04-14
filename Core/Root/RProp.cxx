#include <vector>
#include <string>

#include "TuningTools/neuralnetwork/RProp.h"

namespace TuningTool
{

//==============================================================================
RProp::RProp() 
  : IMsgService("RProp"),
    Backpropagation(),
    prev_dw(nullptr),
    prev_db(nullptr),
    delta_w(nullptr),
    delta_b(nullptr){;}

//==============================================================================
RProp::RProp(const NetConfHolder &net, 
             const MSG::Level msglevel, 
             const std::string &name ) 
  : IMsgService("RProp"),
    Backpropagation(net, msglevel, name),
    deltaMax(net.getDeltaMax()),
    deltaMin(net.getDeltaMin()),
    incEta(net.getIncEta()),
    decEta(net.getDecEta()),
    initEta(net.getInitEta()),
    prev_dw(nullptr),
    prev_db(nullptr),
    delta_w(nullptr),
    delta_b(nullptr)
{

  // Allocate space for this object:
  allocateSpace();

  //Initializing the dynamically allocated values.
  for (unsigned i=0; i<(nNodes.size() - 1); i++)
  {
    for (unsigned j=0; j<nNodes[i+1]; j++) 
    {
      prev_db[i][j] = 0.;
      delta_b[i][j] = this->initEta;
      
      for (unsigned k=0; k<nNodes[i]; k++)
      {
        prev_dw[i][j][k] = 0.;
        delta_w[i][j][k] = this->initEta;
      }
    }
  }
}

//==============================================================================
RProp::RProp(const RProp &net) 
  : IMsgService("RProp"),
    Backpropagation(),
    prev_dw(nullptr),
    prev_db(nullptr),
    delta_w(nullptr),
    delta_b(nullptr)
{
  this->operator=(net);
}

//==============================================================================
void RProp::copyPrevDeltas(const RProp &net)
{
  for (unsigned i=0; i<(nNodes.size() - 1); i++)
  {
    memcpy(prev_db[i], net.prev_db[i], nNodes[i+1]*sizeof(REAL));
    memcpy(delta_b[i], net.delta_b[i], nNodes[i+1]*sizeof(REAL));
    for (unsigned j=0; j<nNodes[i+1]; j++) 
    {
      memcpy(prev_dw[i][j], net.prev_dw[i][j], nNodes[i]*sizeof(REAL));
      memcpy(delta_w[i][j], net.delta_w[i][j], nNodes[i]*sizeof(REAL));
    }
  }
}

//==============================================================================
RProp& RProp::operator=(const RProp &net)
{
  if ( this == &net) {
    return *this;
  }

  Backpropagation::operator=(net);

  deltaMax = net.deltaMax;
  deltaMin = net.deltaMin;
  incEta = net.incEta;
  decEta = net.decEta;
  initEta = net.initEta;

  if (!isAllocated()){
    allocateSpace();
  }
  
  this->copyPrevDeltas(net);

  return *this;
}

//==============================================================================
bool RProp::isAllocated() const 
{
  if ( prev_db != nullptr &&
       delta_b != nullptr &&
       prev_dw != nullptr &&
       delta_w != nullptr )
  {
    return true;
  } else if ( prev_db == nullptr &&
              delta_b == nullptr &&
              prev_dw == nullptr &&
              delta_w == nullptr )
  {
    return false;
  } else {
    MSG_FATAL("RProp pointers point both to memory regions and to "
        "nullptr.")
  }
}

//==============================================================================
void RProp::allocateSpace()
{
  // Call parent space allocation:
  if ( !Backpropagation::isAllocated() ) {
    Backpropagation::allocateSpace();
  }

  if ( isAllocated() ) {
    MSG_ERROR("Attempted to reallocate " << getLogName() 
        << "(" << m_name << ")");
    return;
  }

  MSG_DEBUG("Allocating RProp space for " << m_name << "...");
  
  const unsigned size = nNodes.size() - 1;

  try {
    // FIXME Discontinous memory allocation may affect on perfomance if
    // compiler does not optimize this for us:
    //
    // Approach 1: Faster way, simply allocate each variable per time
    //
    // Approach 2: Allocate a continuous memory region and pass it to an
    //             ndarray to manage it. 
    prev_db = new REAL* [size];
    delta_b = new REAL* [size];
    prev_dw = new REAL** [size];
    delta_w = new REAL** [size];
    for (unsigned i=0; i<size; i++)
    {
      prev_db[i] = new REAL [nNodes[i+1]];
      delta_b[i] = new REAL [nNodes[i+1]];
      prev_dw[i] = new REAL* [nNodes[i+1]];
      delta_w[i] = new REAL* [nNodes[i+1]];
      for (unsigned j=0; j<nNodes[i+1]; j++) 
      {
        prev_dw[i][j] = new REAL [nNodes[i]];
        delta_w[i][j] = new REAL [nNodes[i]];
      }
    }
  } catch (const std::bad_alloc &xa) {
    MSG_FATAL("Abort! Reason: " << xa.what() );
  }
}

//==============================================================================
RProp::~RProp()
{
  // Deallocating the delta bias matrix.
  releaseMatrix(prev_db);
  releaseMatrix(delta_b);

  // Deallocating the delta weights matrix.
  releaseMatrix(prev_dw);
  releaseMatrix(delta_w);
}


//==============================================================================
void RProp::updateWeights(const unsigned /*numEvents*/)
{
  for (unsigned i=0; i<(nNodes.size()-1); i++)
  {
    for (unsigned j=0; j<nNodes[(i+1)]; j++)
    {
      //If the node is frozen, we just reset the accumulators,
      //otherwise, we actually train the weights connected to it.
      if (frozenNode[i][j])
      {
        MSG_DEBUG("Skipping updating node " << j 
            << " from hidden layer " << i 
            << ", since it is frozen!");
        for (unsigned k=0; k<nNodes[i]; k++) {
          dw[i][j][k] = 0;
        }
        if (usingBias[i]) {
          db[i][j] = 0;
        } else {
          bias[i][j] = 0;
        }
      } else {
        for (unsigned k=0; k<nNodes[i]; k++)
        {
          if ( notFrozenW[i][j][k] ) {
            updateW(delta_w[i][j][k], 
                dw[i][j][k], 
                prev_dw[i][j][k], 
                weights[i][j][k]);
          }
        }
        if (usingBias[i]) {
          updateW(delta_b[i][j], db[i][j], prev_db[i][j], bias[i][j]);
        } else {
          bias[i][j] = 0;
        }
      }
    }
  }
}


//==============================================================================
void RProp::updateW(REAL &delta, REAL &d, REAL &prev_d, REAL &w)
{
  const REAL val = prev_d * d;
        
  if (val > 0.) {
    delta = min((delta*incEta), deltaMax);
  } else if (val < 0.) {
    delta = max((delta*decEta), deltaMin);
  }

  w += (sign(d) * delta);
  prev_d = d;
  d = 0;
}

//===============================================================================
void RProp::copyNeededTrainingInfo(const Backpropagation &net)
{
  if ( this == &net) {
    return;
  }

  Backpropagation::copyNeededTrainingInfo(net);

  const RProp *rprop_net(nullptr);

  if ( (rprop_net = dynamic_cast<const RProp*>(&net)) != nullptr )
  {
    this->copyPrevDeltas(*rprop_net);
  } else {
    MSG_FATAL("Attempted to copy needed information to a RProp training "
        "algorithm from an trainining algorithm which isn't an instance "
        "from it!"); 
  }
}

//===============================================================================
void RProp::copyNeededTrainingInfoFast(const Backpropagation &net)
{
  Backpropagation::copyNeededTrainingInfoFast(net);
  this->copyPrevDeltas(static_cast<const RProp&>(net));
}


//==============================================================================
void RProp::showInfo() const
{
  Backpropagation::showInfo();
  MSG_INFO("TRAINING ALGORITHM INFORMATION");
  MSG_INFO("Training algorithm: Resilient Backpropagation");
  MSG_INFO("Maximum allowed learning rate value (deltaMax) = " 
      << deltaMax);
  MSG_INFO("Minimum allowed learning rate value (deltaMin) = " 
      << deltaMin);
  MSG_INFO("Learning rate increasing factor (incEta) = " << incEta);
  MSG_INFO("Learning rate decreasing factor (decEta) = " << decEta);
  MSG_INFO("Initial learning rate value (initEta) = " << initEta);
}

} // namespace TuningTool

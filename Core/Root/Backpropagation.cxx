#include <vector>
#include <string>
#include <cstdlib>
#include <typeinfo>
#include <sstream>

#include "TuningTools/neuralnetwork/Backpropagation.h"

namespace TuningTool
{

//==============================================================================
Backpropagation::Backpropagation() 
  : IMsgService("Backpropagation"),
    NeuralNetwork(),
    sigma(nullptr),
    dw(nullptr),
    db(nullptr),
    frozenNode(nullptr),
    notFrozenW(nullptr){;}
 
//==============================================================================
Backpropagation::Backpropagation(const NetConfHolder &net, 
                                 const MSG::Level msglevel, 
                                 const std::string& name) 
  : IMsgService("Backpropagation"),
    NeuralNetwork(net, msglevel, name),
    learningRate(net.getLearningRate()),
    decFactor(net.getDecFactor()),
    sigma(nullptr),
    dw(nullptr),
    db(nullptr),
    frozenNode(nullptr),
    notFrozenW(nullptr)
{

  // Allocate space for this object:
  allocateSpace();

  // Verifying if there are frozen nodes and seting them.
  for (unsigned i=0; i<(nNodes.size()-1); i++)
  {
    // For the frozen nodes, we first initialize them all as unfrozen.
    setFrozen(i, false);
    
    // Initializing dw and db.
    for (unsigned j=0; j<nNodes[i+1]; j++) 
    {
      this->db[i][j] = 0.;
      this->sigma[i][j] = 0.;
      for (unsigned k=0; k<nNodes[i]; k++) {
        this->dw[i][j][k] = 0.;
        this->notFrozenW[i][j][k] = 1;
      }
    }
  }
}

//==============================================================================
Backpropagation::Backpropagation(const Backpropagation &net) 
  : IMsgService("Backpropagation"),
    NeuralNetwork(),
    learningRate(net.learningRate),
    decFactor(net.decFactor),
    sigma(nullptr),
    dw(nullptr),
    db(nullptr),
    frozenNode(nullptr),
    notFrozenW(nullptr)
{
  this->operator=(net);
}

//==============================================================================
void Backpropagation::copyFrozenNodes(const Backpropagation &net)
{
  for (unsigned i=0; i<(nNodes.size() - 1); i++)
  {
    memcpy(frozenNode[i], net.frozenNode[i], nNodes[i+1]*sizeof(bool));
  }
}

//==============================================================================
void Backpropagation::copyDeltas(const Backpropagation &net)
{
  for (unsigned i=0; i<(nNodes.size() - 1); i++)
  {
    memcpy(db[i], net.db[i], nNodes[i+1]*sizeof(REAL));
    for (unsigned j=0; j<nNodes[i+1]; j++)
    {
      memcpy(dw[i][j], net.dw[i][j], nNodes[i]*sizeof(REAL));
    }
  }
}

//==============================================================================
void Backpropagation::copyFrozenW(const Backpropagation &net)
{
  for (unsigned i=0; i<(nNodes.size() - 1); i++)
  {
    for (unsigned j=0; j<nNodes[i+1]; j++)
    {
      memcpy(notFrozenW[i][j], net.notFrozenW[i][j], nNodes[i]*sizeof(int));
    }
  }
}

//==============================================================================
void Backpropagation::copySigmas(const Backpropagation &net)
{
  for (unsigned i=0; i<(nNodes.size() - 1); i++)
  {
    memcpy(sigma[i], net.sigma[i], nNodes[i+1]*sizeof(REAL));
  }
}

//==============================================================================
Backpropagation& Backpropagation::operator=(const Backpropagation &net)
{ 
  // Assign parent class members
  NeuralNetwork::operator=(net);

  learningRate = net.learningRate;
  decFactor = net.decFactor;

  if (!isAllocated()){
    allocateSpace();
  }

  this->copyFrozenNodes(net);
  this->copySigmas(net);
  this->copyDeltas(net);
  this->copyFrozenW(net);

  return *this;
}

//===============================================================================
bool Backpropagation::isAllocated() const
{
  if ( frozenNode != nullptr &&
       notFrozenW != nullptr &&
       db != nullptr &&
       sigma != nullptr &&
       dw != nullptr )
  {
    return true;
  } else if ( frozenNode == nullptr &&
              notFrozenW == nullptr &&
              db == nullptr &&
              sigma == nullptr &&
              dw == nullptr )
  {
    return false;
  } else {
    MSG_FATAL("Backpropagation pointers point both to memory regions and to "
        "nullptr.")
  }
}


//==============================================================================
void Backpropagation::allocateSpace()
{
  // Allocate space for parent class
  if ( !NeuralNetwork::isAllocated() ){
    NeuralNetwork::allocateSpace();
  }

  if ( isAllocated() ) {
    MSG_ERROR("Attempted to reallocate " << getLogName() 
        << "(" << m_name << ")");
    return;
  }

  MSG_DEBUG("Allocating Backpropagation space for " 
      << m_name << "...");

  const unsigned size = nNodes.size() - 1;

  try {
    frozenNode = new bool* [size];
    db = new REAL* [size];
    sigma = new REAL* [size];
    dw = new REAL** [size];
    notFrozenW = new int** [size];
    for (unsigned i=0; i<size; i++)
    {
      frozenNode[i] = new bool [nNodes[i+1]];
      db[i] = new REAL [nNodes[i+1]];
      sigma[i] = new REAL [nNodes[i+1]];
      dw[i] = new REAL* [nNodes[i+1]];
      notFrozenW[i] = new int* [nNodes[i+1]];
      for (unsigned j=0; j<nNodes[i+1]; j++)
      {
        dw[i][j] = new REAL [nNodes[i]];
        notFrozenW[i][j] = new int [nNodes[i]];
      }
    }
  } catch (const std::bad_alloc &xa) {
    MSG_FATAL("Abort! Reason: " << xa.what() );
  }
}

//==============================================================================
Backpropagation::~Backpropagation()
{
  MSG_DEBUG("Deallocating Backpropagation space for " << m_name << "...");
  releaseMatrix(db);
  releaseMatrix(dw);
  releaseMatrix(notFrozenW);
  releaseMatrix(sigma);

  // Deallocating the frozenNode matrix.
  if (frozenNode)
  {
    for (unsigned i=0; i<(nNodes.size()-1); i++) {
      delete [] frozenNode[i];
    }
    delete [] frozenNode;
  }
}

//==============================================================================
void Backpropagation::retropropagateError(const REAL *output, 
    const REAL *target)
{
  const unsigned size = nNodes.size() - 1;

  for (unsigned i=0; i<nNodes[size]; i++) {
    sigma[size-1][i] = (target[i] - output[i]) * 
      CALL_TRF_FUNC(trfFunc[size-1])(output[i], true);
  }

  //Retropropagating the error.
  for (int i=(size-2); i>=0; i--)
  {
    for (unsigned j=0; j<nNodes[i+1]; j++)
    {
      sigma[i][j] = 0;

      for (unsigned k=0; k<nNodes[i+2]; k++)
      {
        sigma[i][j] += sigma[i+1][k] * weights[(i+1)][k][j];
      }

      sigma[i][j] *= CALL_TRF_FUNC(trfFunc[i])(layerOutputs[i+1][j], true);
    }
  }
}


//==============================================================================
void Backpropagation::calculateNewWeights(const REAL *output, 
    const REAL *target)
{
  const unsigned size = nNodes.size() - 1;

  retropropagateError(output, target);

  //Accumulating the deltas.
  for (unsigned i=0; i<size; i++)
  {
    for (unsigned j=0; j<nNodes[(i+1)]; j++)
    {
      for (unsigned k=0; k<nNodes[i]; k++)
      {
        dw[i][j][k] += sigma[i][j] * layerOutputs[i][k] * notFrozenW[i][j][k];
      }
      db[i][j] += (sigma[i][j]);
    }
  }
}

//==============================================================================
void Backpropagation::addToGradient(const Backpropagation &net)
{
  //Accumulating the deltas.
  for (unsigned i=0; i<(nNodes.size()-1); i++)
  {
    for (unsigned j=0; j<nNodes[(i+1)]; j++)
    {
      for (unsigned k=0; k<nNodes[i]; k++)
      {
        dw[i][j][k] += net.dw[i][j][k];
      }
      db[i][j] += net.db[i][j];
    }
  }
}

//===============================================================================
void Backpropagation::singletonInputNode( const unsigned nodeIdx, const unsigned pIdx )
{
  // Processing layers and init weights
  if ( nodeIdx < nNodes[1] ){
    for (unsigned k=0; k<nNodes[0]; k++)
    {
      weights[0][nodeIdx][k] = ( k == pIdx )?1.:0.;
    }
    for (unsigned j=0; j<nNodes[1]; j++) {
      if ( j != nodeIdx ) {
        notFrozenW[0][j][pIdx] = 0;
        weights[0][j][pIdx] = 0.;
      }
    }
    frozenNode[0][nodeIdx] = true;
    bias[0][nodeIdx] = 0.;
  } else {
    MSG_ERROR( "Couldn't set input node " << nodeIdx << " to singleton value." );
  }
}

//===============================================================================
void Backpropagation::updateInputLayer( const std::vector<REAL> weights
                     , const std::vector<int> frozen
                     , const std::vector<REAL> bias)
{
  std::vector<REAL>::const_iterator itrW = weights.begin();
  std::vector<REAL>::const_iterator itrB = bias.begin();
  std::vector<int>::const_iterator itrF  = frozen.begin();
  for (unsigned j=0; j<nNodes[1]; j++){
    for (unsigned k=0; k<nNodes[0]; k++)
    {
      this->weights[0][j][k] = (*itrW++);
      this->notFrozenW[0][j][k] = (*itrF++)?0:1;
    }
    this->bias[0][j] = (*itrB++);
  }
}

//==============================================================================
void Backpropagation::updateWeights(const unsigned numEvents)
{
  const REAL val = 1. / static_cast<REAL>(numEvents);
  
  for (unsigned i=0; i<(nNodes.size()-1); i++)
  {
    for (unsigned j=0; j<nNodes[(i+1)]; j++)
    {
      // If the node is frozen, we just reset the accumulators, otherwise, we
      // actually train the weights connected to it.
      if (frozenNode[i][j])
      {
        MSG_DEBUG("Skipping updating node " 
            << j << " from hidden layer " 
            << i << ", since it is frozen!");
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
          weights[i][j][k] += (learningRate * val * dw[i][j][k] * notFrozenW[i][j][k]);
          dw[i][j][k] = 0;
        }
        if (usingBias[i]) {
          bias[i][j] += (learningRate * val * db[i][j]);
          db[i][j] = 0;
        } else {
          bias[i][j] = 0;
        }
      }
    }
  }
}


//==============================================================================
void Backpropagation::showInfo() const
{
  NeuralNetwork::showInfo();
  MSG_INFO("TRAINING ALGORITHM INFORMATION:");
  MSG_INFO("Training algorithm : Gradient Descent");
  MSG_INFO("Learning rate      : " << learningRate);
  MSG_INFO("Decreasing factor  : " << decFactor);
      
  for (unsigned i=0; i<nNodes.size()-1; i++) 
  {
    std::ostringstream aux;
    aux << "Frozen Nodes in hidden layer " << i << ":";
    bool frozen = false;
    for (unsigned j=0; j<nNodes[i+1]; j++)
    {
      if (frozenNode[i][j])
      {
        aux << " " << j;
        frozen = true;
      }
    }
    if (!frozen) aux << " NONE";
    MSG_INFO(aux.str());

  }
}

//==============================================================================
bool Backpropagation::isFrozen(unsigned layer) const
{
  for (unsigned i=0; i<nNodes[layer+1]; i++)
  {
    if (!frozenNode[layer][i]) return false;
  }

  return true;
}

//==============================================================================
REAL Backpropagation::applySupervisedInput(const REAL *input, 
    const REAL *target, 
    const REAL* &output)
{
  int size = (nNodes.size()-1);
  REAL error = 0;

  // Propagating the input.
  output = propagateInput(input);
    
  //Calculating the error.
  for (unsigned i=0; i<nNodes[size]; i++){
    error += SQR(target[i] - output[i]);
  }
  //Returning the MSE
  return (error / nNodes[size]);
}

//===============================================================================
void Backpropagation::copyNeededTrainingInfo(const Backpropagation &net)
{
  if ( this == &net) {
    return;
  }
  this->operator=(net);
  //this->copyWeigthsFast(net);
  //this->copyDeltas(net);
  //this->copyFrozenW(net);
  //this->copyFrozen(net);
}

//===============================================================================
void Backpropagation::copyNeededTrainingInfoFast(const Backpropagation &net)
{
  this->operator=(net);
  //this->copyWeigthsFast(net);
  //this->copyDeltas(net);
  //this->copyFrozenW(net);
  //this->copyFrozen(net);
}


} // namespace TuningTool

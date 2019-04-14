
#include "TuningTools/neuralnetwork/NeuralNetwork.h"
#include "TuningTools/system/util.h"

#include <iostream>
#include <new>
#include <cstdlib>
#include <vector>
#include <string>
#include <sstream>
#include <stdexcept>

namespace TuningTool
{

//===============================================================================
NeuralNetwork::NeuralNetwork()
  : IMsgService("NeuralNetwork"),
    MsgService(MSG::FATAL),
    m_name("Unnamed"),
    weights(nullptr),
    bias(nullptr),
    layerOutputs(nullptr){;}


//===============================================================================
NeuralNetwork::NeuralNetwork( const MSG::Level msglevel,
               const std::string &name,
               const bool useColor )
  : IMsgService("NeuralNetwork"),
    MsgService(msglevel),
    m_name(name),
    weights(nullptr),
    bias(nullptr),
    layerOutputs(nullptr)
{
  this->setUseColor(useColor);
}

//===============================================================================
NeuralNetwork::NeuralNetwork( const NetConfHolder &net, 
                              const MSG::Level msglevel, 
                              const std::string& name )
  : IMsgService("NeuralNetwork"),
    MsgService(msglevel),
    m_name(name),
    weights(nullptr),
    bias(nullptr),
    layerOutputs(nullptr),
    nNodes(net.getNodes())
{
  MSG_DEBUG( "Creating new object of type " << getLogName() << "...");
  // Allocate memory for the neural network
  allocateSpace();

  MSG_DEBUG("Number of nodes in layer 0 " << nNodes[0] );

  for (size_t i=0; i< nNodes.size()-1; i++)
  {
    MSG_DEBUG("Number of nodes in layer " << (i+1) << ": " 
        << nNodes[(i+1)]);
    const std::string transFunction = net.getTrfFuncStr(i);
    this->trfFuncStr.push_back(transFunction);
    this->usingBias.push_back(net.isUsingBias(i));
    MSG_DEBUG("Layer " << (i+1) << " is using bias? " << this->usingBias[i]);

    if (transFunction == TGH_ID)
    {
      this->trfFunc.push_back(&NeuralNetwork::hyperbolicTangent);
      MSG_DEBUG("Transfer function in layer " << (i+1) << ": tanh");
    }
    else if (transFunction == LIN_ID)
    {
      this->trfFunc.push_back(&NeuralNetwork::linear);
      MSG_DEBUG("Transfer function in layer " << (i+1) << ": purelin");
    }
    else throw std::runtime_error("Transfer function not specified!");
  }
}

//===============================================================================
NeuralNetwork::NeuralNetwork(const NeuralNetwork &net)
  : IMsgService(net.getLogName()),
    MsgService(net.getMsgLevel()),
    m_name(net.m_name),
    weights(nullptr),
    bias(nullptr),
    layerOutputs(nullptr),
    nNodes(net.nNodes)
{
  this->operator=(net);
}

//===============================================================================
NeuralNetwork& NeuralNetwork::operator=(const NeuralNetwork &net)
{
  if ( this == &net){
    return *this;
  }

  setLogName( net.getLogName() );
  setMsgLevel( net.getMsgLevel() );

  MSG_DEBUG( "Duplicating " << getLogName()
      << "(" << m_name << ")..." );

  nNodes.assign(net.nNodes.begin(), net.nNodes.end());
  usingBias.assign(net.usingBias.begin(), net.usingBias.end());
  trfFunc.assign(net.trfFunc.begin(), net.trfFunc.end());
  trfFuncStr.assign(net.trfFuncStr.begin(), net.trfFuncStr.end());  

  if (!isAllocated()){
    allocateSpace();
  }

  layerOutputs[0] = net.layerOutputs[0]; // This will be a pointer to the input event.
  this->m_name = net.m_name;
  this->copyWeigths(net);
  return *this;
}

//===============================================================================
void NeuralNetwork::copyWeigths(const NeuralNetwork &net)
{
  if ( this == &net){
    return;
  }

  if ( !std::equal( this->nNodes.begin(),
                    this->nNodes.end(),
                    net.nNodes.begin() ) )
  {
    MSG_WARNING("Attempted to copy weigths from one network with different "
        "architeture, aborted copying weigths.");
    return;
  }

  copyWeigthsFast( net );
}

//===============================================================================
void NeuralNetwork::copyWeigthsFast(const NeuralNetwork &net)
{
  MSG_DEBUG( "Copying " << net.m_name << " network weigths to "
             << this->m_name );

  for (unsigned i=0; i<(nNodes.size()-1); i++)
  {
    memcpy(bias[i], net.bias[i], nNodes[i+1]*sizeof(REAL));
    memcpy(layerOutputs[i+1], net.layerOutputs[i+1], nNodes[i+1]*sizeof(REAL));
    for (unsigned j=0; j<nNodes[i+1]; j++) {
      memcpy(weights[i][j], net.weights[i][j], nNodes[i]*sizeof(REAL));
    }
  }
}

//===============================================================================
void NeuralNetwork::loadWeights( const std::vector<REAL> &weightsVec, const std::vector<REAL> &biasVec )
{
  const unsigned size =  nNodes.size() - 1;
  std::vector<REAL>::const_iterator itrW = weightsVec.begin();
  std::vector<REAL>::const_iterator itrB = biasVec.begin(); 
  ///Set weights and bias from external code
  for(unsigned i=0; i < size; ++i){
    for(unsigned j=0; j < nNodes[(i+1)]; ++j){
      bias[i][j] = (*itrB++);
      for(unsigned k=0; k < nNodes[i]; ++k)
        weights[i][j][k] =  (*itrW++);
    }
  }
}

//===============================================================================
void NeuralNetwork::initWeights()
{
  // Processing layers and init weights
  for (unsigned i=0; i<(nNodes.size()-1); i++)
  {
    for (unsigned j=0; j<nNodes[(i+1)]; j++)
    {
      for (unsigned k=0; k<nNodes[i]; k++)
      {
        weights[i][j][k] = static_cast<REAL>( util::rand_float_range(-1, 1)  );

      }
      bias[i][j] = (usingBias[i]) ? 
        static_cast<REAL>( util::rand_float_range(-1,1) ) : 
        0.;
    }
  }

  // Apply Nguyen-Widrow weight initialization algorithm
  for (unsigned i=0; i<(nNodes.size()-1); i++)
  {
    float beta = 0.7*pow((float) nNodes[i+1], (float) 1/nNodes[0]);
    for (unsigned j=0; j<nNodes[(i+1)]; j++)
    {
      REAL norm = util::get_norm_of_weight(weights[i][j], nNodes[i]);
      for (unsigned k=0; k<nNodes[i]; k++)
      {  
        weights[i][j][k] *= beta/norm;
        // MSG_INFO( 
        // "w[" << i << "][" << j << "][" << k << "] = " << weights[i][j][k] 
        // << " with norm = " << norm << " beta = " << beta);
      }
      bias[i][j] *= beta/norm;
      // MSG_INFO("b[" << i << "][" << j << "]  = " << bias[i][j]);
    }
  }

}

//bool NeuralNetwork::setTransferFunctions()
bool NeuralNetwork::removeOutputTansigTF()
{
  if ( trfFunc.size() ){
    MSG_DEBUG("Set last node TF to linear..." );
    this->trfFunc.at(trfFunc.size()-1) = (&NeuralNetwork::linear);
    return true;
  }
  return false;
  //for (size_t i=0; i< nNodes.size()-1; i++)
  //{
  //  const std::string transFunction = net.getTrfFuncStr(i);
  //  MSG_DEBUG("Setting node " << (i+1) << " transfer function to : " 
  //      << transFunction );
  //  this->trfFuncStr.at(i) = transFunction;
  //  if (transFunction == TGH_ID)
  //  {
  //    this->trfFunc.at(i) = (&NeuralNetwork::hyperbolicTangent);
  //    MSG_DEBUG("Transfer function in layer " << (i+1) << ": tanh");
  //  }
  //  else if (transFunction == LIN_ID)
  //  {
  //    this>trfFunc.at(i) = (&NeuralNetwork::linear);
  //    MSG_DEBUG("Transfer function in layer " << (i+1) << ": purelin");
  //  }
  //  else throw std::runtime_error("Transfer function not specified!");
  //}
}

//===============================================================================
bool NeuralNetwork::isAllocated() const
{
  if ( layerOutputs != nullptr &&
       bias != nullptr &&
       weights != nullptr )
  {
    return true;
  } else if ( layerOutputs == nullptr &&
              bias == nullptr &&
              weights == nullptr )
  {
    return false;
  } else {
    MSG_FATAL("NeuralNetwork pointers point both to memory regions and to "
        "nullptr.")
  }
}

//===============================================================================
void NeuralNetwork::allocateSpace()
{

  if ( isAllocated() ) {
    MSG_ERROR("Attempted to reallocate " << getLogName() 
        << "(" << m_name << ")");
    return;
  }

  MSG_DEBUG("Allocating NeuralNetwork space for " << m_name << "...");

  try {
    layerOutputs = new REAL* [nNodes.size()];
    layerOutputs[0] = nullptr; // This will be a pointer to the input event.

    const unsigned size = nNodes.size() - 1;

    bias = new REAL* [size];
    weights = new REAL** [size];

    for (unsigned i=0; i<size; i++)
    {
      bias[i] = new REAL [nNodes[i+1]];
      layerOutputs[i+1] = new REAL [nNodes[i+1]];
      weights[i] = new REAL* [nNodes[i+1]];
      for (unsigned j=0; j<nNodes[i+1]; j++) weights[i][j] = new REAL [nNodes[i]];
    }
  } catch (const std::bad_alloc &xa) {
    MSG_FATAL("Abort! Reason: " << xa.what() );
  }
}

//===============================================================================
NeuralNetwork::~NeuralNetwork()
{

  MSG_DEBUG("Destroying object " 
      << getLogName() << "(" << m_name << ")...");
  const unsigned size = nNodes.size() - 1;

  // Deallocating the bias and weight matrices.
  releaseMatrix(bias);
  releaseMatrix(weights);
  
  // Deallocating the hidden outputs matrix.
  if (layerOutputs)
  {
    for (unsigned i=1; i<size; i++)
    {
      delete [] layerOutputs[i];
    }
    delete [] layerOutputs;
  }
}

//===============================================================================
void NeuralNetwork::showInfo() const
{
  MSG_INFO("NEURAL NETWORK CONFIGURATION INFO");
  MSG_INFO("Number of Layers (including the input): " << nNodes.size());
  
  for (unsigned i=0; i<nNodes.size(); i++)
  {
    MSG_INFO("Layer " << i << " Configuration:");
    MSG_INFO("Number of Nodes   : " << nNodes[i]);
    
    if (i)
    {
      std::ostringstream aux;
      aux << "Transfer function : ";
      if (trfFunc[(i-1)] == (&NeuralNetwork::hyperbolicTangent)) aux << "tanh";
      else if (trfFunc[(i-1)] == (&NeuralNetwork::linear)) aux << "purelin";
      else aux << "UNKNOWN!";

      aux << ", bias        : ";
      if (usingBias[(i-1)]) aux << "true";
      else  aux << "false";
      MSG_INFO(aux.str());
    }      
  }
}

//===============================================================================
const REAL* NeuralNetwork::propagateInput(const REAL *input) const
{
  const unsigned size = (nNodes.size() - 1);

  // Placing the input. though we are removing the const' ness no changes are
  // perfomed.
  layerOutputs[0] = const_cast<REAL*>(input);

  // Propagating the input through the network.
  for (unsigned i=0; i<size; i++)
  {
    for (unsigned j=0; j<nNodes[i+1]; j++)
    {
      layerOutputs[i+1][j] = bias[i][j];
      for (unsigned k=0; k<nNodes[i]; k++)
      {
        layerOutputs[i+1][j] += layerOutputs[i][k] * weights[i][j][k];
      }
      layerOutputs[i+1][j] = CALL_TRF_FUNC(trfFunc[i])(layerOutputs[i+1][j], false);
    }
  }
  
  // Returning the network's output.
  return layerOutputs[size];
}


//===============================================================================
void NeuralNetwork::releaseMatrix(REAL **b)
{
  if (b)
  {
    for (unsigned i=0; i<(nNodes.size()-1); i++)
    {
      if (b[i]) delete [] b[i];
    }
    delete [] b;
    b = NULL;
  }
}

//===============================================================================
void NeuralNetwork::releaseMatrix(bool **b)
{
  if (b)
  {
    for (unsigned i=0; i<(nNodes.size()-1); i++)
    {
      if (b[i]) delete [] b[i];
    }
    delete [] b;
    b = NULL;
  }
}

//===============================================================================
void NeuralNetwork::releaseMatrix(REAL ***w)
{
  if (w)
  {
    for (unsigned i=0; i<(nNodes.size()-1); i++)
    {
      if (w[i])
      {
        for (unsigned j=0; j<nNodes[i+1]; j++)
        {
          if (w[i][j]) delete [] w[i][j];
        }
        delete [] w[i];
      }
    }
    delete [] w;
    w = NULL;
  }
}

//===============================================================================
void NeuralNetwork::releaseMatrix(int ***w)
{
  if (w)
  {
    for (unsigned i=0; i<(nNodes.size()-1); i++)
    {
      if (w[i])
      {
        for (unsigned j=0; j<nNodes[i+1]; j++)
        {
          if (w[i][j]) delete [] w[i][j];
        }
        delete [] w[i];
      }
    }
    delete [] w;
    w = NULL;
  }
}

//===============================================================================
void NeuralNetwork::setUsingBias(const unsigned layer, const bool val)
{
  usingBias[layer] = val;
  
  //If not using layers, we assign the biases values
  //in the layer to 0.
  if(!usingBias[layer])
  {
    for (unsigned i=0; i<nNodes[(layer+1)]; i++)
    {
      bias[layer][i] = 0;
    }
  }
}

} // namespace TuningTool

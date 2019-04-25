#include "TuningTools/training/Standard.h"

#include <stdexcept>

//==============================================================================
StandardTraining::StandardTraining( TuningTool::Backpropagation *net 
    , const Ndarray<REAL,2>* inTrn
    , const Ndarray<REAL,1>* outTrn
    , const Ndarray<REAL,2>* inVal
    , const Ndarray<REAL,1>* outVal 
    , const unsigned bSize
    , MSG::Level msglevel) 
  : IMsgService( "Training" ),
    Training(net, bSize, msglevel)
{

  if ( inTrn->getShape(0) != inVal->getShape(0) ) {
    throw std::invalid_argument("Input training and validating events " 
        "dimension does not match!");
  }
  if ( outTrn->getShape(0) != outVal->getShape(0) ) {
    throw std::invalid_argument("Output training and validating events "
        "dimension does not match!");
  }
  if ( inTrn->getShape(0) != outTrn->getShape(0) ) {
    throw std::invalid_argument("Number of input and target training "
        "events does not match!");
  }
  if ( inVal->getShape(0) != outVal->getShape(0) ) {
    throw std::invalid_argument("Number of input and target validating "
        "events does not match!");
  }

  inTrnData  = (inTrn->getPtr());
  outTrnData = (outTrn->getPtr());
  inValData  = (inVal->getPtr());
  outValData = (outVal->getPtr());
  inputSize  = inTrn->getShape(1);
  outputSize = outTrn->getShape(1);
 
  // FIXME When changing to new DM version
  dmTrn = new DataManager( inTrn->getShape(0) /*, batchSize*/ );
  numValEvents = inVal->getShape(0);
  MSG_DEBUG("Standard training was created.");
}
 
//==============================================================================
StandardTraining::~StandardTraining()
{
  delete dmTrn;
}

//==============================================================================
void StandardTraining::valNetwork(REAL &mseVal, 
    REAL &/*spVal*/, REAL &/*detVal*/, REAL &/*faVal*/)
{
  REAL gbError = 0.;
  REAL error = 0.;
  const REAL *output;

  const REAL *input = inValData;
  const REAL *target = outValData;
  const int numEvents = static_cast<int>(numValEvents);
  
  int i, thId;
  TuningTool::Backpropagation **nv = netVec;

#ifdef USE_OMP
  int chunk = chunkSize;
  #pragma omp parallel shared(input,target,chunk,nv,gbError) \
    private(i,thId,output,error)
#endif
  {
    thId = omp_get_thread_num();
    error = 0.;

#ifdef USE_OMP
    #pragma omp for schedule(dynamic,chunk) nowait
#endif
    for (i=0; i<numEvents; i++)
    {
      error += nv[thId]->applySupervisedInput(&input[i*inputSize], 
          &target[i*outputSize], output);
    }

#ifdef USE_OMP
    #pragma omp critical
#endif
    gbError += error;
  }
  
  mseVal = gbError / static_cast<REAL>(numEvents);
}


//==============================================================================
REAL StandardTraining::trainNetwork()
{
  unsigned pos;
  REAL gbError = 0.;
  REAL error = 0.;
  const REAL *output;

  const REAL *input = inTrnData;
  const REAL *target = outTrnData;

  int i, thId;
  TuningTool::Backpropagation **nv = netVec;
  DataManager *dm = dmTrn;
  const int nEvents = (batchSize) ? batchSize : dm->size();

#ifdef USE_OMP
  int chunk = chunkSize;
  #pragma omp parallel shared(input,target,chunk,nv,gbError,dm) \
    private(i,thId,output,error,pos)
#endif
  {
    thId = omp_get_thread_num(); 
    error = 0.;

#ifdef USE_OMP
    #pragma omp for schedule(dynamic,chunk) nowait
#endif
    for (i=0; i<nEvents; i++)
    {
      // FIXME When changing to new DM version
#ifdef USE_OMP
      #pragma omp critical
#endif
      pos = dm->get(/*i*/);
      
      error += nv[thId]->applySupervisedInput(
          &input[pos*inputSize], 
          &target[pos*outputSize], 
          output);
      nv[thId]->calculateNewWeights(output, 
          &target[pos*outputSize]);
    }

#ifdef USE_OMP
    #pragma omp critical
#endif
    gbError += error;    
  }

  updateGradients();
  updateWeights();
  
  return (gbError / static_cast<REAL>(nEvents));
}

//==============================================================================
void StandardTraining::showInfo(const unsigned nEpochs) const
{
  MSG_INFO("TRAINING DATA INFORMATION (Standard Network)");
  MSG_INFO("Number of Epochs          : " << nEpochs);
}

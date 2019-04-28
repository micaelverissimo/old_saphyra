#include "TuningTools/training/PatternRec.h"

//==============================================================================
PatternRecognition::PatternRecognition(
    TuningTool::Backpropagation *net, std::vector< Ndarray<REAL,2>* > inTrn, 
    std::vector< Ndarray<REAL,2>* > inVal, std::vector< Ndarray<REAL,2>* > inTst,  
    const TrainGoal mode, const unsigned bSize,
    const REAL signalWeight, const REAL noiseWeight, MSG::Level msglevel) 
  : IMsgService( "PatternRecognition" ),
    Training(net, bSize, msglevel), 
    trainGoal(mode),
    goalDet(1.0),
    goalFa(0.0)
{
  MSG_DEBUG("Starting a Pattern Recognition Training Object");
  // Initialize weights for SP calculation
  this->signalWeight = signalWeight;
  this->noiseWeight = noiseWeight;
  bool hasTstData = !inTst.empty();
  useSP = (trainGoal != MSE_STOP) ? true: false; 

  if (useSP) {
    bestGoalSP  = 0.;
    bestGoalDet = 0.;
    bestGoalFa  = 0.;
    if(trainGoal == SP_STOP) {
      MSG_DEBUG("Using SP validation criteria.");
    }
    if(trainGoal == MULTI_STOP) {
      MSG_DEBUG("Using SP, DET and FA validation criteria.");
    }
  } else {
    MSG_DEBUG("Using MSE validation criteria.");
  }
  
  numPatterns = inTrn.size();
  MSG_DEBUG("Number of patterns: " << numPatterns);
  outputSize = (numPatterns == 2) ? 1 : numPatterns;
  
  // The last 2 parameters for the training case will not be used by the
  // function, so, there is no problem passing the corresponding validation
  // variables to this first function call.
  MSG_DEBUG("Allocating memory for training data.");
  allocateDataset(inTrn, true, inTrnList, epochValOutputs, numValEvents);
  MSG_DEBUG("Allocating memory for validation data.");
  allocateDataset(inVal, false, inValList, epochValOutputs, numValEvents);
  if (hasTstData) {
    MSG_DEBUG("Allocating memory for testing data.");
    allocateDataset(inTst, false, inTstList, epochTstOutputs, numTstEvents);
  }
  //Creating the targets for each class (maximum sparsed oututs).
  targList = new const REAL* [numPatterns];  
  for (unsigned i=0; i<numPatterns; i++)
  {
    REAL *target = new REAL [outputSize];
    for (unsigned j=0; j<outputSize; j++) target[j] = -1;
    target[i] = 1;
    //Saving the target in the list.
    targList[i] = target;    
  }
  
  MSG_DEBUG("Input events dimension: " << inputSize);
  MSG_DEBUG("Output events dimension: " << outputSize);
}

//==============================================================================
void PatternRecognition::allocateDataset(
    std::vector< Ndarray<REAL,2>* > dataSet, const bool forTrain, 
    const REAL **&inList, REAL **&out, unsigned *&nEv)
{
  inList = new const REAL* [numPatterns];

  if (!forTrain)
  {
    nEv = new unsigned [numPatterns];
    if (useSP) out = new REAL* [numPatterns];
  }
  
  for (unsigned i=0; i<numPatterns; i++)
  {
    Ndarray<REAL,2>* patData = dataSet[i];
    inputSize = patData->getShape(1);
    inList[i] = patData->getPtr();

    if (forTrain)
    {
      // FIXME When changing to new DM version
      dmTrn.push_back(new DataManager(patData->getShape(0)/*, batchSize*/));
      MSG_DEBUG("Number of events for pattern " << i 
          << ":" << patData->getShape(0));
    } else {
      nEv[i] = static_cast<unsigned>(patData->getShape(0));
      if (useSP) out[i] = new REAL [nEv[i]];
      MSG_DEBUG("Number of events for pattern " << i 
          << ":" << nEv[i]);
    }
  }


}

//==============================================================================
void PatternRecognition::deallocateDataset( const bool forTrain, 
    const REAL **&inList, 
    REAL **&out, 
    unsigned *&nEv)
{
  for (unsigned i=0; i<numPatterns; i++)
  {
    if (forTrain) delete dmTrn[i];
    else if (useSP) delete [] out[i];
  }

  delete [] inList;
  if (!forTrain)
  {
    delete [] nEv;
    if (useSP) delete [] out;
  }
}

//==============================================================================
PatternRecognition::~PatternRecognition()
{
  // The last 2 parameters for the training case will not be used by the
  // function, so, there is no problem passing the corresponding validation
  // variables to this first function call.
  deallocateDataset(true, inTrnList, epochValOutputs, numValEvents);
  deallocateDataset(false, inValList, epochValOutputs, numValEvents);
  if (hasTstData) {
    deallocateDataset(false, inTstList, epochTstOutputs, numTstEvents);
  }
  for (unsigned i=0; i<numPatterns; i++) delete [] targList[i];
  delete [] targList;
}


//==============================================================================
REAL PatternRecognition::sp(const unsigned *nEvents, 
    REAL **epochOutputs, 
    REAL &det,  
    REAL &fa )
{

  // Reset the operations points for MULTI_STOP criteria
  bestsp_point.sp = bestsp_point.det = bestsp_point.fa = 0.0; // DEFAULT or MULTI_STOP 
  det_point.sp    = det_point.det    = det_point.fa = 0.0;// MULTI_STOP
  fa_point.sp     = fa_point.det     = fa_point.fa = 0.0;// MULTI_STOP

  unsigned TARG_SIGNAL, TARG_NOISE;  
  // We consider that our signal has target output +1 and the noise, -1. So, the
  // if below help us figure out which class is the signal.
  if (targList[0][0] > targList[1][0]) // target[0] is our signal.
  {
    TARG_NOISE = 1;
    TARG_SIGNAL = 0;    
  }
  else //target[1] is the signal.
  {
    TARG_NOISE = 0;
    TARG_SIGNAL = 1;
  }

  const REAL *signal = epochOutputs[TARG_SIGNAL];
  const REAL *noise = epochOutputs[TARG_NOISE];
  const REAL signalTarget = targList[TARG_SIGNAL][0];
  const REAL noiseTarget = targList[TARG_NOISE][0];
  const int numSignalEvents = static_cast<int>(nEvents[TARG_SIGNAL]);
  const int numNoiseEvents = static_cast<int>(nEvents[TARG_NOISE]);
  const REAL RESOLUTION = 0.01;
  REAL maxSP    = -1.;

  //reset deltas 
  deltaDet = 999;
  deltaFa  = 999;

  int i;
#ifdef USE_OMP
  int chunk = chunkSize;
#endif


  for (REAL pos = noiseTarget; pos < signalTarget; pos += RESOLUTION)
  {
    REAL sigEffic = 0.;
    REAL noiseEffic = 0.;
    unsigned se, ne;
    
#ifdef USE_OMP
    #pragma omp parallel shared(signal, noise, sigEffic, noiseEffic) \
      private(i,se,ne)
#endif
    {
      se = ne = 0;
      
#ifdef USE_OMP
      #pragma omp for schedule(dynamic,chunk) nowait
#endif
      for (i=0; i<numSignalEvents; i++) if (signal[i] >= pos) se++;
      
#ifdef USE_OMP
      #pragma omp critical
#endif
      sigEffic += static_cast<REAL>(se);

#ifdef USE_OMP
      #pragma omp for schedule(dynamic,chunk) nowait
#endif
      for (i=0; i<numNoiseEvents; i++) if (noise[i] < pos) ne++;
      
#ifdef USE_OMP
      #pragma omp critical
#endif
      noiseEffic += static_cast<REAL>(ne);
    }
    
    sigEffic /= static_cast<REAL>(numSignalEvents);
    noiseEffic /= static_cast<REAL>(numNoiseEvents);

    // Use weights for signal and noise efficiencies
    sigEffic *= signalWeight;
    noiseEffic *= noiseWeight;

    //Using normalized SP calculation.
    const REAL sp = sqrt( ((sigEffic + noiseEffic) / 2) * sqrt(sigEffic * noiseEffic) );

    if (sp > maxSP){
      maxSP            = sp;
      bestsp_point.sp  = maxSP /*best SP*/; bestsp_point.det = sigEffic; bestsp_point.fa  = 1-noiseEffic;
      if(trainGoal != MULTI_STOP){
        det = sigEffic;  fa = 1-noiseEffic;
      }
     
      
    }
    
    if(trainGoal == MULTI_STOP){//the most approximated values than the goals
      // TRAINNET_DET_ID
      if ( std::fabs(sigEffic - goalDet) < deltaDet ){
        fa       = 1-noiseEffic;
        deltaDet = std::abs(sigEffic-goalDet);
        det_point.sp = sp; det_point.det = sigEffic /*detFitted*/; det_point.fa = fa;
      }
      // TRAINNET_FA_ID
      if ( std::fabs((1-noiseEffic) - goalFa) < deltaFa ){
        det     = sigEffic;
        deltaFa = std::abs((1-noiseEffic)-goalFa);
        fa_point.sp = sp; fa_point.det = det; fa_point.fa = 1-noiseEffic /*faFitted*/;
      }
    }


  }


  return maxSP; // The SP value is in percent.
}


//==============================================================================
void PatternRecognition::getNetworkErrors(
    const REAL **inList, 
    const unsigned *nEvents,
    REAL **epochOutputs, 
    REAL &mseRet, 
    REAL &spRet, 
    REAL &detRet, 
    REAL &faRet)
{
  REAL gbError = 0.;
  TuningTool::Backpropagation **nv = this->netVec;
  int totEvents = 0;

  unsigned inputSize = this->inputSize;
  bool useSP = this->useSP;

#if defined(TUNINGTOOL_DBG_LEVEL) && TUNINGTOOL_DBG_LEVEL > 0
  for (unsigned i=0; i < nThreads; i++){ 
    MSG_DEBUG("Printing netVec[" << i << "] weigths:");
    if ( msgLevel( MSG::DEBUG) ){
      netVec[i]->printWeigths();
    }
  }
#endif
  
  for (unsigned pat=0; pat<numPatterns; pat++)
  {
    totEvents += nEvents[pat];

    const REAL * target = targList[pat];
    const REAL * input = inList[pat];
    const REAL *output;
    const int numEvents = nEvents[pat];
    int i, thId;
#ifdef USE_OMP
    int chunk = chunkSize;
#endif
    TuningTool::Backpropagation *thread_nv;
    
    REAL *outList = (useSP) ? epochOutputs[pat] : nullptr;
    
    MSG_DEBUG("Applying performance calculation for pattern " 
        << pat << " (" << numEvents << " events).");

    
#ifdef USE_OMP
    #pragma omp parallel default(none) \
        shared(chunk,nv,inputSize,outList,useSP,input,target) \
        private(i,thId,output,thread_nv) \
        reduction(+:gbError)
#endif
    { // fork
      thId = omp_get_thread_num();

      thread_nv = nv[thId];

#ifdef USE_OMP
      #pragma omp for schedule(dynamic, chunk) nowait
#endif
      for (i=0; i<numEvents; ++i)
      {
        gbError += thread_nv->applySupervisedInput(input + (i*inputSize), 
            target, 
            output);
        if (useSP) outList[i] = output[0];
      } // no barrier
    } // join

    

    // Display some debuging messages
#if defined(TUNINGTOOL_DBG_LEVEL) && TUNINGTOOL_DBG_LEVEL > 0
    MSG_DEBUG( "gbError is: " << gbError );
    if ( msgLevel( MSG::DEBUG ) ) {
      for (i=0; i<4; ++i)
      {
        nv[0]->applySupervisedInput(input + (i*inputSize), 
            target, 
            output);
        nv[0]->printLayerOutputs();
        msg() << MSG::DEBUG << "The output for pattern[" << pat
          << "] is : " << output[0] << endreq;
      }
      msg() << MSG::DEBUG << "The inputs for pattern[" << pat << "] are: " << endreq;
      for ( int k = 0; k < ((numEvents>3)?(3):(numEvents)); ++k )
      {
        msg() << "[";
        for ( unsigned m = 0; m < inputSize; ++m ){
          msg() << input[k*inputSize+m] << ",";
        } msg() << "],";
        if ( k != 2 ) msg() << endreq;
      } msg() << "]" << endreq;
      msg() << MSG::DEBUG << "The outputs for pattern[" << pat
        << "] are: " << endreq << "[";
      for ( int k = 0; k < ((numEvents>3)?(3):(numEvents)); ++k )
      {
        msg() << outList[k] << ",";
      } msg() << "]" << endreq;
    }
#endif
  }

  mseRet = gbError / static_cast<REAL>(totEvents);
  if (useSP)  {
    spRet = sp(nEvents, epochOutputs, detRet, faRet);
    MSG_DEBUG( "spRet = " << spRet 
        << " | detRet = " << detRet 
        << " | faRet = "  << faRet );
  }
}


//==============================================================================
REAL PatternRecognition::trainNetwork()
{
  MSG_DEBUG("Starting training process for an epoch.");
  TuningTool::Backpropagation **nv = this->netVec;
  TuningTool::Backpropagation *thread_nv;
  REAL gbError = 0;
  int totEvents = 0; // Holds the amount of events presented to the network.
  unsigned inputSize = this->inputSize;
#ifdef USE_OMP
  int chunk = chunkSize;
#endif

  for(unsigned pat=0; pat<numPatterns; pat++)
  {
    // wFactor will allow each pattern to have the same relevance, despite the
    // number of events it contains.
    const REAL *target = targList[pat];
    const REAL *input = inTrnList[pat];
    const REAL *output;
    int i, thId;
    unsigned pos = 0;
    DataManager *dm = dmTrn[pat];

#if defined(TUNINGTOOL_DBG_LEVEL) && TUNINGTOOL_DBG_LEVEL > 0
    MSG_DEBUG("Printing Manager BEFORE running for pat[" << pat << "]");
    if ( msgLevel( MSG::DEBUG ) ){
      dm->print();
    }
#endif

    const int nEvents = (batchSize) ? batchSize : dm->size();

    totEvents += nEvents;

    MSG_DEBUG("Applying training set for pattern " 
        << pat << " by randomly selecting " 
        << nEvents << " events (out of " << dm->size() << ").");

#ifdef USE_OMP
    #pragma omp parallel default(none) \
        shared(chunk,nv,inputSize,input,target,dm) \
        private(i,thId,output,thread_nv,pos) \
        reduction(+:gbError)
#endif
    {
      thId = omp_get_thread_num();

      thread_nv = nv[thId];

#ifdef USE_OMP
      #pragma omp for schedule(dynamic,chunk) nowait
#endif
      for (i=0; i<nEvents; ++i)
      {
        // FIXME When changing to new DM version
#ifdef USE_OMP
        #pragma omp critical
#endif
        pos = dm->get(/*i*/);

        gbError += thread_nv->applySupervisedInput(
            input + (pos*inputSize), 
            target, 
            output);

        //Calculating the weight and bias update values.
        thread_nv->calculateNewWeights(output, target);

#if defined(TUNINGTOOL_DBG_LEVEL) && TUNINGTOOL_DBG_LEVEL > 0
        if ( i < 10 || i > nEvents - 10 ) {
          MSG_DEBUG( "Thread[" << thId << "] executing index[" 
              << i << "] got random index [" << pos << "] and output was [" 
              << output[0] << "]" );
          if ( msgLevel( MSG::DEBUG ) ) {
            thread_nv->printLayerOutputs();
            thread_nv->printWeigths();
            thread_nv->printDeltas();
          }
        } else {
          MSG_DEBUG( "Thread[" << thId << "] executing index[" 
              << i << "] got random index [" << pos << "]" );
        }
#endif
      }
    }

    // FIXME Shift the data manager (when change to new version)
    //dm->shift();
#if defined(TUNINGTOOL_DBG_LEVEL) && TUNINGTOOL_DBG_LEVEL > 0
    if ( msgLevel( MSG::DEBUG ) ){
      MSG_DEBUG("Printing Manager AFTER running for pat[" << pat << "]");
      dm->print();
    }
#endif
  }

#if defined(TUNINGTOOL_DBG_LEVEL) && TUNINGTOOL_DBG_LEVEL > 0
  MSG_DEBUG("BEFORE UPDATES:");
  if ( msgLevel( MSG::DEBUG ) ){
    for (unsigned i=0; i<nThreads; i++){ 
      MSG_DEBUG("Printing netVec[" << i << "] layerOutputs:");
      netVec[i]->printLayerOutputs();
      MSG_DEBUG("Printing netVec[" << i << "] weigths:");
      netVec[i]->printWeigths();
      MSG_DEBUG("Printing netVec[" << i << "] deltas:");
      netVec[i]->printDeltas();
    }
  }
#endif

  updateGradients();
  updateWeights();

#if defined(TUNINGTOOL_DBG_LEVEL) && TUNINGTOOL_DBG_LEVEL > 0
  MSG_DEBUG("AFTER UPDATES:");
  if ( msgLevel( MSG::DEBUG ) ){
    for (unsigned i=0; i<nThreads; i++){ 
      MSG_DEBUG("Printing netVec[" << i << "] weigths:");
      netVec[i]->printWeigths();
    }
  }
#endif

  return (gbError / static_cast<REAL>(totEvents));
}
  

//==============================================================================
void PatternRecognition::showInfo(const unsigned nEpochs) const
{
  MSG_INFO("TRAINING DATA INFORMATION "
      "(Pattern Recognition Optimized Network)");
  MSG_INFO("Number of Epochs          : " 
      << nEpochs);
  MSG_INFO("Using SP  Stopping Criteria      : " 
      << (((trainGoal == SP_STOP) || (trainGoal == MULTI_STOP))  
        ? "true" : "false"));
  MSG_INFO("Using DET Stopping Criteria      : " 
      << ((trainGoal == MULTI_STOP)  ? "true" : "false"));
  MSG_INFO("Using FA  Stopping Criteria      : " 
      << ((trainGoal == MULTI_STOP)  ? "true" : "false"));
}

//==============================================================================
void PatternRecognition::isBestNetwork(
    const REAL currMSEError, const REAL currSPError, const REAL currDetError, 
    const REAL currFaError, ValResult &isBestMSE, ValResult &isBestSP,
    ValResult &isBestDet,   ValResult &isBestFa)
{
  // Knowing whether we have a better network, according to the MSE validation
  // criterium.
  Training::isBestNetwork(
      currMSEError, currSPError, currDetError, currFaError,  
      isBestMSE, isBestSP, isBestDet, isBestFa);

  // Knowing whether we have a better network, accorting to: SP
  isBestGoal( currSPError,   bestGoalSP  , isBestSP);

  if(trainGoal == MULTI_STOP){
    
    // TRAINNET_DET_ID
    if(deltaDet < min_delta_det){
      isBestGoal( 1-currFaError ,   bestGoalFa , isBestDet);
    }else{
      isBestDet = WORSE;
    }

    // TRAINNET_FA_ID
    if(deltaFa < min_delta_fa){
      isBestGoal( currDetError,   bestGoalDet, isBestFa);
    }else{
      isBestFa = WORSE;
    }
  }//Multi Stop criteria

}
  

//==============================================================================
void PatternRecognition::showTrainingStatus( const unsigned epoch, 
    const REAL mseTrn, const REAL mseVal, const REAL spVal, 
    const REAL mseTst, const REAL spTst, const int stopsOn)
{
  switch (trainGoal)
  {
    case SP_STOP: {
      MSG_INFO("Epoch " << epoch 
          << ": mse (train) = " << mseTrn 
          << " mse (val) = " << mseVal 
          << " SP (val) = " << spVal 
          << " SP (tst) = " << spTst);
      break;
    } case MULTI_STOP: {
      MSG_INFO("Epoch " << epoch 
          << ": mse (train) = " << mseTrn 
          << " mse (val) = " << mseVal 
          << " SP (val) = " << spVal 
          << " SP (tst) = " << spTst 
          << " stops = "<< stopsOn );
      break;
    } default: {
      Training::showTrainingStatus(epoch, 
          mseTrn, mseVal, spVal, mseTst, spTst, 
          stopsOn);
    }
  }
}

//==============================================================================
void PatternRecognition::showTrainingStatus( const unsigned epoch, 
    const REAL mseTrn,  const REAL mseVal, const REAL spVal, 
    const int stopsOn)
{
  switch (trainGoal)
  {
    case SP_STOP: {
      MSG_INFO("Epoch " << epoch 
          << ": mse (train) = " << mseTrn << " mse (val) = " << mseVal <<" SP (val) = " << spVal); 
      break;
    } case MULTI_STOP: {
      MSG_INFO("Epoch " << epoch 
          << ": mse (train) = " << mseTrn << " mse (val) = " << mseVal <<" SP (val) = " << spVal 
          << " stops = "<< stopsOn );
      break;
    } default: {
      Training::showTrainingStatus( epoch, 
                                    mseTrn, 
                                    mseVal,
                                    spVal, 
                                    stopsOn );
    }
  }
}


#include "TuningTools/TuningToolPyWrapper.h"

// STL include(s)
#include <cstdlib>
#include <cstring>
#include "TuningTools/system/util.h"

//// Boost numpy api include(s):
//#include <boost/python/numpy/dtype.hpp>
//#include <boost/python/numpy/ndarray.hpp>
//namespace np = boost::python::numpy;


//==============================================================================
TuningToolPyWrapper::TuningToolPyWrapper()
  : TuningToolPyWrapper( MSG::INFO )
{;}

//==============================================================================
TuningToolPyWrapper::TuningToolPyWrapper( const int msglevel )
  : TuningToolPyWrapper( msglevel, false, std::numeric_limits<unsigned>::max() )
{;}

//==============================================================================
TuningToolPyWrapper::TuningToolPyWrapper( const int msglevel, const bool useColor )
  : TuningToolPyWrapper( msglevel, useColor, std::numeric_limits<unsigned>::max() )
{;}

//==============================================================================
TuningToolPyWrapper::TuningToolPyWrapper( const int msglevel, const bool useColor,
    const unsigned seed )
  : IMsgService("TuningToolPyWrapper"),
    MsgService( msglevel, useColor )
{
  // MsgStream Manager object
  m_trainNetwork    = nullptr;
  m_train           = nullptr;
  m_stdTrainingType = true;

  setSeed( seed );
}

//==============================================================================
TuningToolPyWrapper::~TuningToolPyWrapper()
{

  MSG_DEBUG("Releasing memory...");

  if(m_trainNetwork)  delete m_trainNetwork;
  for(unsigned i = 0; i < m_saveNetworks.size(); ++i) {
    delete m_saveNetworks[i];
  }
  if(!m_trnData.empty()) releaseDataSet( m_trnData );
  if(!m_valData.empty()) releaseDataSet( m_valData );
  if(!m_tstData.empty()) releaseDataSet( m_tstData );
}

//==============================================================================
unsigned TuningToolPyWrapper::getSeed() const
{
  return m_seed;
}

//==============================================================================
void TuningToolPyWrapper::setSeed( const unsigned seed ) 
{
  unsigned m_seed = ( seed != std::numeric_limits<unsigned int>::max() )?
      ( seed ) : ( time(nullptr) );

  MSG_INFO("Changing pseudo-random number generator seed to (" << 
      m_seed << ")." );

  std::srand( m_seed ); 
}

//==============================================================================
py::list TuningToolPyWrapper::train_c()
{
 
  // Output will be: [networks, trainEvolution]
  py::list output;

  TrainGoal trainGoal = m_net.getTrainGoal();
  unsigned nClones = ( trainGoal == MULTI_STOP )?3:1;

  if ( ! m_trainNetwork ) {
    MSG_FATAL("Cannot train: no network was initialized!")
  }

  MSG_DEBUG("Cloning initialized network to hold best training epoch...")
  for(unsigned i = 0; i < nClones; ++i) {
    MSG_DEBUG("Cloning for index (" << i << ")" );
    m_saveNetworks.push_back( m_trainNetwork->clone() );
    // FIXME: This strategy will not work when optimizing multiple DETs and FAs
    // at the same time...
    switch ( i )
    {
      case TRAINNET_DEFAULT_ID:
        if ( trainGoal == MSE_STOP ){
          m_saveNetworks[i]->setName("NN_MSE_STOP");
        } else {
          m_saveNetworks[i]->setName("NN_SP_STOP");
        }
        break;
      case TRAINNET_DET_ID:
        m_saveNetworks[i]->setName("NN_DET_STOP");
        break;
      case TRAINNET_FA_ID:
        m_saveNetworks[i]->setName("NN_FA_STOP");
        break;
      default:
        throw std::runtime_error("Couldn't determine saved network type");
    }
  }
  MSG_DEBUG("Finished cloning...")

  //if(!m_tstData.empty()) m_stdTrainingType = false;
  m_stdTrainingType = false;
  // Check if goolType is mse default training  
  bool useSP = (trainGoal != MSE_STOP)? true : false;

  const unsigned show         = m_net.getShow();
  const unsigned fail_limit   = m_net.getMaxFail();
  const unsigned nEpochs      = m_net.getEpochs();
  const unsigned batchSize    = m_net.getBatchSize();
  const unsigned signalWeight = m_net.getSPSignalWeight();
  const unsigned noiseWeight  = m_net.getSPNoiseWeight();

  MSG_DEBUG("Creating training object...")
  if (m_stdTrainingType)
  {
    //m_train = new StandardTraining(m_network, m_in_trn, m_out_trn, m_in_val, m_out_val, batchSize,  getMsgLevel() );
  } else { // It is a pattern recognition network.
    if(m_tstData.empty())
    {
      m_train = new PatternRecognition(m_trainNetwork, 
          m_trnData, m_valData, m_valData, 
          trainGoal , batchSize, signalWeight, noiseWeight, 
          getMsgLevel() );
    } else {
      // If I don't have tstData , I will use the valData as tstData for training.
      m_train = new PatternRecognition( m_trainNetwork, 
          m_trnData, m_valData, m_tstData, 
          trainGoal , batchSize, signalWeight, noiseWeight, 
          getMsgLevel() );
    } 
    m_train->setUseColor( getUseColor() );
    if(trainGoal == MULTI_STOP){
      m_train->setReferences(m_net.getDet(), m_net.getFa());
      m_train->setDeltaDet( MAX_DELTA_VALUE );
      m_train->setDeltaFa( MAX_DELTA_VALUE );
      MSG_DEBUG("Setting MultiStop Criteria with DET = " << m_net.getDet() << " and FA" << m_net.getFa() << " as references");
    }

  }// pattern recognition network

#if defined(TUNINGTOOL_DBG_LEVEL) && TUNINGTOOL_DBG_LEVEL > 0
  MSG_DEBUG("Displaying configuration options...")
  this->showInfo();
  m_trainNetwork->showInfo();
  m_train->showInfo(nEpochs);
#endif

  // Performing the training.
  unsigned num_fails_mse = 0;
  unsigned num_fails_sp  = 0;
  unsigned num_fails_det = 0;
  unsigned num_fails_fa  = 0;
  unsigned dispCounter   = 0;


  REAL det_fitted, fa_fitted , delta_det, delta_fa = 0.;
  ValResult is_best_mse, is_best_sp, is_best_det, is_best_fa;
  bool stop_mse, stop_sp, stop_det, stop_fa = false;

  // Calculating the max_fail limits for each case (MSE and SP, if the case).
  const unsigned fail_limit_mse  = (useSP) ? (fail_limit / 2) : fail_limit; 
  const unsigned fail_limit_sp   = (useSP) ? fail_limit : 0;
  const unsigned fail_limit_det  = (useSP) ? fail_limit : 0;
  const unsigned fail_limit_fa   = (useSP) ? fail_limit : 0;

  bool stop = false;
  int stops_on(0);
  unsigned epoch(0);

  REAL mse_val, sp_val, det_val, fa_val, mse_tst, sp_tst, det_tst, fa_tst = 0.;
  roc::setpoint det_point_val, bestsp_point_val, fa_point_val;
  roc::setpoint det_point_tst, bestsp_point_tst, fa_point_tst;
  
  MSG_DEBUG("Start looping...")


  // Training loop
  for(; epoch < nEpochs; ++epoch){
    //if ( epoch == 0 ){
    //  m_trainNetwork->printFirstLayerWeigths();
    //}
    MSG_DEBUG("=================== Start of Epoch (" << epoch 
         << ") ===================");

    // Training the network and calculating the new weights.
    const REAL mse_trn = m_train->trainNetwork();

    /*
     * IF MULTI_STOP: 
     *   mse_val: mse validation curve from the current training;
     *   sp_val : sp validation curve from SP_STOP (best point found into the ROC);
     *   det_val: det validation curve from FA_STOP (best detection from FA point);
     *   fa_val : fa validation curve form PD_STOP (best false alarm from DET point).
     */
    m_train->valNetwork(mse_val, sp_val, det_val, fa_val);

    // Expert function: return full information if MULTI_STOP is TRUE. If trainGoal is MSE_STOP this function will
    // return structs with zeros, not use for nothing. Otherwise, only the first argument will be used for
    // the SP_STOP case. Usually, the MULTI_STOP was set as default.
    // TODO: Test the MSE and SP stop case to check if we will have some bug into the code.
    m_train->retrieve_operating_points( &bestsp_point_val, &det_point_val, &fa_point_val );
    m_train->retrieve_fitted_values(det_fitted, fa_fitted, delta_det, delta_fa);

    // Testing the new network if a testing dataset was passed.
    if (!m_tstData.empty()){
     /*
      * IF MULTI_STOP: 
      *   mse_tst: mse test curve from the current training;
      *   sp_tst : sp test curve from SP_STOP (best point found into the ROC);
      *   det_tst: det test curve from FA_STOP (best detection from FA point);
      *   fa_tst : fa test curve form PD_STOP (best false alarm from DET point).
      */
      m_train->tstNetwork(mse_tst, sp_tst, det_tst, fa_tst);
      m_train->retrieve_operating_points( &bestsp_point_tst, &det_point_tst, &fa_point_tst );
    }

    // Saving the best weight result.
    m_train->isBestNetwork( mse_val, sp_val, det_val, fa_val, 
                            is_best_mse, is_best_sp, is_best_det, is_best_fa);


    if(epoch > MIN_TRAIN_EPOCH) {  
    
      // Saving best neworks depends on each criteria
      if (is_best_mse == BETTER) {
        num_fails_mse = 0;
        MSG_DEBUG(BOLDMAGENTA << "Best mse was found with mse = " << mse_val << RESET);
        if (trainGoal == MSE_STOP) {
          m_saveNetworks[TRAINNET_DEFAULT_ID]->copyWeigthsFast(*m_trainNetwork);
        }
      } else if (is_best_mse == WORSE || is_best_mse == EQUAL) {
        ++num_fails_mse;
      }

      if (is_best_sp == BETTER) {
        num_fails_sp = 0;
        if( (trainGoal == SP_STOP) || (trainGoal == MULTI_STOP) ) {
          MSG_DEBUG(BOLDBLUE << "Best SP was found with SP = " << sp_val << RESET);
          m_saveNetworks[TRAINNET_DEFAULT_ID]->copyWeigthsFast(*m_trainNetwork);
        }
      } else if (is_best_sp == WORSE || is_best_sp == EQUAL) {
        ++num_fails_sp;
      }
 
      if (is_best_det == BETTER) {
        m_train->setDeltaDet( MIN_DELTA_VALUE );
        num_fails_det = 0;
        if(trainGoal == MULTI_STOP) {
          MSG_DEBUG(BOLDGREEN << "Best det point was found with [det_fitted = " << det_fitted << "] and fa = " 
                             << fa_val << RESET);
          m_saveNetworks[TRAINNET_DET_ID]->copyWeigthsFast(*m_trainNetwork);
        }
      } else if (is_best_det == WORSE || is_best_det == EQUAL) {
        ++num_fails_det;
      }
 
      if (is_best_fa == BETTER) {
        m_train->setDeltaFa( MIN_DELTA_VALUE );
        num_fails_fa = 0;
        if(trainGoal == MULTI_STOP) {
          MSG_DEBUG( BOLDRED << "Best fa point was found with det = " << det_val << " and [fa_fitted = " 
                            << fa_fitted << "]" << RESET);
          m_saveNetworks[TRAINNET_FA_ID]->copyWeigthsFast(*m_trainNetwork);
        }
      } else if (is_best_fa == WORSE || is_best_fa == EQUAL) {
        ++num_fails_fa;
      }

    }else{
      m_train->resetBestGoal();
    }

    // Discovering which of the criterias are telling us to stop.
    stop_mse  = num_fails_mse >= fail_limit_mse;
    stop_sp   = num_fails_sp  >= fail_limit_sp;
    stop_det  = num_fails_det >= fail_limit_det;
    stop_fa   = num_fails_fa  >= fail_limit_fa;
    
    // Save train information
    //if( saveAllPoints || epoch == 0 || (epoch%10)==0 || is_best_mse ==BETTER || is_best_sp == BETTER || is_best_det == BETTER || is_best_fa == BETTER){
    //  MSG_INFO( "Saving train info for epoch "<< epoch );
    m_train->saveTrainInfo(epoch, mse_trn, mse_val, mse_tst, 
                           bestsp_point_val, det_point_val, fa_point_val,
                           bestsp_point_tst, det_point_tst, fa_point_tst,
                           is_best_mse, is_best_sp, is_best_det, is_best_fa, 
                           num_fails_mse, num_fails_sp, num_fails_det, num_fails_fa, 
                           stop_mse, stop_sp, stop_det, stop_fa);
    //}


    if( (trainGoal == MSE_STOP) && (stop_mse) ) stop = true;
    if( (trainGoal == SP_STOP)  && (stop_mse) && (stop_sp) ) stop = true;
    if( (trainGoal == MULTI_STOP) && (stop_mse) && (stop_sp) && (stop_det) && (stop_fa) ) stop = true;

    // Number of stops flags on
    stops_on = (int)stop_mse + (int)stop_sp + (int)stop_det + (int)stop_fa;

    // Stop loop
    if ( stop ) {
      if ( show ) {
        if ( !m_tstData.empty() ) { 
          m_train->showTrainingStatus( epoch, 
              mse_trn, mse_val, sp_val, mse_tst, sp_tst, 
              stops_on );
        } else {
          m_train->showTrainingStatus( epoch, 
              mse_trn, mse_val, sp_val, 
              stops_on);
        }
        MSG_INFO("Maximum number of failures reached. " 
                        "Finishing training...");
      }
      break;
    }

    // Showing partial results at every "show" epochs (if show != 0).
    if ( show ) {
      if ( !dispCounter ) {

        if ( !m_tstData.empty() ) {
          m_train->showTrainingStatus( epoch, 
              mse_trn, mse_val, sp_val, mse_tst, sp_tst, 
              stops_on );
        } else {
          m_train->showTrainingStatus( epoch, 
              mse_trn, mse_val, sp_val, 
              stops_on );
        }
        //m_trainNetwork->printFirstLayerWeigths();
        
      }
      dispCounter = (dispCounter + 1) % show;
    }

  } if ( epoch == nEpochs ) {
    MSG_INFO("Maximum number of epochs (" << 
        nEpochs << ") reached. Finishing training...");
  }
  //m_saveNetworks[0]->printWeigths();

#if defined(TUNINGTOOL_DBG_LEVEL) && TUNINGTOOL_DBG_LEVEL > 0
  if ( msgLevel( MSG::DEBUG ) ){
    MSG_DEBUG( "Printing last epoch weigths:" ){
      m_trainNetwork->printWeigths();
    }
  }
#endif

  // Hold the train evolution before remove object
  flushTrainEvolution( m_train->getTrainInfo() );

  // Release memory
  MSG_DEBUG("Releasing train algorithm...");
  delete m_train;

  MSG_DEBUG("Appending neural networks to python list...");
  saveNetworksToPyList(output);

  MSG_DEBUG("Printing list of appended objects...");
#if defined(TUNINGTOOL_DBG_LEVEL) && TUNINGTOOL_DBG_LEVEL > 0
  if ( msg().msgLevel( MSG::DEBUG ) ) {
    PyObject_Print(py::object(output[py::len(output)-1]).ptr(), stdout, 0);
    //PyObject_Print("\n", stdout, 0);
  }
#endif
  
  MSG_DEBUG("Appending training evolution to python list...");
  output.append( trainEvolutionToPyList() );

  MSG_DEBUG("Exiting train_c...");
  return output;
}


//==============================================================================
py::list TuningToolPyWrapper::valid_c( const DiscriminatorPyWrapper &net )
{
  std::vector<REAL> signal, noise, signalTrn, noiseTrn, signalVal, noiseVal;
  py::list output;
  bool useTst = !m_tstData.empty();

  if(useTst){
    MSG_DEBUG("Propagating train dataset signal:");
    sim( net, m_trnData[0], signalTrn);  
    MSG_DEBUG("Propagating train dataset noise:");
    sim( net, m_trnData[1], noiseTrn);
    MSG_DEBUG("Propagating test dataset signal:");
    sim( net, m_tstData[0], signalVal);  
    MSG_DEBUG("Propagating test dataset noise:");
    sim( net, m_tstData[1], noiseVal);
    MSG_DEBUG("Propagating validation dataset signal:");
    sim( net, m_valData[0], signalVal);  
    MSG_DEBUG("Propagating validation dataset noise:");
    sim( net, m_valData[1], noiseVal);
  
  } else {
    MSG_DEBUG("Propagating validation dataset signal:");
    sim( net, m_valData[0], signalVal);  
    MSG_DEBUG("Propagating validation dataset noise:");
    sim( net, m_valData[1], noiseVal);
    MSG_DEBUG("Propagating train dataset signal:");
    sim( net, m_trnData[0], signalTrn);  
    MSG_DEBUG("Propagating train dataset noise:");
    sim( net, m_trnData[1], noiseTrn);
  
  }

  signal.reserve(signalTrn.size()+signalVal.size());
  noise.reserve(noiseTrn.size()+noiseVal.size());
  signal.insert(signal.end(), signalTrn.begin(), signalTrn.end());
  signal.insert(signal.end(), signalVal.begin(), signalVal.end());
  noise.insert(noise.end(), noiseTrn.begin(), noiseTrn.end());
  noise.insert(noise.end(), noiseVal.begin(), noiseVal.end());
  
    
  output.append( genRoc(signalVal, noiseVal, 0.005) );
  output.append( genRoc(signal, noise, 0.005) );
  output.append( util::std_vector_to_py_list<REAL>(signalTrn)  );
  output.append( util::std_vector_to_py_list<REAL>(noiseTrn)   );
  output.append( util::std_vector_to_py_list<REAL>(signalVal)  );
  output.append( util::std_vector_to_py_list<REAL>(noiseVal)   );

  return output;    
}


//==============================================================================
PyObject* TuningToolPyWrapper::sim_c( const DiscriminatorPyWrapper &net,
    const py::numeric::array &data )
{

  // Check if our array is on the correct type:
  auto handle = util::get_np_array( data );
  // Create our object holder:
  Ndarray<REAL,2> dataHandler( handle );
  // And extract information from it
  long numOfEvents = dataHandler.getShape(0);
  long inputSize = dataHandler.getShape(1);
  const REAL *inputEvents  = dataHandler.getPtr();

  // Create a PyObject of same length
  auto *pyObj = reinterpret_cast<PyArrayObject*>(PyArray_ZEROS( 1
      , &numOfEvents
      , type_to_npy_enum<REAL>::enum_val
      , 0 ));

  // Retrieve its raw pointer:
  REAL* outputEvents = reinterpret_cast<REAL*>(pyObj->data);

  /* This is commented b/c I think it is not needed */
  // Create a smart pointer handle to it (we need it to be deleted
  // as soon as it is not handled anymore)
  //py::handle<> handle( out );

  // Retrieve output size information
  const std::size_t outputSize = net.getNumNodes( 
      net.getNumLayers() - 1 );

  auto netCopy = net;

  unsigned i;
#ifdef USE_OMP
  int chunk = 1000;
  #pragma omp parallel shared(inputEvents, outputEvents, chunk) \
    private(i) firstprivate(netCopy)
#endif
  {
#ifdef USE_OMP
    #pragma omp for schedule(dynamic,chunk) nowait
#endif
    for ( i=0; i < numOfEvents; ++i )
    {
      std::copy_n( netCopy.propagateInput( inputEvents + (i*inputSize) ), 
          outputSize,
          outputEvents + (i*outputSize));
    }
  }

  // TODO Check if arr(handle) does not allocate more space (it only uses the 
  // handle to refer to the object. 
  // TODO What does happen if I set it to return the PyArray instead?
  //py::numeric::array arr( handle );
  //return arr.copy();
  return reinterpret_cast<PyObject*>(pyObj);

}

//==============================================================================
void TuningToolPyWrapper::setData( const py::list& data, 
    std::vector< Ndarray<REAL,2>* > TuningToolPyWrapper::* const setPtr )
{
  // Retrieve this member property from property pointer and set a reference to
  // it:
  std::vector< Ndarray<REAL,2>* > &set = this->*setPtr;

  // Check if set is empty, where we need to clean its previous memory:
  if ( !set.empty() ) {
    releaseDataSet( set );
  }

  // Loop over list and check for elements in which we can extract:
  for( unsigned pattern = 0; pattern < py::len( data ); pattern++ )
  {
    // Extract our array:
    py::extract<py::numeric::array> extractor( data[pattern] );
    if ( extractor.check() )
    {
      // Extract our array:
      const auto &pyObj = static_cast<py::numeric::array>(extractor());
      // Make sure that the input type is a numpy array and get it:
      auto handle = util::get_np_array( pyObj );
      // Retrieve our dataHandler:
      auto dataHandler = new Ndarray< REAL, 2 >( handle );
      // If we arrived here, it is OK, put it on our data set:
      MSG_DEBUG( "Added dataset of size (" 
                 << dataHandler->getShape(0) << "," 
                 << dataHandler->getShape(1) << ")"
               );
      set.push_back( dataHandler );
    } else {
      // We shouldn't be retrieving this, warn user:
      MSG_WARNING( "Input a list with an object on position " 
          << pattern 
          << " which is not a ctype numpy object (in fact it is of type: " 
          << py::extract<std::string>( 
              data[pattern].attr("__class__").attr("__name__"))()
          << ")." );
    }
  }
}

//==============================================================================
void TuningToolPyWrapper::flushTrainEvolution( 
    const std::list<TrainData*> &trnEvolution )
{

  m_trnEvolution.clear();  

  for( const auto& cTrnData : trnEvolution ) 
  {

    TrainDataPyWrapper trainData;

    trainData.setEpoch       ( cTrnData->epoch         );
    trainData.setMseTrn      ( cTrnData->mse_trn       );
    trainData.setMseVal      ( cTrnData->mse_val       );
    trainData.setMseTst      ( cTrnData->mse_tst       );
    trainData.setIsBestMse   ( cTrnData->is_best_mse   );
    trainData.setIsBestSP    ( cTrnData->is_best_sp    );
    trainData.setIsBestDet   ( cTrnData->is_best_det   );
    trainData.setIsBestFa    ( cTrnData->is_best_fa    );
    trainData.setNumFailsMse ( cTrnData->num_fails_mse );
    trainData.setNumFailsSP  ( cTrnData->num_fails_sp  );
    trainData.setNumFailsDet ( cTrnData->num_fails_det );
    trainData.setNumFailsFa  ( cTrnData->num_fails_fa  );
    trainData.setStopMse     ( cTrnData->stop_mse      );
    trainData.setStopSP      ( cTrnData->stop_sp       );
    trainData.setStopDet     ( cTrnData->stop_det      );
    trainData.setStopFa      ( cTrnData->stop_fa       );
 
    //Expert methods to attach the operating point information into the object
    trainData.set_bestsp_point_sp_val ( cTrnData->bestsp_point_val.sp  );
    trainData.set_bestsp_point_det_val( cTrnData->bestsp_point_val.det );
    trainData.set_bestsp_point_fa_val ( cTrnData->bestsp_point_val.fa  );
    trainData.set_bestsp_point_sp_tst ( cTrnData->bestsp_point_tst.sp  );
    trainData.set_bestsp_point_det_tst( cTrnData->bestsp_point_tst.det );
    trainData.set_bestsp_point_fa_tst ( cTrnData->bestsp_point_tst.fa  );
    trainData.set_det_point_sp_val    ( cTrnData->det_point_val.sp     );
    trainData.set_det_point_det_val   ( cTrnData->det_point_val.det    );
    trainData.set_det_point_fa_val    ( cTrnData->det_point_val.fa     );
    trainData.set_det_point_sp_tst    ( cTrnData->det_point_tst.sp     );
    trainData.set_det_point_det_tst   ( cTrnData->det_point_tst.det    );
    trainData.set_det_point_fa_tst    ( cTrnData->det_point_tst.fa     );
    trainData.set_fa_point_sp_val     ( cTrnData->fa_point_val.sp      );
    trainData.set_fa_point_det_val    ( cTrnData->fa_point_val.det     );
    trainData.set_fa_point_fa_val     ( cTrnData->fa_point_val.fa      );
    trainData.set_fa_point_sp_tst     ( cTrnData->fa_point_tst.sp      );
    trainData.set_fa_point_det_tst    ( cTrnData->fa_point_tst.det     );
    trainData.set_fa_point_fa_tst     ( cTrnData->fa_point_tst.fa      );

    m_trnEvolution.push_back(trainData);
  }
}

//==============================================================================
void TuningToolPyWrapper::showInfo()
{
  MSG_INFO( "TuningTools::Options param:\n" 
       << "  show          : " << m_net.getShow()        << "\n"
       << "  trainFcn      : " << m_net.getTrainFcn()    << "\n"
       << "  learningRate  :"  << m_net.getLearningRate()<< "\n"
       << "  DecFactor     :"  << m_net.getDecFactor()   << "\n"
       << "  DeltaMax      :"  << m_net.getDeltaMax()    << "\n"
       << "  DeltaMin      :"  << m_net.getDeltaMin()    << "\n"
       << "  IncEta        :"  << m_net.getIncEta()      << "\n"
       << "  DecEta        :"  << m_net.getDecEta()      << "\n"
       << "  InitEta       :"  << m_net.getInitEta()     << "\n"
       << "  Epochs        :"  << m_net.getEpochs() )
}


//==============================================================================
bool TuningToolPyWrapper::newff( 
    const py::list &nodes, 
    const py::list &trfFunc, 
    const std::string &trainFcn )
{
  MSG_DEBUG("Allocating TuningToolPyWrapper master neural network space...")
  if ( !allocateNetwork(nodes, trfFunc, trainFcn) ) {
    return false;
  }
  MSG_DEBUG("Initialiazing neural network...")
  m_trainNetwork->initWeights();
  return true;
}

//==============================================================================
bool TuningToolPyWrapper::fusionff( 
    const py::list &nodes, 
    const py::list &weights,
    const py::list &frozen,
    const py::list &bias,
    const py::list &trfFunc, 
    const std::string &trainFcn )
{
  MSG_DEBUG("Allocating TuningToolPyWrapper master neural network space...")
  if ( !allocateNetwork(nodes, trfFunc, trainFcn) ) {
    return false;
  }
  MSG_DEBUG("Initialiazing neural network...")
  m_trainNetwork->initWeights();
  MSG_DEBUG("Updating input layer W...")

  const auto cWeights = util::to_std_vector<float>(weights);
  const auto cFrozen  = util::to_std_vector<int>(frozen);
  const auto cBias    = util::to_std_vector<float>(bias);

  m_trainNetwork->updateInputLayer(cWeights, cFrozen, cBias);
  return true;
}

//==============================================================================
bool TuningToolPyWrapper::singletonInputNode( const unsigned nodeIdx, const unsigned pIdx )
{
  MSG_INFO("Using hidden layer node " << nodeIdx << " as single unit to propagate dimension " << pIdx << ".")
  m_trainNetwork->singletonInputNode(nodeIdx, pIdx);
  return true;
}

//==============================================================================
bool TuningToolPyWrapper::loadff( const py::list &nodes, 
    const py::list &trfFunc,  
    const py::list &weights, 
    const py::list &bias, 
    const std::string &trainFcn )
{
  if( !allocateNetwork( nodes, trfFunc, trainFcn) ) {
    return false;
  }

  m_trainNetwork->loadWeights( util::to_std_vector<REAL>(weights), 
      util::to_std_vector<REAL>(bias));
  return true;
}

//==============================================================================
bool TuningToolPyWrapper::allocateNetwork( 
    const py::list &nodes, 
    const py::list &trfFunc, 
    const std::string &trainFcn )
{

  // Reset all networks
  if ( m_trainNetwork ){
    delete m_trainNetwork; m_trainNetwork = nullptr;
    for(unsigned i = 0; i < m_saveNetworks.size(); ++i){
      delete m_saveNetworks[i];
    } 
    m_saveNetworks.clear();
  }
 
  std::vector<unsigned> nNodes = util::to_std_vector<unsigned>(nodes);
  m_net.setNodes(nNodes);
  m_net.setTrfFunc( util::to_std_vector<std::string>(trfFunc) );
  m_net.setTrainFcn(trainFcn);

  if ( trainFcn == TRAINRP_ID ) {
    MSG_DEBUG( "Creating RProp object..." );
    m_trainNetwork = new RProp(m_net, getMsgLevel(), "NN_TRAINRP");
  } else if( trainFcn == TRAINGD_ID ) {
    MSG_DEBUG( "Creating Backpropagation object...");
    m_trainNetwork = new Backpropagation(m_net, getMsgLevel(), "NN_TRAINGD");
  } else {
    MSG_WARNING( "Invalid training algorithm option(" << trainFcn << ")!" );
    return false;
  }
  m_trainNetwork->setUseColor( getUseColor() );
  return true;
}


//==============================================================================
void TuningToolPyWrapper::sim( const DiscriminatorPyWrapper &net,
    const Ndarray<REAL,2> *data,
    std::vector<REAL> &outputVec)
{
  // Retrieve number of input events:
  long numOfEvents = data->getShape(0);
  MSG_DEBUG("numOfEvents: " << numOfEvents);

  // Old end position:
  size_t oldSize = outputVec.size();

  // Increase size to handle data:
  outputVec.resize( oldSize + numOfEvents );

  // Retrieve old end output position:
  std::vector<REAL>::iterator outItr = outputVec.begin() + oldSize;

  // Get the number of outputs from neural network:
  const std::size_t outputSize = net.getNumNodes( net.getNumLayers() - 1 );

  MSG_DEBUG("Creating a copy of neural network: ");
  auto netCopy = net;
  netCopy.setName( netCopy.getName() + "_MultiThread");

  npy_intp i;
  MSG_DEBUG("Initialize loop: ");
#ifdef USE_OMP
  int chunk = 1000;
  #pragma omp parallel shared(data, outItr, chunk) \
      private(i) firstprivate(netCopy)
#endif
  {
#ifdef USE_OMP
    #pragma omp for schedule(dynamic, chunk) nowait
#endif
    for ( i=0; i < numOfEvents; ++i )
    {
      const auto &rings = (*data)[i];
      std::copy_n( netCopy.propagateInput( rings.getPtr() ), 
          outputSize,
          outItr + (i*outputSize));
    }
  }
  MSG_DEBUG("Finished loop.");
}


//==============================================================================
py::list TuningToolPyWrapper::genRoc( const std::vector<REAL> &signal, 
    const std::vector<REAL> &noise, 
    REAL resolution )
{

  std::vector<REAL> sp, det, fa, cut;
  util::genRoc( signal, noise, 1, -1, det, fa, sp, cut, resolution);

  py::list output;
  output.append( util::std_vector_to_py_list<REAL>(sp)  );
  output.append( util::std_vector_to_py_list<REAL>(det) );
  output.append( util::std_vector_to_py_list<REAL>(fa)  );
  output.append( util::std_vector_to_py_list<REAL>(cut) );
  return output;
}

//==============================================================================
py::object multiply(const py::numeric::array &m, float f)
{                                                                        
  PyObject* m_obj = PyArray_FROM_OTF(m.ptr(), NPY_FLOAT, NPY_IN_ARRAY);
  if (!m_obj)
    throw WrongTypeError();

  // to avoid memory leaks, let a Boost::Python object manage the array
  py::object temp(py::handle<>(m_obj));

  // check that m is a matrix of doubles
  int k = PyArray_NDIM(m_obj);
  if (k != 2)
    throw WrongSizeError();

  // get direct access to the array data
  const float* data = static_cast<const float*>(PyArray_DATA(m_obj));

  // make the output array, and get access to its data
  PyObject* res = PyArray_SimpleNew(2, PyArray_DIMS(m_obj), NPY_FLOAT);
  float* res_data = static_cast<float*>(PyArray_DATA(res));

  const unsigned size = PyArray_SIZE(m_obj); // number of elements in array
  for (unsigned i = 0; i < size; ++i)
    res_data[i] = f*data[i];

  return py::object(py::handle<>(res)); // go back to using Boost::Python constructs
}

//==============================================================================
py::object multiply(const py::list &list, float f)
{
  py::list output;
  for( unsigned pattern = 0; pattern < py::len( list ); pattern++ )
  {
    py::extract<py::numeric::array> extractor( list[pattern] );
    if ( extractor.check() )
    {
      // Extract our array:
      const auto &pyObj = static_cast<py::numeric::array>(extractor());
      output.append( multiply( pyObj, f ) );
      // Make sure that the input type is a numpy array and get it:
      auto handle = util::get_np_array( pyObj );
      // Retrieve our dataHandler:
      auto dataHandler = new Ndarray< REAL, 2 >( handle );
      std::cout << "Array size is (" << dataHandler->getShape(0) << ","
                << dataHandler->getShape(1) << ")" << std::endl;
      std::cout << "Input array is: [" << std::endl;
      for ( npy_int i = 0; i < dataHandler->getShape(0) && i < 6; ++i){
        std::cout << "[";
        for ( npy_int j = 0; j < dataHandler->getShape(1) && j < 6; ++j){
          std::cout << (*dataHandler)[i][j] << " ";
        } std::cout << "]" << std::endl;
      } std::cout << "]" << std::endl;
      delete dataHandler;
    }
  }
  return output;
}

//==============================================================================
PyObject* DiscriminatorPyWrapper::propagate_np( const py::numeric::array &data )
{

  // Check if our array is on the correct type:
  auto handle = util::get_np_array( data );
  // Create our object holder:
  Ndarray<REAL,2> dataHandler( handle );
  // And extract information from it
  long numOfEvents = dataHandler.getShape(0);
  long inputSize = dataHandler.getShape(1);
  const REAL *inputEvents  = dataHandler.getPtr();

  // Create a PyObject of same length
  auto *pyObj = reinterpret_cast<PyArrayObject*>(PyArray_ZEROS( 1
      , &numOfEvents
      , type_to_npy_enum<REAL>::enum_val
      , 0 ));

  // Retrieve its raw pointer:
  REAL* outputEvents = reinterpret_cast<REAL*>(pyObj->data);

  // Retrieve output size information
  const std::size_t outputSize = this->getNumNodes( this->getNumLayers() - 1 );

  auto netCopy = (*this);

  unsigned i;
#ifdef USE_OMP
  int chunk = 1000;
  #pragma omp parallel shared(inputEvents, outputEvents, chunk) \
    private(i) firstprivate(netCopy)
#endif
  {
#ifdef USE_OMP
    #pragma omp for schedule(dynamic,chunk) nowait
#endif
    for ( i=0; i < numOfEvents; ++i )
    {
      std::copy_n( netCopy.propagateInput( inputEvents + (i*inputSize) ), 
          outputSize,
          outputEvents + (i*outputSize));
    }
  }

  return reinterpret_cast<PyObject*>(pyObj);

}

//===============================================================================
//DiscriminatorPyWrapper::DiscriminatorPyWrapper(  const std::string& name,
//    const py::numeric::array &nodes,  const py::list &trfFunc,
//    const py::numeric::array &weights, const py::numeric::array &bias
//    /*const std::string &trainFcn = TRAINRP_ID*/)
//  : IMsgService("DiscriminatorPyWrapper"),
//    NeuralNetwork()
//{
//}

DiscriminatorPyWrapper::DiscriminatorPyWrapper(  const std::string& name,
    const MSG::Level lvl, const bool useColor,
    const py::list &nodes,  const py::list &trfFunc,
    const py::list &weights, const py::list &bias
    /*const std::string &trainFcn = TRAINRP_ID*/)
  : IMsgService("DiscriminatorPyWrapper"),
    NeuralNetwork(lvl,  name, useColor)
{

  // Allocate memory for the neural network
  this->nNodes = util::to_std_vector<unsigned>(nodes);
  allocateSpace();
  MSG_INFO( "Creating new object of type " << getLogName() << "...");

  this->loadWeights( util::to_std_vector<REAL>(weights), util::to_std_vector<REAL>(bias));
  auto trfFuncVec = util::to_std_vector<std::string>(trfFunc);
  MSG_DEBUG( "Creating new object of type " << getLogName() << "...");
  MSG_DEBUG("Number of nodes in layer 0 " << nNodes[0] );

  for (size_t i=0; i< nNodes.size()-1; i++)
  {
    MSG_DEBUG("Number of nodes in layer " << (i+1) << ": " << nNodes[(i+1)]);
    const std::string transFunction = trfFuncVec.at(i);
    this->trfFuncStr.push_back(transFunction);
    this->usingBias.push_back(true);
    MSG_DEBUG("Layer " << (i+1) << " is using bias? " << this->usingBias[i]);

    if (transFunction == TGH_ID)
    {
      this->trfFunc.push_back(&DiscriminatorPyWrapper::hyperbolicTangent);
      MSG_DEBUG("Transfer function in layer " << (i+1) << ": tanh");
    }
    else if (transFunction == LIN_ID)
    {
      this->trfFunc.push_back(&DiscriminatorPyWrapper::linear);
      MSG_DEBUG("Transfer function in layer " << (i+1) << ": purelin");
    }
    else throw std::runtime_error("Transfer function not specified!");
  }
  MSG_DEBUG("Transfer functions are:" << this->trfFunc );
  //this->printWeigths();
  //TODO Add frozen nodes
}



namespace __expose_TuningToolPyWrapper__ 
{

//==============================================================================
void __load_numpy(){
  py::numeric::array::set_module_and_type("numpy", "ndarray");
  import_array();
} 


//==============================================================================
void translate_sz(const WrongSizeError& e)                               
{                                                                        
  PyErr_SetString(PyExc_RuntimeError, e.what());                         
}                                                                        

//==============================================================================
void translate_ty(const WrongTypeError& e)
{                                                                        
  PyErr_SetString(PyExc_RuntimeError, e.what());                         
}                                                                        

//==============================================================================
void expose_exceptions()
{
  py::register_exception_translator<WrongSizeError>(&translate_sz);
  py::register_exception_translator<WrongTypeError>(&translate_ty);
}

//==============================================================================
void expose_multiply()
{
  py::object (*arraymultiply)(const py::numeric::array &, float) = &multiply;
  py::object (*listmultiply)(const py::list &, float) = &multiply;

  def("multiply", arraymultiply);
  def("multiply", listmultiply);
}

//==============================================================================
py::object* expose_DiscriminatorPyWrapper()
{
  static py::object _c = py::class_<DiscriminatorPyWrapper>( 
                                    "DiscriminatorPyWrapper", 
                                    py::init<const std::string&, const unsigned int, const bool
                                         , const py::list&, const py::list &
                                         , const py::list&, const py::list &>() )
    //.def(py::init<const std::string&, const py::numeric::array &, const py::numeric::array &,
    //                                      const py::numeric::array &, const py::numeric::array &>())
    .def("getNumLayers",            &DiscriminatorPyWrapper::getNumLayers         )
    .def("getNumNodes",             &DiscriminatorPyWrapper::getNumNodes          )
    .def("getBias",                 &DiscriminatorPyWrapper::getBias              )
    .def("getWeight",               &DiscriminatorPyWrapper::getWeight            )
    .def("getTrfFuncName",          &DiscriminatorPyWrapper::getTrfFuncName       )
    .def("getName",                 &DiscriminatorPyWrapper::getName              )
    .def("removeOutputTansigTF",    &DiscriminatorPyWrapper::removeOutputTansigTF )
    .def("propagate_np",            &DiscriminatorPyWrapper::propagate_np         )
  ;
  return &_c;
}

//==============================================================================
py::object* expose_TrainDataPyWrapper()
{
  static py::object _c = py::class_<TrainDataPyWrapper>("TrainDataPyWrapper", 
                                                         py::no_init)
    .add_property("epoch"               , &TrainDataPyWrapper::getEpoch                )
    .add_property("mseTrn"              , &TrainDataPyWrapper::getMseTrn               )
    .add_property("mseVal"              , &TrainDataPyWrapper::getMseVal               )
    .add_property("mseTst"              , &TrainDataPyWrapper::getMseTst               )
    .add_property("bestsp_point_sp_val" , &TrainDataPyWrapper::get_bestsp_point_sp_val )
    .add_property("bestsp_point_det_val", &TrainDataPyWrapper::get_bestsp_point_det_val)
    .add_property("bestsp_point_fa_val" , &TrainDataPyWrapper::get_bestsp_point_fa_val )
    .add_property("bestsp_point_sp_tst" , &TrainDataPyWrapper::get_bestsp_point_sp_tst )
    .add_property("bestsp_point_det_tst", &TrainDataPyWrapper::get_bestsp_point_det_tst)
    .add_property("bestsp_point_fa_tst" , &TrainDataPyWrapper::get_bestsp_point_fa_tst )
    .add_property("det_point_sp_val"    , &TrainDataPyWrapper::get_det_point_sp_val    )
    .add_property("det_point_det_val"   , &TrainDataPyWrapper::get_det_point_det_val   )
    .add_property("det_point_fa_val"    , &TrainDataPyWrapper::get_det_point_fa_val    )
    .add_property("det_point_sp_tst"    , &TrainDataPyWrapper::get_det_point_sp_tst    )
    .add_property("det_point_det_tst"   , &TrainDataPyWrapper::get_det_point_det_tst   )
    .add_property("det_point_fa_tst"    , &TrainDataPyWrapper::get_det_point_fa_tst    )
    .add_property("fa_point_sp_val"     , &TrainDataPyWrapper::get_fa_point_sp_val     )
    .add_property("fa_point_det_val"    , &TrainDataPyWrapper::get_fa_point_det_val    )
    .add_property("fa_point_fa_val"     , &TrainDataPyWrapper::get_fa_point_fa_val     )
    .add_property("fa_point_sp_tst"     , &TrainDataPyWrapper::get_fa_point_sp_tst     )
    .add_property("fa_point_det_tst"    , &TrainDataPyWrapper::get_fa_point_det_tst    )
    .add_property("fa_point_fa_tst"     , &TrainDataPyWrapper::get_fa_point_fa_tst     )
    .add_property("isBestMse"           , &TrainDataPyWrapper::getIsBestMse            )
    .add_property("isBestSP"            , &TrainDataPyWrapper::getIsBestSP             )
    .add_property("isBestDet"           , &TrainDataPyWrapper::getIsBestDet            )
    .add_property("isBestFa"            , &TrainDataPyWrapper::getIsBestFa             )
    .add_property("numFailsMse"         , &TrainDataPyWrapper::getNumFailsMse          )
    .add_property("numFailsSP"          , &TrainDataPyWrapper::getNumFailsSP           )
    .add_property("numFailsDet"         , &TrainDataPyWrapper::getNumFailsDet          )
    .add_property("numFailsFa"          , &TrainDataPyWrapper::getNumFailsFa           )
    .add_property("stopMse"             , &TrainDataPyWrapper::getStopMse              )
    .add_property("stopSP"              , &TrainDataPyWrapper::getStopSP               )
    .add_property("stopDet"             , &TrainDataPyWrapper::getStopDet              )
    .add_property("stopFa"              , &TrainDataPyWrapper::getStopFa               )
  ;
  return &_c;
}

//==============================================================================
//py::list npArray_genRoc( const np::ndarray &signal, const np::ndarray &background,
py::list npArray_genRoc( const py::numeric::array &signal, const py::numeric::array &background,
    REAL tSgn, REAL tBkg, REAL resolution )
{
  // Convert numpy arrays to std::vectors:
  auto* pSgn = reinterpret_cast<PyArrayObject*>(signal.ptr());
  auto* pBkg = reinterpret_cast<PyArrayObject*>(background.ptr());
  std::vector<REAL> vSgn(reinterpret_cast<REAL*>(pSgn->data), reinterpret_cast<REAL*>(pSgn->data) + PyArray_DIMS(pSgn)[0]),
                    vBkg(reinterpret_cast<REAL*>(pBkg->data), reinterpret_cast<REAL*>(pBkg->data) + PyArray_DIMS(pBkg)[0]);

  //Py_INCREF(pSgn); Py_INCREF(pBkg);
  //REAL *cSgn(nullptr), *cBkg(nullptr); 
  ////(PyObject** op, void* ptr, npy_intp* dims, int nd, int typenum, int itemsize)
  //// PyArray_AsCArray(PyObject **op, void *ptr, npy_intp *dims, int nd, PyArray_Descr* typedescr)
  ////PyArray_AsCArray(ppSgn, cSgn, PyArray_DIMS(paSgn), 1, PyArray_TYPE(paSgn), PyArray_ITEMSIZE(paSgn));
  //std::cout << "Signal dimensions are: " << PyArray_DIMS(pSgn) << std::endl;
  //std::cout << "Signal dimensions are: " << PyArray_DIMS(pSgn)[0] << std::endl;
  //PyArray_AsCArray(ppSgn, cSgn, PyArray_DIMS(pSgn), 1, PyArray_DESCR(pSgn));
  //PyArray_AsCArray(ppBkg, cBkg, PyArray_DIMS(pBkg), 1, PyArray_DESCR(pBkg));
  //std::vector<REAL> vSgn(signal.data(), signal.data() + PyArray_DIMS(pSgn)[0]), vBkg(cBkg, cBkg + PyArray_DIMS(pSgn)[0]);
  // TODO Need to check whether types are 
  std::vector<REAL> sp, det, fa, cut;
  util::genRoc( vSgn, vBkg, tSgn, tBkg, det, fa, sp, cut, resolution);

  py::list output;
  //npy_intp size[1] = {sp.size()};
  //npy_intp strides[1] = {1};
  // PyArray_New(PyTypeObject* subtype, int nd, npy_intp* dims, int type_num, npy_intp* strides, void* data, int itemsize, int flags, PyObject* obj)
  //PyObject* oSP = PyArray_New(&PyArray_Type, 1, size, NPY_FLOAT64, strides, sp.data(), sizeof(REAL)
  //                      , NPY_OWNDATA | NPY_CARRAY, NULL);
  auto oSP = util::vecToNumpyArray(sp);
  auto oDet = util::vecToNumpyArray(det);
  auto oFA = util::vecToNumpyArray(fa);
  auto oCut = util::vecToNumpyArray(cut);
  output.append( oSP  );
  output.append( oDet );
  output.append( oFA  );
  output.append( oCut );
  return output;
}

//==============================================================================
void expose_genRoc()
{
  py::list (*genRoc)( const py::numeric::array &, const py::numeric::array &, REAL tSgn, REAL tBkg, REAL resolution ) = npArray_genRoc;
  def("genRoc", genRoc);
}

//==============================================================================
py::object* expose_TuningToolPyWrapper()
{
  static py::object _c = py::class_<TuningToolPyWrapper>("TuningToolPyWrapper", 
                                                        py::no_init )
    .def( py::init<int>() )
    .def( py::init<int, bool>() )
    .def( py::init<int, bool, unsigned>() )
    .def("loadff"                 ,&TuningToolPyWrapper::loadff              )
    .def("newff"                  ,&TuningToolPyWrapper::newff               )
    .def("fusionff"               ,&TuningToolPyWrapper::fusionff            )
    .def("singletonInputNode"     ,&TuningToolPyWrapper::singletonInputNode  )
    .def("train_c"                ,&TuningToolPyWrapper::train_c             )
    .def("sim_c"                  ,&TuningToolPyWrapper::sim_c               )
    .def("valid_c"                ,&TuningToolPyWrapper::valid_c             )
    .def("showInfo"               ,&TuningToolPyWrapper::showInfo            )
    .def("setFrozenNode"          ,&TuningToolPyWrapper::setFrozenNode       )
    .def("setTrainData"           ,&TuningToolPyWrapper::setTrainData        )
    .def("setValData"             ,&TuningToolPyWrapper::setValData          )
    .def("setTestData"            ,&TuningToolPyWrapper::setTestData         )
    .def("setSeed"                ,&TuningToolPyWrapper::setSeed             )
    .def("getSeed"                ,&TuningToolPyWrapper::getSeed             )
    .add_property("showEvo"       ,&TuningToolPyWrapper::getShow
                                  ,&TuningToolPyWrapper::setShow             )
    .add_property("maxFail"       ,&TuningToolPyWrapper::getMaxFail
                                  ,&TuningToolPyWrapper::setMaxFail          )
    .add_property("batchSize"     ,&TuningToolPyWrapper::getBatchSize
                                  ,&TuningToolPyWrapper::setBatchSize        )
    .add_property("SPNoiseWeight" ,&TuningToolPyWrapper::getSPNoiseWeight
                                  ,&TuningToolPyWrapper::setSPNoiseWeight    )
    .add_property("SPSignalWeight",&TuningToolPyWrapper::getSPSignalWeight
                                  ,&TuningToolPyWrapper::setSPSignalWeight   )
    .add_property("learningRate"  ,&TuningToolPyWrapper::getLearningRate
                                  ,&TuningToolPyWrapper::setLearningRate     )
    .add_property("decFactor"     ,&TuningToolPyWrapper::getDecFactor
                                  ,&TuningToolPyWrapper::setDecFactor        )
    .add_property("deltaMax"      ,&TuningToolPyWrapper::getDeltaMax
                                  ,&TuningToolPyWrapper::setDeltaMax         )
    .add_property("deltaMin"      ,&TuningToolPyWrapper::getDeltaMin
                                  ,&TuningToolPyWrapper::setDeltaMin         )
    .add_property("incEta"        ,&TuningToolPyWrapper::getIncEta
                                  ,&TuningToolPyWrapper::setIncEta           )
    .add_property("decEta"        ,&TuningToolPyWrapper::getDecEta
                                  ,&TuningToolPyWrapper::setDecEta           )
    .add_property("initEta"       ,&TuningToolPyWrapper::getInitEta
                                  ,&TuningToolPyWrapper::setInitEta          )
    .add_property("epochs"        ,&TuningToolPyWrapper::getEpochs
                                  ,&TuningToolPyWrapper::setEpochs           )

    //Stop configurations
    .def("useMSE"                 ,&TuningToolPyWrapper::useMSE              )
    .def("useSP"                  ,&TuningToolPyWrapper::useSP               )

    .def("useAll"                 ,&TuningToolPyWrapper::useAll              )
    .add_property("det"           ,&TuningToolPyWrapper::getDet
                                  ,&TuningToolPyWrapper::setDet              )
    .add_property("fa"            ,&TuningToolPyWrapper::getFa
                                  ,&TuningToolPyWrapper::setFa               )
  ;

  return &_c;
}

}

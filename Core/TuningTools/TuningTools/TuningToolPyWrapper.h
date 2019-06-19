#ifndef TUNINGTOOLS_TUNINGTOOLSPYWRAPPER_H
#define TUNINGTOOLS_TUNINGTOOLSPYWRAPPER_H

// First include must be the defines, always!
#include "TuningTools/system/defines.h"

// STL include(s)
#include <iostream>
#include <string>
#include <vector>
#include <list>
#include <stdexcept>

// Boost include(s):
#include <boost/python.hpp>
namespace py = boost::python;

// Numpy include(s):
#include <numpy/ndarrayobject.h>
#include <numpy/arrayobject.h>

// Package include(s):
#include "TuningTools/system/util.h"
#include "TuningTools/system/macros.h"
#include "TuningTools/system/ndarray.h"
#include "TuningTools/neuralnetwork/NetConfHolder.h"
#include "TuningTools/neuralnetwork/Backpropagation.h"
#include "TuningTools/neuralnetwork/RProp.h"
#include "TuningTools/neuralnetwork/FeedForward.h"
#include "TuningTools/training/Standard.h"
#include "TuningTools/training/PatternRec.h"

// RingerCore include(s):
#include "Gaugi/MsgStream.h"

#define MIN_DELTA_VALUE       0.02
#define MAX_DELTA_VALUE       0.50
#define MIN_TRAIN_EPOCH       5

using namespace TuningTool;

struct WrongSizeError : public std::exception {                          
  const char* what() const throw() { return "Unsupported array size."; } 
};                                                                       
                                                                         
struct WrongTypeError : public std::exception {                          
  const char* what() const throw() { return "Unsupported array type."; } 
};                                                                       

namespace __expose_TuningToolPyWrapper__ 
{

// This is needed by boost::python for correctly importing numpy array
void __load_numpy();

// Boost::Python needs the translators                                   
void translate_sz(const WrongSizeError& e);
void translate_ty(const WrongTypeError& e);

// Exposure functions
void expose_exceptions();
void expose_multiply();
py::object* expose_DiscriminatorPyWrapper();
py::object* expose_TrainDataPyWrapper();
py::object* expose_TuningToolPyWrapper();

void expose_genRoc();

}

///Helper class
class TrainDataPyWrapper
{

  private:
   
    ValResult m_is_best_mse;
    ValResult m_is_best_sp;
    ValResult m_is_best_det;
    ValResult m_is_best_fa;
    unsigned m_epoch;
    unsigned m_num_fails_mse;
    unsigned m_num_fails_sp;
    unsigned m_num_fails_det;
    unsigned m_num_fails_fa;
    bool m_stop_mse;
    bool m_stop_sp;
    bool m_stop_det;
    bool m_stop_fa;

    //MSE_STOP, SP_STOP and MULTI_STOP
    REAL m_mse_trn;
    REAL m_mse_val;
    REAL m_mse_tst;
    //SP_STOP and MULTI_STOP
    REAL m_bestsp_point_sp_val;
    REAL m_bestsp_point_det_val;
    REAL m_bestsp_point_fa_val;
    REAL m_bestsp_point_sp_tst;
    REAL m_bestsp_point_det_tst;
    REAL m_bestsp_point_fa_tst;
    //SP_STOP and MULTI_STOP
    REAL m_det_point_sp_val;
    REAL m_det_point_det_val;
    REAL m_det_point_fa_val;
    REAL m_det_point_sp_tst;
    REAL m_det_point_det_tst;
    REAL m_det_point_fa_tst;
    //SP_STOP and MULTI_STOP
    REAL m_fa_point_sp_val;
    REAL m_fa_point_det_val;
    REAL m_fa_point_fa_val;
    REAL m_fa_point_sp_tst;
    REAL m_fa_point_det_tst;
    REAL m_fa_point_fa_tst;
 
  public:

    PRIMITIVE_SETTER_AND_GETTER(REAL      , setMseTrn, getMseTrn, m_mse_trn);
    PRIMITIVE_SETTER_AND_GETTER(REAL      , setMseVal, getMseVal, m_mse_val);
    PRIMITIVE_SETTER_AND_GETTER(REAL      , setMseTst, getMseTst, m_mse_tst);
    PRIMITIVE_SETTER_AND_GETTER(REAL      , set_bestsp_point_sp_val , get_bestsp_point_sp_val , m_bestsp_point_sp_val );
    PRIMITIVE_SETTER_AND_GETTER(REAL      , set_bestsp_point_det_val, get_bestsp_point_det_val, m_bestsp_point_det_val);
    PRIMITIVE_SETTER_AND_GETTER(REAL      , set_bestsp_point_fa_val , get_bestsp_point_fa_val , m_bestsp_point_fa_val ); 
    PRIMITIVE_SETTER_AND_GETTER(REAL      , set_bestsp_point_sp_tst , get_bestsp_point_sp_tst , m_bestsp_point_sp_tst );
    PRIMITIVE_SETTER_AND_GETTER(REAL      , set_bestsp_point_det_tst, get_bestsp_point_det_tst, m_bestsp_point_det_tst);
    PRIMITIVE_SETTER_AND_GETTER(REAL      , set_bestsp_point_fa_tst , get_bestsp_point_fa_tst , m_bestsp_point_fa_tst );
    PRIMITIVE_SETTER_AND_GETTER(REAL      , set_det_point_sp_val    , get_det_point_sp_val    , m_det_point_sp_val    );
    PRIMITIVE_SETTER_AND_GETTER(REAL      , set_det_point_det_val   , get_det_point_det_val   , m_det_point_det_val   );
    PRIMITIVE_SETTER_AND_GETTER(REAL      , set_det_point_fa_val    , get_det_point_fa_val    , m_det_point_fa_val    ); 
    PRIMITIVE_SETTER_AND_GETTER(REAL      , set_det_point_sp_tst    , get_det_point_sp_tst    , m_det_point_sp_tst    );
    PRIMITIVE_SETTER_AND_GETTER(REAL      , set_det_point_det_tst   , get_det_point_det_tst   , m_det_point_det_tst   );
    PRIMITIVE_SETTER_AND_GETTER(REAL      , set_det_point_fa_tst    , get_det_point_fa_tst    , m_det_point_fa_tst    );
    PRIMITIVE_SETTER_AND_GETTER(REAL      , set_fa_point_sp_val     , get_fa_point_sp_val     , m_fa_point_sp_val     );
    PRIMITIVE_SETTER_AND_GETTER(REAL      , set_fa_point_det_val    , get_fa_point_det_val    , m_fa_point_det_val    );
    PRIMITIVE_SETTER_AND_GETTER(REAL      , set_fa_point_fa_val     , get_fa_point_fa_val     , m_fa_point_fa_val     ); 
    PRIMITIVE_SETTER_AND_GETTER(REAL      , set_fa_point_sp_tst     , get_fa_point_sp_tst     , m_fa_point_sp_tst     );
    PRIMITIVE_SETTER_AND_GETTER(REAL      , set_fa_point_det_tst    , get_fa_point_det_tst    , m_fa_point_det_tst    );
    PRIMITIVE_SETTER_AND_GETTER(REAL      , set_fa_point_fa_tst     , get_fa_point_fa_tst     , m_fa_point_fa_tst     );
    PRIMITIVE_SETTER_AND_GETTER(unsigned  , setEpoch, getEpoch, m_epoch);
    PRIMITIVE_SETTER_AND_GETTER(unsigned  , setNumFailsMse, getNumFailsMse, m_num_fails_mse);
    PRIMITIVE_SETTER_AND_GETTER(unsigned  , setNumFailsSP, getNumFailsSP, m_num_fails_sp);
    PRIMITIVE_SETTER_AND_GETTER(unsigned  , setNumFailsDet, getNumFailsDet, m_num_fails_det);
    PRIMITIVE_SETTER_AND_GETTER(unsigned  , setNumFailsFa, getNumFailsFa, m_num_fails_fa);
    PRIMITIVE_SETTER_AND_GETTER(bool      , setStopMse, getStopMse, m_stop_mse);
    PRIMITIVE_SETTER_AND_GETTER(bool      , setStopSP, getStopSP, m_stop_sp);
    PRIMITIVE_SETTER_AND_GETTER(bool      , setStopDet, getStopDet, m_stop_det);
    PRIMITIVE_SETTER_AND_GETTER(bool      , setStopFa, getStopFa, m_stop_fa);
    
    PRIMITIVE_SETTER(ValResult , setIsBestMse, m_is_best_mse);
    PRIMITIVE_SETTER(ValResult , setIsBestSP,  m_is_best_sp);
    PRIMITIVE_SETTER(ValResult , setIsBestDet, m_is_best_det);
    PRIMITIVE_SETTER(ValResult , setIsBestFa,  m_is_best_fa);

    //Helper functions
    bool getIsBestMse(){ return (m_is_best_mse == BETTER)  ? true:false;}
    bool getIsBestSP(){  return (m_is_best_sp  == BETTER)  ? true:false;}
    bool getIsBestDet(){ return (m_is_best_det  == BETTER) ? true:false;}
    bool getIsBestFa(){  return (m_is_best_fa  == BETTER)  ? true:false;}

};

//==========================================================================================
//==========================================================================================
//==========================================================================================
//==========================================================================================
class DiscriminatorPyWrapper : public NeuralNetwork {
  protected:

    using NeuralNetwork::hyperbolicTangent;
    using NeuralNetwork::linear;

  public:

    DiscriminatorPyWrapper()
      : IMsgService("DiscriminatorPyWrapper"),
        NeuralNetwork(){;}

    DiscriminatorPyWrapper( const NeuralNetwork &net )
      : IMsgService("DiscriminatorPyWrapper"),
        NeuralNetwork(net){;}

    // TODO Add frozen nodes
    DiscriminatorPyWrapper(  const std::string& name,
        const unsigned lvl, const bool useColor,
        const py::list &nodes,  const py::list &trfFunc,
        const py::list &weights, const py::list &bias ):
      DiscriminatorPyWrapper( name, static_cast<MSG::Level>(lvl), useColor,
          nodes, trfFunc, weights, bias ){;}
    DiscriminatorPyWrapper( const std::string& name,
        const MSG::Level msgLevel, const bool useColor,
        const py::list &nodes,  const py::list &trfFunc,
        const py::list &weight, const py::list &bias);

    /**
     * @brief Propagate data in numpy array format
     **/
    PyObject* propagate_np( const py::numeric::array &data );

    ~DiscriminatorPyWrapper(){;}

};

/**
 * @class TuningToolPyWrapper
 * @brief Wrapper class for using C++ Fastnet on python
 *
 * @author Rodrigo Coura Torres <torres.rc@gmail.com>
 * @author Joao Victor da Fonseca Pinto <jodafons@cern.ch>
 * @author Werner Spolidoro Freund <wsfreund@cern.ch>
 *
 * The original TuningTool C++ core was implemented on:
 *
 * https://github.com/rctorres/tuningtool
 *
 * where it was integrated to matlab. In this new version, it is integrated
 * to python through this boost wrapper. 
 *
 **/
class TuningToolPyWrapper : public MsgService
{

  private:

    /// @name TuningToolPyWrapper Properties:
    /// @{
    /// @brief Holds each class training data
    std::vector< Ndarray<REAL,2>* > m_trnData;
    /// @brief Holds each class validation data
    std::vector< Ndarray<REAL,2>* > m_valData;
    /// @brief Holds each class test data
    std::vector< Ndarray<REAL,2>* > m_tstData;

    /// Last used seed used to feed pseudo-random generator
    unsigned m_seed;
    
    /// TuningTool Core
    /// @{ 
    /// @brief Neural Network interface
    NetConfHolder          m_net;
    /// @brief The backpropagation neural network
    Backpropagation       *m_trainNetwork;
    /// @brief The training algorithm
    Training              *m_train; 
    /// @brief Resulting neural networks to be saved
    std::vector< NeuralNetwork* > m_saveNetworks;
    /// @}

    /// Whether to use standard training
    bool m_stdTrainingType;

    /// Hold a list of TrainDataPyWrapper
    std::vector<TrainDataPyWrapper> m_trnEvolution;
    /// @}

    /// @name TuningToolPyWrapper private methods:
    /// @{
    /**
     * @brief Append training evolution to list
     **/
    void flushTrainEvolution( const std::list<TrainData*> &trnEvolution );

    /**
     * Allocate neural network with input configuration
     **/
    bool allocateNetwork( const py::list &nodes, 
        const py::list &trfFunc, 
        const std::string &trainFcn );

    /**
     * Set dataset input
     **/
    void setData( const py::list& data, 
      std::vector< Ndarray<REAL,2>* > TuningToolPyWrapper::* const setPtr );

    /**
     * @brief Release numpy holders 
     *
     * Be warned, however, that this doesn't release the numpy memory, which is 
     * expected to be managed by python.
     **/
    void releaseDataSet( std::vector< Ndarray<REAL,2>* > &vec )
    {
      for( auto* pattern : vec ) {
        delete pattern;
      }
      vec.clear();
    }

    /**
     * @brief propagate data throw neural network
     **/
    void sim( const DiscriminatorPyWrapper &net, 
        const Ndarray<REAL,2> *data,
        std::vector<float> &outputVec);

    /**
     * @brief Generate region of criteria
     **/
    py::list genRoc( const std::vector<REAL> &signalVec, 
        const std::vector<REAL> &noiseVec, 
        REAL resolution );

    /**
     * @brief Return a list of TrainDataPyWrapper
     **/
    py::list trainEvolutionToPyList()
    {
      py::list trainList;
      for( auto& trainDataPyWrapper : m_trnEvolution )
      {
        trainList.append( util::transfer_to_python( new TrainDataPyWrapper( trainDataPyWrapper ) ) );
      }
      return trainList;
    };

    /**
     * @brief Return a list of wrapped NeuralNetwork to python 
     **/
    void saveNetworksToPyList(py::list &list)
    {
      // Create a new lit
      py::list netList;
      // Append a list to the main list of objects
      list.append( netList );
#if defined(TUNINGTOOL_DBG_LEVEL) && TUNINGTOOL_DBG_LEVEL > 0
      int counter = 0;
#endif
      // This actually works because python list is a mutable object:
      for ( auto& net : m_saveNetworks ) 
      {
#if defined(TUNINGTOOL_DBG_LEVEL) && TUNINGTOOL_DBG_LEVEL > 0
        MSG_DEBUG("Appending neural network [" << counter++ << "] to list");
#endif
        // FIXME It would be nice if we could append a python memory handled
        // object to the python exposed wrapper:
        netList.append( util::transfer_to_python( new DiscriminatorPyWrapper( *net ) ) );
      }
    }
    /// @}

 public:
    
    /// Ctors and dtors
    ///@{
    TuningToolPyWrapper();
    TuningToolPyWrapper( const int msglevel );
    TuningToolPyWrapper( const int msglevel,
                         const bool useColor );
    TuningToolPyWrapper( const int msglevel,
                         const bool useColor,
                         const unsigned seed );
    virtual ~TuningToolPyWrapper();
    ///@}

    /**
     * Create new feed forward neural network
     **/
    bool newff( const py::list &nodes,
                const py::list &trfFunc,
                const std::string &trainFcn = TRAINRP_ID );

    /**
     * Crete data fusion feed forward neural network
     **/
    bool fusionff( const py::list &nodes, 
                   const py::list &weights,
                   const py::list &frozen,
                   const py::list &bias,
                   const py::list &trfFunc, 
                   const std::string &trainFcn );

    
    /**
     * Set node to pass input to hidden layer
     **/
    bool singletonInputNode( const unsigned nodeIdx, const unsigned pIdx );

    /**
     * Load feed forward neural network
     **/
    bool loadff( const py::list &nodes,  const py::list &trfFunc,
                 const py::list &weight, const py::list &bias,
                 const std::string &trainFcn = TRAINRP_ID);

    /**
     * Retrieve pseudo random-generator seed
     **/
    unsigned getSeed() const;

    /**
     * Reset random-generator and set new seed
     **/
    void setSeed( const unsigned seed = std::numeric_limits<unsigned int>::max());

    /**
     * @brief Train neural network
     *
     * This function return a list of networks and a list of TrainData
     * evolution. 
     *
     * If MSE_STOP or SP_STOP is enable, this will return a list with one
     * element. But in the other case, MULTI_STOP will return a list where: 
     *
     *     [network_stop_by_sp, network_stop_by_det, network_stop_by_fa]
     *
     * The train data evolution is a list of TrainDataPyWrapper and networks is
     * a list of DiscriminatorPyWrapper. Basically, the outputs are:
     *
     *     [list_of_DeiscriminatorPyWrapper, list_of_TrainDataPyWrapper]
     **/
    py::list train_c();

    /**
     * @brief Feed-forward the data input on network
     **/
    PyObject* sim_c( const DiscriminatorPyWrapper &net,
                     const py::numeric::array &data );

    /**
     * @brief Obtain the input datasets output propagated at neural network
     **/
    py::list valid_c( const DiscriminatorPyWrapper &net );
   
    /**
     * Show configuration information
     **/
    void showInfo();

    /**
     * Set training datasets
     **/
    void setTrainData( const py::list &data   );

    /**
     * Set validation dataset
     **/
    void setValData(   const py::list &data   );

    /**
     * Set test dataset
     **/
    void setTestData(  const py::list &data   );

    /**
     * @brief Frozen node for training.
     **/
    bool setFrozenNode(unsigned layer, unsigned node, bool status=true){
      return m_net.setFrozenNode(layer, node, status);
    };
    
    /// Goal train selection 
    /// @{
    /**
     * @brief Change goal to minimize MSE
     **/
    void useMSE(){  m_net.setTrainGoal( MSE_STOP );    };
    /**
     * @brief Change goal to maximize SP
     **/
    void useSP(){   m_net.setTrainGoal( SP_STOP );     };
    /**
     * @brief Change goal to maximize SP, maximize Pd, minimize Pf
     *
     * Using this criteria as the goal will return three discriminators as
     * output.
     **/
    void useAll(){  m_net.setTrainGoal( MULTI_STOP );  };
    /// @}

    /// Macros
    /// @{
    MEMBER_PRIMITIVE_SETTER_AND_GETTER ( m_net, REAL,        setSPSignalWeight, getSPSignalWeight );
    MEMBER_PRIMITIVE_SETTER_AND_GETTER ( m_net, REAL,        setSPNoiseWeight,  getSPNoiseWeight  );
    MEMBER_PRIMITIVE_SETTER_AND_GETTER ( m_net, unsigned,    setMaxFail,        getMaxFail        );
    MEMBER_PRIMITIVE_SETTER_AND_GETTER ( m_net, unsigned,    setBatchSize,      getBatchSize      );
    MEMBER_PRIMITIVE_SETTER_AND_GETTER ( m_net, unsigned,    setEpochs,         getEpochs         );
    MEMBER_PRIMITIVE_SETTER_AND_GETTER ( m_net, unsigned,    setShow,           getShow           );
    MEMBER_PRIMITIVE_SETTER_AND_GETTER ( m_net, REAL,        setLearningRate,   getLearningRate   );
    MEMBER_PRIMITIVE_SETTER_AND_GETTER ( m_net, REAL,        setDecFactor,      getDecFactor      );
    MEMBER_PRIMITIVE_SETTER_AND_GETTER ( m_net, REAL,        setDeltaMax,       getDeltaMax       );
    MEMBER_PRIMITIVE_SETTER_AND_GETTER ( m_net, REAL,        setDeltaMin,       getDeltaMin       );
    MEMBER_PRIMITIVE_SETTER_AND_GETTER ( m_net, REAL,        setIncEta,         getIncEta         );
    MEMBER_PRIMITIVE_SETTER_AND_GETTER ( m_net, REAL,        setDecEta,         getDecEta         );
    MEMBER_PRIMITIVE_SETTER_AND_GETTER ( m_net, REAL,        setInitEta,        getInitEta        );
    MEMBER_PRIMITIVE_SETTER_AND_GETTER ( m_net, REAL,        setDet,            getDet            );
    MEMBER_PRIMITIVE_SETTER_AND_GETTER ( m_net, REAL,        setFa,             getFa             );
    MEMBER_OBJECT_SETTER_AND_GETTER    ( m_net, std::string, setTrainFcn,       getTrainFcn       );
    /// @}
};


//==============================================================================
inline 
void TuningToolPyWrapper::setTrainData( const py::list& data )
{
  setData( data, &TuningToolPyWrapper::m_trnData );
}

//==============================================================================
inline
void TuningToolPyWrapper::setValData( const py::list &data )
{
  setData( data, &TuningToolPyWrapper::m_valData );
}

//==============================================================================
inline
void TuningToolPyWrapper::setTestData( const py::list &data )
{
  setData( data, &TuningToolPyWrapper::m_tstData );
}

// multiply matrix of float (m) by f                                    
py::object multiply(const py::numeric::array &m, float f);
py::object multiply(const py::list &list, float f);

#endif

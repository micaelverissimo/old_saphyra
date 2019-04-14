#ifndef TUNINGTOOLS_SYSTEM_INEURALNETWORK_H
#define TUNINGTOOLS_SYSTEM_INEURALNETWORK_H

#include "TuningTools/system/defines.h"

#include <vector>
#include <string>
#include <iostream> 

#include "Gaugi/MsgStream.h"
#include "TuningTools/system/macros.h"

namespace TuningTool {

//Interface Classes
class NetConfHolder : public MsgService {

  private:
    ///Network struct parameters
    std::vector<unsigned>       m_nNodes;
    std::vector<std::string>    m_trfFuncStr;
    std::vector<bool>           m_usingBias;
    std::vector< std::vector<bool> > m_frozenNodes;

    /// @{
    /// Training parameters
    std::string m_trainFcn  = TRAINRP_ID;
    REAL m_learningRate     = 0.05;
    REAL m_decFactor        = 1;
    REAL m_deltaMax         = 50;
    REAL m_deltaMin         = 1E-6;
    REAL m_incEta           = 1.10;
    REAL m_decEta           = 0.5;
    REAL m_initEta          = 0.1;
    TrainGoal m_trainGoal   = MSE_STOP;
    unsigned m_maxFail      = 50;
    unsigned m_nEpochs      = 1000;
    unsigned m_batchSize    = 10;
    unsigned m_show         = 2;
    REAL m_sp_signal_weight = 1;  
    REAL m_sp_noise_weight  = 1;
    //Custom stop train parameters
    REAL m_detReference     = 1.0;
    REAL m_faReference      = 0.0;

    /// @}

  public:
    /**
     * @brief Defaul constructor
     *
     * This configuration holder has every information which will be used to
     * set the network struct. This single constructor are inplemented to build
     * a single network with three layers.
     **/
    NetConfHolder( MSG::Level level = MSG::INFO ) 
      : IMsgService("NetConfHolder", MSG::INFO ),
        MsgService( level ){;}
    
    
    /**
     * Set neural network configuration nodes
     **/
    void setNodes( std::vector<unsigned> nodes ){
      m_nNodes = nodes;
      m_usingBias.clear();
      m_frozenNodes.clear();

      for(unsigned i=0; i < m_nNodes.size()-1; ++i){
        m_usingBias.push_back(true);
      }

      //Initialize frozen nodes status with false
      for(unsigned layer=0; layer<m_nNodes.size()-1; ++layer){
        std::vector<bool> nodes;
        for(unsigned node=0; node<m_nNodes[layer+1]; ++node){
          nodes.push_back(false);
        }  
        m_frozenNodes.push_back(nodes);
      }
    };
    
    /**
     * Set a layer number to use bias
     **/
    void setUsingBias(unsigned layer, bool status = true){
      m_usingBias[layer] = status;
    }

    /**
     * @brief Set neural network frozen nodes.
     **/
    bool setFrozenNode(unsigned layer, unsigned node, bool status=true){
      //Add some protections
      if(layer < 1 || layer > m_nNodes.size()){
        MSG_ERROR("Invalid layer for frozen status.");
        return false;
      }
      if(node > m_nNodes[layer]){
        MSG_ERROR("Invalid node for frozen status.");
        return false;
      }
      m_frozenNodes[layer][node] = status;
      return true;
    };

    /// Return frozen status
    bool isFrozenNode(unsigned layer, unsigned node) const 
    {
      return m_frozenNodes[layer][node];
    }

    /// Return the layer bias status. The dafault is true
    bool isUsingBias(unsigned layer) const 
    {
      return m_usingBias[layer];
    }

    /// Return the nNodes std::vector
    std::vector<unsigned> getNodes() const 
    {
      return m_nNodes;
    }

    /// Return the number of nodes into the layer.
    unsigned getNumberOfNodes(unsigned layer=0) const 
    {
      return m_nNodes[layer];
    }

    /// Return the max number of layer.
    unsigned getNumberOfLayers() const {
      return m_nNodes.size();
    }

    /// Return the tranfer function.
    std::string getTrfFuncStr(unsigned layer) const 
    {
      return m_trfFuncStr[layer];
    }
    
    /// Define get and setter for the properties
    OBJECT_SETTER_AND_GETTER(std::string, setTrainFcn     , getTrainFcn           , m_trainFcn            );      
    PRIMITIVE_SETTER_AND_GETTER(TrainGoal, setTrainGoal   , getTrainGoal          , m_trainGoal           );      
    PRIMITIVE_SETTER_AND_GETTER(REAL, setMaxFail          , getMaxFail            , m_maxFail             );      
    PRIMITIVE_SETTER_AND_GETTER(REAL, setSPSignalWeight   , getSPSignalWeight     , m_sp_signal_weight    );      
    PRIMITIVE_SETTER_AND_GETTER(REAL, setSPNoiseWeight    , getSPNoiseWeight      , m_sp_noise_weight     );      
    PRIMITIVE_SETTER_AND_GETTER(REAL, setLearningRate     , getLearningRate       , m_learningRate        );      
    PRIMITIVE_SETTER_AND_GETTER(REAL, setDecFactor        , getDecFactor          , m_decFactor           );      
    PRIMITIVE_SETTER_AND_GETTER(REAL, setDeltaMax         , getDeltaMax           , m_deltaMax            );      
    PRIMITIVE_SETTER_AND_GETTER(REAL, setDeltaMin         , getDeltaMin           , m_deltaMin            );      
    PRIMITIVE_SETTER_AND_GETTER(REAL, setIncEta           , getIncEta             , m_incEta              );      
    PRIMITIVE_SETTER_AND_GETTER(REAL, setDecEta           , getDecEta             , m_decEta              );      
    PRIMITIVE_SETTER_AND_GETTER(REAL, setInitEta          , getInitEta            , m_initEta             );      
    PRIMITIVE_SETTER_AND_GETTER(REAL, setEpochs           , getEpochs             , m_nEpochs             );      
    PRIMITIVE_SETTER_AND_GETTER(REAL, setBatchSize        , getBatchSize          , m_batchSize           );      
    PRIMITIVE_SETTER_AND_GETTER(REAL, setShow             , getShow               , m_show                );      
    PRIMITIVE_SETTER_AND_GETTER(REAL, setDet              , getDet                , m_detReference        );      
    PRIMITIVE_SETTER_AND_GETTER(REAL, setFa               , getFa                 , m_faReference         );      
    PRIMITIVE_SETTER_AND_GETTER(std::vector<std::string>, setTrfFunc   , getTrfFunc    , m_trfFuncStr     );      
};


}
#endif

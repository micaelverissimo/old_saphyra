#ifndef TUNINGTOOLS_DEFINES_H
#define TUNINGTOOLS_DEFINES_H

#include <string>

// Boost include(s):
#include <boost/python.hpp>

// Numpy include(s):
#include <numpy/ndarraytypes.h>

/**
 * Define DBG_LEVEL if this package is on debug mode
 **/
#if defined(TUNINGTOOL_DBG_LEVEL)
# ifndef DBG_LEVEL
# define DBG_LEVEL TUNINGTOOL_DBG_LEVEL
# endif
#endif

#include "Gaugi/defines.h"

/**
 * @brief Specifies the version of the TuningTool package.
 *
 * This define must be used every time the TuningTool package version must be
 * presented.
 **/
const std::string TUNINGTOOL_VERSION = "1.01";

/** 
 * @brief Implements a very simple exception class for file opening errors.
 *
 * This typedef is used within a try/catch block to report a file opening
 * error.
 **/
typedef const char* OPEN_FILE_ERROR;

/** 
 * @brief Implements a very simple exception class for data initialization
 *        errors.
 * This typedef is used within a try/catch block to report data initialization
 * errors.
 **/
typedef const char* DATA_INIT_ERROR;

/**
 * @brief The file open error exception message.
 * This message should be presented when a open file error exception occurs.
 **/
const std::string OPEN_FILE_ERROR_MSG = "Impossible to open one or more files!";


/**
 * @brief Default size for vectors containing strings.
 *
 * This constant should be used when a vector that will hold long strings, like
 * file names, for instance, must be created. 
 **/
#define LINE_SIZE 500


/// Default value for small general use vectors.
#define SIZE 20

/**
 * @brief Default floating point word size.
 * This data type must be used in ALL floating point variable declaration, so, by
 * simply changing its value we can easily change thw word size of all floating
 * point variables created.
 **/
typedef float REAL;

/**
 * @class npy_enum_from_type
 * @brief Primary Template for wrapping type to its numpy enum type valeu
 *
 * Use type_to_npy_enum<type>::enum_val to obtain the correspondent npy enum
 * value. If the type is unknown or not declared, you will get a compilation
 * error telling type_to_npy_enum does not have enum_val member.
 *
 **/
template<typename T>
struct type_to_npy_enum {};

/**
 * @brief Specialization for float enum.
 **/
template<>
struct type_to_npy_enum< float > {
  static constexpr NPY_TYPES enum_val = NPY_FLOAT;
  static constexpr char ctypes_char = 'f';
};

/**
 * @brief Specialization for double enum.
 **/
template<>
struct type_to_npy_enum< double > {
  static constexpr NPY_TYPES enum_val = NPY_DOUBLE;
  static constexpr char ctypes_char = 'd';
};


/**
 * @brief Macro to call pointers to member functions.
 *
 * Use this macro to call pointer to member functions. In order to improve
 * speed the transfer functions are stored in pointer to functions, and this
 * macro makes easy to call these pointers.
 *
 * @param[in] ptrToTrfFunc pointer pointing to the member function you want to call.
 **/
#define CALL_TRF_FUNC(ptrToTrfFunc)  ((this)->*(ptrToTrfFunc))


/**
 * @brief String ID for the hyperbolic tangent transfer function.
 *
 * This is the only ID for the hyperbolic tangent function for files, so, every
 * time that a file wants to make a reference that it will use this function, this
 * reference is done by this value.
 **/
const std::string TGH_ID = "tansig";


/**
 * @brief String ID for the linear transfer function.
 *
 * This is the only ID for the linear transfer function for files, so, every time
 * that a file wants to make a reference that it will use this function, this
 * reference is done by this value.
 **/
const std::string LIN_ID = "purelin";


/**
 * @brief String ID for the Gradient Descendent Backpropagation neural training.
 *
 * This is the only ID for the Gradient Descendent Backpropagation neural
 * training for files, so, every time that a file wants to make a reference
 * that it will use this training, this reference is done by this value.
 * */
const std::string TRAINGD_ID = "traingd";


/**
 * @brief String ID for the Resilient Backpropagation neural training.
 *
 * This is the only ID for the Resilient Backpropagation neural training for
 * files, so, every time that a file wants to make a reference that it will use
 * this training, this reference is done by this value.
 **/
const std::string TRAINRP_ID = "trainrp";


/// String ID used to inform that no value has been supplied.
const std::string NONE_ID = "NONE";

/**
 * @brief Macro to calculate the square of a number.
 *
 * @param[in] x the value which the square value you want to evaluate.
 **/
#define SQR(x) ((x)*(x))


/**
 * Number min of epochs. This is useful to scape of the case where the fa or pd
 * are max becouse the error and some cases.
 **/
const unsigned NUMBER_MIN_OF_EPOCHS = 5;

/// This is the position into a std::vector that will be hold the save
/// networks during the training step.
/// @{
const unsigned TRAINNET_DEFAULT_ID = 0;
const unsigned TRAINNET_DET_ID     = 1;
const unsigned TRAINNET_FA_ID      = 2;
/// @}

/**
 * Train mode 
 **/ 
enum TrainGoal{
  MSE_STOP   = 0,
  SP_STOP    = 1,
  MULTI_STOP = 2,
};

#endif

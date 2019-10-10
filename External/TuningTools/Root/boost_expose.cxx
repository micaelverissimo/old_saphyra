// Boost include(s):
#include <boost/python.hpp>

#include "TuningTools/TuningToolPyWrapper.h"
#include "TuningTools/system/util.h"

#ifndef __TUNINGTOOLS_LIBRARY_NAME__
#define __TUNINGTOOLS_LIBRARY_NAME__ libTuningTools
#endif

/// BOOST module
BOOST_PYTHON_MODULE(__TUNINGTOOLS_LIBRARY_NAME__)
{

  __expose_TuningToolPyWrapper__::__load_numpy();
  __expose_system_util__::__load_numpy();

  __expose_TuningToolPyWrapper__::expose_exceptions();

  __expose_TuningToolPyWrapper__::expose_multiply();

  __expose_TuningToolPyWrapper__::expose_DiscriminatorPyWrapper();
  __expose_TuningToolPyWrapper__::expose_TrainDataPyWrapper();
  __expose_TuningToolPyWrapper__::expose_TuningToolPyWrapper();
  __expose_TuningToolPyWrapper__::expose_genRoc();
}

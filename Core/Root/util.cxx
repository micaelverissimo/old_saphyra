// Local include(s):
#include "TuningTools/system/util.h"
#include "TuningTools/system/defines.h"
#include "TuningTools/system/ndarray.h"

// Boost include(s):
#include <boost/python.hpp>

// Numpy include(s):
#include <numpy/ndarrayobject.h>
#include <numpy/arrayobject.h>

// STL include(s):
#include <vector>
#include <string>

namespace __expose_system_util__ {

//==============================================================================
void __load_numpy(){
  py::numeric::array::set_module_and_type("numpy", "ndarray");
  import_array();
} 

}

namespace util
{


//==============================================================================
float rand_float_range(float min, float max){
  return  (max - min) * ((((float) std::rand()) / (float) RAND_MAX)) + min ;
}

//==============================================================================
REAL get_norm_of_weight( REAL *weight , size_t size){
  
  REAL sum=0;
  for(size_t i=0; i < size; ++i){
    sum += pow(weight[i],2);
  }
  return sqrt(sum);
}

//==============================================================================
void genRoc( const std::vector<REAL> &signal, 
    const std::vector<REAL> &noise, 
    REAL signalTarget, REAL noiseTarget, 
    std::vector<REAL> &det,  std::vector<REAL> &fa, 
    std::vector<REAL> &sp, std::vector<REAL> &cut, 
    const REAL RESOLUTION, 
    REAL signalWeight,
    REAL noiseWeight)
{
  const unsigned nSignal = signal.size();
  const unsigned nNoise  = noise.size();
  const REAL* sPtr = signal.data();
  const REAL* nPtr = noise.data();
  unsigned i(0);

#ifdef USE_OMP
  int chunk = 10000;
#endif

  for (REAL pos = noiseTarget; pos < signalTarget; pos += RESOLUTION)
  {
    REAL sigEffic = 0.;
    REAL noiseEffic = 0.;
    unsigned se, ne;
#ifdef USE_OMP
    #pragma omp parallel shared(sPtr, nPtr, sigEffic, noiseEffic) private(i,se,ne)
#endif
    {
      se = ne = 0;
#ifdef USE_OMP
      #pragma omp for schedule(dynamic,chunk) nowait
#endif
      for (i=0; i<nSignal; i++) if (sPtr[i] >= pos) se++;
      
#ifdef USE_OMP
      #pragma omp critical
#endif
      sigEffic += static_cast<REAL>(se);

#ifdef USE_OMP
      #pragma omp for schedule(dynamic,chunk) nowait
#endif
      for (i=0; i<nNoise; i++) if (nPtr[i] < pos) ne++;
      
#ifdef USE_OMP
      #pragma omp critical
#endif
      noiseEffic += static_cast<REAL>(ne);
    }
    
    sigEffic /= static_cast<REAL>(nSignal);
    noiseEffic /= static_cast<REAL>(nNoise);

    // Use weights for signal and noise efficiencies
    sigEffic *= signalWeight;
    noiseEffic *= noiseWeight;

    //Using normalized SP calculation.
    sp.push_back( sqrt( ((sigEffic + noiseEffic) / 2) * sqrt(sigEffic * noiseEffic) ) );
    det.push_back( sigEffic );
    fa.push_back( 1-noiseEffic );
    cut.push_back( pos );
  }
}

//==============================================================================
py::handle<PyObject> get_np_array( const py::numeric::array &pyObj, int ndims ) 
{
  // Make sure that the input type is a numpy array:
  if ( static_cast<std::string>(py::extract<std::string>(
          pyObj.attr("__class__").attr("__name__"))) != "ndarray")
  {
    throw std::runtime_error( "Input an object of type " 
        + static_cast<std::string>(
          py::extract<std::string>(pyObj.attr("__class__").attr("__name__") ))
        + " which is an non numpy.ndarray object.");
  }
  // holds the correct type:
  char type = static_cast<char>(py::extract<char>(
        pyObj.attr("dtype").attr("char")));
  if ( type != type_to_npy_enum<REAL>::ctypes_char )
  {
    throw std::runtime_error(std::string("numpy.ndarray is of type ")
        + std::string("").append(1, type ) 
        + "and does not match floating point type defined at compile "
        "time. Please, input a numpy array of typechar('"
        + std::string("").append(1, type_to_npy_enum<REAL>::ctypes_char) 
        + "')");
  }
  // Create numpy object:
  PyObject* numpy = PyArray_FROM_OTF(pyObj.ptr()
                       , NPY_FLOAT
                       , NPY_IN_ARRAY  // Make sure that object is continuous
                      );
  if ( ! numpy ) {
    throw std::runtime_error("Couldn't create numpy array from input object!");
  }

  py::handle<PyObject> ptr(numpy);
  // Check if it is of right dimension:
  if ( PyArray_NDIM( numpy ) != ndims ) 
  {
    throw std::runtime_error("Data dimensions do not match required type.");
  }
  return ptr;
}

} // namespace util

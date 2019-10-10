#ifndef TUNINGTOOLS_UTIL_H
#define TUNINGTOOLS_UTIL_H

#include <boost/python.hpp>
#include <algorithm>
#include <ctime>
#include <cstdlib>
#include <iostream>
#include <vector>
#include <map>
#include "math.h"

// Define system variables
#include "TuningTools/system/defines.h"

// Numpy include(s):
#include <numpy/ndarrayobject.h>
#include <numpy/arrayobject.h>

// Python boost
#include <boost/python/stl_iterator.hpp>
namespace py = boost::python;

namespace __expose_system_util__ 
{
/// This is needed by boost::python to correctly import numpy array.
void __load_numpy();
}

namespace util
{

//==============================================================================
template< typename T >
inline 
std::vector< T > to_std_vector( const py::object& iterable )
{
  return std::vector< T >( py::stl_input_iterator< T >( iterable ), 
      py::stl_input_iterator< T >( ) );
}

template< typename T>
inline py::object vecToNumpyArray(std::vector<T> const& vec, int np_type = NPY_FLOAT32 )
{
  npy_intp size = vec.size();
  T* data = size ? const_cast<T*>(&vec[0]) : static_cast<T*>(NULL);
  PyObject * pyObj = PyArray_SimpleNewFromData(1, &size, np_type, data);
  py::handle<> handle ( pyObj );
  py::numeric::array arr(static_cast<py::numeric::array>(handle));
  return arr.copy();
}

//==============================================================================
template< typename T >
inline 
void convert_to_array_and_copy( const py::object& iterable, T* &array )
{
  std::vector<T> aux = std::vector<T>(
      py::stl_input_iterator< T >( iterable ), 
      py::stl_input_iterator< T >( ) );
  memcpy( array, aux.data(), aux.size()*sizeof(T) );
}

//==============================================================================
template <class T>
inline
py::list std_vector_to_py_list(std::vector<T> vec) 
{
  typename std::vector<T>::iterator iter;
  boost::python::list list;
  for (iter = vec.begin(); iter != vec.end(); ++iter) {
    list.append(*iter);
  }
  return list;
}

//==============================================================================
template< typename T >
inline
void cat_std_vector( std::vector<T> a, std::vector<T> &b)
{
  b.insert( b.end(),a.begin(), a.end() );
}

/// Return a float random number between min and max value
/// This function will be used to generate the weight random numbers
float rand_float_range(float min = -1.0, float max = 1.0);

/// Return the norm of the weight
REAL get_norm_of_weight( REAL *weight , size_t size);

/// Fill roc values from target values
void genRoc( const std::vector<REAL> &signal, 
    const std::vector<REAL> &noise, 
    REAL signalTarget, REAL noiseTarget, 
    std::vector<REAL> &det,  std::vector<REAL> &fa, 
    std::vector<REAL> &sp, std::vector<REAL> &cut, 
    const REAL RESOLUTION = 0.01, 
    REAL signalWeight = 1,
    REAL noiseWeight = 1);

/// Check whether numpy array representation is correct
py::handle<PyObject> get_np_array( const py::numeric::array &pyObj, 
                                   int ndim = 2 );


/// @brief Transfer ownership to a Python object.  If the transfer fails,
///        then object will be destroyed and an exception is thrown.
/// See http://stackoverflow.com/a/32291471/1162884 for more details.
template <typename T>
py::object transfer_to_python(T* t)
{
  // Transfer ownership to a smart pointer, allowing for proper cleanup
  // incase Boost.Python throws.
  std::unique_ptr<T> ptr(t);

  // Create a functor with a call policy that will have Boost.Python
  // manage the new object, then invoke it.
  py::object object = py::make_function(
    [t]() { return t; },
    py::return_value_policy<py::manage_new_object>(),
    boost::mpl::vector<T*>())();

  // As the Python object now has ownership, release ownership from
  // the smart pointer.
  ptr.release();
  return object;
}
 
} // namespace util


#endif
